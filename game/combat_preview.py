"""Combat preview helpers shared by tactical UI and combat resolution math."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .unit import Unit

GRID_SIZE = 32


@dataclass(frozen=True)
class AttackPreview:
    min_damage: int
    max_damage: int
    hit_chance: float
    crit_chance: float
    warning: str | None = None


def estimate_attack_preview(attacker: Unit, defender: Unit, attack_kind: str) -> AttackPreview:
    """Estimate combat outcome from the same core values used by attack resolution."""
    if not attacker.stats or not defender.stats:
        return AttackPreview(0, 0, 0.0, 0.0)

    if attack_kind == "psi":
        stat_name = "psi"
        is_psi = True
    elif attack_kind == "melee":
        stat_name = "str"
        is_psi = False
    else:
        stat_name = "agi"
        is_psi = False

    attack_value = max(0, int(getattr(attacker.stats, stat_name, 0)))
    defense_value = max(0, int(getattr(defender.stats, "defense", 0))) + max(0, int(defender.in_cover_bonus))

    if attack_value <= 0:
        return AttackPreview(0, 0, 0.0, 0.0)

    hit_chance = attack_value / (attack_value + defense_value) if (attack_value + defense_value) else 0.0
    base_damage = attack_value
    mitigated_damage = base_damage
    if is_psi and defender.is_psi_defending:
        mitigated_damage = max(0, base_damage - 1)
    elif not is_psi and defender.is_defending:
        mitigated_damage = max(0, base_damage - 1)

    # Crit is a non-authoritative UI estimate based on attack-vs-defense edge.
    crit_chance = 0.05 + max(0.0, min(0.25, (attack_value - defense_value) / 100))

    return AttackPreview(
        min_damage=mitigated_damage,
        max_damage=mitigated_damage,
        hit_chance=max(0.0, min(1.0, hit_chance)),
        crit_chance=max(0.0, min(0.30, crit_chance)),
    )


def line_of_fire_warning(attacker: Unit, defender: Unit, allies: Iterable[Unit]) -> str | None:
    """Return a warning when a friendly unit can be hit on the line of fire."""
    ax, ay = attacker.position
    tx, ty = defender.position
    for ally in allies:
        if ally is attacker or ally is defender or ally.health <= 0:
            continue
        px, py = ally.position
        if not _point_on_segment_with_tolerance(ax, ay, tx, ty, px, py, tolerance=GRID_SIZE * 0.35):
            continue
        return "Warning: friendly-fire or line collision possible"
    return None


def _point_on_segment_with_tolerance(ax: int, ay: int, bx: int, by: int, px: int, py: int, tolerance: float) -> bool:
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay
    ab_len2 = abx * abx + aby * aby
    if ab_len2 == 0:
        return False
    dot = apx * abx + apy * aby
    if dot < 0 or dot > ab_len2:
        return False
    cross = abs(apx * aby - apy * abx)
    return (cross / (ab_len2 ** 0.5)) <= tolerance
