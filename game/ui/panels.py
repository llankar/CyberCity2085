"""Reusable panel and status-bar drawing helpers for command screens."""

from __future__ import annotations

import arcade

from . import palette
from .facility import BASE_BACKDROP_ASSET, FacilityRoom, build_facility_rooms
from .room_interaction import (
    ActionButton,
    RoomUIState,
    active_room_rect,
    close_button_rect,
    layout_roster_card_rects,
)


_TEXTURE_CACHE = {}


def _load_texture_once(path: str):
    """Load UI art lazily so drawing helpers stay cheap per frame."""
    if path not in _TEXTURE_CACHE:
        try:
            _TEXTURE_CACHE[path] = arcade.load_texture(path)
        except (FileNotFoundError, OSError):
            _TEXTURE_CACHE[path] = None
    return _TEXTURE_CACHE[path]


def _draw_circle_filled(center_x: int, center_y: int, radius: int, color) -> None:
    if hasattr(arcade, "draw_circle_filled"):
        arcade.draw_circle_filled(center_x, center_y, radius, color)
    else:
        arcade.draw_lrbt_rectangle_filled(
            center_x - radius, center_x + radius, center_y - radius, center_y + radius, color
        )


def _draw_circle_outline(center_x: int, center_y: int, radius: int, color, width: int = 2) -> None:
    if hasattr(arcade, "draw_circle_outline"):
        arcade.draw_circle_outline(center_x, center_y, radius, color, width)
    else:
        arcade.draw_line(center_x - radius, center_y, center_x + radius, center_y, color, width)
        arcade.draw_line(center_x, center_y - radius, center_x, center_y + radius, color, width)


