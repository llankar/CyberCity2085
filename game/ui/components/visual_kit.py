"""Shared Visual 2.x Arcade kit: cached type, chrome, cards and interaction states.

Render-only. Every hit routes to a screen's existing controller.
"""

from dataclasses import dataclass
from pathlib import Path
from math import sin
import arcade
from game.ui.layouts.world_map_beacons import Rect
from game.ui.components.world_map_beacons import HolographicRenderer
from game.ui.panels import _load_texture_once, _draw_icon
from game.ui.theme.typography import scale_font_size
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, TEXT, MUTED, PURPLE


@dataclass
class UIHit:
    left: float
    bottom: float
    right: float
    top: float
    action: str
    data: object = None
    tooltip: str = ""

    def contains(self, x, y):
        return self.left <= x <= self.right and self.bottom <= y <= self.top


class VisualKit:
    def __init__(self):
        self.paint = HolographicRenderer()
        self.hover = None
        self.hover_amount = 0.0
        self._size = None
        self._tiles = {}
        self._scan_mesh = None
        self._meter_meshes = {}
        self._text_batch = None
        self._previous_texts = set()
        self._frame_texts = set()
        self.regions = {}
        self.text_bounds = []

    def update(self, dt):
        self.hover_amount += ((1.0 if self.hover else 0.0) - self.hover_amount) * min(
            1, dt * 12
        )

    def text(self, *args, **kwargs):
        label = self.paint.text(
            *args, **kwargs, batch=self._text_batch, draw=self._text_batch is None
        )
        if self._text_batch is not None:
            self._frame_texts.add(label)
        return label

    def label(
        self,
        text,
        x,
        y,
        size=14,
        color=TEXT,
        *,
        width=None,
        bold=False,
        anchor_x="left",
        anchor_y="center",
    ):
        size = scale_font_size(max(13, size * self.u))
        if width is not None:
            text = self.paint.fit(str(text), width, size, bold)
        result = self.text(
            str(text),
            x,
            y,
            size,
            color,
            bold=bold,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            accessibility=False,
        )
        self.text_bounds.append(
            (result.text, x, y, result.content_width, result.content_height)
        )
        return result

    def image(self, path, rect, *, cover=True, alpha=255):
        tex = _load_texture_once(path) if path else None
        if tex is None:
            return
        self.texture(tex, rect, cover=cover, alpha=alpha)

    def texture(self, tex, rect, *, cover=True, alpha=255):
        # Crop texture coordinates, never stretch portraits or paint outside panels.
        if cover:
            ratio = rect.width / rect.height
            tw, th = tex.width, tex.height
            key = (id(tex), round(ratio, 3))
            if key not in self._tiles:
                cw, ch = (
                    (int(th * ratio), th) if tw / th > ratio else (tw, int(tw / ratio))
                )
                self._tiles[key] = tex.crop((tw - cw) // 2, 0, max(1, cw), max(1, ch))
            tex = self._tiles[key]
            target = rect
        else:
            ratio = min(rect.width / tex.width, rect.height / tex.height)
            w, h = tex.width * ratio, tex.height * ratio
            x, y = rect.center
            target = Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        arcade.draw_texture_rect(
            tex,
            arcade.LBWH(target.left, target.bottom, target.width, target.height),
            alpha=alpha,
        )

    def icon(self, key, x, y, size=24, color=CYAN):
        aliases = {
            "assets": "nodes",
            "command": "target",
            "gears": "settings",
            "journal": "layers",
            "recruit": "squad",
            "armory": "layers",
            "credits": "coins",
            "intel": "antenna",
            "research": "chip",
            "black_ops": "delete",
            "right": "next",
            "left": "previous",
        }
        name = aliases.get(key, key)
        path = Path("assets/ui/squad_command/icons") / (name + ".png")
        texture = _load_texture_once(str(path)) if path.exists() else None
        if texture is not None:
            side = size * self.u
            arcade.draw_texture_rect(
                texture,
                arcade.LBWH(x - side / 2, y - side / 2, side, side),
                color=arcade.types.Color.from_iterable(color),
            )
        else:
            _draw_icon(key, int(x), int(y), int(size * self.u), color)

    def hit(self, rect, action, data=None, tooltip=""):
        self.view._hits.append(
            UIHit(rect.left, rect.bottom, rect.right, rect.top, action, data, tooltip)
        )

    def button(
        self,
        rect,
        label,
        action,
        data=None,
        *,
        color=CYAN,
        icon=None,
        primary=False,
        tooltip="",
    ):
        hot = self.hover == (action, data)
        if primary or hot:
            self.paint.glow(
                *rect.center,
                rect.width * 1.08,
                rect.height * 1.8,
                color,
                65
                + (
                    25 * sin(self.view._elapsed * 2)
                    if primary
                    and not getattr(self, "reduced_motion", False)
                    and not getattr(self.view, "_hq_reduced_motion", False)
                    and not getattr(
                        getattr(self.view, "_settings", None), "reduced_motion", False
                    )
                    else 20 * self.hover_amount
                ),
            )
        self.paint.panel(rect, color, selected=primary or hot)
        if hot:
            arcade.draw_lrbt_rectangle_filled(
                rect.left + 4,
                rect.right - 4,
                rect.bottom + 3,
                rect.top - 3,
                (*color, 22),
            )
        tx = rect.center[0]
        if icon:
            self.icon(icon, rect.left + 22 * self.u, rect.center[1], 26, color)
            tx += 12 * self.u
        available = rect.width - (66 if icon else 16) * self.u
        if primary:
            font_size = scale_font_size(max(13, 23 * self.u))
            while (
                font_size > 12
                and self.paint.fit(label, available, font_size, True) != label
            ):
                font_size -= 1
            self.text(
                label,
                tx,
                rect.center[1],
                font_size,
                color,
                bold=True,
                anchor_x="center",
                anchor_y="center",
                accessibility=False,
            )
        else:
            self.label(
                label,
                tx,
                rect.center[1],
                14,
                color,
                width=available,
                bold=True,
                anchor_x="center",
            )
        self.hit(rect, action, data, tooltip or label)

    def panel(self, rect, title, icon):
        self.paint.panel(rect, CYAN)
        hh = 47 * self.u
        arcade.draw_line(
            rect.left + 12 * self.u,
            rect.top - hh,
            rect.right - 12 * self.u,
            rect.top - hh,
            (*CYAN, 140),
            1,
        )
        self.icon(icon, rect.left + 26 * self.u, rect.top - hh / 2, 25)
        self.label(
            title,
            rect.left + 49 * self.u,
            rect.top - hh / 2,
            24,
            bold=True,
            width=rect.width - 62 * self.u,
        )

    def meter(self, rect, fraction, color, segments=6):
        if not hasattr(self.paint, "_mesh"):
            return self._immediate_meter(rect, fraction, color, segments)
        fraction = max(0, min(1, fraction))
        key = (rect.width, rect.height, fraction, tuple(color), segments, self.u)
        mesh = self._meter_meshes.get(key)
        if mesh is None:
            if len(self._meter_meshes) > 128:
                for old in self._meter_meshes.values():
                    old.clear()
                self._meter_meshes.clear()
            polygon, line, outline, finish = self.paint._mesh()
            gap = 2 * self.u
            width = (rect.width - gap * (segments - 1)) / segments
            for i in range(segments):
                x = i * (width + gap)
                polygon(
                    [
                        (x, 0),
                        (x + width, 0),
                        (x + width, rect.height),
                        (x, rect.height),
                    ],
                    (30, 48, 58, 255),
                )
                fill = max(0, min(1, fraction * segments - i))
                if fill:
                    polygon(
                        [
                            (x, 0),
                            (x + width * fill, 0),
                            (x + width * fill, rect.height),
                            (x, rect.height),
                        ],
                        (*color[:3], 255),
                    )
            mesh = finish()
            self._meter_meshes[key] = mesh
        mesh.center_x, mesh.center_y = rect.left, rect.bottom
        mesh.draw()

    def _immediate_meter(self, rect, fraction, color, segments=6):
        fraction = max(0, min(1, fraction))
        gap = 2 * self.u
        width = (rect.width - gap * (segments - 1)) / segments
        for i in range(segments):
            l = rect.left + i * (width + gap)
            arcade.draw_lrbt_rectangle_filled(
                l, l + width, rect.bottom, rect.top, (30, 48, 58, 255)
            )
            fill = max(0, min(1, fraction * segments - i))
            if fill:
                arcade.draw_lrbt_rectangle_filled(
                    l, l + width * fill, rect.bottom, rect.top, color
                )

    def begin(self, view, width, height, background=None, overlay_alpha=195):
        """Start one shared frame; cache glyphs, textures and measurements."""
        self.view = view
        self.gs = getattr(view, "game_state", None)
        self.u = max(0.70, min(width / 1672, height / 941, 1.7))
        if self._text_batch is None and hasattr(view.window, "ctx"):
            from pyglet.graphics import Batch

            self._text_batch = Batch()
        if self._size != (width, height):
            self.paint.resize()
            self._tiles.clear()
            self._previous_texts = set()
            self._size = (width, height)
        if len(self.paint._texts) > 400:
            self.paint.clear_text_cache()
            self._previous_texts = set()
        self._frame_texts = set()
        self.text_bounds = []
        self.regions = {}
        view._hits = []
        full = Rect(0, 0, width, height)
        if background is not None:
            if isinstance(background, str):
                self.image(background, full)
            else:
                self.texture(background, full)
        arcade.draw_lrbt_rectangle_filled(
            0, width, 0, height, (1, 8, 15, max(0, min(255, overlay_alpha)))
        )

    def end(self):
        if self._text_batch is not None:
            cached = set(self.paint._texts.values())
            for item in (self._previous_texts - self._frame_texts) & cached:
                item.visible = False
            for item in self._frame_texts - self._previous_texts:
                item.visible = True
            self._previous_texts = set(self._frame_texts)
            self._text_batch.draw()

    def word(self, fr, en):
        return en

    def card(
        self,
        rect,
        title,
        subtitle="",
        *,
        action=None,
        data=None,
        selected=False,
        color=CYAN,
        icon=None,
        tooltip="",
    ):
        hot = self.hover == (action, data) if action else False
        self.paint.panel(rect, GOLD if selected else color, selected=selected or hot)
        x = rect.left + 16 * self.u
        if icon:
            self.icon(icon, x + 10 * self.u, rect.top - 24 * self.u, 25, color)
            x += 34 * self.u
        self.label(
            title,
            x,
            rect.top - 24 * self.u,
            19,
            TEXT,
            bold=True,
            width=rect.right - x - 14 * self.u,
        )
        if subtitle:
            self.label(
                subtitle,
                x,
                rect.top - 49 * self.u,
                14,
                MUTED,
                width=rect.right - x - 14 * self.u,
            )
        if action:
            self.hit(rect, action, data, tooltip or str(title) + "\n" + str(subtitle))

    def badge(self, text, rect, color=CYAN):
        self.paint.panel(rect, color)
        self.label(
            text,
            *rect.center,
            13,
            color,
            bold=True,
            width=rect.width - 12 * self.u,
            anchor_x="center",
        )

    def stat(self, rect, label, value, icon="chip", color=CYAN, fraction=None):
        self.paint.panel(rect, color)
        self.icon(icon, rect.left + 24 * self.u, rect.top - 25 * self.u, 24, color)
        self.label(
            label,
            rect.left + 43 * self.u,
            rect.top - 25 * self.u,
            14,
            MUTED,
            width=rect.width - 54 * self.u,
        )
        self.label(
            str(value),
            rect.left + 18 * self.u,
            rect.bottom + rect.height * 0.36,
            30,
            color,
            bold=True,
            width=rect.width - 30 * self.u,
        )
        if fraction is not None:
            self.meter(
                Rect(
                    rect.left + 16 * self.u,
                    rect.bottom + 12 * self.u,
                    rect.right - 16 * self.u,
                    rect.bottom + 18 * self.u,
                ),
                fraction,
                color,
            )

    def resource_bar(self, gs, rect):
        values = [(self.word("FONDS", "FUNDS"), gs.available_funds, "coins")]
        values += [
            (
                self.word("CRÉDITS", "CREDITS") if key == "credits" else key.upper(),
                gs.strategic_resources.get(key, 0),
                icon,
            )
            for key, icon in [
                ("credits", "chip"),
                ("intel", "antenna"),
                ("salvage", "gears"),
                ("influence", "squad"),
            ]
        ]
        gap = 8 * self.u
        width = (rect.width - gap * 4) / 5
        for i, (name, value, icon) in enumerate(values):
            r = Rect(
                rect.left + i * (width + gap),
                rect.bottom,
                rect.left + i * (width + gap) + width,
                rect.top,
            )
            self.paint.panel(r, CYAN)
            self.icon(
                icon, r.left + 23 * self.u, r.center[1], 25, GOLD if i == 0 else CYAN
            )
            self.label(
                name,
                r.left + 43 * self.u,
                r.top - 17 * self.u,
                12,
                MUTED,
                width=r.width - 50 * self.u,
            )
            self.label(
                f"{value:,}",
                r.left + 43 * self.u,
                r.bottom + 18 * self.u,
                22,
                GOLD if i == 0 else CYAN,
                bold=True,
                width=r.width - 50 * self.u,
            )

    def paragraph(self, text, rect, size=16, color=TEXT):
        """Wrap using the same font metrics as the actual cached labels."""
        font = scale_font_size(max(13, size * self.u))
        words = str(text).split()
        lines = []
        line = ""
        for word in words:
            candidate = (line + " " + word).strip()
            if line and self.paint.fit(candidate, rect.width, font) != candidate:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        leading = max(19 * self.u, font * 1.5)
        capacity = max(1, int(rect.height / leading))
        for i, line in enumerate(lines[:capacity]):
            if i == capacity - 1 and len(lines) > capacity:
                line += " …"
            self.label(
                line,
                rect.left,
                rect.top - leading * (i + 0.5),
                size,
                color,
                width=rect.width,
            )
        return len(lines) * leading

    def divider(self, left, right, y, color=CYAN):
        arcade.draw_line(left, y, right, y, (*color[:3], 90), 1)

    def action(
        self,
        rect,
        label,
        action,
        data=None,
        *,
        enabled=True,
        selected=False,
        danger=False,
        primary=False,
        icon=None,
        tooltip="",
    ):
        color = RED if danger else GOLD if primary or selected else CYAN
        if enabled:
            self.button(
                rect,
                label,
                action,
                data,
                color=color,
                primary=primary or selected,
                icon=icon,
                tooltip=tooltip,
            )
        else:
            self.paint.panel(rect, MUTED)
            self.label(
                label,
                *rect.center,
                14,
                MUTED,
                width=rect.width - 18 * self.u,
                anchor_x="center",
            )
            self.hit(rect, "ui_disabled", None, tooltip or label)
