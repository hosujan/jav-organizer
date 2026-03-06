# CLI Reference

## `jav-fetch`
Fetch metadata and upsert into SQLite.

```bash
uv run jav-fetch MISM-410
uv run jav-fetch MISM-410 ABW-123 SSIS-456
uv run jav-fetch --file ids.txt
uv run jav-fetch --db jav.db MISM-410
```

## `jav-media`
Resolve poster/preview URLs and optionally download files.

```bash
uv run jav-media MISM-410
uv run jav-media --file ids.txt
uv run jav-media MISM-410 --no-download
uv run jav-media MISM-410 --media-dir ./media
uv run jav-media --db jav.db MISM-410
```

## `jav-db`
Inspect and export local database records.

```bash
uv run jav-db --db jav.db list
uv run jav-db --db jav.db show MISM-410
uv run jav-db --db jav.db search "MISM"
uv run jav-db --db jav.db stats
uv run jav-db --db jav.db export --format json
uv run jav-db --db jav.db export --format csv
```

## `jav-web`
Run local scanner/processor/player frontend.

```bash
uv run jav-web
uv run jav-web --db jav.db --media-dir ./media
uv run jav-web --video-dir /path/to/local/videos
uv run jav-web --host 127.0.0.1 --port 8765
```
