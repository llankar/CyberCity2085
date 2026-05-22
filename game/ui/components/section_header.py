"""Shared section header helpers."""
from __future__ import annotations

import arcade

from .. import palette
from ..theme.typography import typography


def draw_section_header(text: str, left: int, bottom: int) -> None:
    arcade.draw_text(text, left, bottom, palette.RESOURCE, typography.body_secondary)
