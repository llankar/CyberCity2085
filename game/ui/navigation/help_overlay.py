from __future__ import annotations

from dataclasses import dataclass


GLOBAL_SHORTCUTS = [
    "Tab / Shift+Tab: naviguer le focus",
    "Entrée: activer l'élément focalisé",
    "H: afficher/masquer l'aide",
    "Esc: fermer la room active",
]


@dataclass
class HelpOverlayState:
    visible: bool = False

    def toggle(self) -> None:
        self.visible = not self.visible


def build_hint_banner(view_key: str, room_key: str | None = None) -> str:
    context = room_key or "tower"
    if view_key == "squad":
        return f"[{context}] Tab focus | Entrée action | A/D agent | 1-3 mission | B lancement | H aide"
    if view_key == "corp":
        return f"[{context}] Tab focus | Entrée action | C ville | R escouade | D jour | H aide"
    return f"[{context}] Tab focus | Entrée action | C corp | R escouade | D jour | H aide"


def build_help_lines(view_key: str, room_key: str | None, actions: list[str]) -> list[str]:
    lines = ["AIDE CLAVIER // Command UI", *GLOBAL_SHORTCUTS]
    lines.append(f"Vue: {view_key} | Contexte: {room_key or 'tower'}")
    if actions:
        lines.append("Raccourcis contextuels:")
        lines.extend(f"- {action}" for action in actions[:6])
    return lines
