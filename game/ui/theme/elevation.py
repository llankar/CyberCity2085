"""Semantic elevation and stroke tokens."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ElevationTokens:
    base: int = 0
    surface: int = 10
    overlay: int = 20
    interactive: int = 30

    # Backward-compatible aliases
    panel: int = 10
    modal: int = 20
    controls: int = 30


@dataclass(frozen=True)
class StrokeTokens:
    hairline: int = 1
    regular: int = 2
    strong: int = 3


elevation = ElevationTokens()
stroke = StrokeTokens()
