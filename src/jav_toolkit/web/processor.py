from __future__ import annotations

import time

from ..config import DELAY, open_db
from ..media import download_media, save_media_urls, scrape_media_urls
from ..scraper import fetch_detail, search_id, upsert_video
from .state import AppState


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
                existing = conn.execute(
                    "SELECT 1 FROM videos WHERE jav_id=?",
                    (jav_id,),
                ).fetchone()
                if existing and not state.force_override:
                    state.add_log(f"[DB] {jav_id} found in sqlite, skip metadata fetch")
                else:
                    url = search_id(jav_id)
                    if not url:
                        state.add_log(f"[WARN] {jav_id} search failed")
                        continue

                    data = fetch_detail(url, jav_id)
                    if not data:
                        state.add_log(f"[WARN] {jav_id} detail fetch failed")
                        continue

                    upsert_video(conn, data)

                media_row = conn.execute(
                    "SELECT poster_url, preview_mp4_url FROM videos WHERE jav_id=?",
                    (jav_id,),
                ).fetchone()
                has_db_poster = bool(media_row and media_row["poster_url"])
                has_db_preview = bool(media_row and media_row["preview_mp4_url"])
                has_local_poster = bool(item.get("has_poster_local"))
                has_local_preview = bool(item.get("has_preview_local"))

                if has_db_poster and has_db_preview and not state.force_override:
                    media = {
                        "poster": media_row["poster_url"],
                        "preview_mp4": media_row["preview_mp4_url"],
                    }
                    state.add_log(f"[DB] {jav_id} media urls found in sqlite, skip media scrape")
                else:
                    media = scrape_media_urls(jav_id)
                save_media_urls(conn, jav_id, media)
                if has_local_poster and has_local_preview and not state.force_override:
                    state.add_log(f"[MEDIA] {jav_id} local poster+preview found, skip download")
                else:
                    saved = download_media(
                        jav_id,
                        media,
                        state.media_dir,
                        overwrite_existing=state.force_override,
                    )
                    item["has_poster_local"] = bool(saved.get("poster")) or has_local_poster
                    item["has_preview_local"] = bool(saved.get("preview_mp4")) or has_local_preview
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
