"""Typography hierarchy tokens for CyberCity command UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TypographyTokens:
    screen_title: int = 26
    panel_title: int = 16
    body_secondary: int = 14
    meta: int = 12
    # Backward-compatible aliases
    title: int = 26
    section: int = 16


typography = TypographyTokens()
