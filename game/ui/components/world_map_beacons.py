"""Reusable Arcade holographic mission beacons and cached neon typography."""

from math import sin, cos, pi
from pathlib import Path
import arcade
from game.ui.screens.world_map import texture_rect
from game.ui.theme.typography import scale_font_size

PALETTE = {
    "story": (255, 181, 52),
    "operation": (39, 232, 255),
    "narrative": (193, 132, 255),
    "urgent": (255, 67, 83),
}
CATEGORY = {
    "story": "MISSION PRINCIPALE",
    "operation": "OPÉRATION",
    "narrative": "NARRATIVE",
    "urgent": "URGENTE",
}


def rgba(color, alpha):
    return (*color[:3], max(0, min(255, int(alpha))))


def category_for(mission, narrative=False):
    tags = {
        str(getattr(t, "name", t)).lower() for t in getattr(mission, "tags", []) or []
    }
    hint = getattr(mission, "emotional_impact_hint", {}) or {}
    if isinstance(hint, dict):
        tags.update(str(t).lower() for t in (hint.get("normalized_tags", []) or []))
    title = str(getattr(mission, "title", "")).upper()
    if (
        getattr(mission, "is_urgent", False)
        or getattr(mission, "urgent", False)
        or "[URGENT]" in title
        or tags & {"urgent", "emergency", "time_sensitive"}
    ):
        return "urgent"
    if narrative:
        return "narrative"
    if "[STORY]" in title or "story" in tags or getattr(mission, "is_story", False):
        return "story"
    return "operation"


