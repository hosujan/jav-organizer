"""
jav fetch --media — download poster and preview MP4.
Uses Playwright to intercept real CDN URLs, with smart filtering to reject
ad/tracker URLs and a CDN-pattern prober as fallback.

Usage:
    jav fetch --media MISM-410
    jav fetch --media MISM-410 ABW-123
    jav fetch --media --file ids.txt --no-download
    jav fetch --media MISM-410 --media-dir ./media
"""

from __future__ import annotations
import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from .config import (
    BASE_URL,
    BROWSER_HEADLESS,
    BROWSER_PROFILE_DIR,
    DELAY,
    LANG,
    MEDIA_DIR,
    open_db,
)


# ── CDN allow-list ────────────────────────────────────────────────────────────
# Only accept image/media URLs from these domains.
# Anything from ad networks, trackers, analytics is rejected.
CDN_DOMAINS = {
    "fourhoi.com",
    "missav.ws",
    "missav.com",
    "fivetiu.com",   # alternate CDN seen on some titles
    "sixtop.com",
    "cdn.missav",
}

AD_DOMAINS = {
    "myavlive.com", "go.myavlive.com",
    "googletagmanager", "google-analytics", "doubleclick",
    "amazon-adsystem", "ads.", "track.", "click.", "stat.",
    "affiliate", "banner", "popup",
}

MIN_VALID_BYTES = 500


def _is_cdn_url(url: str) -> bool:
    """True only if the URL comes from a known CDN domain."""
    host = urlparse(url).netloc.lower()
    if any(ad in host for ad in AD_DOMAINS):
        return False
    return any(cdn in host for cdn in CDN_DOMAINS)


# ── Playwright browser scrape ─────────────────────────────────────────────────

def _challenge_signal(page) -> str | None:
    url = page.url.lower()
    title = (page.title() or "").strip().lower()
    if "cdn-cgi/challenge" in url or "challenge-platform" in url:
        return f"url={page.url}"
    if title in {"just a moment...", "attention required! | cloudflare", "verify you are human"}:
        return f"title={title}"
    selectors = (
        "#challenge-form",
        "#cf-challenge-running",
        "#challenge-running",
        "iframe[src*='challenges.cloudflare.com']",
        "input[name='cf_ch_verify']",
    )
    for selector in selectors:
        if page.query_selector(selector):
            return f"selector={selector}"
    return None


def _wait_for_challenge_clear(page, *, headless: bool) -> None:
    reason = _challenge_signal(page)
    if not reason:
        return

    print(f"  [WARN] bot challenge detected ({reason}).")
    if not headless and sys.stdin.isatty():
        print("  [INFO] complete verification in the browser window (up to 120s).")
        for _ in range(60):
            page.wait_for_timeout(2_000)
            if not _challenge_signal(page):
                print("  [OK] challenge cleared.")
                return
        print("  [WARN] challenge still present after 120s, continuing anyway.")
        return

    page.wait_for_timeout(8_000)


def scrape_media_urls(jav_id: str, *, headless: bool = BROWSER_HEADLESS) -> dict:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    page_url = f"{BASE_URL}/{LANG}/{jav_id.lower()}"
    results: dict = {
        "poster":      None,
        "preview_mp4": None,
    }
    captured: list[str] = []
    profile_dir = BROWSER_PROFILE_DIR.expanduser().resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)

    print(f"  [BROWSER] {page_url}")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="zh-TW",
            extra_http_headers={"Accept-Language": "zh-TW,zh;q=0.9"},
        )
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.on("request",  lambda req: captured.append(req.url))
        page.on("response", lambda res: captured.append(res.url))   # also catch redirects

        try:
            page.goto(page_url, wait_until="domcontentloaded", timeout=30_000)
            _wait_for_challenge_clear(page, headless=headless)
            page.wait_for_timeout(4_000)   # let lazy assets load
        except PWTimeout:
            print("  [WARN] page load timed out, parsing partial content")

        html = page.content()

        # ── og:image → poster ─────────────────────────────────────────────
        og = page.query_selector('meta[property="og:image"]')
        if og:
            val = og.get_attribute("content") or ""
            if _is_cdn_url(val):
                results["poster"] = val

        # ── Parse all inline <script> blocks ─────────────────────────────
        _parse_js_vars(html, results)

        # ── Classify every intercepted network URL ────────────────────────
        _scan_network(captured, results)

        # ── Hover player to trigger preview load ──────────────────────────
        if not results["preview_mp4"]:
            player = page.query_selector(
                "video, .video-player, #player, [class*='player'], [id*='player']"
            )
            if player:
                try:
                    player.hover()
                    page.wait_for_timeout(2_500)
                    _scan_network(captured, results)
                except Exception:
                    pass

        ctx.close()

    # ── CDN pattern prober (fallback) ─────────────────────────────────────
    # If we found the poster URL we know the CDN base path, probe common patterns.
    if results["poster"]:
        _probe_cdn_patterns(jav_id, results)

    _log_results(jav_id, results)
    return results


# ── JS variable extraction ────────────────────────────────────────────────────

