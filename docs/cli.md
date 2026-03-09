# CLI Reference

## `jav`
Run without arguments to launch an interactive shell.

```bash
uv run jav
```

Shell capabilities:
- direct commands: `fetch ...`, `db ...`, `serve ...`
- natural prompts: `get metadata for MISM-410`, `download media for ABW-123`
- slash commands: `/help`, `/clear`, `/quit`
- shell UX: persistent command history (`~/.jav_cli_history`) + tab autocomplete

Natural-language routing examples:
- `MISM-410` → `jav fetch MISM-410` (info + media)
- `metadata for MISM-410` → `jav fetch --info MISM-410`
- `no-download preview for MISM-410` → `jav fetch --media --no-download MISM-410`
- `stats` → `jav db stats`

## `jav fetch`
Fetch metadata and/or media.

```bash
uv run jav fetch MISM-410
uv run jav fetch --info MISM-410
uv run jav fetch --media MISM-410
uv run jav fetch --media --file ids.txt
uv run jav fetch --media --no-download MISM-410
uv run jav fetch --media --save-db MISM-410
uv run jav fetch --media --media-dir /custom/path/media MISM-410
uv run jav fetch --info --help
uv run jav fetch --media --help
uv run jav fetch --help
```

Notes:
- `uv run jav fetch --info` fetches and compares with DB, then asks whether to save (default: `No`).
- `uv run jav fetch --media` saves files to repo-root `./media` by default and does not save URLs to DB unless `--save-db` is passed.
- `uv run jav fetch` runs info then media with the same non-persistent defaults.

## `jav db`
Inspect and export local database records.

```bash
uv run jav db --db jav.db list
uv run jav db --db jav.db show MISM-410
uv run jav db --db jav.db search "MISM"
uv run jav db --db jav.db stats
uv run jav db --db jav.db export --format json
uv run jav db --db jav.db export --format csv
uv run jav db --help
```

## `jav serve`
Run local scanner/processor/player frontend.

```bash
uv run jav serve
uv run jav serve --video-dir /path/to/local/videos
uv run jav serve --dir /path/to/local/videos
uv run jav serve --host 127.0.0.1 --port 8765
uv run jav serve --force-override
uv run jav serve --help
```

Note:
- `serve` always rescans the selected source folder and keeps video paths in memory only.
- `serve` saves metadata/media URLs to DB (skip if existing) and saves media files under `<selected_video_dir>/media` (skip if existing).
- `--force-override` forces metadata/media refresh and overwrites existing local media files.
