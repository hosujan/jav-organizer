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

