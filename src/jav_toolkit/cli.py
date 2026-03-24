"""Unified CLI entrypoint for jav-toolkit."""

from __future__ import annotations

import argparse
import os
import shlex
import sys
import time
from pathlib import Path

from . import db, media, scraper
from .config import BROWSER_HEADLESS, DELAY, open_db
from .web import server

_HISTORY_FILE = Path.home() / ".jav_cli_history"
_SLASH_COMMANDS: dict[str, str] = {
    "/help": "show help and examples",
    "/config": "configure interactive shell behavior",
    "/clear": "clear screen and redraw banner",
    "/quit": "exit interactive shell",
}
_ROOT_COMMANDS = ("fetch", "db", "serve")
_REPL_TOKENS = sorted(
    {
        *_ROOT_COMMANDS,
        "list",
        "show",
        "search",
        "stats",
        "export",
        "--format",
        "json",
        "csv",
        "jav",
        *_SLASH_COMMANDS.keys(),
        "help",
        "clear",
        "quit",
    }
)
_BANNER = r"""
       __               ________    ____
      / /___ __   __   / ____/ /   /  _/
 __  / / __ `/ | / /  / /   / /    / /
/ /_/ / /_/ /| |/ /  / /___/ /____/ /
\____/\__,_/ |___/   \____/_____/___/
"""
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    _CONSOLE: Console | None = Console()
except Exception:
    _CONSOLE = None

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.application.current import get_app
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import FileHistory

    _PTK_AVAILABLE = True
except Exception:
    _PTK_AVAILABLE = False

_PROMPT_SESSION: PromptSession[str] | None = None if _PTK_AVAILABLE else None
_BROWSER_HEADLESS = BROWSER_HEADLESS


def _clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _print_info_box() -> None:
    version = "0.1.0"
    cwd = os.getcwd()
    home = str(Path.home())
    display_cwd = cwd.replace(home, "~", 1) if cwd.startswith(home) else cwd

    # Visual width matching the user's example
    width = 60

    # Truncate directory if too long for the box
    max_dir_len = width - 15
    if len(display_cwd) > max_dir_len:
        display_cwd = "…" + display_cwd[-(max_dir_len - 1) :]

    if _CONSOLE:
        table = Table.grid(padding=(0, 1))
        table.add_column()
        table.add_column(justify="right")
        table.add_row(f"[bold cyan]>_[/bold cyan] jav-toolkit (v{version})", "")
        table.add_row("", "")
        table.add_row("provider:  MissAV (zh)", "[dim]/config to change[/dim]")
        table.add_row(f"directory: {display_cwd}", "")
        _CONSOLE.print(Panel(table, border_style="bright_black", width=60))
        return

    print(f"╭{'─' * (width - 2)}╮")

    # Line 1: >_ jav-toolkit (v0.1.0)
    line1 = f">_ jav-toolkit (v{version})"
    print(f"│ {line1:<{width - 4}} │")

    # Line 2: Spacer
    print(f"│ {' ' * (width - 4)} │")

    # Line 3: provider: MissAV (zh) /config to change
    left3 = "provider:  MissAV (zh)"
    right3 = "/config to change"
    gap3 = (width - 4) - len(left3) - len(right3)
    print(f"│ {left3}{' ' * gap3}{right3} │")

    # Line 4: directory: ...
    line4 = f"directory: {display_cwd}"
    print(f"│ {line4:<{width - 4}} │")

    print(f"╰{'─' * (width - 2)}╯")


def _print_banner() -> None:
    if _CONSOLE:
        _CONSOLE.print(f"[bold magenta]{_BANNER}[/bold magenta]")
    else:
        print(_BANNER)
    _print_info_box()
    _print_status("Exact commands only. Type `/help` for command syntax.")


def _print_status(message: str) -> None:
    if _CONSOLE:
        _CONSOLE.print(f"[dim]{message}[/dim]")
    else:
        print(message)


def _print_warn(message: str) -> None:
    if _CONSOLE:
        _CONSOLE.print(f"[yellow]{message}[/yellow]")
    else:
        print(message)


