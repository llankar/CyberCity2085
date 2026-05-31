from __future__ import annotations

from dataclasses import dataclass

from .input_map import active_shortcuts_for_screen


@dataclass
class HelpOverlayState:
    visible: bool = False

    def toggle(self) -> None:
        self.visible = not self.visible


def build_hint_banner(view_key: str, room_key: str | None = None, has_room_open: bool = False) -> str:
    context = room_key or "tower"
    items = active_shortcuts_for_screen(view_key, has_room_open)
    banner_items = items[:4]
    if has_room_open and not any("Esc" in item for item in banner_items):
        banner_items = banner_items[:-1] + ["Esc close room"]
    shortcuts = " | ".join(banner_items)
    return f"[{context}] {shortcuts}"


def build_help_lines(view_key: str, room_key: str | None, actions: list[str], has_room_open: bool = False) -> list[str]:
    lines = [
        "KEYBOARD HELP // Command UI",
        "Tab / Shift+Tab: move focus",
        "Enter: activate focused item",
        "H: show/hide help",
        f"View: {view_key} | Context: {room_key or 'tower'}",
        "Active shortcuts:",
        *[f"- {line}" for line in active_shortcuts_for_screen(view_key, has_room_open)[:5]],
    ]
    if actions:
        lines.append("Room/list actions:")
        lines.extend(f"- {action}" for action in actions[:4])
    return lines
