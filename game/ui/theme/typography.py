"""Typography hierarchy tokens and global text scaling for the UI."""

from __future__ import annotations

from dataclasses import dataclass

import arcade


TEXT_SIZE_OPTIONS: tuple[str, ...] = ("small", "medium", "large")
_TEXT_SIZE_SCALE: dict[str, float] = {
    "small": 0.90,
    "medium": 1.00,
    "large": 1.15,
}
_CURRENT_TEXT_SIZE = "medium"
_CURRENT_TEXT_SCALE = _TEXT_SIZE_SCALE[_CURRENT_TEXT_SIZE]


def normalize_text_size(text_size: str | None) -> str:
    value = str(text_size).strip().lower() if text_size is not None else ""
    if value in _TEXT_SIZE_SCALE:
        return value
    return "medium"


def set_text_size(text_size: str | None) -> str:
    """Set the global UI text scale and return the normalized size label."""
    global _CURRENT_TEXT_SIZE, _CURRENT_TEXT_SCALE
    _CURRENT_TEXT_SIZE = normalize_text_size(text_size)
    _CURRENT_TEXT_SCALE = _TEXT_SIZE_SCALE[_CURRENT_TEXT_SIZE]
    return _CURRENT_TEXT_SIZE


def get_text_size() -> str:
    return _CURRENT_TEXT_SIZE


def scale_font_size(font_size: int | float) -> int:
    """Scale a font size using the active UI text size preset."""
    try:
        return max(1, int(round(float(font_size) * _CURRENT_TEXT_SCALE)))
    except (TypeError, ValueError):
        return 12


def _patch_arcade_draw_text() -> None:
    if getattr(arcade, "_cybercity_draw_text_scaled", False):
        return

    original_draw_text = arcade.draw_text

    def _scaled_draw_text(*args, **kwargs):
        scaled_args = list(args)
        scaled_kwargs = dict(kwargs)
        if "font_size" in scaled_kwargs:
            scaled_kwargs["font_size"] = scale_font_size(scaled_kwargs["font_size"])
        elif len(scaled_args) >= 5:
            scaled_args[4] = scale_font_size(scaled_args[4])
        else:
            scaled_kwargs["font_size"] = scale_font_size(12)
        return original_draw_text(*tuple(scaled_args), **scaled_kwargs)

    arcade.draw_text = _scaled_draw_text
    arcade._cybercity_draw_text_scaled = True


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

_patch_arcade_draw_text()
