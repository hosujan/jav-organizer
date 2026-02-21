from __future__ import annotations

import re
from pathlib import Path

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".m4v", ".ts", ".webm",
}
JAV_ID_RE = re.compile(r"([a-z]{2,10})[-_ ]?(\d{2,5})", re.IGNORECASE)


def normalize_jav_id(text: str) -> str | None:
    match = JAV_ID_RE.search(text)
    if not match:
        return None
    return f"{match.group(1).upper()}-{match.group(2)}"


def scan_video_files(base_dir: Path) -> list[dict]:
    seen: set[str] = set()
    items: list[dict] = []
    media_root = (base_dir / "media").resolve()
    for path in sorted(base_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in VIDEO_EXTENSIONS:
            continue
        resolved = path.resolve()
        if media_root in resolved.parents:
            continue
        jav_id = normalize_jav_id(path.stem) or normalize_jav_id(str(path))
        if not jav_id or jav_id in seen:
            continue
        seen.add(jav_id)
        items.append({
            "jav_id": jav_id,
            "file_path": str(resolved),
            "file_name": path.name,
        })
    return items


def scan_media_files(media_root: Path) -> dict[str, dict[str, bool]]:
    if not media_root.exists() or not media_root.is_dir():
        return {}

    out: dict[str, dict[str, bool]] = {}
    for child in sorted(media_root.iterdir()):
        if not child.is_dir():
            continue
        jav_id = child.name.upper()
        has_poster = any(
            path.exists() and path.stat().st_size > 500
            for path in (
                child / "poster.jpg",
                child / "poster.jpeg",
                child / "poster.png",
                child / "poster.webp",
            )
        )
        preview = child / "preview.mp4"
        has_preview = preview.exists() and preview.stat().st_size > 500
        out[jav_id] = {
            "has_poster_local": has_poster,
            "has_preview_local": has_preview,
        }
    return out
