"""Live equipment pane for Squad Command; dispatches existing management actions."""

import arcade
from game.management.equipment import EQUIPMENT_SLOTS, Weapon, Armor
from game.ui.layouts.world_map_beacons import Rect
from game.ui.panels import _load_texture_once
from game.ui.portraits import portrait_path_for_character
from .squad_style import CYAN, GOLD, MINT, TEXT, MUTED


def draw_equipment(self, r):
    u = self.u
    gs = self.gs
    index = self.view.deployment_cursor
    char = gs.characters[index] if 0 <= index < len(gs.characters) else None
    self.panel(
        r,
        self.tr("equipment") + (" — " + char.name.upper() if char else ""),
        "armory",
    )
    if char is None:
        self.label(
            self.tr("select_agent"),
            *r.center,
            18,
            MUTED,
            anchor_x="center",
            width=r.width - 30 * u,
        )
        return
    inner = Rect(r.left + 10 * u, r.bottom + 46 * u, r.right - 10 * u, r.top - 56 * u)
    hero_right = inner.left + inner.width * 0.43
    portrait = Rect(inner.left, inner.bottom, hero_right - 7 * u, inner.top)
    hero_art = Rect(
        portrait.left,
        portrait.top - min(portrait.height * 0.64, portrait.width * 1.45),
        portrait.right,
        portrait.top,
    )
    self.image(portrait_path_for_character(char), hero_art)
    stats_top = hero_art.bottom - 10 * u
    stats_bottom = portrait.bottom + 77 * u
    entries = [
        ("STR", "str", char.stats.str),
        ("AGI", "agi", char.stats.agi),
        ("PSI", "psi", char.stats.psi),
        ("DEF", "def", char.stats.defense),
        ("CON", "con", char.stats.con),
        (self.tr("hp"), None, char.stats.max_hp),
    ]
    cell_w = (portrait.width - 5 * u) / 2
    cell_h = max(26 * u, (stats_top - stats_bottom - 10 * u) / 3)
    for n, (name, key, value) in enumerate(entries):
        l = portrait.left + (n % 2) * (cell_w + 5 * u)
        top = stats_top - (n // 2) * (cell_h + 5 * u)
        cell = Rect(l, top - cell_h, l + cell_w, top)
        self.paint.panel(cell, GOLD if key and char.pending_points else CYAN)
        self.label(name, l + 7 * u, cell.center[1] + 8 * u, 11, CYAN, bold=True)
        self.label(str(value), l + 7 * u, cell.center[1] - 11 * u, 18, TEXT, bold=True)
        if key and char.pending_points:
            plus = Rect(
                cell.right - 29 * u,
                cell.bottom + 3 * u,
                cell.right - 3 * u,
                cell.top - 3 * u,
            )
            self.label("+", *plus.center, 25, GOLD, bold=True, anchor_x="center")
            self.hit(plus, "spend_stat_point", (index, key), self.tr("upgrade"))
    self.regions["hero"] = portrait
    self.hit(hero_art, "squad_sheet", index, self.tr("full_sheet"))
    shade = Rect(
        portrait.left, portrait.bottom, portrait.right, portrait.bottom + 70 * u
    )
    arcade.draw_lrbt_rectangle_filled(
        shade.left, shade.right, shade.bottom, shade.top, (1, 10, 18, 220)
    )
    self.label(
        self.tr("level", level=char.stats.level),
        shade.left + 10 * u,
        shade.top - 16 * u,
        13,
        CYAN,
        bold=True,
    )
    self.label(
        self.tr("full_sheet") + " >",
        shade.left + 10 * u,
        shade.bottom + 18 * u,
        12,
        TEXT,
        width=shade.width - 20 * u,
    )
    self.hit(shade, "squad_sheet", index, self.tr("full_sheet"))
    sheet = _load_texture_once("assets/ui/squad_command/equipment_sheet.png")
    left = hero_right + 3 * u
    gap = 7 * u
    row_h = (inner.height - 5 * gap) / 6
    for i, slot in enumerate(EQUIPMENT_SLOTS):
        top = inner.top - i * (row_h + gap)
        rect = Rect(left, top - row_h, inner.right, top)
        item = char.loadout.item_for_slot(slot)
        color = GOLD if slot == "special_gear" and item else CYAN
        self.paint.panel(
            rect,
            color,
            selected=self.hover
            in [("equip_prev", (index, slot)), ("equip_next", (index, slot))],
        )
        art_w = min(72 * u, rect.width * 0.25)
        ar = Rect(
            rect.left + 3 * u,
            rect.bottom + 3 * u,
            rect.left + art_w,
            rect.top - 3 * u,
        )
        if isinstance(item, Weapon) and any(
            tag in item.tags for tag in ("blade", "katana", "melee")
        ):
            self.icon("sword", *ar.center, 48, CYAN)
        elif sheet:
            key = ("equipment", i)
            if key not in self._tiles:
                self._tiles[key] = sheet.crop(
                    (i % 2) * (sheet.width // 2),
                    (i // 2) * (sheet.height // 3),
                    sheet.width // 2,
                    sheet.height // 3,
                )
            self.texture(self._tiles[key], ar, cover=False, alpha=255 if item else 105)
        tx = ar.right + 5 * u
        right = rect.right - 41 * u
        self.label(
            self.tr("slot." + slot),
            tx,
            rect.top - 12 * u,
            10.5,
            CYAN,
            bold=True,
            width=right - tx,
        )
        self.label(
            item.name.upper() if item else self.tr("empty"),
            tx,
            rect.center[1] + 2 * u,
            14,
            TEXT if item else MUTED,
            bold=True,
            width=right - tx,
        )
        detail = []
        if isinstance(item, Weapon):
            detail.extend([f"RNG {item.range_cells}", f"DMG +{item.damage_bonus}"])
        elif isinstance(item, Armor):
            detail.append(self.tr("mitigation", value=item.mitigation))
        if item:
            detail.extend(
                f"{key.upper()} {value:+}"
                for key, value in item.stat_bonuses.items()
                if value
            )
        self.label(
            "  ".join(detail),
            tx,
            rect.bottom + 12 * u,
            10.5,
            MINT,
            width=right - tx,
        )
        for j, (symbol, action) in enumerate(
            [("‹", "equip_prev"), ("›", "equip_next")]
        ):
            arrow = Rect(
                rect.right - (40 - j * 20) * u,
                rect.center[1] - 15 * u,
                rect.right - (21 - j * 20) * u,
                rect.center[1] + 15 * u,
            )
            self.label(symbol, *arrow.center, 28, CYAN, bold=True, anchor_x="center")
            self.hit(
                arrow,
                action,
                (index, slot),
                ((item.name + " · " + ", ".join(detail)) if item else self.tr("empty")),
            )
    totals = char.loadout.total_stat_bonuses()
    summary = (
        self.tr("totals")
        + "  "
        + ("   ".join(f"{k.upper()} {v:+}" for k, v in totals.items() if v) or "—")
    )
    self.label(
        summary,
        r.left + 14 * u,
        r.bottom + 24 * u,
        12,
        MINT,
        bold=True,
        width=r.width - 28 * u,
    )

    self.hit(
        Rect(r.left + 10 * u, r.bottom + 9 * u, r.right - 10 * u, r.bottom + 38 * u),
        "squad_total_info",
        tooltip=summary,
    )
