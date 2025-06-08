from dataclasses import dataclass
from typing import Tuple
import arcade

@dataclass
class Unit:
    position: Tuple[int, int]
    action_points: int = 2
    sprite: arcade.Sprite | None = None

    def move(self, dx: int, dy: int):
        x, y = self.position
        self.position = (x + dx, y + dy)
        if self.sprite:
            self.sprite.center_x = self.position[0]
            self.sprite.center_y = self.position[1]
        self.action_points -= 1
