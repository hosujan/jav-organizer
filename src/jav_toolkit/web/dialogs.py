from __future__ import annotations

import subprocess
import sys
import threading


def _choose_directory_macos() -> str | None:
    script = """
try
    POSIX path of (choose folder with prompt "Select video directory")
on error number -128
    ""
end try
""".strip()
    try:
        proc = subprocess.run(
            ["osascript", "-e", script],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    path = proc.stdout.strip()
    return path or None


def choose_directory_dialog() -> str | None:
    if sys.platform == "darwin":
        chosen = _choose_directory_macos()
        if chosen:
            return chosen

    # tkinter dialogs are not thread-safe across platforms.
    if threading.current_thread() is not threading.main_thread():
        return None
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None
    root = tk.Tk()
    root.withdraw()
    root.update()
    path = filedialog.askdirectory(title="Select video directory")
    root.destroy()
    return path or None
