from dataclasses import dataclass
from typing import Tuple

from .character import Character
import arcade

from .stats import PlayerStats, EnemyStats, perform_attack

@dataclass
class Unit:
    position: Tuple[int, int]
    stats: PlayerStats | EnemyStats | None = None
    character: Character | None = None
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

    def _perform_attack(self, other: "Unit", stat: str, range_: int) -> int:
        if self.action_points <= 0 or not self.stats or not other.stats:
            return 0
        if self.distance_to(other) <= range_ * 32:
            before = other.stats.hp
            hit = perform_attack(
                self.stats,
                other.stats,
                stat,
                phys_def=other.is_defending,
                psi_def=other.is_psi_defending,
            )
            damage = max(0, before - other.stats.hp) if hit else 0
            other.health = other.stats.hp
            self.action_points -= 1
            other.is_defending = False
            other.is_psi_defending = False
            return damage
        return 0

    def attack(self, other: "Unit") -> int:
        """Backward compatible melee attack."""
        return self.melee_attack(other)

    def melee_attack(self, other: "Unit") -> int:
        return self._perform_attack(other, stat="str", range_=1)

    def shoot(self, other: "Unit") -> int:
        return self._perform_attack(other, stat="agi", range_=3)

    def psi_attack(self, other: "Unit") -> int:
        return self._perform_attack(other, stat="psi", range_=2)

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
