"""
Metadata scraping for REPL-driven `fetch` workflow.
"""

from __future__ import annotations
import json
import re
import time
from datetime import datetime
from typing import Literal
from urllib.parse import urljoin, urlparse

from .config import BASE_URL, DELAY, LANG, open_db


# ── Playwright page fetch ─────────────────────────────────────────────────────

def _browser_get(url: str, wait_ms: int = 2000) -> tuple[str, str]:
    """Return (final_url, html) using a real Chromium browser."""
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

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
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_timeout(wait_ms)
        except PWTimeout:
            print("  [WARN] page load timed out, parsing partial content")
        final_url = page.url
        html = page.content()
        ctx.close()
        browser.close()
    return final_url, html


# ── Search ────────────────────────────────────────────────────────────────────

def search_id(jav_id: str) -> str | None:
    """Return canonical detail-page URL, skipping uncensored-leak variants."""
    from bs4 import BeautifulSoup

    search_url = f"{BASE_URL}/{LANG}/search/{jav_id.lower()}"
    print(f"  [SEARCH] {search_url}")
    try:
        _, html = _browser_get(search_url)
    except Exception as e:
        print(f"  [ERROR] search failed: {e}")
        return None

    soup = BeautifulSoup(html, "lxml")
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

def fetch_detail(url: str, jav_id: str) -> dict | None:
    from bs4 import BeautifulSoup

    # Ensure language prefix
    parsed = urlparse(url)
    path = parsed.path
    if not path.startswith(f"/{LANG}/"):
        path = f"/{LANG}/{path.lstrip('/')}"
        url = f"{BASE_URL}{path}"

    print(f"  [DETAIL] {url}")
    try:
        _, html = _browser_get(url, wait_ms=3000)
    except Exception as e:
        print(f"  [ERROR] detail fetch failed: {e}")
        return None

    soup = BeautifulSoup(html, "lxml")
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
    og_desc = (
        soup.find("meta", property="og:description")
        or soup.find("meta", attrs={"name": "description"})
    )
    if og_desc:
        data["plot"] = og_desc.get("content", "").strip()

    # Structured metadata rows
    for row in soup.select(
        "div.grid-cols-1 > div, div.space-y-2 > div, div.detail > div"
    ):
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
    "時長": "duration_min",     "片長": "duration_min",
    "發行商": "publisher",      "廠商": "publisher",
    "標籤": "label",            "系列": "series",
    "導演": "director",         "評分": "rating",
}
_ACTRESS_KEYS = {"女優", "演員", "出演", "Cast"}
_GENRE_KEYS   = {"類型", "標籤", "Tags", "Genre", "分類"}
_ALIAS_SPLIT_RE = re.compile(r"[,/、，・;；]\s*")


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


def _parse_fallback(soup, data: dict):
    full_text = soup.get_text("\n")
    if "release_date" not in data:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", full_text)
        if m:
            data["release_date"] = m.group(1)
    if "duration_min" not in data:
        m = re.search(r"(\d{2,3})\s*(?:分鐘|分|min)", full_text)
        if m:
            data["duration_min"] = int(m.group(1))


