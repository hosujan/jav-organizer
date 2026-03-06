"""
jav-web — local frontend for scanning a video directory and building a library.

Flow:
1) choose local video directory
2) process files one by one (metadata -> sqlite, media -> local media folder)
3) browse library with poster + hover preview
4) open local playback page
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from .config import DELAY, MEDIA_DIR, open_db
from .media import download_media, save_media_urls, scrape_media_urls
from .scraper import fetch_detail, search_id, upsert_video


VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".m4v", ".ts", ".webm",
}
JAV_ID_RE = re.compile(r"([a-z]{2,10})[-_ ]?(\d{2,5})", re.IGNORECASE)


def normalize_jav_id(text: str) -> str | None:
    m = JAV_ID_RE.search(text)
    if not m:
        return None
    return f"{m.group(1).upper()}-{m.group(2)}"


def scan_video_files(base_dir: Path) -> list[dict]:
    seen: set[str] = set()
    items: list[dict] = []
    for p in sorted(base_dir.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in VIDEO_EXTENSIONS:
            continue
        jav_id = normalize_jav_id(p.stem) or normalize_jav_id(str(p))
        if not jav_id or jav_id in seen:
            continue
        seen.add(jav_id)
        items.append({
            "jav_id": jav_id,
            "file_path": str(p.resolve()),
            "file_name": p.name,
        })
    return items


def choose_directory_dialog() -> str | None:
    # macOS AppKit requires UI windows on the main thread.
    if threading.current_thread() is not threading.main_thread():
        return None
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None
    root = tk.Tk()
    root.withdraw()
    root.update()
    path = filedialog.askdirectory(title="Select video directory")
    root.destroy()
    return path or None


def _first_existing(patterns: list[Path]) -> Path | None:
    for pat in patterns:
        matches = sorted(pat.parent.glob(pat.name))
        if matches:
            return matches[0]
    return None


@dataclass
class AppState:
    db_path: Path
    media_dir: Path
    selected_dir: Path | None = None
    items: list[dict] = field(default_factory=list)
    processing: bool = False
    processed: int = 0
    total: int = 0
    current: str | None = None
    logs: list[str] = field(default_factory=list)
    worker: threading.Thread | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)

    def add_log(self, msg: str):
        with self.lock:
            self.logs.append(msg)
            self.logs = self.logs[-300:]

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "selected_dir": str(self.selected_dir) if self.selected_dir else None,
                "processing": self.processing,
                "processed": self.processed,
                "total": self.total,
                "current": self.current,
                "logs": list(self.logs[-80:]),
                "items": list(self.items),
            }


def process_queue(state: AppState):
    with state.lock:
        state.processing = True
        state.processed = 0
        state.total = len(state.items)
        state.current = None
    state.add_log(f"[START] processing {state.total} video(s)")

    conn = open_db(state.db_path)
    try:
        for idx, item in enumerate(state.items, 1):
            jav_id = item["jav_id"]
            with state.lock:
                state.current = jav_id
            state.add_log(f"[{idx}/{state.total}] {jav_id} begin")

            try:
                url = search_id(jav_id)
                if not url:
                    state.add_log(f"[WARN] {jav_id} search failed")
                    continue

                data = fetch_detail(url, jav_id)
                if not data:
                    state.add_log(f"[WARN] {jav_id} detail fetch failed")
                    continue

                upsert_video(conn, data)
                conn.execute(
                    "UPDATE videos SET local_video_path=? WHERE jav_id=?",
                    (item["file_path"], jav_id),
                )
                conn.commit()

                media = scrape_media_urls(jav_id)
                save_media_urls(conn, jav_id, media)
                download_media(jav_id, media, state.media_dir)
                state.add_log(f"[OK] {jav_id}")
            except Exception as e:
                state.add_log(f"[ERROR] {jav_id} {e}")
            finally:
                with state.lock:
                    state.processed = idx
                time.sleep(DELAY)
    finally:
        conn.close()
        with state.lock:
            state.processing = False
            state.current = None
        state.add_log("[DONE] processing finished")


class AppHandler(BaseHTTPRequestHandler):
    state: AppState

    def log_message(self, format: str, *args):
        return

    def _json(self, payload: dict | list, code: int = 200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _text(self, body: str, code: int = 200, ctype: str = "text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _safe_under(self, path: Path, root: Path) -> bool:
        try:
            path.resolve().relative_to(root.resolve())
            return True
        except Exception:
            return False

    def _serve_file(self, path: Path, allow_range: bool = False):
        if not path.exists() or not path.is_file():
            self.send_error(404, "not found")
            return

        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        size = path.stat().st_size
        range_header = self.headers.get("Range")

        if allow_range and range_header:
            m = re.match(r"bytes=(\d*)-(\d*)", range_header.strip())
            if not m:
                self.send_error(416, "invalid range")
                return
            start_str, end_str = m.groups()
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else size - 1
            if start > end or end >= size:
                self.send_error(416, "range not satisfiable")
                return
            length = end - start + 1

            self.send_response(206)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(length))
            self.end_headers()

            with path.open("rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(1024 * 64, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
            return

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        if allow_range:
            self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(size))
        self.end_headers()
        with path.open("rb") as f:
            while True:
                chunk = f.read(1024 * 64)
                if not chunk:
                    break
                self.wfile.write(chunk)

    def _query(self) -> dict[str, list[str]]:
        return parse_qs(urlparse(self.path).query)

    def _load_videos(self) -> list[dict]:
        conn = open_db(self.state.db_path)
        try:
            rows = conn.execute("""
                SELECT jav_id, title, release_date, publisher, local_video_path,
                       poster_url, preview_mp4_url
                FROM videos
                WHERE local_video_path IS NOT NULL
                ORDER BY release_date DESC, jav_id DESC
            """).fetchall()
            out: list[dict] = []
            for r in rows:
                media_dir = self.state.media_dir / r["jav_id"]
                poster_local = _first_existing([
                    media_dir / "poster.jpg",
                    media_dir / "poster.jpeg",
                    media_dir / "poster.png",
                    media_dir / "poster.webp",
                ])
                preview_local = media_dir / "preview.mp4"
                out.append({
                    "jav_id": r["jav_id"],
                    "title": r["title"],
                    "release_date": r["release_date"],
                    "publisher": r["publisher"],
                    "has_local_video": bool(r["local_video_path"]),
                    "poster_url": f"/api/poster?id={quote(r['jav_id'])}",
                    "preview_url": f"/api/preview?id={quote(r['jav_id'])}",
                    "has_poster_local": bool(poster_local),
                    "has_preview_local": preview_local.exists(),
                })
            return out
        finally:
            conn.close()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._text(INDEX_HTML)
            return
        if path.startswith("/watch/"):
            jav_id = unquote(path.split("/watch/", 1)[1]).upper()
            self._text(WATCH_HTML.replace("__JAV_ID__", jav_id))
            return
        if path == "/api/state":
            self._json(self.state.snapshot())
            return
        if path == "/api/videos":
            self._json(self._load_videos())
            return
        if path == "/api/poster":
            q = self._query()
            jav_id = (q.get("id") or [""])[0].upper()
            if not jav_id:
                self.send_error(400, "missing id")
                return
            media_dir = self.state.media_dir / jav_id
            poster = _first_existing([
                media_dir / "poster.jpg",
                media_dir / "poster.jpeg",
                media_dir / "poster.png",
                media_dir / "poster.webp",
            ])
            if poster:
                self._serve_file(poster)
                return
            conn = open_db(self.state.db_path)
            try:
                row = conn.execute(
                    "SELECT poster_url FROM videos WHERE jav_id=?",
                    (jav_id,),
                ).fetchone()
            finally:
                conn.close()
            if row and row["poster_url"]:
                self.send_response(302)
                self.send_header("Location", row["poster_url"])
                self.end_headers()
                return
            self.send_error(404, "poster not found")
            return
        if path == "/api/preview":
            q = self._query()
            jav_id = (q.get("id") or [""])[0].upper()
            if not jav_id:
                self.send_error(400, "missing id")
                return
            preview = self.state.media_dir / jav_id / "preview.mp4"
            if preview.exists():
                self._serve_file(preview, allow_range=True)
                return
            conn = open_db(self.state.db_path)
            try:
                row = conn.execute(
                    "SELECT preview_mp4_url FROM videos WHERE jav_id=?",
                    (jav_id,),
                ).fetchone()
            finally:
                conn.close()
            if row and row["preview_mp4_url"]:
                self.send_response(302)
                self.send_header("Location", row["preview_mp4_url"])
                self.end_headers()
                return
            self.send_error(404, "preview not found")
            return
        if path == "/api/local-video":
            q = self._query()
            jav_id = (q.get("id") or [""])[0].upper()
            if not jav_id:
                self.send_error(400, "missing id")
                return
            conn = open_db(self.state.db_path)
            try:
                row = conn.execute(
                    "SELECT local_video_path FROM videos WHERE jav_id=?",
                    (jav_id,),
                ).fetchone()
            finally:
                conn.close()
            if not row or not row["local_video_path"]:
                self.send_error(404, "local video not found")
                return
            video_path = Path(row["local_video_path"])
            if not self.state.selected_dir or not self._safe_under(video_path, self.state.selected_dir):
                self.send_error(403, "video path outside selected directory")
                return
            self._serve_file(video_path, allow_range=True)
            return

        self.send_error(404, "not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", "0"))
        body_raw = self.rfile.read(content_length) if content_length else b"{}"
        try:
            body = json.loads(body_raw.decode("utf-8"))
        except Exception:
            body = {}

        if path == "/api/select-directory":
            chosen = choose_directory_dialog()
            if not chosen:
                chosen = (body.get("path") or "").strip()
            if not chosen:
                self._json(
                    {
                        "ok": False,
                        "error": "native folder picker unavailable here; please enter path manually",
                    },
                    400,
                )
                return
            folder = Path(chosen).expanduser().resolve()
            if not folder.exists() or not folder.is_dir():
                self._json({"ok": False, "error": "invalid directory"}, 400)
                return

            items = scan_video_files(folder)
            with self.state.lock:
                self.state.selected_dir = folder
                self.state.items = items
                self.state.processed = 0
                self.state.total = len(items)
                self.state.current = None
                self.state.logs = []
            self.state.add_log(f"[SCAN] {len(items)} file(s) with JAV IDs in {folder}")
            self._json({"ok": True, "selected_dir": str(folder), "count": len(items)})
            return

        if path == "/api/process":
            with self.state.lock:
                if self.state.processing:
                    self._json({"ok": False, "error": "processing already running"}, 400)
                    return
                if not self.state.items:
                    self._json({"ok": False, "error": "no scanned videos"}, 400)
                    return
                t = threading.Thread(target=process_queue, args=(self.state,), daemon=True)
                self.state.worker = t
                t.start()
            self._json({"ok": True})
            return

        self.send_error(404, "not found")


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>JAV Organizer</title>
  <style>
    :root {
      --bg: #f3efe4;
      --panel: #fffaf0;
      --ink: #1f2933;
      --muted: #6b7280;
      --accent: #0f766e;
      --line: #d6d3c7;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at 10% 10%, #fff8e7 0, var(--bg) 45%, #ece7db 100%);
    }
    .wrap {
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 4px 16px rgba(20, 20, 20, 0.06);
    }
    h1 {
      margin: 0 0 8px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      font-size: 26px;
    }
    .row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }
    button, input {
      font: inherit;
      border-radius: 10px;
      border: 1px solid var(--line);
      padding: 10px 12px;
      background: #fff;
    }
    button.primary {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
      cursor: pointer;
    }
    .hint { color: var(--muted); font-size: 14px; }
    .logs {
      background: #111827;
      color: #d1fae5;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      border-radius: 10px;
      padding: 10px;
      height: 180px;
      overflow: auto;
      font-size: 12px;
      white-space: pre-wrap;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 14px;
    }
    .card {
      position: relative;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--line);
      background: #fff;
      text-decoration: none;
      color: inherit;
      transform: translateY(0);
      transition: transform .18s ease, box-shadow .18s ease;
    }
    .card:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(15, 118, 110, 0.18);
    }
    .media {
      position: relative;
      aspect-ratio: 2 / 3;
      background: #e5e7eb;
      overflow: hidden;
    }
    .media img, .media video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .media video {
      position: absolute;
      inset: 0;
      opacity: 0;
      transition: opacity .2s ease;
      pointer-events: none;
    }
    .card:hover .media video { opacity: 1; }
    .meta {
      padding: 10px;
      font-size: 13px;
    }
    .meta .id { font-weight: 700; letter-spacing: .03em; }
    @media (max-width: 680px) {
      .wrap { padding: 14px; }
      h1 { font-size: 22px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel">
      <h1>JAV Organizer</h1>
      <p class="hint">Choose local folder -> process one by one -> browse and play local videos.</p>
      <div class="row">
        <button id="chooseBtn" class="primary">Choose Local Directory</button>
        <input id="manualPath" type="text" placeholder="Fallback: enter local path manually" style="min-width:320px" />
        <button id="manualBtn">Use Path</button>
        <button id="processBtn" class="primary">Start Processing</button>
      </div>
      <p id="status" class="hint"></p>
    </div>

    <div class="panel">
      <div class="row" style="justify-content:space-between">
        <strong>Progress</strong>
        <span id="progressText" class="hint"></span>
      </div>
      <div id="logs" class="logs"></div>
    </div>

    <div class="panel">
      <strong>Library</strong>
      <div id="grid" class="grid" style="margin-top:12px"></div>
    </div>
  </div>

  <script>
    const statusEl = document.getElementById("status");
    const progressEl = document.getElementById("progressText");
    const logsEl = document.getElementById("logs");
    const gridEl = document.getElementById("grid");
    const chooseBtn = document.getElementById("chooseBtn");
    const processBtn = document.getElementById("processBtn");
    const manualBtn = document.getElementById("manualBtn");
    const manualPath = document.getElementById("manualPath");

    async function post(url, body) {
      const res = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body || {})
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || res.statusText);
      return data;
    }

    async function get(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    }

    async function chooseDir() {
      try {
        const data = await post("/api/select-directory", {});
        statusEl.textContent = "Selected: " + data.selected_dir + " (" + data.count + " matched videos)";
        await refreshState();
      } catch (e) {
        statusEl.textContent = "Choose failed: " + e.message;
      }
    }

    async function chooseManual() {
      const path = manualPath.value.trim();
      if (!path) return;
      try {
        const data = await post("/api/select-directory", {path});
        statusEl.textContent = "Selected: " + data.selected_dir + " (" + data.count + " matched videos)";
        await refreshState();
      } catch (e) {
        statusEl.textContent = "Path failed: " + e.message;
      }
    }

    async function startProcess() {
      try {
        await post("/api/process", {});
        statusEl.textContent = "Processing started.";
      } catch (e) {
        statusEl.textContent = "Start failed: " + e.message;
      }
    }

    function renderLogs(lines) {
      logsEl.textContent = lines.join("\\n");
      logsEl.scrollTop = logsEl.scrollHeight;
    }

    function renderGrid(videos) {
      gridEl.innerHTML = "";
      for (const v of videos) {
        const a = document.createElement("a");
        a.className = "card";
        a.href = "/watch/" + encodeURIComponent(v.jav_id);
        const title = (v.title || "Untitled").replaceAll('"', "&quot;");
        a.innerHTML = `
          <div class="media">
            <img src="${v.poster_url}" alt="${title}" loading="lazy" />
            <video muted loop playsinline preload="none" src="${v.preview_url}"></video>
          </div>
          <div class="meta">
            <div class="id">${v.jav_id}</div>
            <div>${title}</div>
            <div class="hint">${v.release_date || "—"} ${v.publisher || ""}</div>
          </div>
        `;
        const vid = a.querySelector("video");
        a.addEventListener("mouseenter", () => { vid.play().catch(() => {}); });
        a.addEventListener("mouseleave", () => { vid.pause(); vid.currentTime = 0; });
        gridEl.appendChild(a);
      }
    }

    async function refreshState() {
      const state = await get("/api/state");
      const current = state.current ? " current: " + state.current : "";
      progressEl.textContent = state.processed + " / " + state.total + (state.processing ? " (running)" : " (idle)") + current;
      renderLogs(state.logs || []);
      const videos = await get("/api/videos");
      renderGrid(videos);
    }

    chooseBtn.addEventListener("click", chooseDir);
    manualBtn.addEventListener("click", chooseManual);
    processBtn.addEventListener("click", startProcess);

    refreshState();
    setInterval(refreshState, 2000);
  </script>
</body>
</html>
"""


