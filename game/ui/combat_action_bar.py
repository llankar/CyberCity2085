"""Reusable tactical combat action bar drawing and hit-testing."""

from __future__ import annotations

import arcade

from ..combat_actions import CombatAction
from ..combat_preview import AttackPreview
from . import palette
from .panels import _draw_icon, draw_panel
from .room_interaction import UIRect


BAR_HEIGHT = 112
BUTTON_WIDTH = 96
BUTTON_HEIGHT = 58
BUTTON_GAP = 10


def combat_action_bar_rect(width: int) -> UIRect:
    """Return the bottom-center action bar rectangle."""
    bar_width = min(width - 28, 880)
    return UIRect((width - bar_width) // 2, 18, bar_width, BAR_HEIGHT)


def layout_combat_action_buttons(
    width: int, actions: list[CombatAction]
) -> list[tuple[CombatAction, UIRect]]:
    """Lay out action buttons in a centered command strip."""
    if not actions:
        return []
    bar = combat_action_bar_rect(width)
    button_width = min(BUTTON_WIDTH, max(66, (bar.width - 48) // max(1, len(actions))))
    total_width = len(actions) * button_width + (len(actions) - 1) * BUTTON_GAP
    left = bar.left + max(20, (bar.width - total_width) // 2)
    bottom = bar.bottom + 24
    return [
        (
            action,
            UIRect(
                left + index * (button_width + BUTTON_GAP),
                bottom,
                button_width,
                BUTTON_HEIGHT,
            ),
        )
        for index, action in enumerate(actions)
    ]


def combat_action_at_point(
    buttons: list[tuple[CombatAction, UIRect]], x: int, y: int
) -> CombatAction | None:
    """Return the clicked combat action, if the point hits a button."""
    for action, rect in buttons:
        if rect.contains(x, y):
            return action
    return None


def draw_combat_action_bar(
    width: int,
    height: int,
    actions: list[CombatAction],
    unit_name: str,
    action_points: int,
    message: str = "",
    *,
    preview: AttackPreview | None = None,
    warning: str | None = None,
) -> list[tuple[CombatAction, UIRect]]:
    """Draw the tactical action bar and return its clickable button rects."""
    bar = combat_action_bar_rect(width)
    draw_panel(bar.left, bar.bottom, bar.width, bar.height, "Action Deck")
    arcade.draw_text(
        f"{unit_name.upper()} // AP {max(0, action_points)}",
        bar.left + 18,
        bar.top - 51,
        palette.RESOURCE,
        11,
    )
    if message:
        arcade.draw_text(
            message[:72], bar.left + 220, bar.top - 51, palette.MUTED_TEXT, 10
        )

    if preview:
        preview_text = (
            f"DMG {preview.min_damage}-{preview.max_damage}  "
            f"HIT {int(preview.hit_chance * 100)}%  "
            f"CRIT {int(preview.crit_chance * 100)}%"
        )
        arcade.draw_text(preview_text, bar.left + 18, bar.top - 69, palette.TEXT, 10)
    if warning:
        arcade.draw_text(warning[:72], bar.left + 18, bar.top - 87, palette.WARNING, 10)

    buttons = layout_combat_action_buttons(width, actions)
    for action, rect in buttons:
        arcade.draw_lrbt_rectangle_filled(
            rect.left, rect.right, rect.bottom, rect.top, palette.ACTION_BUTTON_FILL
        )
        arcade.draw_line(
            rect.left, rect.top, rect.right, rect.top, palette.PANEL_BORDER, 2
        )
        arcade.draw_line(
            rect.left, rect.bottom, rect.right, rect.bottom, palette.GRID_LINE, 1
        )
        _draw_icon(action.icon, rect.center_x, rect.bottom + 37, 20, palette.ACCENT)
        arcade.draw_text(
            action.label.upper(),
            rect.center_x,
            rect.bottom + 18,
            palette.TEXT,
            9,
            anchor_x="center",
        )
        if action.hotkey:
            arcade.draw_text(
                action.hotkey,
                rect.center_x,
                rect.bottom + 8,
                palette.WARNING,
                8,
                anchor_x="center",
            )
    return buttons
