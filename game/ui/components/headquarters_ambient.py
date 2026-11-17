"""Subtle bounded room displays and exterior rain; no simulation/campaign writes."""

import math
import random
import arcade
from .squad_style import CYAN


class HeadquartersAmbient:
    def __init__(self):
        self.size = None
        self.rain = None

    def draw(self, p, time, reduced=False):
        if reduced:
            return
        l = p.layout
        u = p.u
        if self.size != (l.width, l.height):
            if self.rain is not None:
                self.rain.clear()
            polygon, line, outline, finish = p.paint._mesh()
            rng = random.Random(2085)
            for _ in range(80):
                x = (
                    rng.uniform(0, l.width * 0.13)
                    if rng.random() < 0.5
                    else rng.uniform(l.width * 0.88, l.width)
                )
                y = rng.uniform(0, l.height)
                for dy in (0, l.height):
                    line(
                        (x, y + dy),
                        (x - 3 * u, y + dy - 18 * u),
                        (94, 206, 232, 45),
                        max(0.65, u),
                    )
            self.rain = finish()
            self.size = (l.width, l.height)
        self.rain.center_y = -(time * 110 * u) % l.height - l.height
        self.rain.draw()
        for index, r in enumerate(l.rooms):
            # A narrow scan stays on the room's display area, above its label rail.
            phase = (time * (0.10 + index * 0.012) + index * 0.16) % 1
            x = r.left + r.width * (0.25 + phase * 0.47)
            y = r.bottom + r.height * 0.58
            arcade.draw_line(x, y - 8 * u, x, y + 10 * u, (*CYAN, 35), 1)
            if index in (0, 2, 4, 5):
                pulse = 0.5 + 0.5 * math.sin(time * 0.8 + index)
                p.paint.glow(
                    r.center[0],
                    r.bottom + r.height * 0.63,
                    55 * u,
                    40 * u,
                    CYAN,
                    10 + 8 * pulse,
                )
        # Elevator motion provides a visual link between the three levels.
        x = l.art.left + l.art.width * 0.49
        y = l.art.bottom + l.art.height * (0.39 + ((time * 0.065) % 1) * 0.40)
        p.paint.glow(x, y, 13 * u, 45 * u, (255, 188, 86), 24)
