from __future__ import annotations

from .focus_manager import FocusItem


def keyboard_action_for_focus(item: FocusItem | None) -> str | None:
    if item is None:
        return None
    if item.kind == "room":
        return "open_room"
    if item.kind == "action":
        return item.key
    if item.kind == "mission":
        return "select_mission"
    if item.kind == "agent":
        return "select_agent"
    return None


def active_shortcuts_for_screen(view_key: str, has_room_open: bool) -> list[str]:
    if view_key == "command_deck":
        shortcuts = ["Tab/Shift+Tab focus", "Enter activate", "Up/Down mission", "A/D agent", "H help"]
    elif view_key == "mission_board":
        shortcuts = ["Tab/Shift+Tab focus", "Enter activate", "Up/Down mission", "1-3 quick choices", "H help"]
    else:
        shortcuts = ["Tab/Shift+Tab focus", "Enter activate", "C city", "R squad", "H help"]
    if has_room_open:
        shortcuts.append("Esc close room")
    return shortcuts
