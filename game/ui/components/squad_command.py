"""Live Squad Command presentation; all mutations route through ManagementView."""

import arcade
from game.i18n import t
from game.ui.layouts.world_map_beacons import Rect
from game.ui.layouts.squad_command import squad_command_layout
from game.ui.theme.typography import scale_font_size, get_text_size

from .squad_style import CYAN, GOLD, MINT, RED, TEXT, MUTED


from .visual_kit import VisualKit, UIHit as SquadHit


class SquadCommandRenderer(VisualKit):
    def __init__(self):
        super().__init__()
        self.roster_first = 0
        self.roster_capacity = 5
        self._last_notice = None
        self._notice_text = ""
        self._notice_until = 0.0

    def tr(self, key, **kwargs):
        return t("squad." + key, self.gs.ui_language, **kwargs)

    def draw(self, view, w, h):
        self.view = view
        self.gs = view.game_state
        latest = view.notifications.latest_text_lines(1)
        notice = latest[0] if latest else None
        if notice != self._last_notice:
            from .squad_copy import notification_summary

            self._last_notice = notice
            self._notice_text = notification_summary(notice) if notice else ""
            self._notice_until = view._elapsed + 4.0
        self.layout = squad_command_layout(w, h)
        self.u = self.layout.scale
        if self._text_batch is None and hasattr(view.window, "ctx"):
            from pyglet.graphics import Batch

            self._text_batch = Batch()
        self._frame_texts = set()
        if hasattr(self.paint, "clear_text_cache") and len(self.paint._texts) > 300:
            self.paint.clear_text_cache()
            self._previous_texts = set()
        if self._size != (w, h):
            self.paint.resize()
            self._tiles.clear()
            self._previous_texts = set()
            if self._scan_mesh is not None:
                self._scan_mesh.clear()
            for mesh in self._meter_meshes.values():
                mesh.clear()
            self._meter_meshes.clear()
            if hasattr(self.paint, "_mesh"):
                polygon, line, outline, finish = self.paint._mesh()
                for y in range(0, h, 6):
                    line((0, y), (w, y), (5, 19, 28, 35), 1)
                self._scan_mesh = finish()
            self._size = (w, h)
        view._hits = []
        self.regions = {}
        self.text_bounds = []
        self.image(
            "assets/missions/backgrounds/city/city_01_neon_alley.jpg", Rect(0, 0, w, h)
        )
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (1, 8, 14, 175))
        # A restrained scan pattern and neon dividers keep the game art visible.
        if self._scan_mesh is not None:
            self._scan_mesh.draw()
        else:
            for y in range(0, h, 6):
                arcade.draw_line(0, y, w, y, (5, 19, 28, 35), 1)
        self.header()
        self.agents(self.layout.roster)
        self.equipment(self.layout.equipment)
        self.mission(self.layout.mission)
        self.footer()
        self.tooltip(w, h)
        if self._text_batch is not None:
            cached = set(self.paint._texts.values())
            for label in (self._previous_texts - self._frame_texts) & cached:
                label.visible = False
            for label in self._frame_texts - self._previous_texts:
                label.visible = True
            self._previous_texts = self._frame_texts
            self._text_batch.draw()

    def header(self):
        r = self.layout.header
        w = self.layout.width
        arcade.draw_lrbt_rectangle_filled(0, w, r.bottom, r.top, (1, 11, 17, 220))
        arcade.draw_line(15, r.bottom, w - 15, r.bottom, (*CYAN, 140), 1.5)
        self.icon("city", 38 * self.u, r.center[1], 38)
        brand = self.label(
            "CYBERCITY", 67 * self.u, r.center[1], 33, bold=True, color=TEXT
        )
        self.label(
            "2085",
            67 * self.u + brand.content_width + 10 * self.u,
            r.center[1],
            33,
            bold=True,
            color=GOLD,
        )
        values = [
            ("funds", self.gs.available_funds, "credits"),
            ("credits", self.gs.strategic_resources.get("credits", 0), "research"),
            ("intel", self.gs.strategic_resources.get("intel", 0), "intel"),
            ("salvage", self.gs.strategic_resources.get("salvage", 0), "settings"),
            ("influence", self.gs.strategic_resources.get("influence", 0), "nodes"),
        ]
        left = w * 0.36
        right = w - 125 * self.u
        cell = (right - left) / len(values)
        for i, (key, value, icon) in enumerate(values):
            x = left + i * cell
            self.icon(icon, x + 13 * self.u, r.center[1], 25, GOLD if i == 0 else CYAN)
            self.label(
                self.tr(key),
                x + 36 * self.u,
                r.center[1] + 14 * self.u,
                12,
                bold=True,
                width=cell - 42 * self.u,
            )
            self.label(
                f"{value:,}",
                x + 36 * self.u,
                r.center[1] - 12 * self.u,
                22,
                bold=True,
                width=cell - 42 * self.u,
            )
            if i:
                arcade.draw_line(
                    x - 8 * self.u,
                    r.bottom + 12 * self.u,
                    x - 8 * self.u,
                    r.top - 12 * self.u,
                    (*CYAN, 90),
                    1,
                )
        for i, (icon, action, color) in enumerate(
            [("settings", "squad_settings", CYAN), ("close", "squad_close", RED)]
        ):
            x = w - (110 - i * 57) * self.u
            rect = Rect(
                x, r.center[1] - 22 * self.u, x + 45 * self.u, r.center[1] + 22 * self.u
            )
            self.paint.panel(rect, color)
            if icon == "close":
                for sign in [-1, 1]:
                    arcade.draw_line(
                        rect.center[0] - 10 * self.u,
                        rect.center[1] - sign * 10 * self.u,
                        rect.center[0] + 10 * self.u,
                        rect.center[1] + sign * 10 * self.u,
                        color,
                        2,
                    )
            else:
                self.icon(icon, *rect.center, 27, color)
            self.hit(rect, action, tooltip=self.tr("settings" if i == 0 else "close"))

    def agents(self, r):
        from .squad_agents import draw_agents

        draw_agents(self, r)

    def equipment(self, r):
        from .squad_equipment import draw_equipment

        draw_equipment(self, r)

    def mission(self, r):
        from .squad_mission import draw_mission

        draw_mission(self, r)

    def footer(self):
        u = self.u
        r = self.layout.footer
        w = self.layout.width
        arcade.draw_lrbt_rectangle_filled(0, w, 0, r.top, (0, 9, 16, 240))
        arcade.draw_line(18 * u, r.top, w - 18 * u, r.top, (*CYAN, 150), 1.5)
        specs = [
            ("next_step", "right", CYAN),
            ("recruit_prompt", "recruit", CYAN),
            ("remove_agent", "black_ops", RED),
            ("agent_prev", "left", CYAN),
            ("select_agent", "squad", CYAN),
            ("agent_next", "right", CYAN),
            ("slot_prev", "left", CYAN),
            ("slot_next", "right", CYAN),
            ("save", "save", CYAN),
            ("load", "load", CYAN),
        ]
        gap = 8 * u
        margin = 20 * u
        bw = (w - 2 * margin - gap * (len(specs) - 1)) / len(specs)
        top = r.top - 25 * u
        bottom = max(27, 20 * u)
        for i, (action, icon, color) in enumerate(specs):
            rect = Rect(
                margin + i * (bw + gap), bottom, margin + i * (bw + gap) + bw, top
            )
            hot = self.hover == ("squad_nav", action)
            self.paint.panel(rect, color, selected=hot)
            compact_large = get_text_size() == "large" and w < 1400
            if compact_large:
                self.icon(icon, *rect.center, 33, (*color, 28))
            else:
                self.icon(icon, rect.left + 16 * u, rect.center[1], 22, color)
            caption = self.tr("nav." + action)
            words = caption.split("|")
            line_height = scale_font_size(max(13, 11 * u)) * 1.7
            for j, line in enumerate(words):
                self.label(
                    line,
                    (rect.center[0] if compact_large else rect.left + 34 * u),
                    rect.center[1]
                    + (len(words) - 1) * line_height / 2
                    - j * line_height,
                    11,
                    TEXT,
                    bold=True,
                    width=rect.width - (10 if compact_large else 38) * u,
                    anchor_x="center" if compact_large else "left",
                )
            self.hit(rect, "squad_nav", action, caption.replace("|", " "))
        self.label(
            self.tr(
                "day_slot",
                day=self.gs.calendar.current_day,
                slot=self.view.selected_save_slot,
            ),
            20 * u,
            r.top - 12 * u,
            11,
            MUTED,
        )
        self.label(
            "F1–F6 · "
            + self.tr("rooms")
            + "   /   < > · "
            + self.tr("agents")
            + "   /   "
            + self.tr("space_toggle"),
            w - 20 * u,
            r.top - 12 * u,
            11,
            MUTED,
            anchor_x="right",
        )
        feedback = (
            self._notice_text
            if self.view._elapsed < self._notice_until
            else self.view.message
        )
        if feedback:
            self.label(
                feedback,
                w / 2,
                max(11, 9 * u),
                11,
                GOLD,
                width=w - 30 * u,
                anchor_x="center",
            )

    def tooltip(self, w, h):
        if not self.hover:
            return
        hit = next(
            (
                hit
                for hit in reversed(self.view._hits)
                if (hit.action, hit.data) == self.hover and hit.tooltip
            ),
            None,
        )
        if hit is None:
            return
        # Full names and tactical details remain accessible even after ellipsis.
        content = hit.tooltip.replace("\n", "  /  ")
        self.label(
            content,
            w / 2,
            self.layout.footer.top + max(11, 11 * self.u),
            11,
            GOLD,
            width=w - 40 * self.u,
            anchor_x="center",
        )
