from __future__ import annotations

import argparse
import json
import mimetypes
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from ..config import MEDIA_DIR, open_db
from .dialogs import choose_directory_dialog
from .pages import ORGANIZE_HTML, VIDEO_HTML, VIEW_HTML, WATCH_HTML
from .processor import process_queue
from .scanner import scan_video_files
from .state import AppState


def _first_existing(patterns: list[Path]) -> Path | None:
    for pattern in patterns:
        matches = sorted(pattern.parent.glob(pattern.name))
        if matches:
            return matches[0]
    return None


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
            match = re.match(r"bytes=(\d*)-(\d*)", range_header.strip())
            if not match:
                self.send_error(416, "invalid range")
                return
            start_str, end_str = match.groups()
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

            with path.open("rb") as file_obj:
                file_obj.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = file_obj.read(min(1024 * 64, remaining))
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
        with path.open("rb") as file_obj:
            while True:
                chunk = file_obj.read(1024 * 64)
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
            for row in rows:
                media_dir = self.state.media_dir / row["jav_id"]
                poster_local = _first_existing([
                    media_dir / "poster.jpg",
                    media_dir / "poster.jpeg",
                    media_dir / "poster.png",
                    media_dir / "poster.webp",
                ])
                preview_local = media_dir / "preview.mp4"
                out.append({
                    "jav_id": row["jav_id"],
                    "title": row["title"],
                    "release_date": row["release_date"],
                    "publisher": row["publisher"],
                    "has_local_video": bool(row["local_video_path"]),
                    "poster_url": f"/api/poster?id={quote(row['jav_id'])}",
                    "preview_url": f"/api/preview?id={quote(row['jav_id'])}",
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
            self.send_response(302)
            self.send_header("Location", "/organize")
            self.end_headers()
            return
        if path == "/organize":
            self._text(ORGANIZE_HTML)
            return
        if path == "/view":
            self._text(VIEW_HTML)
            return
        if path.startswith("/video/"):
            jav_id = unquote(path.split("/video/", 1)[1]).upper()
            self._text(VIDEO_HTML.replace("__JAV_ID__", jav_id))
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
        if path == "/api/video":
            q = self._query()
            jav_id = (q.get("id") or [""])[0].upper()
            if not jav_id:
                self.send_error(400, "missing id")
                return
            conn = open_db(self.state.db_path)
            try:
                row = conn.execute(
                    """
                    SELECT v.jav_id, v.title, v.plot, v.release_date, v.duration_min,
                           v.cover_url, v.page_url, v.publisher, v.label, v.series,
                           v.director, v.rating, v.poster_url, v.preview_gif_url,
                           v.preview_mp4_url, v.screenshots_json, v.fetched_at,
                           v.local_video_path,
                           GROUP_CONCAT(DISTINCT a.name) AS actresses,
                           GROUP_CONCAT(DISTINCT g.name) AS genres
                    FROM videos v
                    LEFT JOIN video_actresses va ON va.video_id = v.id
                    LEFT JOIN actresses a ON a.id = va.actress_id
                    LEFT JOIN video_genres vg ON vg.video_id = v.id
                    LEFT JOIN genres g ON g.id = vg.genre_id
                    WHERE v.jav_id=?
                    GROUP BY v.id
                    """,
                    (jav_id,),
                ).fetchone()
            finally:
                conn.close()
            if not row:
                self.send_error(404, "video not found")
                return
            actresses = [x.strip() for x in (row["actresses"] or "").split(",") if x.strip()]
            genres = [x.strip() for x in (row["genres"] or "").split(",") if x.strip()]
            try:
                screenshots = json.loads(row["screenshots_json"] or "[]")
            except Exception:
                screenshots = []
            self._json(
                {
                    "jav_id": row["jav_id"],
                    "title": row["title"],
                    "plot": row["plot"],
                    "release_date": row["release_date"],
                    "duration_min": row["duration_min"],
                    "cover_url": row["cover_url"],
                    "page_url": row["page_url"],
                    "publisher": row["publisher"],
                    "label": row["label"],
                    "series": row["series"],
                    "director": row["director"],
                    "rating": row["rating"],
                    "has_local_video": bool(row["local_video_path"]),
                    "poster_url": f"/api/poster?id={quote(row['jav_id'])}",
                    "preview_url": f"/api/preview?id={quote(row['jav_id'])}",
                    "preview_gif_url": row["preview_gif_url"],
                    "preview_mp4_url": row["preview_mp4_url"],
                    "actresses": actresses,
                    "genres": genres,
                    "screenshots": screenshots,
                    "fetched_at": row["fetched_at"],
                }
            )
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
                thread = threading.Thread(target=process_queue, args=(self.state,), daemon=True)
                self.state.worker = thread
                thread.start()
            self._json({"ok": True})
            return

        self.send_error(404, "not found")


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
