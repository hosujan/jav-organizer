"""Unified CLI entrypoint for jav-toolkit."""

from __future__ import annotations

import argparse
import difflib
import os
import shlex
import sys
from contextlib import nullcontext
from pathlib import Path

from . import db, media, scraper
from .web import server

_HISTORY_FILE = Path.home() / ".jav_cli_history"
_SLASH_COMMANDS: dict[str, str] = {
    "/help": "show help and examples",
    "/clear": "clear screen and redraw banner",
    "/quit": "exit interactive shell",
}
_ROOT_COMMANDS = ("fetch", "db", "serve")
_REPL_TOKENS = sorted(
    {
        *_ROOT_COMMANDS,
        "--info",
        "--media",
        "--file",
        "--db",
        "--no-download",
        "--save-db",
        "--media-dir",
        "list",
        "show",
        "search",
        "stats",
        "export",
        "--format",
        "json",
        "csv",
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
    _print_status("Type `/help` for commands, `/quit` to exit.")


def _print_status(message: str) -> None:
    if _CONSOLE:
        _CONSOLE.print(f"[dim]{message}[/dim]")
    else:
        print(message)


def _print_agent_action(message: str) -> None:
    if _CONSOLE:
        _CONSOLE.print(f"[cyan][agent][/cyan] {message}")
    else:
        print(f"[agent] {message}")


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
            candidates = [token for token in (*_ROOT_COMMANDS, *_SLASH_COMMANDS.keys())]

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
    sub.add_parser("fetch", help="Fetch metadata/media workflows")
    sub.add_parser("db", help="Query/export local database")
    sub.add_parser("serve", help="Run local web frontend")
    return parser


def _build_fetch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jav fetch",
        description="Fetch metadata and/or media. Default: run info then media.",
    )
    parser.add_argument("ids", nargs="*", help="JAV IDs, e.g. MISM-410")
    parser.add_argument("--file", "-f", help="Text file with one ID per line")
    parser.add_argument("--db", default="jav.db", help="SQLite database path")
    parser.add_argument("--info", action="store_true", help="Run metadata fetch only")
    parser.add_argument("--media", action="store_true", help="Run media fetch only")
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="When running media step, resolve URLs only",
    )
    parser.add_argument(
        "--save-db",
        action="store_true",
        help="When running media step, save media URLs to DB",
    )
    parser.add_argument(
        "--media-dir",
        help="Override media output directory (default: ./media in repository root)",
    )
    return parser


def _run_fetch(args: argparse.Namespace) -> None:
    run_info = args.info or not (args.info or args.media)
    run_media = args.media or not (args.info or args.media)

    info_argv: list[str] = []
    media_argv: list[str] = []

    if args.file:
        info_argv += ["--file", args.file]
        media_argv += ["--file", args.file]
    info_argv += ["--db", args.db]
    media_argv += ["--db", args.db]

    if args.no_download:
        media_argv.append("--no-download")
    if args.save_db:
        media_argv.append("--save-db")

    if run_media:
        media_root = Path(args.media_dir).expanduser().resolve() if args.media_dir else Path("media").resolve()
        media_root.mkdir(parents=True, exist_ok=True)
        media_argv += ["--media-dir", str(media_root)]

    info_argv += list(args.ids)
    media_argv += list(args.ids)

    if run_info:
        scraper.main(info_argv, prog="jav fetch --info")
    if run_media:
        media.main(media_argv, prog="jav fetch --media")


def _print_shell_help() -> None:
    if _CONSOLE:
        table = Table(title="Interactive Commands", show_header=True, header_style="bold cyan")
        table.add_column("Category", style="green", no_wrap=True)
        table.add_column("Examples")
        table.add_row("CLI commands", "fetch --info MISM-410")
        table.add_row("CLI commands", "fetch --media MISM-410 --no-download")
        table.add_row("CLI commands", "db list | db show MISM-410 | db search Emma | db stats")
        table.add_row("Slash commands", "/help  /clear  /quit")
        _CONSOLE.print(table)
        return

    print("Interactive commands:")
    print("  CLI commands:")
    print("    fetch --info MISM-410")
    print("    fetch --media MISM-410 --no-download")
    print("    fetch MISM-410 ABW-123")
    print("    db list | db show MISM-410 | db search Emma | db stats")
    print("    serve")
    print("")
    print("  Slash commands:")
    for cmd, desc in _SLASH_COMMANDS.items():
        print(f"    {cmd:<7} {desc}")


def _fuzzy_match(word: str, candidates: list[str], cutoff: float = 0.6) -> str | None:
    matches = difflib.get_close_matches(word, candidates, n=1, cutoff=cutoff)
    return matches[0] if matches else None


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


def _parse_shell_input(raw: str) -> list[str] | None:
    text = raw.strip()
    if not text:
        return None

    if text.startswith("/"):
        cmd = text[1:].strip().lower()
        if not cmd:
            _print_slash_indicators("/")
            return None
        if cmd in {"quit", "exit", "q"}:
            return ["__quit__"]
        if cmd in {"clear", "cls"}:
            return ["__clear__"]
        if cmd in {"help", "h", "?"}:
            _print_shell_help()
            return None

        full_cmd = "/" + cmd
        prefix_matches = [name for name in _SLASH_COMMANDS if name.startswith(full_cmd)]
        if prefix_matches:
            _print_slash_indicators(full_cmd)
            return None

        corrected = _fuzzy_match(full_cmd, list(_SLASH_COMMANDS.keys()))
        if corrected:
            _print_agent_action(f"autocorrected {full_cmd} -> {corrected}")
            if corrected == "/quit":
                return ["__quit__"]
            if corrected == "/clear":
                return ["__clear__"]
            _print_shell_help()
            return None

        _print_warn(f"Unknown slash command: {full_cmd}")
        _print_status("Type `/` to see available slash commands.")
        return None

    if text.lower() in {"quit", "exit", "q"}:
        return ["__quit__"]
    if text.lower() in {"clear", "cls"}:
        return ["__clear__"]
    if text.lower() in {"help", "h", "?"}:
        _print_shell_help()
        return None

    try:
        tokens = shlex.split(text)
    except ValueError as err:
        _print_warn(f"Parse error: {err}")
        return None

    if tokens:
        first = tokens[0]
        if first in _ROOT_COMMANDS:
            return tokens
        corrected = _fuzzy_match(first, list(_ROOT_COMMANDS))
        if corrected:
            _print_agent_action(f"autocorrected {first} -> {corrected}")
            return [corrected, *tokens[1:]]

    _print_warn("Could not understand command.")
    _print_status("Use CLI commands only: `fetch ...`, `db ...`, `serve`, `/`, or `/help`.")
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
            context = _CONSOLE.status(
                f"[bold green]Running[/bold green] jav {' '.join(argv)}...",
                spinner="dots",
            ) if _CONSOLE else nullcontext()
            with context:
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
        fetch_raw = argv[1:]
        if any(flag in fetch_raw for flag in ("-h", "--help")):
            info_mode = "--info" in fetch_raw
            media_mode = "--media" in fetch_raw
            if info_mode and not media_mode:
                scraper.main(["--help"], prog="jav fetch --info")
                return
            if media_mode and not info_mode:
                media.main(["--help"], prog="jav fetch --media")
                return
        fetch_parser = _build_fetch_parser()
        fetch_args = fetch_parser.parse_args(fetch_raw)
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

    if not argv:
        _run_interactive_shell()
        return

    _dispatch(argv)


if __name__ == "__main__":
    main()
