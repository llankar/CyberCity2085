"""Cyberware summary pane replacing mission choice in Squad Command."""

from game.agents.cyberware import BY_ID, combat_bonuses
from game.ui.layouts.world_map_beacons import Rect
from .squad_style import CYAN, GOLD, MINT, TEXT, MUTED


def draw_cyberware(self, r):
    self.panel(r, "CYBERWARE", "chip")
    body = Rect(r.left + 16 * self.u, r.bottom + 16 * self.u, r.right - 16 * self.u, r.top - 62 * self.u)
    if not self.gs.characters:
        self.paragraph("Select an agent to inspect augmentation capacity.", body)
        return
    index = min(max(self.view.deployment_cursor, 0), len(self.gs.characters) - 1)
    char = self.gs.characters[index]
    self.label(char.name.upper(), body.left, body.top - 20 * self.u, 22, TEXT, bold=True, width=body.width)
    self.label(f"HUMANITY  {char.humanity} / 5", body.left, body.top - 52 * self.u, 17, GOLD, bold=True, width=body.width)
    y = body.top - 92 * self.u
    installed = [BY_ID[key] for key in char.installed_cyberware if key in BY_ID]
    if not installed:
        self.paragraph("No implants installed. Open the dedicated sheet to trade Humanity for tactical advantages.", Rect(body.left, y - 100 * self.u, body.right, y), 14)
    for item in installed:
        card = Rect(body.left, y - 74 * self.u, body.right, y)
        self.paint.panel(card, MINT)
        self.label(item.name.upper(), card.left + 10 * self.u, card.top - 21 * self.u, 14, TEXT, bold=True, width=card.width - 20 * self.u)
        self.label(f"{item.zone} T{item.power_tier}  //  ¥{item.credit_cost:,}  H-{item.humanity_cost}", card.left + 10 * self.u, card.top - 39 * self.u, 10, GOLD, width=card.width - 20 * self.u)
        bonuses = "  ".join(f"+{v} {k.upper()}" for k, v in item.combat_bonuses.items())
        self.label(bonuses, card.left + 10 * self.u, card.bottom + 11 * self.u, 11, CYAN, width=card.width - 20 * self.u)
        y -= 84 * self.u
    totals = "  ".join(f"+{v} {k.upper()}" for k, v in combat_bonuses(char.installed_cyberware).items())
    if totals:
        self.label("TOTAL  " + totals, body.left, body.bottom + 66 * self.u, 12, MUTED, bold=True, width=body.width)
    button = Rect(body.left, body.bottom, body.right, body.bottom + 48 * self.u)
    self.paint.panel(button, CYAN, selected=True)
    self.label("OPEN CYBERWARE SHEET", *button.center, 13, CYAN, bold=True, anchor_x="center")
    self.hit(button, "open_cyberware", index, "Open Cyberware body slots")
