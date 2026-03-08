# Troubleshooting

## Playwright Not Installed
```bash
uv run playwright install chromium
```

## Empty Scan Results
- Confirm extension is supported: `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.m4v`, `.ts`, `.webm`.
- Ensure filename/path includes recognizable IDs like `ABW-123`.

## Missing Metadata or Media
- Source site may not contain the ID.
- Site structure can vary by title.
- Retry later or verify manually.

## Port Already In Use
```bash
uv run jav serve --port 8877
```

## Separate Data Environments
```bash
uv run jav serve --db ./data/dev.db --video-dir /path/to/dev/videos
```
