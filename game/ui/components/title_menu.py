"""Cinematic title chrome and real menu controls using shared cached UI primitives."""

import arcade
import math
from math import sin
from game.ui.layouts.world_map_beacons import Rect
from game.ui.layouts.title_menu import title_layout
from game.ui.panels import _load_texture_once
from game.ui.theme.typography import scale_font_size
from game.version import build_label
from .squad_command import SquadCommandRenderer
from .squad_style import CYAN, GOLD, TEXT, MUTED
from .title_atmosphere import TitleAtmosphere


class TitleMenuRenderer(SquadCommandRenderer):
    def __init__(self):
        super().__init__()
        self.atmosphere = TitleAtmosphere()
        self._chrome = {}
        self.wordmark = None
        self.wordmark_loaded = False

    def draw(self, view, w, h):
        self.view = view
        self.layout = title_layout(w, h)
        self.u = self.layout.scale
        if self._text_batch is None:
            from pyglet.graphics import Batch

            self._text_batch = Batch()
        if self._size != (w, h):
            self.paint.resize()
            self._previous_texts = set()
            self._size = (w, h)
            self._tiles.clear()
            for mesh in self._chrome.values():
                mesh.clear()
            self._chrome.clear()
        if len(self.paint._texts) > 250:
            self.paint.clear_text_cache()
            self._previous_texts = set()
        self._frame_texts = set()
        self.text_bounds = []
        self.background(w, h)
        self.atmosphere.draw(self, w, h, view._elapsed, view._reduced_motion)
        self.logo()
        for i, (rect, (label, key)) in enumerate(
            zip(self.layout.buttons, view.menu_items)
        ):
            self.menu_button(rect, label, key, i)
        self.footer()
        if view._message:
            r = self.layout.notice
            arcade.draw_lrbt_rectangle_filled(
                r.left, r.right, r.bottom, r.top, (1, 8, 14, 225)
            )
            self.label(
                view._message,
                *r.center,
                14,
                GOLD,
                width=r.width - 12 * self.u,
                anchor_x="center"
            )
        cached = set(self.paint._texts.values())
        for label in (self._previous_texts - self._frame_texts) & cached:
            label.visible = False
        for label in self._frame_texts - self._previous_texts:
            label.visible = True
        self._previous_texts = set(self._frame_texts)
        self._text_batch.draw()

    def background(self, w, h):
        texture = self.view._background_texture
        if texture:
            self.texture(texture, Rect(0, 0, w, h))
        else:
            arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (2, 9, 17))
            # Final fallback still has a skyline; missing art never hides the menu.
            for i in range(22):
                x = i * w / 21
                top = h * (0.25 + (i * 17 % 13) / 30)
                arcade.draw_lrbt_rectangle_filled(x, x + w / 32, 0, top, (7, 22, 32))
                arcade.draw_line(x + 3, top - 15, x + 3, top - 50, (42, 121, 140), 2)

    def frame(self, r, color, active=False, bevel=22):
        key = (r.width, r.height, color, active, bevel, self.u)
        mesh = self._chrome.get(key)
        if mesh is None:
            polygon, line, outline, finish = self.paint._mesh()
            w, h = r.width, r.height
            b = min(bevel * self.u, h * 0.32)
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
            polygon(points, (1, 12, 19, 235))
            for width, alpha in (
                ((10, 12), (5, 40), (2, 250))
                if active
                else ((7, 8), (3, 22), (1.3, 220))
            ):
                outline(points, (*color, alpha), width * self.u)
            line(
                (b + 10 * self.u, h - 4 * self.u),
                (w - b - 8 * self.u, h - 4 * self.u),
                (*color, 100),
                self.u,
            )
            mesh = finish()
            self._chrome[key] = mesh
        mesh.center_x, mesh.center_y = r.left, r.bottom
        mesh.draw()

    def logo(self):
        r = self.layout.logo
        u = self.u
        self.paint.glow(*r.center, r.width * 1.04, r.height * 1.7, CYAN, 38)
        self.frame(r, CYAN, active=True, bevel=32)
        # Short magenta/orange corner lights match the reference's high-tech wordmark plate.
        for sign in (-1, 1):
            x = r.center[0] + sign * r.width * 0.43
            arcade.draw_line(
                x - 18 * u, r.top, x + 18 * u, r.top, (255, 84, 127), 3 * u
            )
            arcade.draw_line(x - 18 * u, r.bottom, x + 18 * u, r.bottom, GOLD, 2 * u)
        if not self.wordmark_loaded:
            texture = _load_texture_once("assets/ui/title/wordmark.png")
            if texture:
                # Alpha threshold ignores isolated semitransparent generator specks.
                bbox = (
                    texture.image.getchannel("A")
                    .point(lambda a: 255 if a > 192 else 0)
                    .getbbox()
                )
                self.wordmark = texture.crop(
                    *(
                        (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
                        if bbox
                        else (0, 0, texture.width, texture.height)
                    )
                )
            self.wordmark_loaded = True
        target = Rect(
            r.left + 42 * u, r.bottom + 19 * u, r.right - 42 * u, r.top - 19 * u
        )
        if self.wordmark:
            self.texture(self.wordmark, target, cover=False)
        else:
            self.label(
                "CYBERCITY 2085",
                *r.center,
                60,
                TEXT,
                bold=True,
                anchor_x="center",
                width=r.width - 50 * u
            )
        # Genuine vector skyline emblem above the logo rather than flattened menu UI.
        cx = r.center[0]
        for i, height in enumerate((8, 19, 31, 53, 37, 70, 94, 58, 35, 22, 10)):
            x = cx + (i - 5) * 12 * u
            arcade.draw_lrbt_rectangle_filled(
                x - 4 * u,
                x + 4 * u,
                r.top + 3 * u,
                r.top + (height + 3) * u,
                (*CYAN, 220),
            )
            arcade.draw_line(
                x,
                r.top + (height + 3) * u,
                x,
                r.top + (height + 11) * u,
                (*CYAN, 160),
                u,
            )
        sub = self.layout.subtitle
        self.paint.panel(sub, CYAN)
        self.label(
            "C O V E R T   O P E R A T I O N S   C O M M A N D",
            *sub.center,
            19,
            TEXT,
            anchor_x="center",
            width=sub.width - 24 * u
        )
        for side in (-1, 1):
            x = sub.center[0] + side * (sub.width / 2 + 32 * u)
            for i in range(3):
                arcade.draw_polygon_filled(
                    [
                        (x + i * 14 * u - 11 * u, sub.bottom + 6 * u),
                        (x + i * 14 * u, sub.bottom + 6 * u),
                        (x + i * 14 * u - 11 * u, sub.top - 9 * u),
                        (x + i * 14 * u - 22 * u, sub.top - 9 * u),
                    ],
                    CYAN,
                )

    def icon(self, key, x, y, size=24, color=CYAN):
        radius = size * self.u / 2
        stroke = max(1.6, 2.3 * self.u)
        if key == "play":
            arcade.draw_polygon_outline(
                [
                    (x - radius * 0.65, y - radius),
                    (x + radius, y),
                    (x - radius * 0.65, y + radius),
                ],
                color,
                stroke,
            )
        elif key == "power":
            cache_key = ("power", radius, stroke, color)
            mesh = self._chrome.get(cache_key)
            if mesh is None:
                polygon, line, outline, finish = self.paint._mesh()
                points = [
                    (
                        math.cos(math.radians(135 + i * 270 / 32)) * radius * 0.85,
                        math.sin(math.radians(135 + i * 270 / 32)) * radius * 0.85,
                    )
                    for i in range(33)
                ]
                for first, second in zip(points, points[1:]):
                    line(first, second, (*color, 255), stroke)
                line((0, radius * 1.1), (0, -radius * 0.05), (*color, 255), stroke)
                mesh = finish()
                self._chrome[cache_key] = mesh
            mesh.center_x, mesh.center_y = x, y
            mesh.draw()
        else:
            super().icon(key, x, y, size, color)

    def menu_button(self, r, label, key, index):
        u = self.u
        enabled = key != "continue" or self.view._continue_available
        active = index == self.view._hover_index and enabled
        color = GOLD if active else CYAN if enabled else (84, 117, 126)
        amount = self.view._focus_amounts[index]
        self.paint.glow(
            *r.center,
            r.width * 1.14,
            r.height * 1.8,
            color,
            (
                15
                + amount
                * 60
                * (
                    1
                    if self.view._reduced_motion
                    else 0.9 + 0.1 * sin(self.view._elapsed * 2)
                )
                if enabled
                else 8
            )
        )
        self.frame(r, color, active=active, bevel=25)
        if active:
            arcade.draw_lrbt_rectangle_filled(
                r.left + 10 * u,
                r.right - 10 * u,
                r.bottom + 4 * u,
                r.top - 4 * u,
                (*GOLD, 15),
            )
            if not self.view._reduced_motion:
                x = (
                    r.left
                    + 14 * u
                    + ((self.view._elapsed * 0.25) % 1) * (r.width - 40 * u)
                )
                arcade.draw_line(
                    x, r.bottom + 8 * u, x + 20 * u, r.top - 8 * u, (*GOLD, 58), 5 * u
                )
        icons = {
            "new_game": "play",
            "continue": "next",
            "settings": "settings",
            "quit": "power",
        }
        self.icon(icons[key], r.left + 65 * u, r.center[1], 36, color)
        # Large active labels remain actual Arcade text, supporting accessibility sizing.
        self.label(
            label,
            r.center[0] + 10 * u,
            r.center[1],
            27,
            TEXT if enabled else (129, 154, 162),
            bold=True,
            anchor_x="center",
            width=r.width - 175 * u,
        )
        for i in range(3):
            x = r.right - (62 - i * 15) * u
            arcade.draw_polygon_filled(
                [
                    (x, r.bottom + 8 * u),
                    (x + 9 * u, r.bottom + 8 * u),
                    (x + 43 * u, r.top - 8 * u),
                    (x + 34 * u, r.top - 8 * u),
                ],
                (*color, 120 if active else 50),
            )

    def footer(self):
        u = self.u
        r = self.layout.footer
        self.paint.panel(r, CYAN)
        # Three physically distinct footer zones avoid the old version/hint collision.
        motion = self.layout.motion
        self.icon("settings", motion.left + 16 * u, motion.center[1], 22, CYAN)
        self.label(
            "MOTION: " + ("REDUCED" if self.view._reduced_motion else "FULL") + " [M]",
            motion.left + 35 * u,
            motion.center[1],
            13,
            CYAN,
            width=motion.width - 40 * u,
        )
        self.label(
            build_label() + "  //  AEGIS CORPORATION",
            *r.center,
            14,
            TEXT,
            anchor_x="center",
            width=r.width * 0.43
        )
        self.label(
            "ARROWS / MOUSE  //  ENTER",
            r.right - 19 * u,
            r.center[1],
            13,
            CYAN,
            anchor_x="right",
            width=r.width * 0.28,
        )
