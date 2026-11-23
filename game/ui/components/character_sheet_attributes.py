"""Attribute upgrades, exact readiness values and a live equipment hologram."""

import arcade
from game.ui.layouts.world_map_beacons import Rect
from game.ui.panels import _load_texture_once
from .character_sheet_model import ATTRIBUTE_ORDER, READINESS_ORDER
from .squad_style import CYAN, GOLD, MINT, TEXT, MUTED
from .character_sheet import VIOLET, LOCKED

ATTRIBUTE_ICONS = {
    "str": "fist",
    "agi": "bolt",
    "psi": "psi",
    "def": "shield",
    "con": "heart",
}
READINESS_ICONS = {
    "hp": "heart",
    "aim": "target",
    "defense": "shield",
    "initiative": "next",
    "resolve": "cube",
    "recovery_rate": "heal",
}


def draw_attributes(p, r):
    u = p.u
    c = p.character
    p.panel(r, p.tr("attributes"), "dna")
    left = r.left + 12 * u
    top = r.top - 62 * u
    bottom = r.bottom + 14 * u
    gap = 9 * u
    width = (r.width - 24 * u - 4 * gap) / 5
    for index, (key, label) in enumerate(ATTRIBUTE_ORDER):
        rect = Rect(
            left + index * (width + gap),
            bottom,
            left + index * (width + gap) + width,
            top,
        )
        value = getattr(c.stats, "defense" if key == "def" else key)
        available = c.pending_points > 0
        color = VIOLET if key == "psi" else CYAN
        action = "sheet_spend_stat" if available else "sheet_info"
        data = (p.index, key) if available else ("attribute", key)
        p.card(
            rect,
            color,
            action,
            data,
            p.tr("upgrade_help", name=label, points=c.pending_points),
            ("attribute", "defense" if key == "def" else key),
        )
        x = rect.center[0]
        p.icon(ATTRIBUTE_ICONS[key], x, rect.top - 28 * u, 32, color)
        p.label(label, x, rect.top - 63 * u, 17, TEXT, bold=True, anchor_x="center")
        p.label(
            str(value),
            x,
            rect.center[1] - 14 * u,
            34,
            TEXT,
            bold=True,
            anchor_x="center",
        )
        button = Rect(
            x - 18 * u, rect.bottom + 10 * u, x + 18 * u, rect.bottom + 43 * u
        )
        p.paint.panel(button, GOLD if available else CYAN)
        p.label(
            "+",
            *button.center,
            29,
            GOLD if available else LOCKED,
            bold=True,
            anchor_x="center"
        )


def draw_readiness(p, r):
    u = p.u
    p.panel(r, p.tr("readiness"), "heart")
    gap = 8 * u
    left = r.left + 12 * u
    width = (r.width - 24 * u - 5 * gap) / 6
    for i, (key, label) in enumerate(READINESS_ORDER):
        rect = Rect(
            left + i * (width + gap),
            r.bottom + 15 * u,
            left + i * (width + gap) + width,
            r.top - 61 * u,
        )
        color = VIOLET if key == "resolve" else CYAN
        p.paint.panel(rect, color)
        x = rect.center[0]
        p.icon(READINESS_ICONS[key], x, rect.top - 24 * u, 26, color)
        p.label(label, x, rect.top - 55 * u, 13, TEXT, anchor_x="center")
        p.label(
            str(p.data.derived[key]),
            x,
            rect.bottom + 24 * u,
            29,
            TEXT,
            bold=True,
            anchor_x="center",
        )
        p.hit(
            rect,
            "sheet_info",
            ("readiness", key),
            p.tr("derived_help", name=label, value=p.data.derived[key]),
        )


def draw_schematic(p, r):
    u = p.u
    c = p.character
    if r.height < 50:
        return
    p.paint.panel(r, CYAN)
    for x in range(int(r.left + 8 * u), int(r.right - 5 * u), max(12, int(22 * u))):
        arcade.draw_line(x, r.bottom + 8 * u, x, r.top - 8 * u, (*CYAN, 25), 1)
    for y in range(int(r.bottom + 8 * u), int(r.top - 5 * u), max(12, int(22 * u))):
        arcade.draw_line(r.left + 8 * u, y, r.right - 8 * u, y, (*CYAN, 25), 1)
    scan = r.bottom + 8 * u + ((p.view._elapsed * 0.18) % 1) * (r.height - 16 * u)
    arcade.draw_line(r.left + 8 * u, scan, r.right - 8 * u, scan, (*CYAN, 40), 1)
    item = c.loadout.primary_weapon
    p.label(
        p.tr("loadout"),
        r.left + 13 * u,
        r.top - 20 * u,
        13,
        CYAN,
        bold=True,
        width=r.width - 25 * u,
    )
    if item:
        sheet = _load_texture_once("assets/ui/squad_command/equipment_sheet.png")
        if "blade" in item.tags or "katana" in item.tags:
            p.icon("sword", *r.center, min(100, r.height / u * 0.55), CYAN)
        elif sheet:
            key = ("sheet_weapon",)
            if key not in p._tiles:
                p._tiles[key] = sheet.crop(0, 0, sheet.width // 2, sheet.height // 3)
            p.texture(
                p._tiles[key],
                Rect(
                    r.left + 35 * u, r.bottom + 31 * u, r.right - 35 * u, r.top - 28 * u
                ),
                cover=False,
                alpha=235,
            )
        p.label(
            item.name.upper(),
            r.left + 13 * u,
            r.bottom + 17 * u,
            15,
            TEXT,
            bold=True,
            width=r.width - 26 * u,
        )
    else:
        p.icon(
            "psi" if c.role == "psi" else "robot" if c.role == "robot" else "target",
            *r.center,
            min(80, r.height / u * 0.5),
            VIOLET if c.role == "psi" else CYAN
        )
        p.label(
            p.tr("no_weapon"),
            r.left + 13 * u,
            r.bottom + 17 * u,
            13,
            MUTED,
            width=r.width - 26 * u,
        )
