from __future__ import annotations

import argparse
import json
import mimetypes
import re
import threading
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from ..config import MEDIA_DIR, get_setting, open_db, set_setting
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


def _parse_iso_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
    except Exception:
        return None


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


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

        def safe_write(data: bytes) -> bool:
            try:
                self.wfile.write(data)
                return True
            except (BrokenPipeError, ConnectionResetError, OSError):
                return False

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
            try:
                self.end_headers()
            except (BrokenPipeError, ConnectionResetError, OSError):
                return

            with path.open("rb") as file_obj:
                file_obj.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = file_obj.read(min(1024 * 64, remaining))
                    if not chunk:
                        break
                    if not safe_write(chunk):
                        return
                    remaining -= len(chunk)
            return

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        if allow_range:
            self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(size))
        try:
            self.end_headers()
        except (BrokenPipeError, ConnectionResetError, OSError):
            return
        with path.open("rb") as file_obj:
            while True:
                chunk = file_obj.read(1024 * 64)
                if not chunk:
                    break
                if not safe_write(chunk):
                    return

    def _query(self) -> dict[str, list[str]]:
        return parse_qs(urlparse(self.path).query)

    def _recommendation_score(self, row: dict) -> float:
        now = datetime.now(UTC)
        score = 0.0
        if row.get("has_local_video"):
            score += 8.0
        if row.get("has_preview_local"):
            score += 3.0
        if row.get("has_poster_local"):
            score += 2.0

        rating = _to_float(row.get("rating"), default=0.0)
        if rating > 0:
            score += min(rating, 5.0) * 0.9

        release_dt = _parse_iso_date(row.get("release_date"))
        if release_dt:
            age_days = max(0, (now - release_dt).days)
            score += max(0.0, 4.5 - (age_days / 80.0))

        progress_percent = _to_float(row.get("progress_percent"), default=0.0)
        if 3.0 <= progress_percent < 96.0:
            score += 5.0
        elif progress_percent >= 96.0:
            score -= 1.5

        return round(score, 3)

    def _upsert_watch_progress(
        self,
        jav_id: str,
        *,
        position_sec: float,
        duration_sec: float | None,
        event: str,
    ):
        duration = duration_sec if duration_sec and duration_sec > 0 else None
        position = max(position_sec, 0.0)
        percent = 0.0
        if duration:
            percent = max(0.0, min(100.0, (position / duration) * 100.0))
        elif event == "ended":
            percent = 100.0

        if event == "reset":
            position = 0.0
            percent = 0.0
            state = "started"
        elif event == "ended" or percent >= 96.0:
            state = "completed"
            percent = max(percent, 100.0 if event == "ended" else percent)
        elif percent >= 3.0:
            state = "in_progress"
        else:
            state = "started"

        conn = open_db(self.state.db_path)
        try:
            conn.execute(
                """
                INSERT INTO watch_progress (jav_id, position_sec, duration_sec, percent, state, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(jav_id) DO UPDATE SET
                    position_sec=excluded.position_sec,
                    duration_sec=excluded.duration_sec,
                    percent=excluded.percent,
                    state=excluded.state,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (jav_id, position, duration, percent, state),
            )
            conn.commit()
        finally:
            conn.close()

    def _recommendations_for(self, jav_id: str, limit: int = 12) -> list[dict]:
        videos = self._load_videos()
        if not videos:
            return []
        target = next((v for v in videos if v.get("jav_id") == jav_id), None)
        if not target:
            return sorted(
                videos,
                key=lambda v: _to_float(v.get("recommendation_score"), default=0.0),
                reverse=True,
            )[:limit]

        target_genres = set(target.get("genres") or [])
        target_actresses = set(target.get("actresses") or [])
        target_publisher = target.get("publisher")
        target_release = _parse_iso_date(target.get("release_date"))

        ranked: list[tuple[float, dict]] = []
        for item in videos:
            if item.get("jav_id") == jav_id:
                continue

            score = _to_float(item.get("recommendation_score"), default=0.0)
            item_genres = set(item.get("genres") or [])
            item_actresses = set(item.get("actresses") or [])
            overlap_genres = len(target_genres & item_genres)
            overlap_actresses = len(target_actresses & item_actresses)
            if overlap_genres:
                score += overlap_genres * 1.2
            if overlap_actresses:
                score += overlap_actresses * 1.8
            if target_publisher and item.get("publisher") == target_publisher:
                score += 1.1

            item_release = _parse_iso_date(item.get("release_date"))
            if target_release and item_release:
                day_gap = abs((target_release - item_release).days)
                if day_gap <= 120:
                    score += 1.4
                elif day_gap <= 365:
                    score += 0.8

            ranked.append((score, item))

        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in ranked[:limit]]

    def _load_videos(self) -> list[dict]:
        conn = open_db(self.state.db_path)
        try:
            rows = conn.execute("""
                SELECT v.jav_id, v.title, v.release_date, v.publisher, v.local_video_path,
                       v.poster_url, v.preview_mp4_url, v.rating, v.duration_min,
                       GROUP_CONCAT(DISTINCT a.name) AS actresses,
                       GROUP_CONCAT(DISTINCT g.name) AS genres,
                       wp.position_sec AS progress_sec,
                       wp.duration_sec AS progress_duration_sec,
                       wp.percent AS progress_percent,
                       wp.state AS watch_state,
                       wp.updated_at AS progress_updated_at
                FROM videos v
                LEFT JOIN video_actresses va ON va.video_id = v.id
                LEFT JOIN actresses a ON a.id = va.actress_id
                LEFT JOIN video_genres vg ON vg.video_id = v.id
                LEFT JOIN genres g ON g.id = vg.genre_id
                LEFT JOIN watch_progress wp ON wp.jav_id = v.jav_id
                WHERE v.local_video_path IS NOT NULL
                GROUP BY v.id
                ORDER BY v.release_date DESC, v.jav_id DESC
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
                actresses = [x.strip() for x in (row["actresses"] or "").split(",") if x.strip()]
                genres = [x.strip() for x in (row["genres"] or "").split(",") if x.strip()]
                item = {
                    "jav_id": row["jav_id"],
                    "title": row["title"],
                    "release_date": row["release_date"],
                    "publisher": row["publisher"],
                    "rating": row["rating"],
                    "duration_min": row["duration_min"],
                    "actresses": actresses,
                    "genres": genres,
                    "has_local_video": bool(row["local_video_path"]),
                    "poster_url": f"/api/poster?id={quote(row['jav_id'])}",
                    "preview_url": f"/api/preview?id={quote(row['jav_id'])}",
                    "has_poster_local": bool(poster_local),
                    "has_preview_local": preview_local.exists(),
                    "progress_sec": _to_float(row["progress_sec"], default=0.0),
                    "progress_duration_sec": _to_float(row["progress_duration_sec"], default=0.0),
                    "progress_percent": _to_float(row["progress_percent"], default=0.0),
                    "watch_state": row["watch_state"] or None,
                    "progress_updated_at": row["progress_updated_at"],
                }
                item["recommendation_score"] = self._recommendation_score(item)
                out.append(item)
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
        if path == "/api/recommendations":
            q = self._query()
            jav_id = (q.get("id") or [""])[0].upper()
            if not jav_id:
                self.send_error(400, "missing id")
                return
            limit_raw = (q.get("limit") or ["12"])[0]
            try:
                limit = max(1, min(30, int(limit_raw)))
            except Exception:
                limit = 12
            self._json(self._recommendations_for(jav_id, limit=limit))
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
                           v.local_video_path, wp.position_sec, wp.duration_sec,
                           wp.percent, wp.state, wp.updated_at,
                           GROUP_CONCAT(DISTINCT a.name) AS actresses,
                           GROUP_CONCAT(DISTINCT g.name) AS genres
                    FROM videos v
                    LEFT JOIN video_actresses va ON va.video_id = v.id
                    LEFT JOIN actresses a ON a.id = va.actress_id
                    LEFT JOIN video_genres vg ON vg.video_id = v.id
                    LEFT JOIN genres g ON g.id = vg.genre_id
                    LEFT JOIN watch_progress wp ON wp.jav_id = v.jav_id
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
                    "progress_sec": _to_float(row["position_sec"], default=0.0),
                    "progress_duration_sec": _to_float(row["duration_sec"], default=0.0),
                    "progress_percent": _to_float(row["percent"], default=0.0),
                    "watch_state": row["state"] or None,
                    "progress_updated_at": row["updated_at"],
                }
            )
            return
        if path == "/api/watch-progress":
            q = self._query()
            jav_id = (q.get("id") or [""])[0].upper()
            if not jav_id:
                self.send_error(400, "missing id")
                return
            conn = open_db(self.state.db_path)
            try:
                row = conn.execute(
                    """
                    SELECT jav_id, position_sec, duration_sec, percent, state, updated_at
                    FROM watch_progress
                    WHERE jav_id=?
                    """,
                    (jav_id,),
                ).fetchone()
            finally:
                conn.close()
            if not row:
                self._json(
                    {
                        "jav_id": jav_id,
                        "position_sec": 0.0,
                        "duration_sec": None,
                        "percent": 0.0,
                        "state": "started",
                        "updated_at": None,
                    }
                )
                return
            self._json(
                {
                    "jav_id": row["jav_id"],
                    "position_sec": _to_float(row["position_sec"], default=0.0),
                    "duration_sec": _to_float(row["duration_sec"], default=0.0),
                    "percent": _to_float(row["percent"], default=0.0),
                    "state": row["state"] or "started",
                    "updated_at": row["updated_at"],
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
            conn = open_db(self.state.db_path)
            try:
                set_setting(conn, "last_video_dir", str(folder))
            finally:
                conn.close()
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

        if path == "/api/watch-progress":
            jav_id = str(body.get("id") or "").upper().strip()
            if not jav_id:
                self._json({"ok": False, "error": "missing id"}, 400)
                return
            conn = open_db(self.state.db_path)
            try:
                exists = conn.execute(
                    "SELECT 1 FROM videos WHERE jav_id=?",
                    (jav_id,),
                ).fetchone()
            finally:
                conn.close()
            if not exists:
                self._json({"ok": False, "error": "video not found"}, 404)
                return

            position_sec = _to_float(body.get("position_sec"), default=0.0)
            duration_value = body.get("duration_sec")
            duration_sec = _to_float(duration_value, default=0.0) if duration_value is not None else None
            event = str(body.get("event") or "progress").strip().lower()
            if event not in {"progress", "ended", "reset"}:
                event = "progress"

            self._upsert_watch_progress(
                jav_id,
                position_sec=position_sec,
                duration_sec=duration_sec,
                event=event,
            )
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
    start_dir: Path | None = None
    if args.video_dir:
        candidate = Path(args.video_dir).expanduser().resolve()
        if candidate.exists() and candidate.is_dir():
            start_dir = candidate
    else:
        conn = open_db(state.db_path)
        try:
            raw = get_setting(conn, "last_video_dir")
        finally:
            conn.close()
        if raw:
            candidate = Path(raw).expanduser().resolve()
            if candidate.exists() and candidate.is_dir():
                start_dir = candidate

    if start_dir:
        state.selected_dir = start_dir
        state.items = scan_video_files(start_dir)
        state.total = len(state.items)
        state.add_log(f"[SCAN] {len(state.items)} file(s) with JAV IDs in {start_dir}")
        conn = open_db(state.db_path)
        try:
            set_setting(conn, "last_video_dir", str(start_dir))
        finally:
            conn.close()

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
