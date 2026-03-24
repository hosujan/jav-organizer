# jav-toolkit

Local-first JAV organizer with CLI and web UI:
- metadata + media fetch (`fetch <id>` in REPL)
- SQLite querying/export (`jav db`)
- local web app (`jav serve`)

## Documentation
- [Getting Started](docs/getting-started.md)
- [CLI Reference](docs/cli.md)
- [Web UI Guide](docs/web-ui.md)
- [Architecture and Data](docs/architecture.md)
- [Database Migrations Guide](docs/db-migrations.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Development Guide](docs/development.md)

## Quick Start
```bash
uv sync
uv run playwright install chromium
uv run jav
```

Then in REPL:
```text
jav> serve
```

Open: `http://127.0.0.1:8765`
