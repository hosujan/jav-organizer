"""
jav-media — download poster, screenshots, and preview GIF/MP4 via Playwright.

Usage (after `uv run`):
    jav-media MISM-410
    jav-media MISM-410 ABW-123
    jav-media --file ids.txt --no-download
    jav-media MISM-410 --media-dir /Volumes/NAS/jav/media
"""

from __future__ import annotations
import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from .config import BASE_URL, DELAY, LANG, MEDIA_DIR, open_db


# ── Browser scraping via Playwright ──────────────────────────────────────────

def scrape_media_urls(jav_id: str) -> dict:
    """
    Open a real Chromium browser, intercept all network requests,
    and harvest every media asset URL for the given JAV ID.
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    page_url = f"{BASE_URL}/{LANG}/{jav_id.lower()}"
    results: dict = {
        "poster":      None,
        "preview_gif": None,
        "preview_mp4": None,
        "screenshots": [],
    }
    captured: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="zh-TW",
            extra_http_headers={"Accept-Language": "zh-TW,zh;q=0.9"},
        )
        page = ctx.new_page()
        page.on("request", lambda req: captured.append(req.url))

        print(f"  [BROWSER] {page_url}")
        try:
            page.goto(page_url, wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_timeout(3_000)
        except PWTimeout:
            print("  [WARN] page load timed out, parsing partial content")

        html = page.content()

        # og:image → poster
        og = page.query_selector('meta[property="og:image"]')
        if og:
            results["poster"] = og.get_attribute("content")

        # Fallback: CDN img tag
        if not results["poster"]:
            for img in page.query_selector_all("img"):
                src = img.get_attribute("src") or img.get_attribute("data-src") or ""
                if "fourhoi" in src or "cover" in src.lower():
                    results["poster"] = src
                    break

        # Parse JS variables embedded in <script> blocks
        _parse_js_vars(html, results)

        # Classify captured network URLs
        _scan_network(captured, results)

        # Screenshot <img> tags
        seen: set[str] = set()
        for img in page.query_selector_all("img"):
            src = img.get_attribute("src") or img.get_attribute("data-src") or ""
            if not src or src in seen:
                continue
            seen.add(src)
            if any(k in src.lower() for k in ["thumb", "screenshot", "sample", "cap", "snapshot"]):
                if src not in results["screenshots"]:
                    results["screenshots"].append(src)

        # Hover the player to trigger lazy GIF load
        player = page.query_selector(".video-player, video, #player, [class*='player']")
        if player and not results["preview_gif"]:
            try:
                player.hover()
                page.wait_for_timeout(2_000)
                _scan_network(captured, results)
            except Exception:
                pass

        ctx.close()
        browser.close()

    _log_results(jav_id, results)
    return results


# ── URL classification helpers ────────────────────────────────────────────────

def _parse_js_vars(html: str, results: dict):
    _JS = {
        "poster":      [
            r'player_poster\s*=\s*["\']([^"\']+)["\']',
            r'"poster"\s*:\s*"([^"]+)"',
        ],
        "preview_gif": [
            r'preview_gif\s*=\s*["\']([^"\']+\.gif)["\']',
            r'["\']([^"\']+\.gif)["\']',
        ],
        "preview_mp4": [
            r'preview_video\s*=\s*["\']([^"\']+\.mp4)["\']',
            r'"preview"\s*:\s*"([^"]+\.mp4)"',
        ],
    }
    for key, pats in _JS.items():
        if results.get(key):
            continue
        for pat in pats:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                url = m.group(1)
                if url.startswith("//"):
                    url = "https:" + url
                if url.startswith("http"):
                    results[key] = url
                    break

    # Screenshot arrays
    for pat in [r'screenshots?\s*[=:]\s*\[([^\]]+)\]', r'sample_images?\s*[=:]\s*\[([^\]]+)\]']:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            for u in re.findall(r'["\']([^"\']+\.jpe?g)["\']', m.group(1)):
                full = u if u.startswith("http") else "https:" + u.lstrip("/")
                if full not in results["screenshots"]:
                    results["screenshots"].append(full)


def _scan_network(captured: list[str], results: dict):
    for url in captured:
        ul  = url.lower()
        ext = Path(urlparse(url).path).suffix.lower()

        if not results["poster"] and ext in (".jpg", ".jpeg", ".png", ".webp"):
            if "fourhoi" in ul or "cover" in ul:
                results["poster"] = url

        if not results["preview_gif"] and ext == ".gif":
            results["preview_gif"] = url

        if not results["preview_mp4"] and ext == ".mp4":
            if any(k in ul for k in ["preview", "sample", "trailer"]):
                results["preview_mp4"] = url

        if ext in (".jpg", ".jpeg", ".png"):
            if any(k in ul for k in ["thumb", "screenshot", "cap", "sample", "snapshot"]):
                if url not in results["screenshots"]:
                    results["screenshots"].append(url)


def _log_results(jav_id: str, r: dict):
    print(f"  Poster      : {r['poster'] or '—'}")
    print(f"  Preview GIF : {r['preview_gif'] or '—'}")
    print(f"  Preview MP4 : {r['preview_mp4'] or '—'}")
    print(f"  Screenshots : {len(r['screenshots'])}")


# ── File downloader ───────────────────────────────────────────────────────────

def download_media(jav_id: str, results: dict, base_dir: Path = MEDIA_DIR) -> dict:
    out_dir = base_dir / jav_id.upper()
    out_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Referer": f"{BASE_URL}/",
    })

    def dl(url: str, name: str) -> str | None:
        if not url:
            return None
        dest = out_dir / name
        if dest.exists():
            print(f"    [skip] {name}")
            return str(dest)
        try:
            print(f"    [↓] {name}")
            r = session.get(url, timeout=30, stream=True)
            r.raise_for_status()
            dest.write_bytes(b"".join(r.iter_content(8192)))
            print(f"         {dest.stat().st_size // 1024} KB")
            return str(dest)
        except Exception as e:
            print(f"    [ERR] {name}: {e}")
            return None

    saved: dict = {"screenshots": []}

    if results.get("poster"):
        ext = Path(urlparse(results["poster"]).path).suffix or ".jpg"
        saved["poster"] = dl(results["poster"], f"poster{ext}")

    if results.get("preview_gif"):
        saved["preview_gif"] = dl(results["preview_gif"], "preview.gif")

    if results.get("preview_mp4"):
        saved["preview_mp4"] = dl(results["preview_mp4"], "preview.mp4")

    for i, url in enumerate(results.get("screenshots", []), 1):
        ext = Path(urlparse(url).path).suffix or ".jpg"
        local = dl(url, f"screenshot_{i:02d}{ext}")
        if local:
            saved["screenshots"].append(local)

    print(f"  → {out_dir}/")
    return saved


# ── DB update ─────────────────────────────────────────────────────────────────

def save_media_urls(conn, jav_id: str, results: dict):
    conn.execute("""
        UPDATE videos SET
            poster_url       = ?,
            preview_gif_url  = ?,
            preview_mp4_url  = ?,
            screenshots_json = ?
        WHERE jav_id = ?
    """, (
        results.get("poster"),
        results.get("preview_gif"),
        results.get("preview_mp4"),
        json.dumps(results.get("screenshots", []), ensure_ascii=False),
        jav_id.upper(),
    ))
    conn.commit()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="jav-media",
        description="Download poster, screenshots and preview GIF/MP4",
    )
    parser.add_argument("ids", nargs="*")
    parser.add_argument("--file", "-f")
    parser.add_argument("--db", default="jav.db")
    parser.add_argument("--no-download", action="store_true",
                        help="Only update DB with URLs; skip file downloads")
    parser.add_argument("--media-dir", default=str(MEDIA_DIR))
    args = parser.parse_args()

    ids = list(args.ids)
    if args.file:
        ids += Path(args.file).read_text().splitlines()
    ids = [i.strip().upper() for i in ids if i.strip()]

    if not ids:
        parser.print_help()
        sys.exit(1)

    conn       = open_db(args.db)
    media_base = Path(args.media_dir)

    for jav_id in ids:
        print(f"\n{'─'*50}\n{jav_id}")
        try:
            results = scrape_media_urls(jav_id)
            save_media_urls(conn, jav_id, results)
            if not args.no_download:
                download_media(jav_id, results, media_base)
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback; traceback.print_exc()
        time.sleep(DELAY)

    conn.close()
    print("\n✓ Done")


if __name__ == "__main__":
    main()