def _unique_keep_order(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = value.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _expand_actress_names(raw_name: str) -> list[str]:
    value = raw_name.strip()
    if not value:
        return []

    # Handles forms like: "二葉惠麻 (二葉エマ)"
    match = re.fullmatch(r"(.+?)\s*[（(]\s*(.+?)\s*[）)]\s*$", value)
    if not match:
        return [value]

    primary = match.group(1).strip()
    alias_text = match.group(2).strip()
    aliases = _ALIAS_SPLIT_RE.split(alias_text) if alias_text else []
    return _unique_keep_order([primary, *aliases])


def _load_aliases(row) -> list[str]:
    try:
        data = json.loads(row["aliases_json"] or "[]")
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
    except Exception:
        pass
    return []


def _find_actress_row_by_any_name(conn, names: list[str]):
    if not names:
        return None

    placeholders = ",".join("?" for _ in names)
    row = conn.execute(
        f"SELECT id, name, aliases_json FROM actresses WHERE name IN ({placeholders}) LIMIT 1",
        tuple(names),
    ).fetchone()
    if row:
        return row

    # Fallback in Python to avoid requiring SQLite JSON1 extension features.
    for actress in conn.execute("SELECT id, name, aliases_json FROM actresses").fetchall():
        alias_set = set(_load_aliases(actress))
        if any(name in alias_set for name in names):
            return actress
    return None


def _upsert_actress(conn, raw_name: str) -> int:
    names = _expand_actress_names(raw_name)
    if not names:
        raise ValueError("actress name is empty")

    primary = names[0]
    row = _find_actress_row_by_any_name(conn, names)
    if not row:
        aliases = _unique_keep_order([x for x in names[1:] if x != primary])
        payload = json.dumps(aliases, ensure_ascii=False)
        conn.execute(
            "INSERT INTO actresses (name, aliases_json) VALUES (?, ?)",
            (primary, payload),
        )
        return conn.execute(
            "SELECT id FROM actresses WHERE name=?",
            (primary,),
        ).fetchone()["id"]

    existing_name = row["name"]
    merged_aliases = _unique_keep_order([
        *_load_aliases(row),
        *[x for x in names if x != existing_name],
    ])
    payload = json.dumps(merged_aliases, ensure_ascii=False)
    conn.execute(
        "UPDATE actresses SET aliases_json=? WHERE id=?",
        (payload, row["id"]),
    )
    return row["id"]


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
        aid = _upsert_actress(conn, name)
        conn.execute("INSERT OR IGNORE INTO video_actresses VALUES (?,?)", (vid_id, aid))

    for name in data.get("genres", []):
        conn.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (name,))
        gid = conn.execute("SELECT id FROM genres WHERE name=?", (name,)).fetchone()["id"]
        conn.execute("INSERT OR IGNORE INTO video_genres VALUES (?,?)", (vid_id, gid))

    conn.commit()
    return vid_id


def fetch_ids(ids: list[str], db_path: str = "jav.db", save_mode: Literal["ask", "yes", "no"] = "ask") -> None:
    normalized_ids = [i.strip().upper() for i in ids if i.strip()]
    if not normalized_ids:
        raise ValueError("fetch_ids requires at least one JAV ID")

    conn = open_db(db_path)

    for jav_id in normalized_ids:
        print(f"\n{'─'*50}\n{jav_id}")
        url = search_id(jav_id)
        if not url:
            continue
        time.sleep(DELAY)
        data = fetch_detail(url, jav_id)
        if not data:
            continue

        existing = conn.execute(
            "SELECT title, release_date, publisher, director, rating FROM videos WHERE jav_id=?",
            (jav_id,),
        ).fetchone()
        print("  [DB ]")
        if existing:
            print(f"    title       : {existing['title'] or '—'}")
            print(f"    release_date: {existing['release_date'] or '—'}")
            print(f"    publisher   : {existing['publisher'] or '—'}")
            print(f"    director    : {existing['director'] or '—'}")
            print(f"    rating      : {existing['rating'] if existing['rating'] is not None else '—'}")
        else:
            print("    (no existing DB record)")
        print("  [NEW]")
        print(f"    title       : {data.get('title') or '—'}")
        print(f"    release_date: {data.get('release_date') or '—'}")
        print(f"    publisher   : {data.get('publisher') or '—'}")
        print(f"    director    : {data.get('director') or '—'}")
        print(f"    rating      : {data.get('rating') if data.get('rating') is not None else '—'}")

        save = False
        if save_mode == "yes":
            save = True
        elif save_mode == "no":
            save = False
            print("  [INFO] save mode=no: skipping DB write.")
        elif sys.stdin.isatty():
            answer = input("  Save fetched info to DB? [y/N/ya/na]: ").strip().lower()
            if answer in {"ya", "yes all"}:
                save_mode = "yes"
                save = True
                print("  [INFO] save mode=yes for all remaining IDs.")
            elif answer in {"na", "no all"}:
                save_mode = "no"
                save = False
                print("  [INFO] save mode=no for all remaining IDs.")
            else:
                save = answer in {"y", "yes"}
        else:
            print("  [INFO] non-interactive mode: defaulting to not save.")
        if save:
            vid_id = upsert_video(conn, data)
            print(f"  [OK] saved id={vid_id}")
        else:
            print("  [SKIP] not saved to DB")
        time.sleep(DELAY)

    conn.close()
    print(f"\n✓ Done — reviewed against {db_path}")
