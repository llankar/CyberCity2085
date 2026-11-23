"""Full-screen holographic character dossier built from reusable command widgets."""

from pathlib import Path
from math import sin
import arcade
from game.i18n import t
from game.ui.layouts.world_map_beacons import Rect
from game.ui.layouts.character_sheet import character_sheet_layout, paged_grid
from game.ui.components.squad_command import SquadCommandRenderer, SquadHit
from game.ui.components.squad_style import CYAN, GOLD, MINT, RED, TEXT, MUTED
from game.ui.components.character_sheet_model import build_character_sheet_data
from game.ui.panels import _load_texture_once
from game.ui.theme.typography import get_text_size, scale_font_size

VIOLET = (200, 130, 255)
LOCKED = (111, 140, 153)


class CharacterSheetRenderer(SquadCommandRenderer):
    def __init__(self):
        super().__init__()
        self.first_rows = {"skills": 0, "talents": 0}
        self.grids = {}
        self.scroll_target = "skills"
        self.character_id = None
        self.visible_skills = set()
        self.visible_talents = set()
        self.last_values = {}
        self.flash_keys = set()
        self.flash_until = 0.0

    def tr(self, key, **kwargs):
        return t("sheet." + key, self.gs.ui_language, **kwargs)

    def icon(self, key, x, y, size=24, color=CYAN):
        path = Path("assets/ui/character_sheet/icons") / (key + ".png")
        texture = _load_texture_once(str(path)) if path.exists() else None
        if texture is not None:
            side = size * self.u
            arcade.draw_texture_rect(
                texture,
                arcade.LBWH(x - side / 2, y - side / 2, side, side),
                color=arcade.types.Color.from_iterable(color),
            )
        else:
            super().icon(key, x, y, size, color)

    def hit(self, rect, action, data=None, tooltip=""):
        self.view._modal_hits.append(
            SquadHit(
                rect.left, rect.bottom, rect.right, rect.top, action, data, tooltip
            )
        )

    def draw(self, view, w, h):
        self.index = view.expanded_agent_sheet_index
        self.character = view.game_state.characters[self.index]
        identity = (id(self.character), self.character.name)
        if identity != self.character_id:
            self.first_rows = {"skills": 0, "talents": 0}
            self.character_id = identity
            self.last_values = {}
        self.data = build_character_sheet_data(self.character)
        values = {("attribute", k): v for k, v in self.data.attributes.items()}
        values.update({("skill", s.key): s.rank for s in self.data.skills})
        values.update(
            {("talent", item.node.id): item.state for item in self.data.talents}
        )
        changed = {
            key
            for key, value in values.items()
            if key in self.last_values and value != self.last_values[key]
        }
        if changed:
            self.flash_keys = changed
            self.flash_until = view._elapsed + 0.5
        self.last_values = values
        self.visible_skills = set()
        self.visible_talents = set()
        view._modal_hits = []
        super().draw(view, w, h)

    def header(self):
        self.layout = character_sheet_layout(self.layout.width, self.layout.height)
        u = self.u
        r = self.layout.header
        w = self.layout.width
        char = self.character
        arcade.draw_lrbt_rectangle_filled(0, w, r.bottom, r.top, (0, 12, 20, 235))
        self.icon("city", 35 * u, r.center[1], 37)
        brand = self.label("CYBERCITY", 66 * u, r.center[1], 25, CYAN, bold=True)
        year_x = 76 * u + brand.content_width
        year = self.label("2085", year_x, r.center[1], 25, GOLD, bold=True)
        self.label(
            "// " + self.tr("dossier"),
            year_x + year.content_width + 18 * u,
            r.center[1],
            17,
            CYAN,
            width=max(1, w * 0.56 - year_x - year.content_width - 18 * u),
        )
        left = w * 0.58
        right = w - 100 * u
        cw = (right - left - 16 * u) / 2
        for i, (key, value, color, icon) in enumerate(
            [
                ("pending", char.pending_points, CYAN, "shield"),
                ("talent_points", char.talent_points, GOLD, "layers"),
            ]
        ):
            box = Rect(
                left + i * (cw + 16 * u),
                r.bottom + 8 * u,
                left + i * (cw + 16 * u) + cw,
                r.top - 8 * u,
            )
            self.paint.panel(box, color, selected=value > 0)
            self.icon(icon, box.left + 21 * u, box.center[1], 25, color)
            self.label(
                self.tr(key),
                box.left + 42 * u,
                box.center[1],
                14,
                TEXT,
                bold=True,
                width=box.width - 91 * u,
            )
            self.label(
                str(value),
                box.right - 20 * u,
                box.center[1],
                27,
                color,
                bold=True,
                anchor_x="right",
            )
        close = Rect(w - 64 * u, r.bottom + 8 * u, w - 16 * u, r.top - 8 * u)
        self.paint.panel(close, RED, selected=self.hover == ("sheet_close", None))
        x, y = close.center
        arcade.draw_line(x - 11 * u, y - 11 * u, x + 11 * u, y + 11 * u, RED, 3 * u)
        arcade.draw_line(x - 11 * u, y + 11 * u, x + 11 * u, y - 11 * u, RED, 3 * u)
        self.hit(close, "sheet_close", tooltip=self.tr("close"))
        banner = self.layout.banner
        self.paint.panel(banner, CYAN)
        cyber = Rect(banner.right - 190 * u, banner.bottom + 8 * u, banner.right - 16 * u, banner.top - 8 * u)
        self.paint.panel(cyber, VIOLET, selected=self.hover == ("sheet_cyberware", None))
        self.label("CYBERWARE", cyber.center[0], cyber.center[1], 12, VIOLET, bold=True, anchor_x="center")
        self.hit(cyber, "sheet_cyberware", tooltip="Open cyberware sheet")
        self.icon("target", banner.left + 27 * u, banner.center[1], 30, GOLD)
        name = self.label(
            char.name.upper(),
            banner.left + 56 * u,
            banner.center[1],
            30,
            TEXT,
            bold=True,
            width=banner.width * 0.38,
        )
        role = t("squad.role." + char.role, self.gs.ui_language)
        if role.startswith("squad."):
            role = char.role.upper()
        self.role_label = role
        self.label(
            " //  " + role + "  //  " + self.tr("level", level=char.stats.level),
            banner.left + 70 * u + name.content_width,
            banner.center[1],
            22,
            TEXT,
            width=banner.width * 0.56,
        )

    def agents(self, _):
        from .character_sheet_identity import draw_identity
        from .character_sheet_talents import draw_talents

        draw_identity(self, self.layout.identity)
        draw_talents(self, self.layout.talents)

    def equipment(self, _):
        from .character_sheet_attributes import (
            draw_attributes,
            draw_readiness,
            draw_schematic,
        )

        draw_attributes(self, self.layout.attributes)
        draw_readiness(self, self.layout.readiness)
        draw_schematic(self, self.layout.schematic)

    def mission(self, _):
        from .character_sheet_skills import draw_skills

        draw_skills(self, self.layout.skills)

    def footer(self):
        r = self.layout.footer
        u = self.u
        self.paint.panel(r, CYAN)
        hit = next(
            (
                hit
                for hit in reversed(self.view._modal_hits)
                if self.hover == (hit.action, hit.data) and hit.tooltip
            ),
            None,
        )
        if hit:
            lines = hit.tooltip.split("\n")[:2]
            line_height = scale_font_size(max(13, 12 * u)) * 1.2
            for i, line in enumerate(lines):
                self.label(
                    line,
                    r.left + 12 * u,
                    r.center[1] + (len(lines) - 1) * line_height / 2 - i * line_height,
                    12,
                    GOLD,
                    width=r.width - 24 * u,
                )
        else:
            self.icon("target", r.left + 22 * u, r.center[1], 20)
            self.label(
                self.tr("instruction", points=self.character.pending_points),
                r.left + 43 * u,
                r.center[1],
                13,
                TEXT,
                width=r.width - 195 * u,
            )
            self.label(
                self.tr("talent_short", points=self.character.talent_points),
                r.right - 14 * u,
                r.center[1],
                13,
                GOLD,
                bold=True,
                anchor_x="right",
            )

    def card(self, rect, color, action, data, tooltip="", flash=None):
        hot = self.hover == (action, data)
        changed = flash in self.flash_keys and self.view._elapsed < self.flash_until
        if hot or changed:
            self.paint.glow(
                *rect.center,
                rect.width * 1.08,
                rect.height * 1.15,
                color,
                45 + 20 * self.hover_amount,
            )
        frame = VIOLET if color == VIOLET else GOLD if hot or changed else color
        self.paint.panel(rect, frame, selected=hot or changed)
        self.hit(rect, action, data, tooltip)

    def paragraph(self, text, rect, size=13, color=TEXT, bold=False):
        return self.text(
            text,
            rect.left,
            rect.top,
            scale_font_size(max(12, size * self.u)),
            color,
            bold=bold,
            width=int(rect.width),
            multiline=True,
            anchor_y="top",
            accessibility=False,
        )

    def grid(self, key, rect, count, columns, min_height):
        self.regions[key] = rect
        grid = paged_grid(
            rect, count, columns, min_height, 9 * self.u, self.first_rows[key]
        )
        self.grids[key] = grid
        self.first_rows[key] = grid.first_row
        return grid

    def pager(self, key, panel, grid):
        if not grid.max_first_row:
            return
        u = self.u
        first = grid.first_row * grid.columns + 1
        last = min(
            grid.total_rows * grid.columns,
            (grid.first_row + grid.visible_rows) * grid.columns,
        )
        count = len(self.data.skills) if key == "skills" else len(self.data.talents)
        self.label(
            f"{first}–{min(last,count)}/{count}",
            panel.right - 63 * u,
            panel.top - 23 * u,
            11,
            MUTED,
            anchor_x="right",
        )
        for i, (step, icon) in enumerate([(-1, "previous"), (1, "next")]):
            box = Rect(
                panel.right - (56 - i * 27) * u,
                panel.top - 36 * u,
                panel.right - (32 - i * 27) * u,
                panel.top - 10 * u,
            )
            self.icon(
                icon,
                *box.center,
                18,
                CYAN if 0 <= grid.first_row + step <= grid.max_first_row else LOCKED,
            )
            self.hit(box, "sheet_page", (key, step), self.tr("scroll"))
        rail = Rect(
            panel.right - 6 * u,
            self.regions[key].bottom,
            panel.right - 3 * u,
            self.regions[key].top,
        )
        thumb = rail.height * grid.visible_rows / max(1, grid.total_rows)
        top = rail.top - grid.first_row / grid.max_first_row * (rail.height - thumb)
        arcade.draw_lrbt_rectangle_filled(
            rail.left, rail.right, rail.bottom, rail.top, (16, 38, 48, 255)
        )
        arcade.draw_lrbt_rectangle_filled(rail.left, rail.right, top - thumb, top, CYAN)

    def scroll(self, key, step):
        grid = self.grids.get(key)
        if grid:
            self.first_rows[key] = max(
                0, min(grid.max_first_row, self.first_rows[key] + int(step))
            )

    def mouse_motion(self, x, y):
        self.hover = None
        for key, rect in self.regions.items():
            if key in ("skills", "talents") and rect.contains(x, y):
                self.scroll_target = key
        for hit in reversed(self.view._modal_hits):
            if hit.contains(x, y):
                self.hover = (hit.action, hit.data)
                break

    def mouse_scroll(self, x, y, scroll_y):
        for key in ("skills", "talents"):
            if key in self.regions and self.regions[key].contains(x, y):
                self.scroll(key, -scroll_y)
                break

    def tooltip(self, w, h):
        pass  # The reserved instruction strip already draws the active detail.
