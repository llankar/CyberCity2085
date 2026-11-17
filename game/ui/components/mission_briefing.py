"""Holographic briefing orchestrator, reusing cached Squad Command primitives."""

import arcade
from game.i18n import t
from game.agent_readiness import estimate_mission_stress, projected_stress
from game.deployment import selected_deployable_agents
from game.ui.layouts.world_map_beacons import Rect
from game.ui.layouts.mission_briefing import briefing_layout
from .character_sheet import CharacterSheetRenderer
from .briefing_content import briefing_lines
from .briefing_widgets import scroll_text, scroll_card
from .squad_style import CYAN, GOLD, MINT, RED, TEXT, MUTED

VIOLET = (203, 130, 255)


class MissionBriefingRenderer(CharacterSheetRenderer):
    """Only presentation state lives here; launch remains owned by the view."""

    def __init__(self):
        super().__init__()
        self.offsets = {}
        self.scroll_regions = {}
        self.visible_lines = {}
        self.focus = "complications"
        self.map_open = False

    def icon(self, key, x, y, size=24, color=CYAN):
        radius = size * self.u / 2
        stroke = max(1.5, 2 * self.u)
        if key == "warning":
            arcade.draw_polygon_outline(
                [
                    (x - radius, y - radius * 0.75),
                    (x + radius, y - radius * 0.75),
                    (x, y + radius),
                ],
                color,
                stroke,
            )
            arcade.draw_line(
                x, y - radius * 0.18, x, y + radius * 0.48, color, stroke * 1.4
            )
            arcade.draw_circle_filled(x, y - radius * 0.43, stroke, color)
        elif key in ("clock", "abort"):
            arcade.draw_circle_outline(x, y, radius * 0.85, color, stroke)
            if key == "clock":
                arcade.draw_line(x, y, x, y + radius * 0.55, color, stroke)
                arcade.draw_line(
                    x, y, x + radius * 0.42, y - radius * 0.12, color, stroke
                )
            else:
                d = radius * 0.4
                arcade.draw_line(x - d, y - d, x + d, y + d, color, stroke)
                arcade.draw_line(x - d, y + d, x + d, y - d, color, stroke)
        else:
            super().icon(key, x, y, size, color)

    def tr(self, key, **kwargs):
        return t("briefing." + key, self.gs.ui_language, **kwargs)

    # Use management's reusable hit representation, not dossier modal hits.
    def hit(self, rect, action, data=None, tooltip=""):
        from .squad_command import SquadCommandRenderer

        SquadCommandRenderer.hit(self, rect, action, data, tooltip)

    def draw(self, view, w, h):
        from game.ui.screens.mission_briefing_view import selected_support_assets

        self.view, self.gs, self.mission = view, view.game_state, view.mission
        self.layout = briefing_layout(w, h)
        self.u = self.layout.scale
        if self._text_batch is None:
            from pyglet.graphics import Batch

            self._text_batch = Batch()
        if self._size != (w, h):
            self.paint.resize()
            self._previous_texts = set()
            self._tiles.clear()
            self._size = (w, h)
        if len(self.paint._texts) > 300:
            self.paint.clear_text_cache()
            self._previous_texts = set()
        self._frame_texts = set()
        self.text_bounds = []
        view._hits = []
        self.scroll_regions = {}
        self.visible_lines = {}
        # Map matching is already resolved by _load_assets; no I/O or campaign writes here.
        self.facts = view._facts
        self.agents = selected_deployable_agents(
            self.gs.characters, self.gs.selected_agent_names
        )
        self.assets = selected_support_assets(self.gs)
        self.lines = briefing_lines(self.gs, self.mission, self.facts)
        self.art = view._scene_art
        self.image(self.art, Rect(0, 0, w, h))
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (1, 8, 14, 190))
        self.header()
        from .briefing_scene import draw_scene
        from .briefing_squad import draw_squad, draw_support

        draw_scene(self, self.layout.scene)
        self.metrics()
        draw_squad(self, self.layout.squad)
        draw_support(self, self.layout.support)
        scroll_card(
            self,
            "success",
            self.layout.success,
            self.tr("success"),
            self.lines["success"],
            MINT,
            "next",
        )
        scroll_card(
            self,
            "failure",
            self.layout.failure,
            self.tr("failure"),
            self.lines["failure"],
            RED,
            "delete",
        )
        self.footer()
        if self.map_open:
            # Flush before drawing the modal so background labels cannot bleed through it.
            self.finish_text()
            self._frame_texts = set()
            self.map_modal()
        self.finish_text()

    def finish_text(self):
        cached = set(self.paint._texts.values())
        for label in (self._previous_texts - self._frame_texts) & cached:
            label.visible = False
        for label in self._frame_texts - self._previous_texts:
            label.visible = True
        self._previous_texts = set(self._frame_texts)
        self._text_batch.draw()

    def header(self):
        u = self.u
        r = self.layout.header
        self.icon("city", r.left + 30 * u, r.center[1], 45)
        brand = self.label(
            "CYBERCITY", r.left + 66 * u, r.center[1], 31, CYAN, bold=True
        )
        year_x = r.left + 78 * u + brand.content_width
        year = self.label("2085", year_x, r.center[1], 31, GOLD, bold=True)
        caption_x = year_x + year.content_width + 24 * u
        self.label(
            "// " + self.tr("title"),
            caption_x,
            r.center[1],
            20,
            TEXT,
            width=self.layout.width * 0.54 - caption_x,
        )
        self.label(
            self.mission.district.upper()
            + "  //  "
            + self.mission.target_faction.upper(),
            r.right - 12 * u,
            r.center[1],
            17,
            TEXT,
            anchor_x="right",
            width=r.width * 0.39,
        )
        r = self.layout.banner
        self.paint.panel(r, CYAN)
        self.icon("next", r.left + 32 * u, r.center[1], 44, GOLD)
        self.label(
            self.mission.title.upper(),
            r.left + 66 * u,
            r.center[1],
            39,
            TEXT,
            bold=True,
            width=r.width - 285 * u,
        )
        day = Rect(
            r.right - 210 * u, r.bottom + 13 * u, r.right - 20 * u, r.top - 13 * u
        )
        self.paint.panel(day, GOLD, selected=True)
        self.label(
            self.tr("day", day=self.gs.calendar.current_day),
            *day.center,
            26,
            GOLD,
            bold=True,
            anchor_x="center",
            width=day.width - 20 * u,
        )

    def metric(self, rect, title, value, icon, color, fraction=None):
        u = self.u
        self.paint.glow(*rect.center, rect.width * 1.08, rect.height * 1.12, color, 35)
        self.paint.panel(rect, color, selected=True)
        self.icon(icon, rect.left + 37 * u, rect.center[1], 43, color)
        self.label(
            title,
            rect.left + 73 * u,
            rect.top - 22 * u,
            17,
            TEXT,
            width=rect.width - 84 * u,
        )
        self.label(
            value,
            rect.left + 73 * u,
            rect.bottom + 37 * u,
            31,
            color,
            bold=True,
            width=rect.width - 85 * u,
        )
        if fraction is not None:
            self.meter(
                Rect(
                    rect.right - rect.width * 0.43,
                    rect.bottom + 5 * u,
                    rect.right - 13 * u,
                    rect.bottom + 9 * u,
                ),
                fraction,
                color,
                10,
            )

    def metrics(self):
        l = self.layout
        risk = self.mission.risk_level
        color = RED if risk > 6 else GOLD if risk > 3 else MINT
        self.metric(l.risk, self.tr("risk"), f"{risk}/10", "warning", color, risk / 10)
        # Half-width metrics place labels above the value without a large icon gutter.
        cost = sum(max(0, int(a.deploy_cost)) for a in self.assets)
        for rect, key, value, icon, color in [
            (
                l.duration,
                "duration",
                self.tr("days", n=self.mission.duration_days),
                "clock",
                CYAN,
            ),
            (l.reward, "net", f"{self.mission.fund_reward-cost:+,}", "coins", MINT),
        ]:
            self.paint.panel(rect, color)
            if key != "net":
                self.icon(
                    icon, rect.left + 22 * self.u, rect.top - 22 * self.u, 24, color
                )
            self.label(
                self.tr(key),
                rect.center[0] if key == "net" else rect.left + 43 * self.u,
                rect.top - 22 * self.u,
                15,
                TEXT,
                width=rect.width - (16 if key == "net" else 50) * self.u,
                anchor_x="center" if key == "net" else "left",
            )
            self.label(
                value,
                rect.center[0],
                rect.bottom + 24 * self.u,
                23,
                color,
                bold=True,
                width=rect.width - 16 * self.u,
                anchor_x="center",
            )
            self.hit(
                rect,
                "info",
                key,
                (
                    self.tr("fund_breakdown", gross=self.mission.fund_reward, cost=cost)
                    if key == "net"
                    else value
                ),
            )
        projected = [projected_stress(a, self.mission) for a in self.agents]
        band = f"{min(projected)}–{max(projected)}" if projected else "—"
        self.metric(
            l.stress,
            self.tr("projected"),
            band,
            "brain",
            GOLD,
            (max(projected) / 100 if projected else 0),
        )
        self.hit(
            l.stress,
            "info",
            "stress",
            self.tr("pressure_add", n=estimate_mission_stress(self.mission)),
        )
        scroll_card(
            self,
            "complications",
            l.complications,
            self.tr("complications"),
            self.lines["complications"],
            GOLD,
            "warning",
        )
        # Subdued scene texture gives the human-impact panel the reference's violet atmosphere.
        scroll_card(
            self,
            "impact",
            l.impact,
            self.tr("impact"),
            self.lines["impact"],
            VIOLET,
            "squad",
        )

    def footer(self):
        self.button(
            self.layout.abort,
            self.tr("abort") + "  [ESC]",
            "abort",
            color=RED,
            icon="abort",
            primary=True,
        )
        self.button(
            self.layout.deploy,
            self.tr("deploy") + "  [ENTER]",
            "deploy",
            color=MINT,
            icon="next",
            primary=True,
        )
        self.view._abort_rect = (
            self.layout.abort.left,
            self.layout.abort.bottom,
            self.layout.abort.right,
            self.layout.abort.top,
        )
        self.view._deploy_rect = (
            self.layout.deploy.left,
            self.layout.deploy.bottom,
            self.layout.deploy.right,
            self.layout.deploy.top,
        )
        # Hover explanations remain inside a reserved footer rail.
        hit = next(
            (h for h in self.view._hits if (h.action, h.data) == self.hover), None
        )
        if hit and hit.tooltip and hit.action == "info":
            self.label(
                hit.tooltip,
                self.layout.width / 2,
                106 * self.u,
                13,
                CYAN,
                anchor_x="center",
                width=self.layout.width * 0.85,
            )

    def scroll_text(self, *args, **kw):
        return scroll_text(self, *args, **kw)

    def pager(self, key, r, first, maximum):
        u = self.u
        for step in (-1, 1):
            x = r.right - (53 if step < 0 else 24) * u
            rect = Rect(x - 12 * u, r.top - 33 * u, x + 12 * u, r.top - 8 * u)
            self.icon("previous" if step < 0 else "next", *rect.center, 20, CYAN)
            self.hit(rect, "scroll", (key, step))
        self.scroll_regions.setdefault(key, (r, maximum))

    def scroll(self, key, step):
        if key in self.scroll_regions:
            maximum = self.scroll_regions[key][1]
            self.offsets[key] = max(0, min(maximum, self.offsets.get(key, 0) + step))

    def motion(self, x, y):
        self.hover = None
        for key, (rect, _) in self.scroll_regions.items():
            if rect.contains(x, y):
                self.focus = key
        for hit in reversed(self.view._hits):
            if hit.contains(x, y):
                self.hover = (hit.action, hit.data)
                break

    def map_modal(self):
        u = self.u
        w, h = self.layout.width, self.layout.height
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (0, 5, 10, 245))
        r = Rect(35 * u, 35 * u, w - 35 * u, h - 35 * u)
        self.paint.panel(r, CYAN, selected=True)
        self.label(
            self.tr("tactical") + " // " + self.tr("close_map"),
            r.left + 25 * u,
            r.top - 26 * u,
            22,
            CYAN,
            bold=True,
            width=r.width - 45 * u,
        )
        image = Rect(
            r.left + 20 * u, r.bottom + 20 * u, r.right - 20 * u, r.top - 60 * u
        )
        if self.view._map_texture:
            self.texture(self.view._map_texture, image, cover=False)
        else:
            self.label(self.tr("no_map"), *image.center, 22, MUTED, anchor_x="center")
        self.view._hits = []
        self.hit(r, "close_map")
