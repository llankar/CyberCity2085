"""Shared clickable-state metadata and non-chromatic indicators."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccessibilityState:
    """Render-neutral state information for a clickable UI element."""

    name: str
    icon: str
    pattern: str
    text_prefix: str


ClickableStates = {
    "normal": AccessibilityState("normal", "○", "solid", "[N]"),
    "hover": AccessibilityState("hover", "◉", "dot", "[H]"),
    "active": AccessibilityState("active", "◆", "stripe", "[A]"),
    "disabled": AccessibilityState("disabled", "⛔", "cross", "[D]"),
    "focus": AccessibilityState("focus", "▣", "double", "[F]"),
}


def label_with_non_color_indicator(text: str, state: str) -> str:
    """Prefix text with icon+token to avoid color-only meaning."""
    resolved = ClickableStates.get(state, ClickableStates["normal"])
    return f"{resolved.text_prefix} {resolved.icon} {text}"
