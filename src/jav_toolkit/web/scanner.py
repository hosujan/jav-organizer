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
    for path in sorted(base_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in VIDEO_EXTENSIONS:
            continue
        jav_id = normalize_jav_id(path.stem) or normalize_jav_id(str(path))
        if not jav_id or jav_id in seen:
            continue
        seen.add(jav_id)
        items.append({
            "jav_id": jav_id,
            "file_path": str(path.resolve()),
            "file_name": path.name,
        })
    return items

