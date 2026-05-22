"""Shared badge style values."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BadgeStyle:
    text_size: int = 9


badge_style = BadgeStyle()
