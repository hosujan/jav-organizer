"""Unified CLI entrypoint for jav-toolkit."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import sys
from pathlib import Path

from . import db, media, scraper
from .web import server

_ID_RE = re.compile(r"\b([A-Za-z]{2,10})[-_]?(\d{2,6})\b")
_HISTORY_FILE = Path.home() / ".jav_cli_history"
_REPL_TOKENS = sorted(
    {
        "fetch",
        "db",
        "serve",
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
        "/help",
        "/clear",
        "/quit",
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
    print(_BANNER)
    _print_info_box()
    print("\nType `/help` for commands, `/quit` to exit.")


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
            candidates = [token for token in ("fetch", "db", "serve", "/help", "/clear", "/quit")]

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


def _extract_ids(text: str) -> list[str]:
    found: list[str] = []
    for prefix, number in _ID_RE.findall(text):
        jav_id = f"{prefix.upper()}-{number}"
        if jav_id not in found:
            found.append(jav_id)
    return found


def _print_shell_help() -> None:
    print("Interactive commands:")
    print("  fetch --info MISM-410")
    print("  fetch --media MISM-410 --no-download")
    print("  fetch MISM-410 ABW-123")
    print("  db list | db show MISM-410 | db search Emma | db stats")
    print("  serve")
    print("")
    print("Natural prompts also work:")
    print("  get metadata for MISM-410")
    print("  download media for ABW-123 and SSIS-456")
    print("  no-download preview for MISM-410")
    print("")
    print("Slash commands:")
    print("  /help   show this help")
    print("  /clear  clear screen and redraw banner")
    print("  /quit   exit shell")


def _translate_nl_to_argv(raw: str) -> list[str] | None:
    text = raw.strip()
    lower = text.lower()
    ids = _extract_ids(text)

    if lower in {"serve", "start server", "open web", "web ui", "ui"}:
        return ["serve"]

    if lower in {"db list", "list"}:
        return ["db", "list"]
    if lower in {"db stats", "stats"}:
        return ["db", "stats"]

    show_match = re.search(r"\b(?:show|detail)\s+([A-Za-z]{2,10}[-_]?\d{2,6})\b", text, re.IGNORECASE)
    if show_match:
        extracted = _extract_ids(show_match.group(1))
        if extracted:
            return ["db", "show", extracted[0]]

    search_match = re.search(r"\b(?:search|find)\s+(.+)$", text, re.IGNORECASE)
    if search_match and not ids:
        return ["db", "search", search_match.group(1).strip()]

    if "export" in lower:
        if "csv" in lower:
            return ["db", "export", "--format", "csv"]
        return ["db", "export", "--format", "json"]

    intent_info = any(word in lower for word in ("info", "metadata", "meta", "scrape", "detail"))
    intent_media = any(word in lower for word in ("media", "poster", "preview", "download"))

    if ids and not (intent_info or intent_media):
        intent_info = True
        intent_media = True

    if ids and (intent_info or intent_media):
        argv = ["fetch"]
        if intent_info and not intent_media:
            argv.append("--info")
        elif intent_media and not intent_info:
            argv.append("--media")
        if "no-download" in lower or "no download" in lower:
            argv.append("--no-download")
        if "save-db" in lower or "save db" in lower:
            argv.append("--save-db")
        argv.extend(ids)
        return argv

    return None


def _parse_shell_input(raw: str) -> list[str] | None:
    text = raw.strip()
    if not text:
        return None

    if text.startswith("/"):
        cmd = text[1:].strip().lower()
        if cmd in {"quit", "exit", "q"}:
            return ["__quit__"]
        if cmd in {"clear", "cls"}:
            return ["__clear__"]
        if cmd in {"help", "h", "?"}:
            _print_shell_help()
            return None
        print(f"Unknown slash command: /{cmd}")
        print("Try /help")
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
        print(f"Parse error: {err}")
        return None

    if tokens and tokens[0] in {"fetch", "db", "serve"}:
        return tokens

    mapped = _translate_nl_to_argv(text)
    if mapped:
        print(f"[agent] -> jav {' '.join(mapped)}")
        return mapped

    print("Could not understand command.")
    print("Try `fetch MISM-410`, `db list`, `serve`, or `/help`.")
    return None


def _run_interactive_shell() -> None:
    if not sys.stdin.isatty():
        print("No command provided. Use --help for usage.")
        raise SystemExit(1)

    _setup_readline()
    _clear_screen()
    _print_banner()

    while True:
        try:
            raw = input("jav> ")
        except (EOFError, KeyboardInterrupt):
            print("")
            return

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
