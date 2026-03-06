# Repository Guidelines

## Project Structure & Module Organization
- Core package code lives in `src/jav_toolkit/`.
- Main CLI entry points are:
  - `scraper.py` (`jav-fetch`) for metadata scraping.
  - `media.py` (`jav-media`) for poster/preview/screenshot download.
  - `db.py` (`jav-db`) for local SQLite queries and exports.
  - `config.py` for shared constants (base URL, language, paths, DB helpers).
- Runtime outputs are local-only: `media/` for downloaded assets and `*.db` (for example `jav.db`) for SQLite data.

## Build, Test, and Development Commands
- `uv sync`: install and lock project dependencies from `pyproject.toml`/`uv.lock`.
- `uv run playwright install chromium`: one-time browser install required by scraper/media flows.
- `uv run jav-fetch MISM-410`: scrape and store metadata for one ID (or pass multiple IDs / `--file ids.txt`).
- `uv run jav-media MISM-410 --no-download`: resolve media URLs without saving files.
- `uv run jav-db list` / `uv run jav-db show MISM-410`: inspect stored records.
- `uv run jav-db export --format json`: export local DB snapshots.

## Coding Style & Naming Conventions
- Python 3.12+, 4-space indentation, and type hints for public functions.
- Use `snake_case` for functions/variables, `UPPER_SNAKE_CASE` for constants, and clear CLI-oriented function names.
- Keep modules focused by concern (scraping, media capture, DB operations, shared config).
- Prefer small helper functions for parsing/classification logic; preserve existing CLI log style (`[SEARCH]`, `[DETAIL]`, `[WARN]`, etc.).

## Testing Guidelines
- There is currently no committed automated test suite.
- New features should include `pytest` tests under `tests/` with files named `test_<module>.py`.
- Target CLI and parser behavior first (ID resolution, field extraction, media URL filtering).
- Recommended local run once tests are added: `uv run pytest`.

## Commit & Pull Request Guidelines
- Follow existing history style: short, imperative, lowercase commit subjects (for example `use playwright for all scripts`).
- Keep each commit scoped to one change set.
- PRs should include:
  - What changed and why.
  - Commands used for verification.
  - Sample CLI output when scraper/media behavior changes.
  - Linked issue/ticket when available.

## Security & Configuration Tips
- Do not commit generated data (`media/`, `*.db`, virtualenvs); these are already ignored.
- Avoid hardcoding secrets or personal paths; prefer CLI flags such as `--db` and `--media-dir`.
