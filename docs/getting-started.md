# Getting Started

## Requirements
- Python `3.12+`
- `uv`
- Playwright Chromium (one-time install)

## Install
```bash
uv sync
uv run playwright install chromium
```

## Run Web App
```bash
uv run jav
```

Then run in REPL:
```text
jav> serve
```

Default URL: `http://127.0.0.1:8765`

## First Run Flow
1. Open `Organize`.
2. Select your local video directory.
3. Click `Start Processing`.
4. Use `Browse`, `All Titles`, and `Watch`.

## Quick CLI Examples
```text
jav> fetch MISM-410
jav> db search MISM-410
jav> db list
```
