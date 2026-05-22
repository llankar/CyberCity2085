"""Semantic spacing tokens for command surfaces."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpacingTokens:
    stack_tight: int = 8
    stack_default: int = 14
    section_gap: int = 18
    panel_gap: int = 24
    screen_margin: int = 34

    # Backward-compatible aliases
    xs: int = 8
    sm: int = 14
    md: int = 18
    lg: int = 24
    xl: int = 34


spacing = SpacingTokens()
