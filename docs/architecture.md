# Architecture and Data

## Core Components
- `src/jav_toolkit/scraper.py`: metadata scraping and DB upsert.
- `src/jav_toolkit/media.py`: media URL discovery and local downloads.
- `src/jav_toolkit/db.py`: DB inspection and export commands.
- `src/jav_toolkit/web/server.py`: local HTTP server + APIs.
- `src/jav_toolkit/web/processor.py`: scan/process pipeline.
- `src/jav_toolkit/config.py`: shared config + SQLite schema.

## Storage
- Database: `jav.db` by default.
- `fetch <id>` default media root: repo `./media`.
- `jav serve` media root: `<selected_video_dir>/media` (auto-created).

Media structure:
```text
media/
  MISM-410/
    poster.jpg|jpeg|png|webp
    preview.mp4
```

## Key Tables
- `videos`: metadata, media URLs, local video path.
- `watch_progress`: playback position and watch state.
- `actresses`, `video_actresses`
- `genres`, `video_genres`
- `app_settings`: app-level persisted settings.

## Behavior Notes
- Last selected video directory is stored in `app_settings.last_video_dir` and auto-restored in `jav serve`.
- Processing queue skips metadata fetch when JAV ID already exists in SQLite.
- Processing queue skips media URL scrape when media URLs already exist in SQLite.
- Media download step reuses existing local `poster.*` and `preview.mp4` when present.
- Playback uses HTTP range streaming for local seek support.
