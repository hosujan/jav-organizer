# jav-toolkit

Local-first JAV organizer with:
- metadata scraping (`jav-fetch`)
- poster/preview media handling (`jav-media`)
- SQLite inspection/export (`jav-db`)
- browser UI for scan/process/playback (`jav-web`)

The app stores everything locally (database + media files) and does not require cloud services.

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Quick Start](#quick-start)
4. [CLI Reference](#cli-reference)
5. [Web UI Guide](#web-ui-guide)
6. [Data and Storage](#data-and-storage)
7. [Behavior Notes](#behavior-notes)
8. [Troubleshooting](#troubleshooting)

## Features
- Scrape metadata into SQLite by JAV ID.
- Resolve and download poster + preview MP4.
- Scan a local video directory and link each file to its JAV ID.
- Track watch progress and resume playback.
- Recommendation rails and dedicated `All Titles` catalog page.
- Cache-aware processing to avoid repeated network work.

## Requirements
- Python `3.12+`
- `uv`
- Playwright Chromium (one-time install)

## Quick Start
```bash
uv sync
uv run playwright install chromium
```

### Start the web app
```bash
uv run jav-web
```

Default URL: `http://127.0.0.1:8765`

### Typical first-run flow
1. Open `Organize`.
2. Select your local video directory.
3. Click `Start Processing`.
4. Open `Browse` / `All Titles` / `Watch`.

## CLI Reference

### `jav-fetch` (metadata)
Fetch metadata and save/upsert into SQLite.

```bash
uv run jav-fetch MISM-410
uv run jav-fetch MISM-410 ABW-123 SSIS-456
uv run jav-fetch --file ids.txt
uv run jav-fetch --db jav.db MISM-410
```

### `jav-media` (media URLs + download)
Resolve poster/preview URLs and optionally download local files.

```bash
uv run jav-media MISM-410
uv run jav-media --file ids.txt
uv run jav-media MISM-410 --no-download
uv run jav-media MISM-410 --media-dir ./media
uv run jav-media --db jav.db MISM-410
```

### `jav-db` (query/export)
Inspect local database records.

```bash
uv run jav-db --db jav.db list
uv run jav-db --db jav.db show MISM-410
uv run jav-db --db jav.db search "MISM"
uv run jav-db --db jav.db stats
uv run jav-db --db jav.db export --format json
uv run jav-db --db jav.db export --format csv
```

### `jav-web` (web UI)
Run local scanner/processor/player frontend.

```bash
uv run jav-web
uv run jav-web --db jav.db --media-dir ./media
uv run jav-web --video-dir /path/to/local/videos
uv run jav-web --host 127.0.0.1 --port 8765
```

## Web UI Guide

### `Organize`
- Choose local directory and run processing.
- Shows progress/logs/history.
- Selected directory is persisted and restored on next launch.

### `Browse`
- Featured hero + recommendation rails.
- Lightweight discovery filters.
- Button to open dedicated `All Titles` page.

### `All Titles`
- Full catalog page with search, filters, and sort controls.
- Responsive card grid with watch progress status.

### `Video` and `Watch`
- Metadata detail page with preview and facts.
- Full playback page with progress save/resume and Up Next list.

## Data and Storage

### Default local outputs
- DB: `jav.db` (unless overridden with `--db`)
- Media root: `media/` (unless overridden with `--media-dir`)

Media files are organized by JAV ID:
```text
media/
  MISM-410/
    poster.jpg|jpeg|png|webp
    preview.mp4
```

### Key SQLite tables
- `videos`: core metadata + local video path + media URLs
- `watch_progress`: position/percent/state for playback resume
- `actresses`, `genres`, join tables
- `app_settings`: app-level settings (e.g., last selected video directory)

## Behavior Notes

### Persistent last video directory
When you select a folder in `Organize`, the app stores it in SQLite (`app_settings.last_video_dir`) and restores it next time `jav-web` starts (unless `--video-dir` is explicitly provided).

### Processing optimization (skip repeated work)
During `Start Processing`:
- If a JAV ID already exists in SQLite, metadata fetch is skipped.
- If `poster_url` / `preview_mp4_url` already exist in SQLite, media URL scraping is skipped.
- Before downloading, local media folder is checked:
  - existing `poster.*` is reused
  - existing `preview.mp4` is reused

### Playback transport
Video streaming uses HTTP range responses for local-file seeking. Client disconnects are handled safely (broken-pipe write attempts are ignored server-side).

## Troubleshooting

### Playwright not installed
```bash
uv run playwright install chromium
```

### Empty scan results
- Confirm file extensions are supported (`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.m4v`, `.ts`, `.webm`).
- Ensure filenames or paths contain recognizable IDs like `ABW-123`.

### No metadata/media for some IDs
- Source site may not have that title or structure may differ.
- Re-run later or use manual verification for edge titles.

### Port already in use
```bash
uv run jav-web --port 8877
```

### Use separate environments/data
Pass both `--db` and `--media-dir` to isolate datasets:
```bash
uv run jav-web --db ./data/dev.db --media-dir ./data/media
```
