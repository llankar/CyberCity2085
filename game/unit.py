from dataclasses import dataclass
from typing import Tuple
import arcade

@dataclass
class Unit:
    position: Tuple[int, int]
    attack_range: int = 1
    health: int = 3
    action_points: int = 2
    sprite: arcade.Sprite | None = None

    def move(self, dx: int, dy: int):
        x, y = self.position
        self.position = (x + dx, y + dy)
        if self.sprite:
            self.sprite.center_x = self.position[0]
            self.sprite.center_y = self.position[1]
        self.action_points -= 1

    def reset_actions(self):
        self.action_points = 2

    def distance_to(self, other: "Unit") -> float:
        return ((self.position[0] - other.position[0]) ** 2 + (self.position[1] - other.position[1]) ** 2) ** 0.5

    def attack(self, other: "Unit") -> bool:
        if self.action_points <= 0:
            return False
        if self.distance_to(other) <= self.attack_range * 32:
            other.health -= 1
            self.action_points -= 1
            return True
        return False
