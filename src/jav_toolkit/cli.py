"""Unified CLI entrypoint for jav-toolkit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import db, media, scraper
from .web import server


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
    parser.add_argument("--save-db", action="store_true", help="When running media step, save media URLs to DB")
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


def _prompt_fetch_mode() -> list[str] | None:
    print("Fetch modes:")
    print("  uv run jav fetch --info")
    print("  uv run jav fetch --media")
    print("  (no flag runs both: info then media)")
    print("  1) --info")
    print("  2) --media")
    print("  3) both")
    print("  q) back")
    choice = input("Select [1-3/q]: ").strip().lower()
    if choice == "q":
        return None
    if choice == "1":
        return ["--info"]
    if choice == "2":
        return ["--media"]
    if choice == "3":
        return []
    print("Invalid choice")
    return None


def _run_prompt() -> list[str] | None:
    if not sys.stdin.isatty():
        print("No command provided. Use --help for usage.")
        raise SystemExit(1)

    print("Choose an action:")
    print("  1) fetch")
    print("  2) db")
    print("  3) serve")
    print("  q) quit")
    choice = input("Select [1-3/q]: ").strip().lower()
    if choice == "q":
        return None
    if choice == "1":
        fetch_mode_args = _prompt_fetch_mode()
        if fetch_mode_args is None:
            return None
        return ["fetch", *fetch_mode_args]
    if choice == "2":
        return ["db"]
    if choice == "3":
        return ["serve"]
    print("Invalid choice")
    return None


def main() -> None:
    argv = list(sys.argv[1:])

    if not argv:
        prompted = _run_prompt()
        if prompted is None:
            return
        argv = prompted

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


if __name__ == "__main__":
    main()
