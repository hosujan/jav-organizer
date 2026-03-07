"""Unified CLI entrypoint for jav-toolkit."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from . import db, media, scraper
from .web import server

RunFunc = Callable[[list[str] | None, str], None]

MENU_CHOICES: dict[str, tuple[str, RunFunc, str]] = {
    "1": ("fetch info", scraper.main, "jav fetch info"),
    "2": ("fetch media", media.main, "jav fetch media"),
    "3": ("db", db.main, "jav db"),
    "4": ("serve", server.main, "jav serve"),
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jav",
        description="Unified CLI for jav-toolkit",
    )
    sub = parser.add_subparsers(dest="command")

    fetch = sub.add_parser("fetch", help="Fetch data workflows")
    fetch_sub = fetch.add_subparsers(dest="fetch_command")
    fetch_info = fetch_sub.add_parser("info", add_help=False, help="Fetch metadata")
    fetch_info.add_argument("args", nargs=argparse.REMAINDER)
    fetch_media = fetch_sub.add_parser("media", add_help=False, help="Fetch/download media assets")
    fetch_media.add_argument("args", nargs=argparse.REMAINDER)

    cmd_db = sub.add_parser("db", add_help=False, help="Query/export local database")
    cmd_db.add_argument("args", nargs=argparse.REMAINDER)

    cmd_serve = sub.add_parser("serve", add_help=False, help="Run local web frontend")
    cmd_serve.add_argument("args", nargs=argparse.REMAINDER)

    return parser


def _normalize_forwarded_args(args: list[str]) -> list[str]:
    if args and args[0] == "--":
        return args[1:]
    return args


def _run_prompt() -> int:
    if not sys.stdin.isatty():
        print("No command provided. Use --help for usage.")
        return 1

    print("Choose an action:")
    for key, (label, _, _) in MENU_CHOICES.items():
        print(f"  {key}) {label}")
    print("  q) quit")

    choice = input("Select [1-4/q]: ").strip().lower()
    if choice == "q":
        return 0

    selected = MENU_CHOICES.get(choice)
    if not selected:
        print("Invalid choice")
        return 1

    _, target, prog = selected
    target([], prog=prog)
    return 0


def main() -> None:
    argv = sys.argv[1:]

    if not argv:
        raise SystemExit(_run_prompt())

    root_parser = _build_parser()

    if argv[0] in {"-h", "--help"}:
        root_parser.parse_args(["--help"])
        return

    command = argv[0]

    if command == "fetch":
        if len(argv) == 1 or argv[1] in {"-h", "--help"}:
            root_parser.parse_args(["fetch", "--help"])
            return
        fetch_command = argv[1]
        rest = _normalize_forwarded_args(argv[2:])
        if fetch_command == "info":
            scraper.main(rest, prog="jav fetch info")
            return
        if fetch_command == "media":
            media.main(rest, prog="jav fetch media")
            return
        print(f"jav fetch: error: invalid action '{fetch_command}'")
        root_parser.parse_args(["fetch", "--help"])
        raise SystemExit(2)

    if command == "db":
        db.main(_normalize_forwarded_args(argv[1:]), prog="jav db")
        return

    if command == "serve":
        server.main(_normalize_forwarded_args(argv[1:]), prog="jav serve")
        return

    print(f"jav: error: invalid command '{command}'")
    root_parser.parse_args(["--help"])
    raise SystemExit(2)


if __name__ == "__main__":
    main()
