"""Shared configuration, constants, and database initialisation."""

from __future__ import annotations
import sqlite3
from pathlib import Path

BASE_URL  = "https://missav.ws"
LANG      = "zh"          # Traditional Chinese
DELAY     = 1.5           # Polite delay between requests (seconds)
MEDIA_DIR = Path("media")

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
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
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
"""


def open_db(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(videos)").fetchall()}
    if "local_video_path" not in cols:
        conn.execute("ALTER TABLE videos ADD COLUMN local_video_path TEXT")
    conn.commit()
    return conn
