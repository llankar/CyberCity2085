from dataclasses import dataclass
import random

ATTRIBUTE_MAX = 10
SKILL_RANK_MAX = 10


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


_CRIT_CHANCE = 0.12  # 12% base critical hit probability


def perform_attack(
    attacker,
    defender,
    stat_name: str,
    *,
    phys_def: bool = False,
    psi_def: bool = False,
    extra_defense: int = 0,
) -> tuple[bool, bool]:
    """Resolve an attack using the given stat name.

    Returns ``(hit, crit)``.  A critical hit deals double damage and has a
    12% base chance on any successful hit.

    ``extra_defense`` stacks on top of the defender's base defense —
    used to apply cover bonuses without mutating the defender's stats.

    Note: the return value is a tuple, but ``if perform_attack(...)`` still
    works because a non-empty tuple is truthy — callers that only check
    hit/miss do not need updating.
    """
    attack_value = getattr(attacker, stat_name)
    defense = defender.defense + extra_defense
    if attack_value <= 0:
        return (False, False)
    chance = attack_value / (attack_value + defense)
    if random.random() < chance:
        crit = random.random() < _CRIT_CHANCE
        damage = attack_value * (2 if crit else 1)
        if stat_name == "psi" and psi_def:
            damage = max(0, damage - 1)
        elif stat_name != "psi" and phys_def:
            damage = max(0, damage - 1)
        defender.hp = max(0, defender.hp - damage)
        return (True, crit)
    return (False, False)

