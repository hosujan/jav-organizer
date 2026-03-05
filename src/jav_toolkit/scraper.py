"""
jav-fetch — scrape metadata from missav.ws (Traditional Chinese) into SQLite.

Usage (after `uv run`):
    jav-fetch MISM-410
    jav-fetch MISM-410 ABW-123 SSIS-456
    jav-fetch --file ids.txt
"""

from __future__ import annotations
import argparse
import json
import re
import sys
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .config import BASE_URL, DELAY, HEADERS, LANG, open_db


# ── HTTP session ──────────────────────────────────────────────────────────────

def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


# ── Search ────────────────────────────────────────────────────────────────────

def search_id(session: requests.Session, jav_id: str) -> str | None:
    """Return the canonical detail-page URL, skipping uncensored-leak results."""
    search_url = f"{BASE_URL}/{LANG}/search/{jav_id.lower()}"
    print(f"  [SEARCH] {search_url}")
    try:
        resp = session.get(search_url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERROR] {e}")
        return None

    soup = BeautifulSoup(resp.text, "lxml")
    id_lower = jav_id.lower()
    candidates: list[str] = []

    for a in soup.find_all("a", href=True):
        path = urlparse(a["href"]).path.rstrip("/")
        if id_lower in path.lower() and "uncensored-leak" not in path.lower():
            full = urljoin(BASE_URL, a["href"])
            if full not in candidates:
                candidates.append(full)

    candidates.sort(key=len)
    if candidates:
        print(f"  [FOUND] {candidates[0]}")
        return candidates[0]

    fallback = f"{BASE_URL}/{LANG}/{id_lower}"
    print(f"  [FALLBACK] {fallback}")
    return fallback


# ── Detail page ───────────────────────────────────────────────────────────────

def fetch_detail(session: requests.Session, url: str, jav_id: str) -> dict | None:
    parsed = urlparse(url)
    path = parsed.path
    if not path.startswith(f"/{LANG}/"):
        path = f"/{LANG}/{path.lstrip('/')}"
        url = f"{BASE_URL}{path}"

    print(f"  [DETAIL] {url}")
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERROR] {e}")
        return None

    soup = BeautifulSoup(resp.text, "lxml")
    data: dict = {
        "jav_id":     jav_id.upper(),
        "page_url":   url,
        "fetched_at": datetime.utcnow().isoformat(),
        "actresses":  [],
        "genres":     [],
    }

    # Title
    h1 = soup.find("h1")
    og_title = soup.find("meta", property="og:title")
    if h1:
        data["title"] = h1.get_text(strip=True)
    elif og_title:
        data["title"] = og_title.get("content", "").strip()

    # Cover URL
    og_img = soup.find("meta", property="og:image")
    if og_img:
        data["cover_url"] = og_img.get("content", "").strip()

    # Plot
    og_desc = soup.find("meta", property="og:description") or \
              soup.find("meta", attrs={"name": "description"})
    if og_desc:
        data["plot"] = og_desc.get("content", "").strip()

    # Structured metadata rows
    for row in soup.select("div.grid-cols-1 > div, div.space-y-2 > div, div.detail > div"):
        _parse_meta_row(row, row.get_text(" ", strip=True), data)

    # Actress names from anchor tags near cast labels
    for tag in soup.find_all(
        ["p", "span", "div"],
        string=re.compile(r"女優|演員|出演|Cast", re.I),
    ):
        for lnk in tag.parent.find_all("a"):
            name = lnk.get_text(strip=True)
            if name and name not in data["actresses"]:
                data["actresses"].append(name)

    # JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            _parse_jsonld(json.loads(script.string or ""), data)
        except Exception:
            pass

    _parse_fallback(soup, data)
    return data


# ── Metadata helpers ──────────────────────────────────────────────────────────

_LABEL_MAP = {
    "發行日期": "release_date", "發售日期": "release_date", "日期": "release_date",
    "時長": "duration_min",    "片長": "duration_min",
    "發行商": "publisher",     "廠商": "publisher",
    "標籤": "label",           "系列": "series",
    "導演": "director",        "評分": "rating",
}
_ACTRESS_KEYS = {"女優", "演員", "出演", "Cast"}
_GENRE_KEYS   = {"類型", "標籤", "Tags", "Genre", "分類"}


def _parse_meta_row(tag, text: str, data: dict):
    for jp_key, db_key in _LABEL_MAP.items():
        if jp_key in text and db_key not in data:
            val = _extract_value(tag, jp_key)
            if val:
                if db_key == "duration_min":
                    m = re.search(r"(\d+)", val)
                    data[db_key] = int(m.group(1)) if m else None
                elif db_key == "rating":
                    m = re.search(r"[\d.]+", val)
                    data[db_key] = float(m.group()) if m else None
                else:
                    data[db_key] = val

    for key in _ACTRESS_KEYS:
        if key in text:
            for a in tag.find_all("a"):
                name = a.get_text(strip=True)
                if name and name not in data["actresses"]:
                    data["actresses"].append(name)

    for key in _GENRE_KEYS:
        if key in text:
            for a in tag.find_all("a"):
                name = a.get_text(strip=True)
                if name and name not in data["genres"] and len(name) < 30:
                    data["genres"].append(name)


