"""Backward-compatible entrypoint for jav-web.

Actress alias rendering is handled in ``jav_toolkit.web.server``.
"""

from .web.server import main

__all__ = ["main"]