def _setup_readline() -> None:
    try:
        import atexit
        import readline  # type: ignore[import-not-found]
    except Exception:
        return

    def complete(text: str, state: int) -> str | None:
        buffer = readline.get_line_buffer()
        begidx = readline.get_begidx()
        prefix = buffer[:begidx]
        at_cmd_start = not prefix.strip()
        candidates = _REPL_TOKENS

        # Favor slash commands when user starts with slash.
        if text.startswith("/"):
            candidates = [token for token in _REPL_TOKENS if token.startswith("/")]
        elif at_cmd_start:
            candidates = [token for token in (*_ROOT_COMMANDS, "jav", *_SLASH_COMMANDS.keys())]

        matches = [token for token in candidates if token.startswith(text)]
        return matches[state] if state < len(matches) else None

    try:
        readline.read_history_file(str(_HISTORY_FILE))
    except FileNotFoundError:
        pass
    except Exception:
        # Keep REPL functional even if history cannot be loaded.
        pass

    readline.set_completer(complete)
    # Keep "-" and "/" inside tokens so flags and slash commands can complete.
    readline.set_completer_delims(" \t\n")
    doc = (readline.__doc__ or "").lower()
    if "libedit" in doc:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")
    readline.set_history_length(1000)

    def _save_history() -> None:
        try:
            readline.write_history_file(str(_HISTORY_FILE))
        except Exception:
            pass

    atexit.register(_save_history)


def _setup_prompt_session() -> None:
    global _PROMPT_SESSION
    if not _PTK_AVAILABLE:
        return
    if _PROMPT_SESSION is not None:
        return

    completer = WordCompleter(list(_REPL_TOKENS), ignore_case=True, sentence=True)
    _PROMPT_SESSION = PromptSession(
        history=FileHistory(str(_HISTORY_FILE)),
        completer=completer,
        complete_while_typing=True,
        auto_suggest=AutoSuggestFromHistory(),
    )


def _slash_toolbar() -> str:
    if not _PTK_AVAILABLE:
        return ""

    text = get_app().current_buffer.text.strip()
    if not text.startswith("/"):
        return ""

    if text == "/":
        matches = list(_SLASH_COMMANDS.keys())
    else:
        matches = [cmd for cmd in _SLASH_COMMANDS if cmd.startswith(text)]

    if not matches:
        return "  no slash command matches"

    lines = ["  slash commands:"]
    lines.extend(f"    - {cmd}" for cmd in matches)
    return "\n".join(lines)


def _read_repl_input(prompt_text: str) -> str:
    if _PROMPT_SESSION is not None:
        return _PROMPT_SESSION.prompt(prompt_text, bottom_toolbar=_slash_toolbar)
    return input(prompt_text)


def _build_root_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jav",
        description="Unified CLI for jav-toolkit",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("fetch", help="Fetch metadata + media by ID")
    sub.add_parser("db", help="Query/export local database")
    sub.add_parser("serve", help="Run local web frontend")
    return parser


def _build_fetch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jav fetch",
        description="Fetch metadata and media by ID.",
    )
    parser.add_argument("ids", nargs="+", help="One or more JAV IDs, e.g. MISM-410")
    return parser


def _run_fetch(args: argparse.Namespace) -> None:
    normalized_ids = [value.strip().upper() for value in args.ids if value.strip()]
    if not normalized_ids:
        _print_warn("Missing JAV ID.")
        return

    db_path = Path("jav.db")
    media_root = Path("media").resolve()
    media_root.mkdir(parents=True, exist_ok=True)

    conn = open_db(db_path)
    plans: list[dict] = []
    try:
        for jav_id in normalized_ids:
            print(f"\n{'─' * 50}\n{jav_id}")
            url = scraper.search_id(jav_id, headless=_BROWSER_HEADLESS)
            if not url:
                continue
            time.sleep(DELAY)

            data = scraper.fetch_detail(url, jav_id, headless=_BROWSER_HEADLESS)
            if not data:
                continue

            media_urls = media.scrape_media_urls(jav_id, headless=_BROWSER_HEADLESS)
            payloads = media.fetch_media_payloads(jav_id, media_urls)

            info_diffs = _diff_video_info(conn, jav_id, data)
            media_diffs, media_changed, media_changed_keys = _diff_media_files(jav_id, media_root, payloads)
            if info_diffs or media_diffs:
                plans.append(
                    {
                        "jav_id": jav_id,
                        "data": data,
                        "media_urls": media_urls,
                        "payloads": payloads,
                        "info_diffs": info_diffs,
                        "media_diffs": media_diffs,
                        "media_changed": media_changed,
                        "media_changed_keys": media_changed_keys,
                    }
                )
            time.sleep(DELAY)

        if not plans:
            _print_status("No metadata/media changes detected. Nothing to save.")
            return

        for plan in plans:
            print(f"\n{plan['jav_id']}:")
            for line in plan["info_diffs"] + plan["media_diffs"]:
                print(f"  {line}")

        info_changed_count = sum(1 for plan in plans if plan["info_diffs"])
        media_changed_count = sum(1 for plan in plans if plan["media_changed"])
        answer = "n"
        if sys.stdin.isatty():
            answer = input(
                f"\n  In total {info_changed_count} videos have updated info, "
                f"and {media_changed_count} videos have new media files. "
                "Save to DB and local disk? [Y/n/ya/na]: "
            ).strip().lower()
        else:
            _print_status("Non-interactive mode: changes detected but save is skipped.")

        if answer in {"", "y", "yes", "ya", "yes all"}:
            for plan in plans:
                if plan["info_diffs"]:
                    scraper.upsert_video(conn, plan["data"])
                media.save_media_urls(conn, plan["jav_id"], plan["media_urls"])
                changed_payloads = {
                    key: value
                    for key, value in plan["payloads"].items()
                    if key in plan["media_changed_keys"]
                }
                saved = media.save_media_payloads(plan["jav_id"], changed_payloads, media_root)
                saved_parts: list[str] = []
                if plan["info_diffs"]:
                    saved_parts.append("metadata")
                if saved:
                    saved_parts.append(", ".join(saved.keys()))
                if not saved_parts:
                    saved_parts.append("no-op")
                _print_status(
                    f"[OK] {plan['jav_id']} saved "
                    f"({'; '.join(saved_parts)})"
                )
        else:
            _print_status("Save skipped.")
    finally:
        conn.close()


