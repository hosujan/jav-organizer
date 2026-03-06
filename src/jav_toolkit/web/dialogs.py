from __future__ import annotations

import threading


def choose_directory_dialog() -> str | None:
    # macOS AppKit requires UI windows on the main thread.
    # Keeping this guard for all platforms avoids toolkit/thread crashes.
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

