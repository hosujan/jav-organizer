# CLI Reference

## `jav`
Run without arguments to launch an interactive shell. This is the only supported launch mode.

```bash
uv run jav
```

Shell capabilities:
- exact commands only: `fetch <id> [id2 ...]`, `db ...`, `serve ...`
- slash commands: `/help`, `/clear`, `/quit`
- shell UX: persistent command history (`~/.jav_cli_history`) + tab autocomplete
- live slash discovery: typing `/` immediately shows slash commands below the prompt
- rich TUI (when `rich` is installed): colored panels/tables

## Command Examples (inside REPL)
Run `uv run jav`, then use shell commands like:

```text
jav> fetch MISM-410
jav> fetch MISM-410 ABW-123
jav> db search MISM-410
jav> db list
jav> serve
jav> /help
```

Notes:
- `fetch <id>` always runs metadata first, then media download, for each ID.
- `fetch` does not accept `--info` or `--media`.
- REPL `fetch` prompts whether to save metadata to DB after metadata is fetched.
- `db ...` commands are forwarded as-is to the DB CLI parser.

Note:
- `serve` always rescans the selected source folder and keeps video paths in memory only.
- `serve` saves metadata/media URLs to DB (skip if existing) and saves media files under `<selected_video_dir>/media` (skip if existing).
- `--force-override` forces metadata/media refresh and overwrites existing local media files.
