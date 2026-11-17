"""Bounded, seeded atmospheric meshes: one draw for rain, static reduced mode."""

import math
import random
import arcade


class TitleAtmosphere:
    def __init__(self):
        self.size = None
        self.rain = None
        self.beacons = None
        self.mist = None

    def prepare(self, p, w, h):
        if self.size == (w, h):
            return
        for mesh in (self.rain, self.beacons):
            if mesh is not None:
                mesh.clear()
        self.size = (w, h)
        rng = random.Random(2085)
        polygon, line, outline, finish = p.paint._mesh()
        # Double-height repeated rain field, translated rather than recreated each frame.
        for _ in range(145):
            x = rng.uniform(-70, w + 70)
            y = rng.uniform(0, h)
            length = rng.uniform(12, 36) * p.u
            for offset in (0, h):
                line(
                    (x, y + offset),
                    (x - 4 * p.u, y + offset - length),
                    (110, 209, 235, rng.randint(20, 65)),
                    max(0.7, p.u),
                )
        self.rain = finish()
        polygon, line, outline, finish = p.paint._mesh()
        for x, y in ((0.18, 0.6), (0.85, 0.68), (0.88, 0.42), (0.23, 0.4)):
            line((x * w, y * h), (x * w, y * h + 8 * p.u), (82, 238, 255, 190), 2 * p.u)
        self.beacons = finish()
        self.mist = arcade.make_soft_circle_texture(128, (92, 188, 220, 255), 255, 0)

    def draw(self, p, w, h, time, reduced):
        self.prepare(p, w, h)
        if reduced:
            return
        self.rain.center_y = -(time * 210 * p.u) % h - h
        self.rain.draw()
        # Gentle existing-city accents, never full-screen strobing or lightning flashes.
        self.beacons.draw()
        pulse = 0.5 + 0.5 * math.sin(time * 0.65)
        for x, y in ((0.19, 0.46), (0.85, 0.61)):
            p.paint.glow(
                w * x, h * y, 65 * p.u, 120 * p.u, (37, 214, 241), 16 + 13 * pulse
            )
        for i in range(2):
            x = w * (0.25 + i * 0.48) + math.sin(time * 0.12 + i) * 34 * p.u
            arcade.draw_texture_rect(
                self.mist,
                arcade.LBWH(x - 220 * p.u, h * 0.16, 440 * p.u, 100 * p.u),
                alpha=12,
            )