def draw_panel(
    left: int, bottom: int, width: int, height: int, title: str = ""
) -> None:
    """Draw an angled tactical glass panel with corporate command lines."""
    right = left + width
    top = bottom + height
    cut = 16
    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, palette.PANEL_FILL)
    arcade.draw_lrbt_rectangle_filled(
        left, right, top - 32, top, palette.PANEL_FILL_DARK
    )
    arcade.draw_lrbt_rectangle_filled(
        left + 8, right - 8, bottom + 8, bottom + 13, palette.ROOM_SUPPORT
    )
    arcade.draw_line(left + cut, top, right, top, palette.PANEL_BORDER, 2)
    arcade.draw_line(left, top - cut, left + cut, top, palette.PANEL_BORDER, 2)
    arcade.draw_line(left, bottom, right - cut, bottom, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(
        right - cut, bottom, right, bottom + cut, palette.PANEL_BORDER_MUTED, 1
    )
    arcade.draw_line(left, bottom, left, top - cut, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(right, bottom + cut, right, top, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(left + 8, top - 32, right - 8, top - 32, palette.GRID_LINE, 1)
    for marker_x in range(left + 22, right - 24, 68):
        arcade.draw_line(
            marker_x, bottom + 13, marker_x + 24, bottom + 13, palette.GRID_LINE, 1
        )
    if title:
        arcade.draw_text(f"// {title.upper()}", left + 14, top - 23, palette.HEADER, 13)


def draw_status_bar(text: str, width: int, height: int) -> None:
    """Draw the top corporate command-HUD status bar."""
    arcade.draw_lrbt_rectangle_filled(
        0, width, height - 48, height, palette.PANEL_FILL_DARK
    )
    arcade.draw_lrbt_rectangle_filled(
        0, min(width, 330), height - 48, height, palette.AMBER_FILL
    )
    arcade.draw_line(0, height - 49, width, height - 49, palette.PANEL_BORDER, 2)
    arcade.draw_line(22, height - 8, 120, height - 8, palette.HEADER, 3)
    slot_right = width - 18
    for _ in range(4):
        slot_left = slot_right - 118
        arcade.draw_lrbt_rectangle_filled(
            slot_left, slot_right, height - 38, height - 13, palette.HUD_SLOT_FILL
        )
        arcade.draw_line(
            slot_left, height - 13, slot_right, height - 13, palette.GRID_LINE, 1
        )
        slot_right = slot_left - 8
    arcade.draw_text(text, 18, height - 31, palette.RESOURCE, 12)


def _room_border_color(room: FacilityRoom):
    if room.accent == "amber":
        return palette.AMBER_BORDER
    if room.accent == "green":
        return palette.TACTICAL_GREEN
    if room.accent == "red":
        return palette.DANGER
    return palette.PANEL_BORDER


def draw_facility_room(room: FacilityRoom) -> None:
    """Draw one lit room in the corporate base cross-section."""
    left = room.left
    right = room.left + room.width
    bottom = room.bottom
    top = room.bottom + room.height
    fill = palette.ROOM_FILL if room.lit else palette.ROOM_FILL_SLEEP
    border = _room_border_color(room)

    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, palette.ROOM_SUPPORT)
    arcade.draw_lrbt_rectangle_filled(left + 4, right - 4, bottom + 4, top - 4, fill)
    arcade.draw_line(left, top, right, top, border, 2)
    arcade.draw_line(left, bottom, right, bottom, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(left, bottom, left, top, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(right, bottom, right, top, palette.PANEL_BORDER_MUTED, 1)

    window_color = (
        palette.ROOM_WINDOW_WARM if room.accent == "amber" else palette.ROOM_WINDOW
    )
    for window_left in range(left + 14, max(left + 15, right - 22), 42):
        arcade.draw_lrbt_rectangle_filled(
            window_left,
            min(window_left + 20, right - 12),
            bottom + 18,
            min(bottom + 34, top - 20),
            window_color,
        )
    for rail_y in range(bottom + 16, top - 16, 24):
        arcade.draw_line(left + 8, rail_y, right - 8, rail_y, palette.GRID_LINE, 1)


def _room_accent_color(room: FacilityRoom):
    if room.accent == "amber":
        return palette.HOTSPOT_AMBER
    if room.accent == "green":
        return palette.HOTSPOT_GREEN
    if room.accent == "red":
        return palette.HOTSPOT_RED
    return palette.HOTSPOT_BORDER


def draw_room_hotspots(width: int, height: int, mode: str) -> None:
    """Add game-readable facility highlights over the raster base art."""
    for room in build_facility_rooms(width, height, mode):
        right = room.left + room.width
        top = room.bottom + room.height
        border = _room_accent_color(room)
        arcade.draw_lrbt_rectangle_filled(
            room.left + 4, right - 4, room.bottom + 4, top - 4, palette.HOTSPOT_FILL
        )
        arcade.draw_line(room.left + 10, top, right - 10, top, border, 2)
        arcade.draw_line(room.left, top - 10, room.left + 10, top, border, 2)
        arcade.draw_line(right - 10, room.bottom, right, room.bottom + 10, border, 2)
        icon_x = room.left + 22
        icon_y = top - 24
        _draw_circle_outline(icon_x, icon_y, 7, border, 2)
        arcade.draw_line(icon_x - 12, icon_y, icon_x - 26, icon_y, border, 1)
        arcade.draw_line(icon_x + 12, icon_y, icon_x + 26, icon_y, border, 1)


def draw_cinematic_hud_wash(width: int, height: int) -> None:
    """Keep image art readable under HUD overlays without hiding it."""
    band_height = max(56, int(height * 0.08))
    arcade.draw_lrbt_rectangle_filled(
        0, width, height - band_height, height, palette.VIGNETTE
    )
    arcade.draw_lrbt_rectangle_filled(0, width, 0, band_height, palette.VIGNETTE)
    for y in range(70, height, 72):
        arcade.draw_line(0, y, width, y, palette.SCANLINE, 1)


def draw_city_corporate_backdrop(width: int, height: int, mode: str = "corp") -> None:
    """Draw a corporate tower cross-section over the night city."""
    if hasattr(arcade, "set_background_color"):
        arcade.set_background_color(palette.BACKGROUND)
    arcade.draw_lrbt_rectangle_filled(0, width, 0, height, palette.BACKGROUND)
    texture = _load_texture_once(BASE_BACKDROP_ASSET)
    if texture is not None and hasattr(arcade, "draw_texture_rect"):
        full_rect = arcade.LBWH(0, 0, width, height)
        arcade.draw_texture_rect(texture, full_rect)
        arcade.draw_lrbt_rectangle_filled(0, width, 0, height, palette.BACKDROP_SHADE)
        draw_room_hotspots(width, height, mode)
        draw_cinematic_hud_wash(width, height)
        return

    arcade.draw_lrbt_rectangle_filled(0, width, 0, int(height * 0.34), palette.CITY_SKY)

    horizon = max(118, int(height * 0.22))
    for index, x in enumerate(range(-40, width + 80, 78)):
        tower_height = horizon + 44 + ((index * 31) % 116)
        arcade.draw_lrbt_rectangle_filled(
            x,
            x + 54,
            0,
            tower_height,
            palette.SKYLINE_SHADOW,
        )
        arcade.draw_line(
            x + 8, tower_height - 18, x + 46, tower_height - 18, palette.GRID_LINE, 1
        )
    arcade.draw_line(0, horizon, width, horizon, palette.CITY_GLOW, 3)

    for y in range(70, height, 72):
        arcade.draw_line(0, y, width, y, palette.SCANLINE, 1)
    for offset in range(-width, width * 2, 96):
        arcade.draw_line(offset, 0, offset + 74, horizon, palette.GRID_LINE, 1)

    rooms = build_facility_rooms(width, height, mode)
    if rooms:
        spine_left = min(room.left for room in rooms) - 18
        spine_right = max(room.left + room.width for room in rooms) + 18
        base_bottom = min(room.bottom for room in rooms) - 14
        base_top = max(room.bottom + room.height for room in rooms) + 14
        arcade.draw_lrbt_rectangle_filled(
            spine_left, spine_right, base_bottom, base_top, palette.ROOM_FILL_DARK
        )
        elevator_x = spine_left + 26
        arcade.draw_lrbt_rectangle_filled(
            elevator_x, elevator_x + 22, base_bottom, base_top, palette.ROOM_SUPPORT
        )
        arcade.draw_line(
            elevator_x + 11,
            base_bottom,
            elevator_x + 11,
            base_top,
            palette.GRID_LINE,
            1,
        )

    for room in rooms:
        draw_facility_room(room)


def draw_megacity_backdrop(width: int, height: int) -> None:
    """Backward-compatible wrapper for the new city/corporate backdrop."""
    draw_city_corporate_backdrop(width, height, "corp")


def draw_graphical_command_surface(
    width: int,
    height: int,
    state: RoomUIState,
    resources: dict[str, int] | None = None,
    room_info_lines: dict[str, list[str]] | None = None,
    roster_cards: list[dict] | None = None,
) -> None:
    """Draw the image-first room UI without text panels."""
    draw_city_corporate_backdrop(width, height, state.mode)
    draw_icon_resource_hud(width, height, resources or {})
    draw_expanded_room_ui(width, height, state, room_info_lines or {}, roster_cards or [])


def draw_icon_resource_hud(width: int, height: int, resources: dict[str, int]) -> None:
    """Draw compact icon-only resource meters."""
    keys = ("credits", "intel", "salvage", "influence")
    size = 34
    gap = 12
    left = 22
    top = height - 18
    for index, key in enumerate(keys):
        x = left + index * (size + gap)
        bottom = top - size
        arcade.draw_lrbt_rectangle_filled(x, x + size, bottom, top, palette.HUD_SLOT_FILL)
        _draw_icon(key, x + size // 2, bottom + size // 2, size - 10, palette.RESOURCE)
        value = max(0, min(100, int(resources.get(key, 0))))
        bar_height = max(3, int((size - 8) * min(value, 40) / 40))
        arcade.draw_lrbt_rectangle_filled(
            x + size + 3,
            x + size + 7,
            bottom + 4,
            bottom + 4 + bar_height,
            palette.RESOURCE,
        )


def draw_expanded_room_ui(
    width: int,
    height: int,
    state: RoomUIState,
    room_info_lines: dict[str, list[str]] | None = None,
    roster_cards: list[dict] | None = None,
) -> None:
    """Draw animated full-screen room expansion and icon buttons."""
    active = active_room_rect(state, width, height)
    if active is None:
        return

    room, rect = active
    border = _room_accent_color(room)
    arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (0, 0, 0, 164))
    texture = _load_texture_once(room.image_path) if room.image_path else None
    if texture is not None:
        room_rect = arcade.LBWH(rect.left, rect.bottom, rect.width, rect.height)
        arcade.draw_texture_rect(texture, room_rect)
        arcade.draw_lrbt_rectangle_filled(
            rect.left, rect.right, rect.bottom, rect.top, palette.EXPANDED_ROOM_SHADE
        )
    else:
        arcade.draw_lrbt_rectangle_filled(
            rect.left, rect.right, rect.bottom, rect.top, palette.EXPANDED_ROOM_FILL
        )
    arcade.draw_line(rect.left, rect.top, rect.right, rect.top, border, 3)
    arcade.draw_line(rect.left, rect.bottom, rect.right, rect.bottom, border, 2)
    arcade.draw_line(rect.left, rect.bottom, rect.left, rect.top, border, 2)
    arcade.draw_line(rect.right, rect.bottom, rect.right, rect.top, border, 2)

    icon_radius = max(34, min(72, rect.width // 9))
    _draw_room_symbol(
        room.key, rect.center_x, rect.center_y + icon_radius, icon_radius, border
    )
    if state.expansion >= 0.48:
        draw_room_title_and_info(
            room.title,
            room_info_lines.get(room.key, []) if room_info_lines else [],
            rect,
            state.action_buttons,
            border,
        )
        if (state.mode == "squad" and room.key in {
            "barracks",
            "medbay",
            "armory",
            "briefing",
            "dossier",
            "insertion",
        }) or (state.mode == "corp" and room.key == "black_ops"):
            draw_roster_cards(rect, state.action_buttons, roster_cards or [], border)
    for scan_x in range(rect.left + 36, rect.right - 24, 58):
        arcade.draw_line(
            scan_x,
            rect.bottom + 28,
            scan_x + 22,
            rect.bottom + 28,
            palette.GRID_LINE,
            1,
        )

    if state.expansion >= 0.72:
        for button in state.action_buttons:
            draw_action_button(button, border)
        draw_close_button(width, height)


def draw_room_title_and_info(title: str, lines: list[str], rect, buttons, border) -> None:
    """Draw room title and compact room state above the action controls."""
    left = rect.left + max(24, rect.width // 28)
    right = rect.right - max(24, rect.width // 28)
    top = rect.top - max(32, rect.height // 12)
    action_top = max((button.rect.top for button in buttons), default=rect.bottom + 92)
    info_bottom = action_top + 42
    panel_bottom = max(info_bottom, top - 190)

    arcade.draw_lrbt_rectangle_filled(
        left - 14,
        right + 14,
        panel_bottom - 16,
        top + 34,
        palette.PANEL_FILL_DARK,
    )
    arcade.draw_line(left, top + 20, right, top + 20, border, 2)
    arcade.draw_text(title.upper(), left, top, palette.HEADER, 22)

    y = top - 34
    max_lines = max(1, int((y - info_bottom) // 22) + 1)
    for line in lines[:max_lines]:
        arcade.draw_text(_fit_room_line(line), left, y, palette.TEXT, 13)
        y -= 22


def _fit_room_line(line: str, limit: int = 76) -> str:
    """Keep room info compact enough for the expanded room overlay."""
    return line if len(line) <= limit else f"{line[: limit - 3]}..."


def draw_roster_cards(rect, buttons, roster_cards: list[dict], border) -> None:
    """Draw graphical agent roster cards in squad rooms."""
    if not roster_cards:
        left = rect.left + max(34, rect.width // 18)
        bottom = rect.bottom + max(160, rect.height // 3)
        arcade.draw_lrbt_rectangle_filled(
            left,
            left + 260,
            bottom,
            bottom + 72,
            palette.AGENT_CARD_FILL,
        )
        _draw_icon("recruit", left + 42, bottom + 36, 44, border)
        arcade.draw_text("NO AGENTS ON ROSTER", left + 84, bottom + 42, palette.TEXT, 12)
        arcade.draw_text("RECRUIT IN BARRACKS OR BLACK OPS", left + 84, bottom + 20, palette.MUTED_TEXT, 9)
        return

    card_rects = layout_roster_card_rects(rect, buttons, len(roster_cards))
    for index, card_rect in enumerate(card_rects):
        draw_agent_card(
            roster_cards[index],
            card_rect.left,
            card_rect.bottom,
            card_rect.width,
            card_rect.height,
            border,
        )


def draw_agent_card(card: dict, left: int, bottom: int, width: int, height: int, border) -> None:
    """Draw one personalized agent card."""
    fill = palette.AGENT_CARD_FILL
    if card.get("selected"):
        fill = palette.AGENT_CARD_SELECTED
    if card.get("active"):
        fill = palette.AGENT_CARD_ACTIVE
    arcade.draw_lrbt_rectangle_filled(left, left + width, bottom, bottom + height, fill)
    arcade.draw_line(left, bottom + height, left + width, bottom + height, _role_color(card), 3)
    arcade.draw_line(left, bottom, left + width, bottom, palette.GRID_LINE, 1)
    if card.get("active"):
        _draw_active_agent_brackets(left, bottom, width, height)
    portrait_size = max(48, min(72, height - 18))
    portrait_left = left + 10
    portrait_bottom = bottom + (height - portrait_size) // 2
    _draw_agent_portrait_asset(card, portrait_left, portrait_bottom, portrait_size, border)
    text_left = portrait_left + portrait_size + 14
    arcade.draw_text(card.get("name", "Agent").upper(), text_left, bottom + height - 28, palette.TEXT, 12)
    arcade.draw_text(card.get("role", "unknown").upper(), text_left, bottom + height - 48, _role_color(card), 9)
    meter_width = max(38, width - (text_left - left) - 14)
    draw_small_meter(text_left, bottom + 22, meter_width, card.get("hp_ratio", 0), palette.TACTICAL_GREEN)
    draw_small_meter(text_left, bottom + 10, meter_width, card.get("stress_ratio", 0), palette.WARNING)
    if card.get("selected"):
        _draw_deployed_marker(left + width - 24, bottom + 19)
    if card.get("pending_points", 0) > 0:
        _draw_upgrade_badge(card.get("pending_points", 0), left + width - 48, bottom + height - 32)
    if card.get("recovery_turns", 0) > 0:
        arcade.draw_lrbt_rectangle_filled(left, left + width, bottom, bottom + 8, palette.DANGER)


def draw_small_meter(left: int, bottom: int, width: int, ratio: float, color) -> None:
    """Draw a compact stat meter on an agent card."""
    clamped = max(0.0, min(1.0, float(ratio)))
    arcade.draw_lrbt_rectangle_filled(left, left + width, bottom, bottom + 5, palette.PANEL_FILL_DARK)
    arcade.draw_lrbt_rectangle_filled(left, left + int(width * clamped), bottom, bottom + 5, color)


def _role_color(card: dict):
    role = card.get("role", "")
    if role == "sniper":
        return palette.ROLE_SNIPER
    if role == "psi":
        return palette.ROLE_PSI
    return palette.ROLE_SAMURAI


def _draw_agent_portrait(card: dict, center_x: int, center_y: int, size: int) -> None:
    """Draw a deterministic stylized portrait from role/name data."""
    role_color = _role_color(card)
    radius = size // 2
    _draw_circle_filled(center_x, center_y, radius, palette.AGENT_PORTRAIT_FILL)
    _draw_circle_outline(center_x, center_y, radius, role_color, 2)
    _draw_circle_filled(center_x, center_y + radius // 4, radius // 3, role_color)
    arcade.draw_lrbt_rectangle_filled(
        center_x - radius // 2,
        center_x + radius // 2,
        center_y - radius // 2,
        center_y + radius // 5,
        role_color,
    )
    seed = sum(ord(char) for char in card.get("name", ""))
    if seed % 2 == 0:
        arcade.draw_line(center_x - radius // 2, center_y + 2, center_x + radius // 2, center_y + 8, palette.DANGER, 2)
    if seed % 3 == 0:
        arcade.draw_line(center_x - radius // 3, center_y + radius // 2, center_x + radius // 3, center_y + radius // 2, palette.ACCENT, 2)
    if card.get("selected"):
        _draw_circle_outline(center_x, center_y, radius + 5, palette.RESOURCE, 2)


def _draw_agent_portrait_asset(card: dict, left: int, bottom: int, size: int, border) -> None:
    """Draw a generated portrait asset, falling back to the procedural mark."""
    path = card.get("portrait_path")
    texture = _load_texture_once(path) if path else None
    if texture is None or not hasattr(arcade, "draw_texture_rect"):
        _draw_agent_portrait(card, left + size // 2, bottom + size // 2, size)
        return
    arcade.draw_lrbt_rectangle_filled(
        left - 3, left + size + 3, bottom - 3, bottom + size + 3, palette.AGENT_PORTRAIT_FILL
    )
    arcade.draw_texture_rect(texture, arcade.LBWH(left, bottom, size, size))
    arcade.draw_line(left - 3, bottom + size + 3, left + size + 3, bottom + size + 3, border, 2)
    arcade.draw_line(left - 3, bottom - 3, left + size + 3, bottom - 3, palette.GRID_LINE, 1)


def _draw_active_agent_brackets(left: int, bottom: int, width: int, height: int) -> None:
    """Draw strong corner brackets for the current active agent."""
    right = left + width
    top = bottom + height
    color = palette.ACTIVE_AGENT_BORDER
    bracket = 34
    arcade.draw_line(left - 2, top + 2, left + bracket, top + 2, color, 3)
    arcade.draw_line(left - 2, top + 2, left - 2, top - bracket, color, 3)
    arcade.draw_line(right + 2, top + 2, right - bracket, top + 2, color, 3)
    arcade.draw_line(right + 2, top + 2, right + 2, top - bracket, color, 3)
    arcade.draw_text("ACTIVE", right - 58, top - 18, color, 9)


def _draw_deployed_marker(center_x: int, center_y: int) -> None:
    """Draw a compact squad-selection mark."""
    _draw_circle_filled(center_x, center_y, 10, palette.DEPLOYED_AGENT_MARK)
    arcade.draw_line(center_x - 5, center_y, center_x - 1, center_y - 5, palette.BACKGROUND, 2)
    arcade.draw_line(center_x - 1, center_y - 5, center_x + 6, center_y + 5, palette.BACKGROUND, 2)


def _draw_upgrade_badge(points: int, left: int, bottom: int) -> None:
    """Draw a numbered pending-upgrade badge."""
    width = 38
    height = 22
    arcade.draw_lrbt_rectangle_filled(
        left, left + width, bottom, bottom + height, palette.RESOURCE
    )
    arcade.draw_text(
        f"PTS {points}",
        left + width // 2,
        bottom + 6,
        palette.BACKGROUND,
        8,
        anchor_x="center",
    )


def draw_action_button(button: ActionButton, border) -> None:
    """Draw an action button with an icon and a short readable label."""
    rect = button.rect
    arcade.draw_lrbt_rectangle_filled(
        rect.left, rect.right, rect.bottom, rect.top, palette.ACTION_BUTTON_FILL
    )
    arcade.draw_line(rect.left, rect.top, rect.right, rect.top, border, 2)
    arcade.draw_line(rect.left, rect.bottom, rect.right, rect.bottom, palette.GRID_LINE, 1)
    arcade.draw_line(rect.left, rect.bottom, rect.left, rect.top, border, 1)
    arcade.draw_line(rect.right, rect.bottom, rect.right, rect.top, border, 1)
    label_height = 18 if button.action.label else 0
    _draw_icon(
        button.action.icon,
        rect.center_x,
        rect.center_y + label_height // 2,
        rect.width - 30,
        border,
    )
    if button.action.label:
        arcade.draw_text(
            button.action.label.upper(),
            rect.center_x,
            rect.bottom - 20,
            palette.TEXT,
            9,
            anchor_x="center",
        )


def draw_close_button(width: int, height: int) -> None:
    """Draw the icon-only close control."""
    rect = close_button_rect(width, height)
    arcade.draw_lrbt_rectangle_filled(
        rect.left, rect.right, rect.bottom, rect.top, palette.ACTION_BUTTON_FILL
    )
    arcade.draw_line(rect.left + 11, rect.bottom + 11, rect.right - 11, rect.top - 11, palette.DANGER, 3)
    arcade.draw_line(rect.left + 11, rect.top - 11, rect.right - 11, rect.bottom + 11, palette.DANGER, 3)


def _draw_room_symbol(key: str, center_x: int, center_y: int, size: int, color) -> None:
    icon = {
        "research": "research",
        "server": "intel",
        "security": "shield",
        "black_ops": "black_ops",
        "executive": "influence",
        "municipal": "city",
        "district": "radar",
        "transit": "armory",
        "barracks": "squad",
        "ops": "radar",
        "intel": "research",
        "medbay": "medbay",
        "armory": "armory",
        "insertion": "launch",
    }.get(key, "city")
    _draw_icon(icon, center_x, center_y, size, color)


def _draw_icon(kind: str, center_x: int, center_y: int, size: int, color) -> None:
    half = size // 2
    if kind in {"credits", "influence"}:
        _draw_circle_outline(center_x, center_y, half // 2, color, 2)
        _draw_circle_filled(center_x, center_y, max(3, half // 6), color)
        arcade.draw_line(center_x - half // 2, center_y, center_x + half // 2, center_y, color, 2)
        return
    if kind in {"intel", "research"}:
        _draw_circle_outline(center_x, center_y, half // 3, color, 2)
        arcade.draw_line(center_x - half, center_y, center_x + half, center_y, color, 2)
        arcade.draw_line(center_x, center_y - half, center_x, center_y + half, color, 2)
        arcade.draw_line(center_x - half // 2, center_y - half // 2, center_x + half // 2, center_y + half // 2, color, 2)
        return
    if kind in {"salvage", "armory"}:
        arcade.draw_lrbt_rectangle_filled(center_x - half, center_x + half, center_y - half // 4, center_y + half // 4, color)
        arcade.draw_line(center_x - half, center_y - half, center_x + half, center_y + half, color, 3)
        return
    if kind == "shield":
        arcade.draw_line(center_x, center_y + half, center_x + half, center_y + half // 3, color, 3)
        arcade.draw_line(center_x + half, center_y + half // 3, center_x + half // 3, center_y - half, color, 3)
        arcade.draw_line(center_x + half // 3, center_y - half, center_x - half // 3, center_y - half, color, 3)
        arcade.draw_line(center_x - half // 3, center_y - half, center_x - half, center_y + half // 3, color, 3)
        arcade.draw_line(center_x - half, center_y + half // 3, center_x, center_y + half, color, 3)
        return
    if kind == "black_ops":
        arcade.draw_line(center_x, center_y + half, center_x + half, center_y, color, 3)
        arcade.draw_line(center_x + half, center_y, center_x, center_y - half, color, 3)
        arcade.draw_line(center_x, center_y - half, center_x - half, center_y, color, 3)
        arcade.draw_line(center_x - half, center_y, center_x, center_y + half, color, 3)
        _draw_circle_filled(center_x, center_y, max(4, half // 5), color)
        return
    if kind in {"city", "squad", "recruit"}:
        for index, scale in enumerate((0.55, 0.8, 0.65)):
            left = center_x - half + index * (half // 2)
            arcade.draw_lrbt_rectangle_filled(
                left, left + half // 3, center_y - half, center_y - half + int(size * scale), color
            )
        return
    if kind == "radar":
        _draw_circle_outline(center_x, center_y, half // 2, color, 2)
        _draw_circle_outline(center_x, center_y, half, color, 1)
        arcade.draw_line(center_x, center_y, center_x + half, center_y + half // 2, color, 3)
        return
    if kind == "medbay":
        arcade.draw_lrbt_rectangle_filled(center_x - half // 5, center_x + half // 5, center_y - half, center_y + half, color)
        arcade.draw_lrbt_rectangle_filled(center_x - half, center_x + half, center_y - half // 5, center_y + half // 5, color)
        return
    if kind == "select":
        _draw_circle_outline(center_x, center_y, half, color, 2)
        arcade.draw_line(center_x - half // 2, center_y, center_x - 3, center_y - half // 2, color, 4)
        arcade.draw_line(center_x - 3, center_y - half // 2, center_x + half // 2, center_y + half // 2, color, 4)
        return
    if kind == "left":
        arcade.draw_line(center_x + half, center_y + half, center_x - half, center_y, color, 4)
        arcade.draw_line(center_x - half, center_y, center_x + half, center_y - half, color, 4)
        return
    if kind == "right":
        arcade.draw_line(center_x - half, center_y + half, center_x + half, center_y, color, 4)
        arcade.draw_line(center_x + half, center_y, center_x - half, center_y - half, color, 4)
        return
    if kind == "launch":
        arcade.draw_line(center_x - half, center_y - half, center_x + half, center_y, color, 4)
        arcade.draw_line(center_x + half, center_y, center_x - half, center_y + half, color, 4)
        arcade.draw_line(center_x - half, center_y + half, center_x - half, center_y - half, color, 4)


def draw_deck_panel(panel) -> None:
    """Draw a command-deck panel from a layout object."""
    draw_panel(panel.left, panel.bottom, panel.width, panel.height, panel.title)
    notch = 18
    arcade.draw_line(
        panel.left + panel.width - notch,
        panel.bottom + panel.height,
        panel.left + panel.width,
        panel.bottom + panel.height - notch,
        palette.PANEL_BORDER,
        2,
    )


def draw_command_screen_frame(
    title: str, width: int, height: int, mode: str = "corp"
) -> None:
    """Draw global corporate-tower chrome around any management screen."""
    draw_city_corporate_backdrop(width, height, mode)
    arcade.draw_lrbt_rectangle_filled(
        14, width - 14, height - 84, height - 52, palette.PANEL_FILL_DARK
    )
    arcade.draw_line(
        14, height - 84, width - 14, height - 84, palette.PANEL_BORDER_MUTED, 1
    )
    arcade.draw_text(title, 28, height - 75, palette.HEADER, 16)


def draw_action_strip(text: str, width: int) -> None:
    """Draw the bottom keyboard command strip."""
    arcade.draw_lrbt_rectangle_filled(0, width, 0, 42, palette.PANEL_FILL_DARK)
    arcade.draw_line(0, 43, width, 43, palette.PANEL_BORDER, 2)
    arcade.draw_text(text, 20, 16, palette.ACCENT, 13)


def draw_tactical_meter(
    left: int, bottom: int, width: int, label: str, value: int
) -> None:
    """Draw a compact 0-100 pressure meter for city/corp status panels."""
    clamped = max(0, min(100, value))
    arcade.draw_text(label.upper(), left, bottom + 9, palette.MUTED_TEXT, 10)
    arcade.draw_lrbt_rectangle_filled(
        left + 110, left + 110 + width, bottom + 8, bottom + 18, palette.PANEL_FILL_DARK
    )
    arcade.draw_lrbt_rectangle_filled(
        left + 110,
        left + 110 + int(width * clamped / 100),
        bottom + 8,
        bottom + 18,
        (
            palette.DANGER
            if clamped >= 70
            else palette.WARNING if clamped >= 40 else palette.TACTICAL_GREEN
        ),
    )