def _extract_value(tag, label: str) -> str | None:
    full = tag.get_text(" ", strip=True)
    if label in full:
        after = full.split(label, 1)[-1].strip().lstrip(":：").strip()
        return after[:200] if after else None
    return None


def _parse_jsonld(ld, data: dict):
    if isinstance(ld, list):
        for item in ld:
            _parse_jsonld(item, data)
        return
    if ld.get("@type") in ("VideoObject", "Movie", "AdultVideo"):
        if "name" in ld and "title" not in data:
            data["title"] = ld["name"]
        if "description" in ld and "plot" not in data:
            data["plot"] = ld["description"]
        if "thumbnailUrl" in ld and "cover_url" not in data:
            data["cover_url"] = ld["thumbnailUrl"]
        if "uploadDate" in ld and "release_date" not in data:
            data["release_date"] = ld["uploadDate"][:10]
        actors = ld.get("actor", [])
        if isinstance(actors, dict):
            actors = [actors]
        for actor in actors:
            name = actor.get("name", "").strip()
            if name and name not in data["actresses"]:
                data["actresses"].append(name)


def _parse_fallback(soup: BeautifulSoup, data: dict):
    full_text = soup.get_text("\n")
    if "release_date" not in data:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", full_text)
        if m:
            data["release_date"] = m.group(1)
    if "duration_min" not in data:
        m = re.search(r"(\d{2,3})\s*(?:分鐘|分|min)", full_text)
        if m:
            data["duration_min"] = int(m.group(1))


# ── DB write ──────────────────────────────────────────────────────────────────

def upsert_video(conn, data: dict) -> int:
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO videos (
            jav_id, title, plot, release_date, duration_min, cover_url,
            page_url, publisher, label, series, director, rating, fetched_at
        ) VALUES (
            :jav_id,:title,:plot,:release_date,:duration_min,:cover_url,
            :page_url,:publisher,:label,:series,:director,:rating,:fetched_at
        )
        ON CONFLICT(jav_id) DO UPDATE SET
            title=excluded.title, plot=excluded.plot,
            release_date=excluded.release_date, duration_min=excluded.duration_min,
            cover_url=excluded.cover_url, page_url=excluded.page_url,
            publisher=excluded.publisher, label=excluded.label,
            series=excluded.series, director=excluded.director,
            rating=excluded.rating, fetched_at=excluded.fetched_at
    """, {k: data.get(k) for k in (
        "jav_id","title","plot","release_date","duration_min","cover_url",
        "page_url","publisher","label","series","director","rating","fetched_at",
    )})

    vid_id = conn.execute(
        "SELECT id FROM videos WHERE jav_id=?", (data["jav_id"],)
    ).fetchone()["id"]

    conn.execute("DELETE FROM video_actresses WHERE video_id=?", (vid_id,))
    conn.execute("DELETE FROM video_genres    WHERE video_id=?", (vid_id,))

    for name in data.get("actresses", []):
        conn.execute("INSERT OR IGNORE INTO actresses (name) VALUES (?)", (name,))
        aid = conn.execute("SELECT id FROM actresses WHERE name=?", (name,)).fetchone()["id"]
        conn.execute("INSERT OR IGNORE INTO video_actresses VALUES (?,?)", (vid_id, aid))

    for name in data.get("genres", []):
        conn.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (name,))
        gid = conn.execute("SELECT id FROM genres WHERE name=?", (name,)).fetchone()["id"]
        conn.execute("INSERT OR IGNORE INTO video_genres VALUES (?,?)", (vid_id, gid))

    conn.commit()
    return vid_id


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="jav-fetch",
        description="Fetch JAV metadata from missav.ws → SQLite",
    )
    parser.add_argument("ids", nargs="*", help="JAV IDs  e.g. MISM-410")
    parser.add_argument("--file", "-f", help="Text file with one ID per line")
    parser.add_argument("--db", default="jav.db", help="SQLite database path (default: jav.db)")
    args = parser.parse_args()

    ids = list(args.ids)
    if args.file:
        ids += Path(args.file).read_text().splitlines()
    ids = [i.strip().upper() for i in ids if i.strip()]

    if not ids:
        parser.print_help()
        sys.exit(1)

    conn    = open_db(args.db)
    session = make_session()

    for jav_id in ids:
        print(f"\n{'─'*50}\n{jav_id}")
        url = search_id(session, jav_id)
        if not url:
            continue
        time.sleep(DELAY)
        data = fetch_detail(session, url, jav_id)
        if not data:
            continue
        vid_id = upsert_video(conn, data)
        print(f"  [OK] saved (id={vid_id})  {data.get('title','')[:60]}")
        time.sleep(DELAY)

    conn.close()
    print(f"\n✓ Done — {args.db}")


if __name__ == "__main__":
    main()
