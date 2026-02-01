# jav-toolkit

Local-first JAV organizer with CLI and web UI:
- metadata scraping (`jav-fetch`)
- media handling (`jav-media`)
- SQLite querying/export (`jav-db`)
- local web app (`jav-web`)

## Documentation
- [Getting Started](docs/getting-started.md)
- [CLI Reference](docs/cli.md)
- [Web UI Guide](docs/web-ui.md)
- [Architecture and Data](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)

## Quick Start
```bash
uv sync
uv run playwright install chromium
uv run jav-web
```

Open: `http://127.0.0.1:8765`