def _format_scalar(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    text = str(value).strip()
    return text if text else "—"


def _format_list(values: list[str]) -> str:
    if not values:
        return "—"
    return ", ".join(values)


def _db_video_snapshot(conn, jav_id: str) -> dict | None:
    row = conn.execute(
        """
        SELECT id, title, plot, release_date, duration_min, cover_url, page_url,
               publisher, label, series, director, rating
        FROM videos
        WHERE jav_id=?
        """,
        (jav_id,),
    ).fetchone()
    if not row:
        return None

    actresses = [
        actress_row["name"]
        for actress_row in conn.execute(
            """
            SELECT a.name
            FROM video_actresses va
            JOIN actresses a ON a.id = va.actress_id
            WHERE va.video_id=?
            ORDER BY a.name
            """,
            (row["id"],),
        ).fetchall()
    ]
    genres = [
        genre_row["name"]
        for genre_row in conn.execute(
            """
            SELECT g.name
            FROM video_genres vg
            JOIN genres g ON g.id = vg.genre_id
            WHERE vg.video_id=?
            ORDER BY g.name
            """,
            (row["id"],),
        ).fetchall()
    ]
    return {
        "title": row["title"],
        "plot": row["plot"],
        "release_date": row["release_date"],
        "duration_min": row["duration_min"],
        "cover_url": row["cover_url"],
        "page_url": row["page_url"],
        "publisher": row["publisher"],
        "label": row["label"],
        "series": row["series"],
        "director": row["director"],
        "rating": row["rating"],
        "actresses": actresses,
        "genres": genres,
    }


def _diff_video_info(conn, jav_id: str, data: dict) -> list[str]:
    fields = [
        "title",
        "plot",
        "release_date",
        "duration_min",
        "cover_url",
        "publisher",
        "label",
        "series",
        "director",
        "rating",
    ]
    existing = _db_video_snapshot(conn, jav_id)
    new_lists = {
        "actresses": sorted({str(v).strip() for v in data.get("actresses", []) if str(v).strip()}),
        "genres": sorted({str(v).strip() for v in data.get("genres", []) if str(v).strip()}),
    }

    diffs: list[str] = []
    if not existing:
        for field in fields:
            new_value = _format_scalar(data.get(field))
            if new_value != "—":
                diffs.append(f"{field}: — -> {new_value}")
        for field in ("actresses", "genres"):
            new_value = _format_list(new_lists[field])
            if new_value != "—":
                diffs.append(f"{field}: — -> {new_value}")
        return diffs

    for field in fields:
        before = _format_scalar(existing.get(field))
        after = _format_scalar(data.get(field))
        if before != after:
            diffs.append(f"{field}: {before} -> {after}")

    for field in ("actresses", "genres"):
        before = _format_list(sorted({str(v).strip() for v in existing.get(field, []) if str(v).strip()}))
        after = _format_list(new_lists[field])
        if before != after:
            diffs.append(f"{field}: {before} -> {after}")
    return diffs


def _size_text(size: int | None) -> str:
    if not size:
        return "—"
    return f"{size // 1024}KB"


def _media_changed(existing_path: Path | None, payload: dict | None) -> tuple[bool, int | None, int | None]:
    before_size: int | None = None
    if existing_path and existing_path.exists():
        before_size = existing_path.stat().st_size
    if not payload:
        return False, before_size, None
    after_size = int(payload["size"])
    if not existing_path or not existing_path.exists():
        return True, before_size, after_size
    try:
        before_bytes = existing_path.read_bytes()
    except Exception:
        return True, before_size, after_size
    return before_bytes != payload["data"], before_size, after_size


def _diff_media_files(jav_id: str, media_root: Path, payloads: dict[str, dict]) -> tuple[list[str], bool, set[str]]:
    local = media.local_media_paths(jav_id, media_root)
    media_diffs: list[str] = []
    media_changed = False
    changed_keys: set[str] = set()

    poster_changed, poster_before, poster_after = _media_changed(local["poster"], payloads.get("poster"))
    if poster_changed:
        media_diffs.append(f"poster: {_size_text(poster_before)} -> {_size_text(poster_after)}")
        media_changed = True
        changed_keys.add("poster")

    preview_changed, preview_before, preview_after = _media_changed(local["preview_mp4"], payloads.get("preview_mp4"))
    if preview_changed:
        media_diffs.append(f"preview.mp4: {_size_text(preview_before)} -> {_size_text(preview_after)}")
        media_changed = True
        changed_keys.add("preview_mp4")

    return media_diffs, media_changed, changed_keys


def _print_shell_help() -> None:
    if _CONSOLE:
        table = Table(title="Interactive Commands", show_header=True, header_style="bold cyan")
        table.add_column("Category", style="green", no_wrap=True)
        table.add_column("Examples")
        table.add_row("CLI commands", "fetch MISM-410")
        table.add_row("CLI commands", "db search MISM-410")
        table.add_row("CLI commands", "db show MISM-410 | db list | db stats")
        table.add_row("CLI commands", "serve")
        table.add_row("Slash commands", "/help  /config  /clear  /quit")
        _CONSOLE.print(table)
        return

    print("Interactive commands:")
    print("  CLI commands:")
    print("    fetch MISM-410")
    print("    fetch MISM-410 ABW-123")
    print("    db search MISM-410")
    print("    db list | db show MISM-410 | db stats")
    print("    serve")
    print("")
    print("  Slash commands:")
    for cmd, desc in _SLASH_COMMANDS.items():
        print(f"    {cmd:<7} {desc}")


def _print_slash_indicators(prefix: str = "") -> None:
    commands = [cmd for cmd in _SLASH_COMMANDS if cmd.startswith(prefix)]
    if not commands:
        _print_warn(f"No slash commands match '{prefix}'.")
        return

    if _CONSOLE:
        table = Table(title=f"Slash Commands ({prefix or 'all'})", show_header=True, header_style="bold magenta")
        table.add_column("Command", style="green")
        table.add_column("Description")
        for cmd in commands:
            table.add_row(cmd, _SLASH_COMMANDS[cmd])
        _CONSOLE.print(table)
        return

    print("Slash commands:")
    for cmd in commands:
        print(f"  {cmd:<7} {_SLASH_COMMANDS[cmd]}")


def _configure_shell() -> None:
    global _BROWSER_HEADLESS
    while True:
        _print_status("Current configuration:")
        _print_status(f"  browser headless mode: {'on' if _BROWSER_HEADLESS else 'off'}")
        print("Choose config item:")
        print(f"  1) browser headless mode ({'on' if _BROWSER_HEADLESS else 'off'})")
        print("  b) back")
        item = input("Select item [1/b, Enter to keep]: ").strip().lower()

        if not item or item in {"b", "back"}:
            _print_status("Exited config menu.")
            return

        if item == "1":
            while True:
                print("Choose browser headless mode:")
                print(f"  1) off (show browser window){' (current)' if not _BROWSER_HEADLESS else ''}")
                print(f"  2) on (run headless){' (current)' if _BROWSER_HEADLESS else ''}")
                print("  b) back")
                choice = input("Select mode [1/2/b, Enter to keep]: ").strip().lower()
                if not choice or choice in {"b", "back"}:
                    break
                if choice == "1":
                    _BROWSER_HEADLESS = False
                elif choice == "2":
                    _BROWSER_HEADLESS = True
                else:
                    _print_warn("Invalid choice. Try again.")
                    continue
                _print_status(f"Saved: browser headless mode = {'on' if _BROWSER_HEADLESS else 'off'}.")
                break
            continue

        _print_warn("Invalid choice. Try again.")


def _parse_shell_input(raw: str) -> list[str] | None:
    text = raw.strip()
    if not text:
        return None

    if text.startswith("/"):
        cmd_text = text[1:].strip().lower()
        if not cmd_text:
            _print_slash_indicators("/")
            return None

        matches = [cmd for cmd in _SLASH_COMMANDS if cmd[1:].startswith(cmd_text)]
        if len(matches) == 1:
            resolved = matches[0]
            if resolved == "/quit":
                return ["__quit__"]
            if resolved == "/clear":
                return ["__clear__"]
            if resolved == "/config":
                _configure_shell()
                return None
            if resolved == "/help":
                _print_shell_help()
                return None

        if len(matches) > 1:
            _print_warn(f"Ambiguous slash command: /{cmd_text}")
            _print_status(f"Matches: {', '.join(matches)}")
            return None

        _print_warn(f"Unknown slash command: /{cmd_text}")
        _print_status("Use slash commands: /help (/h), /config (/co), /clear (/c), /quit (/q).")
        return None

    if text.lower() == "quit":
        return ["__quit__"]
    if text.lower() == "clear":
        return ["__clear__"]
    if text.lower() == "help":
        _print_shell_help()
        return None

    try:
        tokens = shlex.split(text)
    except ValueError as err:
        _print_warn(f"Parse error: {err}")
        return None

    if tokens:
        if tokens[0].lower() == "jav":
            tokens = tokens[1:]
        if not tokens:
            _print_status("Use exact commands: `fetch <id>`, `db ...`, `serve`, `/help`.")
            return None
        first = tokens[0]
        if first in _ROOT_COMMANDS:
            if first == "fetch":
                if len(tokens) < 2:
                    _print_warn("Missing JAV ID.")
                    _print_status("Usage: fetch <id> <id2 ...>")
                    return None
                if any(part.startswith("-") for part in tokens[1:]):
                    _print_warn("Invalid fetch syntax.")
                    _print_status("Usage: fetch <id> <id2 ...>")
                    return None
            return tokens

    _print_warn("Could not understand command.")
    _print_status("Use exact commands: `fetch <id>`, `db ...`, `serve`, `/help`.")
    return None


def _run_interactive_shell() -> None:
    if not sys.stdin.isatty():
        print("No command provided. Use --help for usage.")
        raise SystemExit(1)

    if _PTK_AVAILABLE:
        _setup_prompt_session()
    else:
        _setup_readline()
    _clear_screen()
    _print_banner()

    while True:
        try:
            raw = _read_repl_input("jav> ")
        except (EOFError, KeyboardInterrupt):
            print("")
            return

        if raw.strip() == "/":
            _print_slash_indicators("/")
            continue

        argv = _parse_shell_input(raw)
        if not argv:
            continue
        if argv == ["__quit__"]:
            return
        if argv == ["__clear__"]:
            _clear_screen()
            _print_banner()
            continue

        try:
            _dispatch(argv)
        except SystemExit:
            continue


def _dispatch(argv: list[str]) -> None:
    root_parser = _build_root_parser()
    if argv[0] in {"-h", "--help"}:
        root_parser.parse_args(["--help"])
        return

    command = argv[0]
    if command == "fetch":
        fetch_parser = _build_fetch_parser()
        fetch_args = fetch_parser.parse_args(argv[1:])
        _run_fetch(fetch_args)
        return
    if command == "db":
        db.main(argv[1:], prog="jav db")
        return
    if command == "serve":
        server.main(argv[1:], prog="jav serve")
        return

    print(f"jav: error: invalid command '{command}'")
    root_parser.parse_args(["--help"])
    raise SystemExit(2)


def main() -> None:
    argv = list(sys.argv[1:])

    if argv:
        if argv[0] in {"-h", "--help"}:
            _build_root_parser().print_help()
            print("")
            print("Direct subcommand execution is disabled.")
            print("Start the REPL with: uv run jav")
            raise SystemExit(0)
        print("Direct subcommand execution is disabled.")
        print("Use: uv run jav")
        raise SystemExit(2)

    _run_interactive_shell()


if __name__ == "__main__":
    main()
