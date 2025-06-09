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
    is_defending: bool = False
    is_psi_defending: bool = False

    def move(self, dx: int, dy: int):
        x, y = self.position
        self.position = (x + dx, y + dy)
        if self.sprite:
            self.sprite.center_x = self.position[0]
            self.sprite.center_y = self.position[1]
        self.action_points -= 1

    def reset_actions(self):
        self.action_points = 2
        self.is_defending = False
        self.is_psi_defending = False

    def distance_to(self, other: "Unit") -> float:
        return ((self.position[0] - other.position[0]) ** 2 + (self.position[1] - other.position[1]) ** 2) ** 0.5

    def _perform_attack(self, other: "Unit", damage: int, range_: int, *, psi: bool = False) -> bool:
        if self.action_points <= 0:
            return False
        if self.distance_to(other) <= range_ * 32:
            final_damage = damage
            if psi:
                if other.is_psi_defending:
                    final_damage = max(0, final_damage - 1)
                    other.is_psi_defending = False
            else:
                if other.is_defending:
                    final_damage = max(0, final_damage - 1)
                    other.is_defending = False
            other.health -= final_damage
            self.action_points -= 1
            return True
        return False

    def attack(self, other: "Unit") -> bool:
        """Backward compatible melee attack."""
        return self.melee_attack(other)

    def melee_attack(self, other: "Unit") -> bool:
        return self._perform_attack(other, damage=2, range_=1)

    def shoot(self, other: "Unit") -> bool:
        return self._perform_attack(other, damage=1, range_=3)

    def psi_attack(self, other: "Unit") -> bool:
        return self._perform_attack(other, damage=2, range_=2, psi=True)

    def defend(self) -> bool:
        if self.action_points <= 0:
            return False
        self.is_defending = True
        self.action_points -= 1
        return True

    def psi_defend(self) -> bool:
        if self.action_points <= 0:
            return False
        self.is_psi_defending = True
        self.action_points -= 1
        return True
