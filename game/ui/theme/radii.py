"""Semantic corner-radius tokens."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RadiiTokens:
    control: int = 8
    panel: int = 14

    # Backward-compatible aliases
    sm: int = 8
    md: int = 14


radii = RadiiTokens()
