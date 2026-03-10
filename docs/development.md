# Development Guide

## Local Setup
```bash
uv sync
uv run playwright install chromium
```

## Run Commands During Development
Start REPL:
```bash
uv run jav
```
- Run scraper for one ID:
```text
jav> fetch MISM-410
```
- Resolve/download media:
```text
jav> fetch MISM-410
```
- Inspect DB:
```text
jav> db list
```
- Start web app:
```text
jav> serve --db jav.db --video-dir /path/to/local/videos
```

## Project Structure
- `src/jav_toolkit/config.py`: shared constants + DB schema/init.
- `src/jav_toolkit/scraper.py`: metadata scraping and DB upsert.
- `src/jav_toolkit/media.py`: media URL discovery/download.
- `src/jav_toolkit/db.py`: DB query/export CLI.
- `src/jav_toolkit/web/server.py`: HTTP routes and APIs.
- `src/jav_toolkit/web/pages.py`: HTML/CSS/JS templates.
- `src/jav_toolkit/web/processor.py`: queue processing pipeline.
- `src/jav_toolkit/web/scanner.py`: local file scanning/JAV ID normalization.
- `src/jav_toolkit/web/state.py`: app runtime state model.

## Code Style
- Python `3.12+`
- 4-space indentation, type hints for public functions.
- Keep modules focused by concern.
- Preserve existing log style (`[SEARCH]`, `[DETAIL]`, `[WARN]`, etc.).

## Testing
There is currently no committed automated test suite.

Recommended when changing behavior:
- Add `pytest` tests under `tests/` as `test_<module>.py`.
- Focus first on:
  - ID normalization and file scanning
  - parser/extractor behavior
  - API responses for web routes

Run tests (when present):
```bash
uv run pytest
```

## Common Development Tasks

### Add/adjust DB schema
1. Update `SCHEMA` in `config.py`.
2. Add migration-safe handling in `open_db()` if needed (for existing DB files).
3. Validate with a fresh DB and an existing DB.

### Change web UI behavior
1. Update templates/scripts in `pages.py`.
2. Wire new route/API in `web/server.py` if needed.
3. Compile-check:
```bash
uv run python -m compileall src/jav_toolkit/web/pages.py src/jav_toolkit/web/server.py
```

### Change processing behavior
1. Update queue flow in `web/processor.py`.
2. Verify skip/caching logic with both new and already-processed IDs.
3. Confirm UI logs and progress updates remain clear.

## Release Checklist
1. Run smoke checks:
   - `jav> fetch <sample-id>`
   - `jav> db list`
   - `jav> serve`
2. Verify core web flows:
   - Organize scan/process
   - Browse and All Titles rendering
   - Watch progress save/resume
3. Compile-check modified Python files:
```bash
uv run python -m compileall src
```
4. Update docs (`README.md` + affected files in `docs/`).
5. Ensure generated artifacts (`media/`, `*.db`) are not committed.

## Notes for Contributors
- Avoid committing personal paths or machine-specific config.
- Prefer small, scoped PRs.
- Include verification commands and behavior summary in PR descriptions.
