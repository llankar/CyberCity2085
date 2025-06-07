from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Unit:
    position: Tuple[int, int]
    action_points: int = 2

    def move(self, dx: int, dy: int):
        x, y = self.position
        self.position = (x + dx, y + dy)
        self.action_points -= 1
