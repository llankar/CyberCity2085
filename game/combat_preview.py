"""Combat preview helpers shared by tactical UI and combat resolution math."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .unit import Unit
from .combat.attack_resolution import build_attack_context

GRID_SIZE = 32


@dataclass(frozen=True)
class AttackPreview:
    min_damage: int
    max_damage: int
    hit_chance: float
    crit_chance: float
    warning: str | None = None
    cover_bonus: int = 0
    flanking: bool = False
    in_range: bool = True
    ap_cost: int = 1
    resource_cost: int = 0


def estimate_attack_preview(
    attacker: Unit,
    defender: Unit,
    attack_kind: str,
    *,
    cover_nodes: list | None = None,
    allies: Iterable[Unit] = (),
) -> AttackPreview:
    """Estimate combat outcome from the same core values used by attack resolution."""
    context = build_attack_context(
        attacker, defender, attack_kind, cover_nodes=cover_nodes, allies=allies
    )
    return AttackPreview(
        min_damage=context.normal_damage,
        max_damage=context.critical_damage,
        hit_chance=context.hit_chance,
        crit_chance=context.crit_chance,
        warning="LINE BLOCKED" if context.line_blocked else context.line_warning,
        cover_bonus=context.cover_bonus,
        flanking=context.flanking,
        in_range=context.in_range,
        ap_cost=context.ap_cost,
        resource_cost=context.resource_cost,
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