def _parse_js_vars(html: str, results: dict):
    """
    missav embeds asset URLs directly in inline JS, e.g.:
        var player_poster = "https://fourhoi.com/mism-410/cover-n.jpg"
        var preview_video = "https://fourhoi.com/mism-410/preview.mp4"
        var video_url     = [...]
    """
    _patterns = {
        "poster": [
            r'player_poster\s*[=:]\s*["\']([^"\']+)["\']',
            r'"poster"\s*:\s*"([^"\']+)"',
            r"poster\s*[=:]\s*['\"]([^'\"]+)['\"]",
        ],
        "preview_mp4": [
            r'preview_video\s*[=:]\s*["\']([^"\']+\.mp4)["\']',
            r'preview\s*[=:]\s*["\']([^"\']+\.mp4)["\']',
            r'"preview"\s*:\s*"([^"\']+\.mp4)"',
        ],
    }

    for key, pats in _patterns.items():
        if results.get(key):
            continue
        for pat in pats:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                url = m.group(1)
                if url.startswith("//"):
                    url = "https:" + url
                if url.startswith("http") and _is_cdn_url(url):
                    results[key] = url
                    break


# ── Network URL classifier ────────────────────────────────────────────────────

def _scan_network(captured: list[str], results: dict):
    for url in captured:
        if not _is_cdn_url(url):
            continue
        ul  = url.lower()
        ext = Path(urlparse(url).path).suffix.lower()

        if not results["poster"] and ext in (".jpg", ".jpeg", ".png", ".webp"):
            if "cover" in ul:
                results["poster"] = url

        if not results["preview_mp4"] and ext == ".mp4":
            if any(k in ul for k in ["preview", "sample", "trailer"]):
                results["preview_mp4"] = url


# ── CDN pattern prober ────────────────────────────────────────────────────────

def _probe_cdn_patterns(jav_id: str, results: dict):
    """
    Given a known poster URL like https://fourhoi.com/mism-410/cover-n.jpg,
    derive the CDN base and probe common naming patterns for preview mp4.
    Uses HEAD requests — fast, no big downloads.
    """
    poster_url = results["poster"]
    # Extract base: https://fourhoi.com/mism-410/
    parsed   = urlparse(poster_url)
    base_dir = parsed.scheme + "://" + parsed.netloc + str(Path(parsed.path).parent) + "/"

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Referer": f"{BASE_URL}/",
    })

    def probe(path: str) -> str | None:
        url = base_dir + path
        try:
            r = session.head(url, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                ct = r.headers.get("content-type", "")
                cl = int(r.headers.get("content-length", 0))
                if cl > MIN_VALID_BYTES:           # ignore near-empty responses
                    return url
        except Exception:
            pass
        return None

    # Preview MP4
    if not results["preview_mp4"]:
        for name in ["preview.mp4", "sample.mp4", f"{jav_id.lower()}_preview.mp4"]:
            found = probe(name)
            if found:
                results["preview_mp4"] = found
                print(f"  [PROBE] preview mp4 → {found}")
                break


# ── Logging ───────────────────────────────────────────────────────────────────

def _log_results(jav_id: str, r: dict):
    print(f"\n  Results for {jav_id}:")
    print(f"    Poster      : {r['poster'] or '—'}")
    print(f"    Preview MP4 : {r['preview_mp4'] or '—'}")


# ── File downloader ───────────────────────────────────────────────────────────

def local_media_paths(jav_id: str, base_dir: Path = MEDIA_DIR) -> dict[str, Path | None]:
    out_dir = base_dir / jav_id.upper()
    poster = next(
        (
            path
            for path in (
                out_dir / "poster.jpg",
                out_dir / "poster.jpeg",
                out_dir / "poster.png",
                out_dir / "poster.webp",
            )
            if path.exists() and path.stat().st_size > MIN_VALID_BYTES
        ),
        None,
    )
    preview = out_dir / "preview.mp4"
    if not preview.exists() or preview.stat().st_size <= MIN_VALID_BYTES:
        preview = None
    return {"poster": poster, "preview_mp4": preview}


def fetch_media_payloads(jav_id: str, results: dict) -> dict[str, dict]:
    payloads: dict[str, dict] = {}
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Referer": f"{BASE_URL}/",
    })

    def dl(url: str, name: str, key: str) -> None:
        if not url:
            return
        print(f"    [↓] {name}")
        try:
            response = session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            data = b"".join(response.iter_content(65536))
            if len(data) <= MIN_VALID_BYTES:
                print(f"    [WARN] {name} — response too small ({len(data)} B), skipping")
                return
            payloads[key] = {
                "name": name,
                "url": url,
                "data": data,
                "size": len(data),
            }
            print(f"         {len(data) // 1024} KB  ✓")
        except Exception as err:
            print(f"    [ERR] {name}: {err}")

    poster_url = results.get("poster")
    if poster_url:
        ext = Path(urlparse(poster_url).path).suffix or ".jpg"
        dl(poster_url, f"poster{ext}", "poster")
    preview_url = results.get("preview_mp4")
    if preview_url:
        dl(preview_url, "preview.mp4", "preview_mp4")
    return payloads


