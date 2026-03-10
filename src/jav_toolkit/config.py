"""Shared configuration, constants, and database initialisation."""

from __future__ import annotations
import sqlite3
from pathlib import Path

BASE_URL  = "https://missav.ws"
LANG      = "zh"          # Traditional Chinese
DELAY     = 1.5           # Polite delay between requests (seconds)
MEDIA_DIR = Path("media")
BROWSER_HEADLESS = False  # Playwright browser mode default
BROWSER_PROFILE_DIR = Path(".playwright_profile")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://missav.ws/",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS videos (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    jav_id           TEXT    UNIQUE NOT NULL,
    title            TEXT,
    plot             TEXT,
    release_date     TEXT,
    duration_min     INTEGER,
    cover_url        TEXT,
    page_url         TEXT,
    publisher        TEXT,
    label            TEXT,
    series           TEXT,
    director         TEXT,
    rating           REAL,
    poster_url       TEXT,
    preview_gif_url  TEXT,
    preview_mp4_url  TEXT,
    screenshots_json TEXT,
    fetched_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actresses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT UNIQUE NOT NULL,
    aliases_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS video_actresses (
    video_id   INTEGER REFERENCES videos(id)   ON DELETE CASCADE,
    actress_id INTEGER REFERENCES actresses(id) ON DELETE CASCADE,
    PRIMARY KEY (video_id, actress_id)
);

CREATE TABLE IF NOT EXISTS genres (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS video_genres (
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id)  ON DELETE CASCADE,
    PRIMARY KEY (video_id, genre_id)
);

CREATE TABLE IF NOT EXISTS watch_progress (
    jav_id        TEXT PRIMARY KEY,
    position_sec  REAL NOT NULL DEFAULT 0,
    duration_sec  REAL,
    percent       REAL NOT NULL DEFAULT 0,
    state         TEXT NOT NULL DEFAULT 'started',
    updated_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (jav_id) REFERENCES videos(jav_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS app_settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


def open_db(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def get_setting(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute(
        "SELECT value FROM app_settings WHERE key=?",
        (key,),
    ).fetchone()
    return row["value"] if row else None


def set_setting(conn: sqlite3.Connection, key: str, value: str):
    conn.execute(
        """
        INSERT INTO app_settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """,
        (key, value),
    )
    conn.commit()


def get_last_video_dir(db_path: str | Path) -> Path | None:
    conn = open_db(db_path)
    try:
        raw = get_setting(conn, "last_video_dir")
    finally:
        conn.close()
    if not raw:
        return None
    candidate = Path(raw).expanduser().resolve()
    if candidate.exists() and candidate.is_dir():
        return candidate
    return None


def resolve_media_root(
    db_path: str | Path,
    *,
    video_dir: str | Path | None = None,
    explicit_media_dir: str | Path | None = None,
) -> Path | None:
    if explicit_media_dir:
        return Path(explicit_media_dir).expanduser().resolve()

    if video_dir:
        candidate = Path(video_dir).expanduser().resolve()
        if candidate.exists() and candidate.is_dir():
            return (candidate / "media").resolve()
        return None

    last_dir = get_last_video_dir(db_path)
    if last_dir:
        return (last_dir / "media").resolve()
    return None
