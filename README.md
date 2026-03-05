# jav-toolkit

JAV metadata scraper, media downloader, and local database — powered by missav.ws (Traditional Chinese).

---

## Setup

```bash
cd jav-toolkit
uv sync
uv run playwright install chromium   # one-time
```

---

## Workflow

### Step 1 — Fetch metadata
```bash
uv run jav-fetch MISM-410
uv run jav-fetch MISM-410 ABW-123 SSIS-456
uv run jav-fetch --file ids.txt
```

### Step 2 — Download media
```bash
uv run jav-media MISM-410
uv run jav-media MISM-410 --no-download      # URLs only, no files
uv run jav-media MISM-410 --media-dir /path  # custom folder
```

Output:
```
media/MISM-410/
  poster.jpg
  preview.gif
  preview.mp4
  screenshot_01.jpg ...
```

### Step 3 — Query
```bash
uv run jav-db list
uv run jav-db show MISM-410
uv run jav-db search "二葉惠麻"
uv run jav-db stats
uv run jav-db export --format json
uv run jav-db export --format csv
```

All commands accept `--db path/to/other.db`.
