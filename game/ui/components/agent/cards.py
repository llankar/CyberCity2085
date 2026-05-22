"""Agent card rendering primitives for room overlays."""

from __future__ import annotations

import arcade

from ... import palette
from ...theme import stroke
from ...theme.typography import typography
from ...room_interaction import layout_roster_card_rects
from ..shared.badges import draw_upgrade_badge


def draw_roster_cards(rect, buttons, roster_cards: list[dict], border, draw_icon, load_texture_once, draw_circle_filled, draw_circle_outline) -> None:
    if not roster_cards:
        left = rect.left + max(34, rect.width // 18)
        bottom = rect.bottom + max(160, rect.height // 3)
        arcade.draw_lrbt_rectangle_filled(left, left + 260, bottom, bottom + 72, palette.AGENT_CARD_FILL)
        draw_icon("recruit", left + 42, bottom + 36, 44, border)
        arcade.draw_text("NO AGENTS ON ROSTER", left + 84, bottom + 42, palette.TEXT, 12)
        arcade.draw_text("RECRUIT IN BARRACKS OR BLACK OPS", left + 84, bottom + 20, palette.MUTED_TEXT, 9)
        return
    for index, card_rect in enumerate(layout_roster_card_rects(rect, buttons, len(roster_cards))):
        draw_agent_card(roster_cards[index], card_rect.left, card_rect.bottom, card_rect.width, card_rect.height, border, load_texture_once, draw_circle_filled, draw_circle_outline)


def draw_agent_card(card: dict, left: int, bottom: int, width: int, height: int, border, load_texture_once, draw_circle_filled, draw_circle_outline) -> None:
    fill = palette.AGENT_CARD_ACTIVE if card.get("active") else palette.AGENT_CARD_SELECTED if card.get("selected") else palette.AGENT_CARD_FILL
    arcade.draw_lrbt_rectangle_filled(left, left + width, bottom, bottom + height, fill)
    arcade.draw_line(left, bottom + height, left + width, bottom + height, _role_color(card), 3)
    if card.get("active"):
        _draw_active_agent_brackets(left, bottom, width, height)
    portrait_size = max(48, min(72, height - 18))
    _draw_agent_portrait_asset(card, left + 10, bottom + (height - portrait_size) // 2, portrait_size, border, load_texture_once, draw_circle_filled, draw_circle_outline)
    text_left = left + 10 + portrait_size + 14
    arcade.draw_text(card.get("name", "Agent").upper(), text_left, bottom + height - 28, palette.TEXT, typography.panel_title)
    arcade.draw_text(card.get("role", "unknown").upper(), text_left, bottom + height - 48, _role_color(card), typography.meta)
    if card.get("pending_points", 0) > 0:
        draw_upgrade_badge(card.get("pending_points", 0), left + width - 48, bottom + height - 32)


def _role_color(card: dict):
    return palette.ROLE_SNIPER if card.get("role", "") == "sniper" else palette.ROLE_PSI if card.get("role", "") == "psi" else palette.ROLE_SAMURAI


def _draw_agent_portrait_asset(card, left, bottom, size, border, load_texture_once, draw_circle_filled, draw_circle_outline):
    path = card.get("portrait_path")
    texture = load_texture_once(path) if path else None
    if texture is None or not hasattr(arcade, "draw_texture_rect"):
        _draw_agent_portrait(card, left + size // 2, bottom + size // 2, size, draw_circle_filled, draw_circle_outline)
        return
    arcade.draw_texture_rect(texture, arcade.LBWH(left, bottom, size, size))


def _draw_agent_portrait(card: dict, center_x: int, center_y: int, size: int, draw_circle_filled, draw_circle_outline) -> None:
    role_color = _role_color(card)
    radius = size // 2
    draw_circle_filled(center_x, center_y, radius, palette.AGENT_PORTRAIT_FILL)
    draw_circle_outline(center_x, center_y, radius, role_color, 2)


def _draw_active_agent_brackets(left: int, bottom: int, width: int, height: int) -> None:
    right = left + width
    top = bottom + height
    color = palette.ACTIVE_AGENT_BORDER
    bracket = 34
    arcade.draw_line(left - 2, top + 2, left + bracket, top + 2, color, stroke.strong)
    arcade.draw_line(left - 2, top + 2, left - 2, top - bracket, color, 3)
    arcade.draw_line(right + 2, top + 2, right - bracket, top + 2, color, 3)
    arcade.draw_line(right + 2, top + 2, right + 2, top - bracket, color, 3)
