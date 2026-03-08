from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppState:
    db_path: Path
    media_dir: Path
    selected_dir: Path | None = None
    items: list[dict] = field(default_factory=list)
    video_index: dict[str, str] = field(default_factory=dict)
    force_override: bool = False
    processing: bool = False
    processed: int = 0
    total: int = 0
    current: str | None = None
    logs: list[str] = field(default_factory=list)
    worker: threading.Thread | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)

    def add_log(self, msg: str):
        with self.lock:
            self.logs.append(msg)
            self.logs = self.logs[-300:]

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "selected_dir": str(self.selected_dir) if self.selected_dir else None,
                "processing": self.processing,
                "processed": self.processed,
                "total": self.total,
                "current": self.current,
                "logs": list(self.logs[-80:]),
                "items": list(self.items),
                "force_override": self.force_override,
            }