def save_media_payloads(jav_id: str, payloads: dict[str, dict], base_dir: Path = MEDIA_DIR) -> dict[str, str]:
    saved: dict[str, str] = {}
    out_dir = base_dir / jav_id.upper()
    out_dir.mkdir(parents=True, exist_ok=True)

    poster_payload = payloads.get("poster")
    if poster_payload:
        # Keep only one poster file based on latest extension.
        for old in (out_dir / "poster.jpg", out_dir / "poster.jpeg", out_dir / "poster.png", out_dir / "poster.webp"):
            if old.exists():
                old.unlink()
        poster_path = out_dir / poster_payload["name"]
        poster_path.write_bytes(poster_payload["data"])
        saved["poster"] = str(poster_path)

    preview_payload = payloads.get("preview_mp4")
    if preview_payload:
        preview_path = out_dir / "preview.mp4"
        preview_path.write_bytes(preview_payload["data"])
        saved["preview_mp4"] = str(preview_path)
    return saved

def download_media(
    jav_id: str,
    results: dict,
    base_dir: Path = MEDIA_DIR,
    *,
    overwrite_existing: bool = False,
) -> dict:
    out_dir = base_dir / jav_id.upper()
    out_dir.mkdir(parents=True, exist_ok=True)
    if overwrite_existing:
        for path in (
            out_dir / "poster.jpg",
            out_dir / "poster.jpeg",
            out_dir / "poster.png",
            out_dir / "poster.webp",
            out_dir / "preview.mp4",
        ):
            if path.exists():
                path.unlink()

    local = local_media_paths(jav_id, base_dir)
    poster_existing = local["poster"]
    preview_existing = local["preview_mp4"]

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
        if overwrite_existing and dest.exists():
            dest.unlink()
        if not overwrite_existing and dest.exists() and dest.stat().st_size > MIN_VALID_BYTES:
            print(f"    [skip] {name} (exists)")
            return str(dest)
        try:
            print(f"    [↓] {name}")
            r = session.get(url, timeout=60, stream=True)
            r.raise_for_status()
            data = b"".join(r.iter_content(65536))
            if len(data) < MIN_VALID_BYTES:
                print(f"    [WARN] {name} — response too small ({len(data)} B), skipping")
                return None
            dest.write_bytes(data)
            print(f"         {dest.stat().st_size // 1024} KB  ✓")
            return str(dest)
        except Exception as e:
            print(f"    [ERR] {name}: {e}")
            return None

    saved: dict = {}

    if poster_existing:
        print(f"    [skip] poster (found local: {poster_existing.name})")
        saved["poster"] = str(poster_existing)

    if results.get("poster"):
        if "poster" not in saved:
            ext = Path(urlparse(results["poster"]).path).suffix or ".jpg"
            saved["poster"] = dl(results["poster"], f"poster{ext}")

    if preview_existing:
        print("    [skip] preview.mp4 (found local)")
        saved["preview_mp4"] = str(preview_existing)
    if results.get("preview_mp4"):
        if "preview_mp4" not in saved:
            saved["preview_mp4"] = dl(results["preview_mp4"], "preview.mp4")

    print(f"\n  Saved to: {out_dir}/")
    return saved


# ── DB update ─────────────────────────────────────────────────────────────────

def save_media_urls(conn, jav_id: str, results: dict):
    conn.execute("""
        UPDATE videos SET
            poster_url       = ?,
            preview_mp4_url  = ?,
            preview_gif_url  = NULL,
            screenshots_json = '[]'
        WHERE jav_id = ?
    """, (
        results.get("poster"),
        results.get("preview_mp4"),
        jav_id.upper(),
    ))
    conn.commit()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None, prog: str = "jav fetch --media"):
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Download poster and preview MP4",
    )
    parser.add_argument("ids", nargs="*")
    parser.add_argument("--file", "-f")
    parser.add_argument("--db", default="jav.db")
    parser.add_argument("--no-download", action="store_true", help="Resolve URLs only, skip downloading files")
    parser.add_argument("--media-dir")
    parser.add_argument("--headless", action="store_true", help="Run Playwright in headless mode")
    parser.add_argument("--save-db", action="store_true", help="Persist scraped media URLs to SQLite")
    args = parser.parse_args(argv)

    ids = list(args.ids)
    if args.file:
        ids += Path(args.file).read_text().splitlines()
    ids = [i.strip().upper() for i in ids if i.strip()]

    if not ids:
        parser.print_help()
        sys.exit(1)

    conn = open_db(args.db) if args.save_db else None
    media_root = Path(args.media_dir).expanduser().resolve() if args.media_dir else MEDIA_DIR.resolve()
    media_root.mkdir(parents=True, exist_ok=True)

    for jav_id in ids:
        print(f"\n{'─'*50}\n{jav_id}")
        try:
            results = scrape_media_urls(jav_id, headless=args.headless)
            if conn:
                save_media_urls(conn, jav_id, results)
            if not args.no_download:
                download_media(jav_id, results, media_root, overwrite_existing=True)
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback; traceback.print_exc()
        time.sleep(DELAY)

    if conn:
        conn.close()
    print("\n✓ Done")


if __name__ == "__main__":
    main()
