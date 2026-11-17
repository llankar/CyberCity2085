"""Live Headquarters overview: cached chrome over distinct interactive departments."""

import arcade
from game.i18n import t
from game.ui.layouts.headquarters import (
    headquarters_layout,
    ROOMS,
    HQ_ART,
    HQ_ART_SIZE,
    headquarters_target_at,
)
from game.ui.layouts.world_map_beacons import Rect
from game.ui.facility import BASE_BACKDROP_ASSET
from game.ui.panels import _load_texture_once
from game.ui.theme.typography import scale_font_size, get_text_size
from .squad_command import SquadCommandRenderer
from .squad_style import CYAN, GOLD, TEXT, MUTED
from .headquarters_ambient import HeadquartersAmbient


class HeadquartersRenderer(SquadCommandRenderer):
    def __init__(self):
        super().__init__()
        self.loaded = False
        self.background = None
        self.legacy = False
        self.frames = {}
        self.amounts = {key: 0.0 for key, _, _ in ROOMS}
        self.hover_key = None
        self.ambient = HeadquartersAmbient()
        self.room_textures = {}
        self.wordmark = None

    def load(self):
        if self.loaded:
            return
        self.background = _load_texture_once(HQ_ART)
        if self.background is None:
            self.legacy = True
            self.background = _load_texture_once(BASE_BACKDROP_ASSET)
        self.loaded = True

    def update(self, dt, reduced=False):
        for key, value in self.amounts.items():
            target = 1.0 if key == self.hover_key else 0.0
            self.amounts[key] = (
                target if reduced else value + (target - value) * min(1, dt * 12)
            )

    def motion(self, x, y, w, h):
        self.hover_key = headquarters_target_at(
            w, h, x, y, self.legacy, 1.3 if get_text_size() == "large" else 1.0
        )

    def preview(self, key):
        self.load()
        if self.background is None:
            return None
        if key not in self.room_textures:
            layout = headquarters_layout(*HQ_ART_SIZE, self.legacy)
            r = layout.rooms[
                next(i for i, (name, _, _) in enumerate(ROOMS) if name == key)
            ]
            sx, sy = (
                self.background.width / HQ_ART_SIZE[0],
                self.background.height / HQ_ART_SIZE[1],
            )
            self.room_textures[key] = self.background.crop(
                int(r.left * sx),
                int((HQ_ART_SIZE[1] - r.top) * sy),
                int(r.width * sx),
                int(r.height * sy),
            )
        return self.room_textures[key]

    def draw(self, view, w, h):
        self.load()
        self.view, self.gs = view, view.game_state
        self.layout = headquarters_layout(
            w, h, self.legacy, 1.3 if get_text_size() == "large" else 1.0
        )
        self.u = self.layout.scale
        if self._text_batch is None and hasattr(view.window, "ctx"):
            from pyglet.graphics import Batch

            self._text_batch = Batch()
        if self._size != (w, h):
            self.paint.resize()
            self._previous_texts = set()
            self._size = (w, h)
            for mesh in self.frames.values():
                mesh.clear()
            self.frames.clear()
        if len(self.paint._texts) > 250:
            self.paint.clear_text_cache()
            self._previous_texts = set()
        self._frame_texts = set()
        self.text_bounds = []
        view._hits = []
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (2, 9, 17))
        if self.background:
            self.texture(self.background, self.layout.art, cover=False)
        else:
            self.procedural_rooms()
        reduced = getattr(view, "_hq_reduced_motion", False)
        if hasattr(self.paint, "_mesh"):
            self.ambient.draw(self, view._elapsed, reduced)
        for i, (key, title, icon) in enumerate(ROOMS):
            self.room(i, key, title, icon)
        self.hud()
        self.navigation()
        self.notice()
        if self._text_batch is not None:
            cached = set(self.paint._texts.values())
            for label in (self._previous_texts - self._frame_texts) & cached:
                label.visible = False
            for label in self._frame_texts - self._previous_texts:
                label.visible = True
            self._previous_texts = set(self._frame_texts)
            self._text_batch.draw()

    def outline(self, r, color, selected=False, amount=0):
        if not hasattr(self.paint, "_mesh"):
            arcade.draw_lrbt_rectangle_outline(
                r.left, r.right, r.bottom, r.top, color, 2
            )
            return
        step = round(amount * 6)
        key = (r.width, r.height, color, selected, step, self.u)
        mesh = self.frames.get(key)
        if mesh is None:
            polygon, line, outline, finish = self.paint._mesh()
            w, h = r.width, r.height
            b = 24 * self.u
            points = [
                (0, b),
                (b, 0),
                (w - b, 0),
                (w, b),
                (w, h - b),
                (w - b, h),
                (b, h),
                (0, h - b),
            ]
            outline(
                [(x + 3 * self.u, y - 4 * self.u) for x, y in points],
                (0, 3, 8, 200),
                11 * self.u,
            )
            for width, alpha in (
                ((10, 16), (5, 45), (2, 245))
                if selected
                else ((5, 12), (2, 90), (1, 170))
            ):
                outline(points, (*color, min(255, alpha + step * 5)), width * self.u)
            inset = 7 * self.u
            line((b, h - inset), (w - b, h - inset), (*color, 100), self.u)
            line((b, inset), (w - b, inset), (*color, 85), self.u)
            mesh = finish()
            self.frames[key] = mesh
        mesh.center_x, mesh.center_y = r.left, r.bottom
        mesh.draw()

    def room(self, i, key, title, icon):
        u = self.u
        r = self.layout.rooms[i]
        focus = (
            self.hover_key
            if self.hover_key in self.amounts
            else getattr(self.view, "_hq_last_room", "command")
        )
        selected = key == focus
        hot = key == self.hover_key
        amount = self.amounts[key]
        color = CYAN
        if selected or hot:
            self.paint.glow(
                *r.center, r.width * 1.10, r.height * 1.15, CYAN, 12 + amount * 25
            )
        self.outline(r, color, selected or hot, amount)
        # Category accents remain thin; the base is predominantly cyan, not amber/red.
        accent = (
            (202, 118, 255)
            if key in ("research", "intel")
            else GOLD if key == "assets" else CYAN
        )
        arcade.draw_line(
            r.left + 28 * u,
            r.top - 3 * u,
            r.left + 62 * u,
            r.top - 3 * u,
            (*accent, 150),
            2 * u,
        )
        rail = self.layout.labels[i]
        self.paint.panel(rail, CYAN, selected=selected or hot)
        badge = Rect(
            rail.left + 7 * u, rail.bottom + 5 * u, rail.left + 49 * u, rail.top - 5 * u
        )
        self.paint.panel(badge, CYAN)
        self.label(f"F{i+1}", *badge.center, 19, CYAN, bold=True, anchor_x="center")
        self.label(
            title,
            rail.left + 60 * u,
            rail.center[1],
            21,
            TEXT,
            bold=True,
            width=rail.width - 74 * u,
        )
        if selected or hot:
            self.icon("next", r.right - 29 * u, r.bottom + 23 * u, 30, CYAN)
        self.hit(r, "hq_room", key)

    def hud(self):
        u = self.u
        l = self.layout
        arcade.draw_lrbt_rectangle_filled(
            0, l.width, l.header.bottom, l.height, (1, 9, 17, 238)
        )
        arcade.draw_line(
            0, l.header.bottom, l.width, l.header.bottom, (*CYAN, 130), 1.5 * u
        )
        # Header identity uses the existing title wordmark as an independent logo asset.
        logo = Rect(28 * u, l.header.bottom + 18 * u, 288 * u, l.height - 12 * u)
        if self.wordmark is None:
            texture = _load_texture_once("assets/ui/title/wordmark.png")
            if texture is not None:
                box = (
                    texture.image.getchannel("A")
                    .point(lambda a: 255 if a > 192 else 0)
                    .getbbox()
                )
                self.wordmark = (
                    texture.crop(box[0], box[1], box[2] - box[0], box[3] - box[1])
                    if box
                    else texture
                )
        if self.wordmark:
            self.texture(self.wordmark, logo, cover=False)
        else:
            self.label(
                "CYBERCITY 2085",
                *logo.center,
                23,
                TEXT,
                bold=True,
                anchor_x="center",
                width=logo.width,
            )
        caption = t("hq.title", self.gs.ui_language)
        pitch = max(26 * u, scale_font_size(13) * 1.6)
        self.label(
            caption,
            312 * u,
            l.header.center[1] + pitch / 2,
            21,
            CYAN,
            bold=True,
            width=l.width * 0.40 - 330 * u,
        )
        self.label(
            t("hq.subtitle", self.gs.ui_language),
            312 * u,
            l.header.center[1] - pitch / 2,
            13,
            MUTED,
            width=l.width * 0.40 - 330 * u,
        )
        values = [
            ("funds", self.gs.available_funds, "credits"),
            ("credits", self.gs.strategic_resources.get("credits", 0), "research"),
            ("intel", self.gs.strategic_resources.get("intel", 0), "intel"),
            ("salvage", self.gs.strategic_resources.get("salvage", 0), "settings"),
            ("influence", self.gs.strategic_resources.get("influence", 0), "nodes"),
        ]
        for r, (key, value, icon) in zip(l.resources, values):
            self.paint.panel(r, CYAN)
            title_h = scale_font_size(max(13, 13 * u)) * 1.4
            number_h = scale_font_size(max(13, 23 * u)) * 1.4
            self.icon(icon, r.left + 18 * u, r.bottom + number_h / 2 + 3 * u, 24, CYAN)
            self.label(
                t("squad." + key, self.gs.ui_language),
                r.center[0],
                r.top - title_h / 2 - 3 * u,
                13,
                TEXT,
                bold=True,
                width=r.width - 12 * u,
                anchor_x="center",
            )
            self.label(
                ("¥ " if key == "funds" else "") + f"{value:,}",
                r.left + 40 * u,
                r.bottom + number_h / 2 + 3 * u,
                23,
                CYAN,
                bold=True,
                width=r.width - 48 * u,
            )

    def navigation(self):
        u = self.u
        l = self.layout
        self.paint.panel(l.footer, CYAN)
        for i, r in enumerate(l.navigation):
            key, title, _ = (
                ROOMS[i]
                if i < 6
                else ("close", t("hq.close", self.gs.ui_language), "close")
            )
            hot = key == self.hover_key
            if hot:
                self.paint.panel(r, CYAN, selected=True)
            badge = Rect(
                r.left + 4 * u,
                r.bottom + 7 * u,
                r.left + (56 if i == 6 else 45) * u,
                r.top - 7 * u,
            )
            self.paint.panel(badge, CYAN)
            self.label(
                f"F{i+1}" if i < 6 else "ESC",
                *badge.center,
                18,
                CYAN,
                bold=True,
                anchor_x="center",
            )
            name = title if i != 0 else "COMMAND"
            text_left = badge.right + 10 * u
            width = r.right - text_left - 7 * u
            font = scale_font_size(max(13, 15 * u))
            lines = (
                name.split(" ")
                if self.paint.fit(name, width, font, True) != name
                else [name]
            )
            step = font * 1.3
            for line_index, line in enumerate(lines):
                self.label(
                    line,
                    text_left,
                    r.center[1] + (len(lines) - 1) * step / 2 - line_index * step,
                    15,
                    TEXT,
                    bold=True,
                    width=width,
                )
            if i < 6:
                arcade.draw_line(
                    r.right, r.bottom + 10 * u, r.right, r.top - 10 * u, (*CYAN, 100), u
                )
            self.hit(r, "hq_close" if i == 6 else "hq_room", key)

    def notice(self):
        from .squad_copy import notification_summary

        lines = self.view.notifications.latest_text_lines(1)
        raw = self.view.message or (lines[0] if lines else "")
        if raw != self._last_notice:
            self._last_notice = raw
            self._notice_until = self.view._elapsed + 4
        if not raw or self.view._elapsed > self._notice_until:
            return
        text = notification_summary(raw)
        if "Campaign saved to " in text:
            text = t("hq.saved", self.gs.ui_language)
        elif "Campaign loaded from " in text:
            text = t("hq.loaded", self.gs.ui_language)
        r = self.layout.footer
        u = self.u
        notice = Rect(
            self.layout.width * 0.25,
            r.top + 8 * u,
            self.layout.width * 0.75,
            r.top + 48 * u,
        )
        self.paint.panel(notice, CYAN)
        self.label(
            text,
            *notice.center,
            14,
            TEXT,
            anchor_x="center",
            width=notice.width - 22 * u,
        )

    def procedural_rooms(self):
        for i, r in enumerate(self.layout.rooms):
            arcade.draw_lrbt_rectangle_filled(
                r.left, r.right, r.bottom, r.top, (5, 22, 33)
            )
            self.icon(ROOMS[i][2], *r.center, 52, CYAN)