class HolographicRenderer:
    def __init__(self):
        self._texts = {}
        self._fits = {}
        self._bodies = {}
        self._panels = {}
        self._glows = {}
        self._fonts_loaded = False

    def resize(self):
        for mesh in list(self._bodies.values()) + list(self._panels.values()):
            mesh.clear()
        self._bodies.clear()
        self._panels.clear()
        self._texts.clear()
        self._fits.clear()

    def _prepare(self):
        if self._fonts_loaded:
            return
        font_dir = Path(__file__).resolve().parents[3] / "assets/fonts/rajdhani"
        for path in sorted(font_dir.glob("*.ttf")):
            arcade.load_font(str(path))
        self._fonts_loaded = True

    def text(
        self,
        text,
        x,
        y,
        size,
        color,
        *,
        bold=False,
        width=None,
        anchor_x="left",
        anchor_y="baseline",
        multiline=False,
        accessibility=True
    ):
        self._prepare()
        if accessibility:
            size = scale_font_size(size)
        key = (text, size, tuple(color), bold, width, anchor_x, anchor_y, multiline)
        label = self._texts.get(key)
        if label is None:
            if len(self._texts) > 512:
                self._texts.clear()
            label = arcade.Text(
                text,
                x,
                y,
                color,
                size,
                font_name="Rajdhani",
                bold=bold,
                width=width,
                anchor_x=anchor_x,
                anchor_y=anchor_y,
                multiline=multiline,
            )
            self._texts[key] = label
        if label.x != x:
            label.x = x
        if label.y != y:
            label.y = y
        label.draw()
        return label

    def glow(self, x, y, w, h, color, alpha):
        key = tuple(color[:3])
        if key not in self._glows:
            self._glows[key] = arcade.make_soft_circle_texture(128, (*key, 255), 255, 0)
        arcade.draw_texture_rect(
            self._glows[key],
            texture_rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2),
            alpha=int(alpha),
        )

    def _mesh(self):
        vertices, colors = [], []

        def polygon(points, color):
            for i in range(1, len(points) - 1):
                vertices.extend([points[0], points[i], points[i + 1]])
                colors.extend([color] * 3)

        def line(a, b, color, width):
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = max(0.001, (dx * dx + dy * dy) ** 0.5)
            nx, ny = -dy / length * width / 2, dx / length * width / 2
            polygon(
                [
                    (a[0] + nx, a[1] + ny),
                    (b[0] + nx, b[1] + ny),
                    (b[0] - nx, b[1] - ny),
                    (a[0] - nx, a[1] - ny),
                ],
                color,
            )

        def outline(points, color, width):
            for a, b in zip(points, points[1:] + points[:1]):
                line(a, b, color, width)

        def finish():
            from arcade.shape_list import (
                ShapeElementList,
                create_triangles_filled_with_colors,
            )

            shapes = ShapeElementList()
            shapes.append(create_triangles_filled_with_colors(vertices, colors))
            return shapes

        return polygon, line, outline, finish

    def panel(self, rect, color, *, selected=False):
        key = (round(rect.width, 3), round(rect.height, 3), tuple(color[:3]), selected)
        mesh = self._panels.get(key)
        if mesh is None:
            polygon, line, outline, finish = self._mesh()
            w, h = rect.width, rect.height
            points = [
                (8, 0),
                (w - 8, 0),
                (w, 8),
                (w, h - 8),
                (w - 8, h),
                (8, h),
                (0, h - 8),
                (0, 8),
            ]
            polygon(points, (2, 9, 15, 242))
            for width, alpha in (
                [(8, 20), (4, 55), (1.6, 235)] if selected else [(3, 22), (1, 170)]
            ):
                outline(points, rgba(color, alpha), width)
            line((14, h - 4), (w - 18, h - 4), rgba(color, 115), 1)
            line((w - 24, 4), (w - 8, 4), rgba(color, 150), 2)
            mesh = finish()
            self._panels[key] = mesh
        mesh.center_x, mesh.center_y = rect.left, rect.bottom
        mesh.draw()

    def fit(self, text, width, size, bold=True):
        self._prepare()
        key = (text, round(width, 2), size, bold)
        if key in self._fits:
            return self._fits[key]
        probe = arcade.Text(text, 0, 0, font_size=size, font_name="Rajdhani", bold=bold)
        if probe.content_width <= width:
            result = text
        else:
            low, high = 0, len(text)
            while low < high:
                mid = (low + high + 1) // 2
                probe.text = text[:mid] + "…"
                if probe.content_width <= width:
                    low = mid
                else:
                    high = mid - 1
            result = text[:low] + "…"
        self._fits[key] = result
        return result

    def _body(self, category, selected, u, hover):
        step = round(hover * 8)
        key = (category, selected, round(u, 3), step)
        if key in self._bodies:
            return self._bodies[key]
        color = PALETTE[category]
        polygon, line, outline, finish = self._mesh()
        cy = (77 if selected else 49) * u
        radius = (33 if selected else 17) * u * (1 + 0.14 * step / 8)
        for rw, alpha in [(1.8, 60), (1.3, 130), (1, 235)]:
            a = (90 if selected else 43) * u * rw / 2
            b = (24 if selected else 12) * u * rw / 2
            points = [(cos(i * pi / 16) * a, sin(i * pi / 16) * b) for i in range(32)]
            outline(points, rgba(color, alpha), 1.5 if rw == 1 else 1)
        polygon(
            [
                (-9 * u, 3 * u),
                (9 * u, 3 * u),
                (radius * 0.5, cy - radius * 0.7),
                (-radius * 0.5, cy - radius * 0.7),
            ],
            rgba(color, 45),
        )
        for width, alpha in [(9, 25), (4, 80), (1.5, 220)]:
            line((0, 2 * u), (0, cy - radius * 0.8), rgba(color, alpha), width * u)
        points = [(0, cy + radius), (radius, cy), (0, cy - radius), (-radius, cy)]
        polygon(points, (3, 13, 21, 242))
        for width, alpha in [(10, 16), (6, 28), (3.4, 80), (1.8, 255)]:
            outline(points, rgba(color, alpha), width * u)
        ink = (*tuple(min(255, int(c * 0.4 + 153)) for c in color), 255)
        r = radius * (0.9 if category == "urgent" else 0.68)
        lw = max(1.3, r * 0.10)
        if category == "story":
            for side in [-1, 1]:
                outline(
                    [
                        (0, cy - r * 0.45),
                        (side * r * 0.68, cy - r * 0.25),
                        (side * r * 0.68, cy + r * 0.5),
                        (side * r * 0.14, cy + r * 0.58),
                        (0, cy + r * 0.4),
                    ],
                    ink,
                    lw,
                )
            line((0, cy - r * 0.45), (0, cy + r * 0.4), ink, lw)
        elif category == "urgent":
            line((0, cy + r * 0.5), (0, cy - r * 0.06), ink, lw * 1.8)
            polygon(
                [
                    (-lw, cy - r * 0.5),
                    (lw, cy - r * 0.5),
                    (lw, cy - r * 0.3),
                    (-lw, cy - r * 0.3),
                ],
                ink,
            )
        else:
            for offset in [-0.30, 0, 0.30]:
                outline(
                    [
                        (-r * 0.6, cy + offset * r),
                        (0, cy + r * 0.30 + offset * r),
                        (r * 0.6, cy + offset * r),
                        (0, cy - r * 0.30 + offset * r),
                    ],
                    ink,
                    lw,
                )
        mesh = finish()
        self._bodies[key] = mesh
        return mesh

    def beacon(self, p, time, hover=0):
        color = PALETTE[p.beacon.category]
        selected = p.beacon.selected
        u = p.scale
        phase = time * 2.5 + (sum(map(ord, p.beacon.key)) % 31) * 0.29
        pulse = 0.5 + 0.5 * sin(phase)
        growth = 1 + 0.14 * hover
        radius = (33 if selected else 17) * u * growth
        x, y = p.x, p.y
        cy = y + (77 if selected else 49) * u
        self.glow(
            x,
            y,
            145 * u if selected else 85 * u,
            38 * u if selected else 24 * u,
            color,
            100 + 45 * pulse,
        )
        self.glow(
            x,
            cy,
            radius * 3.8,
            radius * 3.8,
            color,
            65 + 35 * pulse if selected else 40 + 20 * pulse,
        )
        mesh = self._body(p.beacon.category, selected, u, hover)
        mesh.center_x, mesh.center_y = x, y
        mesh.draw()
        if selected:
            for i in range(12):
                angle = i * pi / 6 + time * 0.16
                arcade.draw_line(
                    x + cos(angle) * 60 * u,
                    y + sin(angle) * 16 * u,
                    x + cos(angle) * 66 * u,
                    y + sin(angle) * 19 * u,
                    rgba(color, 120),
                    1,
                )
        arcade.draw_ellipse_filled(
            x, y, 20 * u if selected else 11 * u, 6 * u, (*color, 255)
        )
        self.glow(x, y, 30 * u, 12 * u, (255, 255, 220), 140)
        scan = (sin(time * 1.8) * 0.5 + 0.5) * 1.4 - 0.7
        half = radius * (1 - abs(scan))
        arcade.draw_line(
            x - half,
            cy + scan * radius,
            x + half,
            cy + scan * radius,
            rgba(color, 90),
            1 * u,
        )
        # Attached cartouche; two collision-tested hit regions, no giant hit box.
        label = p.label
        endx = min(max(x, label.left + 5), label.right - 5)
        endy = min(max(cy, label.bottom + 5), label.top - 5)
        arcade.draw_line(
            x + radius if endx > x else x - radius,
            cy,
            endx,
            endy,
            rgba(color, 125),
            1 * u,
        )
        self.panel(label, color, selected=selected or hover > 0.15)
        l, b, r, t = label.left, label.bottom, label.right, label.top
        self.text(
            CATEGORY[p.beacon.category],
            l + 10 * u,
            t - 12 * u,
            10 * u,
            color,
            bold=True,
            anchor_y="center",
            accessibility=False,
        )
        if selected:
            self.text(
                self.fit(p.beacon.site.upper(), label.width - 22 * u, 25 * u),
                l + 11 * u,
                t - 37 * u,
                25 * u,
                (247, 249, 250),
                bold=True,
                anchor_y="center",
                accessibility=False,
            )
            self.text(
                self.fit(p.beacon.title, label.width - 22 * u, 11 * u),
                l + 11 * u,
                b + 15 * u,
                11 * u,
                (255, 231, 187),
                bold=True,
                anchor_y="center",
                accessibility=False,
            )
            for i in range(6):
                sx = r - 70 * u + i * 8 * u
                arcade.draw_line(
                    sx, t - 15 * u, sx + 5 * u, t - 9 * u, rgba(color, 135), 2 * u
                )
        else:
            self.text(
                self.fit(p.beacon.title, label.width - 20 * u, 12 * u),
                l + 10 * u,
                b + 12 * u,
                12 * u,
                (233, 239, 249),
                bold=True,
                anchor_y="center",
                accessibility=False,
            )
