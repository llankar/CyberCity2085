"""Arcade UI helpers.

Keep lightweight text/dashboard modules importable in headless tests by loading the
Arcade-backed ``GameView`` only when callers explicitly request it.
"""

__all__ = ["GameView"]


def __getattr__(name: str):
    if name == "GameView":
        from .base import GameView

        return GameView
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
