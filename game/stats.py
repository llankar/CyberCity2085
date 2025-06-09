from dataclasses import dataclass
import random


@dataclass
class PlayerStats:
    level: int = 1
    defense: int = 1
    psi: int = 1
    str: int = 5
    agi: int = 1
    con: int = 1
    cha: int = 1
    hp: int = 0
    max_hp: int = 0
    xp: int = 0

    def __post_init__(self) -> None:
        self.recalculate_hp()
        if not self.hp:
            self.hp = self.max_hp

    def recalculate_hp(self) -> None:
        self.max_hp = 10 * self.level + self.con
        if self.hp > self.max_hp:
            self.hp = self.max_hp


@dataclass
class EnemyStats:
    level: int = 1
    defense: int = 1
    psi: int = 1
    str: int = 1
    agi: int = 1
    hp: int = 0
    max_hp: int = 0

    def __post_init__(self) -> None:
        self.recalculate_hp()
        if not self.hp:
            self.hp = self.max_hp

    def recalculate_hp(self) -> None:
        self.max_hp = 10 * self.level
        if self.hp > self.max_hp:
            self.hp = self.max_hp


def perform_attack(attacker, defender, stat_name: str, *, phys_def: bool = False, psi_def: bool = False) -> bool:
    """Resolve an attack using the given stat name."""
    attack_value = getattr(attacker, stat_name)
    defense = defender.defense
    if attack_value <= 0:
        return False
    chance = attack_value / (attack_value + defense)
    if random.random() < chance:
        damage = attack_value
        if stat_name == "psi" and psi_def:
            damage = max(0, damage - 1)
        elif stat_name != "psi" and phys_def:
            damage = max(0, damage - 1)
        defender.hp = max(0, defender.hp - damage)
        return True
    return False

