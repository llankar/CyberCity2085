from __future__ import annotations

from dataclasses import dataclass


GLOBAL_SHORTCUTS = [
    "Tab / Shift+Tab: move focus",
    "Enter: activate focused item",
    "H: show/hide help",
    "Esc: close the active room",
]


@dataclass
class HelpOverlayState:
    visible: bool = False

    def toggle(self) -> None:
        self.visible = not self.visible


def build_hint_banner(view_key: str, room_key: str | None = None) -> str:
    context = room_key or "tower"
    if view_key == "squad":
        return f"[{context}] Tab focus | Enter action | A/D agent | 1-3 mission | B launch | H help"
    if view_key == "corp":
        return f"[{context}] Tab focus | Enter action | C city | R squad | D day | H help"
    return f"[{context}] Tab focus | Enter action | C corp | R squad | D day | H help"


def build_help_lines(view_key: str, room_key: str | None, actions: list[str]) -> list[str]:
    lines = ["KEYBOARD HELP // Command UI", *GLOBAL_SHORTCUTS]
    lines.append(f"View: {view_key} | Context: {room_key or 'tower'}")
    if actions:
        lines.append("Contextual shortcuts:")
        lines.extend(f"- {action}" for action in actions[:6])
    return lines