WATCH_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Watch __JAV_ID__</title>
  <style>
    body {
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      background: linear-gradient(120deg, #0f172a, #1f2937);
      color: #f8fafc;
    }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 20px; }
    a { color: #a7f3d0; text-decoration: none; }
    .player {
      margin-top: 12px;
      border-radius: 14px;
      overflow: hidden;
      border: 1px solid rgba(255,255,255,0.16);
      background: #000;
    }
    video { width: 100%; display: block; max-height: 76vh; }
  </style>
</head>
<body>
  <div class="wrap">
    <a href="/">← Back to library</a>
    <h2 style="margin:10px 0 0">__JAV_ID__</h2>
    <div class="player">
      <video controls autoplay playsinline src="/api/local-video?id=__JAV_ID__"></video>
    </div>
  </div>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        prog="jav-web",
        description="Local frontend for directory scan, processing, and playback",
    )
    parser.add_argument("--db", default="jav.db")
    parser.add_argument("--media-dir", default=str(MEDIA_DIR))
    parser.add_argument("--video-dir", help="Optional initial local video directory")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    state = AppState(
        db_path=Path(args.db),
        media_dir=Path(args.media_dir).expanduser().resolve(),
    )
    if args.video_dir:
        folder = Path(args.video_dir).expanduser().resolve()
        if folder.exists() and folder.is_dir():
            state.selected_dir = folder
            state.items = scan_video_files(folder)
            state.total = len(state.items)
            state.add_log(f"[SCAN] {len(state.items)} file(s) with JAV IDs in {folder}")

    AppHandler.state = state
    server = ThreadingHTTPServer((args.host, args.port), AppHandler)
    print(f"  [WEB] http://{args.host}:{args.port}")
    print(f"  [DB]  {state.db_path}")
    print(f"  [MEDIA] {state.media_dir}")
    if state.selected_dir:
        print(f"  [VIDEO] {state.selected_dir}")
    print("  Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
