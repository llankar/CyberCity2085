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
    paralyzed_turns: int = 0
    fire_turns: int = 0
    fire_damage: int = 0
    freeze_turns: int = 0

    def move(self, dx: int, dy: int):
        if self.freeze_turns > 0:
            return False
        x, y = self.position
        self.position = (x + dx, y + dy)
        if self.sprite:
            self.sprite.center_x = self.position[0]
            self.sprite.center_y = self.position[1]
        self.action_points -= 1
        return True

    def reset_actions(self):
        self.action_points = 2
        self.is_defending = False
        self.is_psi_defending = False
        self.start_turn()

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
        """Ranged attack using agility with a 10 cell range."""
        return self._perform_attack(other, stat="agi", range_=10)

    def psi_attack(self, other: "Unit") -> int:
        """Psi attack with a 10 cell range."""
        return self._perform_attack(other, stat="psi", range_=10)

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

    # -------------------------------------------------------------
    # Turn management and special psi abilities
    # -------------------------------------------------------------

    def start_turn(self) -> None:
        """Process status effects at the start of the unit's turn."""
        if self.fire_turns > 0:
            if self.stats:
                self.stats.hp = max(0, self.stats.hp - self.fire_damage)
                self.health = self.stats.hp
            self.fire_turns -= 1
        if self.paralyzed_turns > 0:
            self.action_points = 0
            self.paralyzed_turns -= 1
        if self.freeze_turns > 0:
            self.freeze_turns -= 1

    def psi_paralyze(self, target: "Unit") -> bool:
        if self.action_points <= 0 or not self.stats or not target.stats:
            return False
        turns = max(1, self.stats.level // 5 + 1)
        target.paralyzed_turns = max(target.paralyzed_turns, turns)
        self.action_points -= 1
        return True

    def psi_fire(self, target: "Unit") -> bool:
        if self.action_points <= 0 or not self.stats or not target.stats:
            return False
        damage = 1 + self.stats.level // 5
        turns = max(2, self.stats.level // 2 + 1)
        target.fire_damage = damage
        target.fire_turns = turns
        self.action_points -= 1
        return True

    def psi_ice(self, target: "Unit") -> bool:
        if self.action_points <= 0 or not self.stats or not target.stats:
            return False
        dmg = self.stats.psi // 2
        target.stats.hp = max(0, target.stats.hp - dmg)
        target.health = target.stats.hp
        target.freeze_turns = max(2, self.stats.level // 2 + 1)
        self.action_points -= 1
        return True
