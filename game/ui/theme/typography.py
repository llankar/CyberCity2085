"""Typography hierarchy tokens for CyberCity command UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TypographyTokens:
    screen_title: int = 22
    panel_title: int = 13
    body_secondary: int = 11
    meta: int = 9
    # Backward-compatible aliases
    title: int = 22
    section: int = 13


typography = TypographyTokens()
