"""Authoritative, render-independent tactical attack calculation.

Preview and execution both consume :class:`AttackContext`, preventing the HUD
from promising odds that the resolver does not actually use.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Iterable, TYPE_CHECKING

from game.cover_system import directional_cover, is_flanking
from game.combat.battlefield import trace_sight_line

if TYPE_CHECKING:
    from game.unit import Unit

GRID_SIZE = 32
BASE_CRIT_CHANCE = 0.12


@dataclass(frozen=True)
class AttackContext:
    attack_kind: str
    attack_stat: str
    attack_value: int
    base_defense: int
    cover_bonus: int
    effective_defense: int
    hit_chance: float
    crit_chance: float
    normal_damage: int
    critical_damage: int
    distance_cells: float
    range_cells: int
    in_range: bool
    flanking: bool
    line_blocked: bool
    line_warning: str | None
    ap_cost: int = 1
    resource_cost: int = 0


@dataclass(frozen=True)
class AttackResolution:
    success: bool
    context: AttackContext
    hit: bool = False
    critical: bool = False
    damage: int = 0
    defeated: bool = False
    consumed_ap: int = 0
    consumed_resource: int = 0
    reason: str = ""


def _line_warning(attacker: "Unit", defender: "Unit", allies: Iterable["Unit"]) -> str | None:
    ax, ay = attacker.position
    tx, ty = defender.position
    for ally in allies:
        if ally is attacker or ally is defender or ally.health <= 0:
            continue
        px, py = ally.position
        abx, aby = tx - ax, ty - ay
        apx, apy = px - ax, py - ay
        length2 = abx * abx + aby * aby
        if not length2:
            continue
        dot = apx * abx + apy * aby
        if 0 <= dot <= length2:
            cross = abs(apx * aby - apy * abx)
            if cross / (length2 ** 0.5) <= GRID_SIZE * 0.35:
                return "ALLY IN LINE"
    return None


def build_attack_context(
    attacker: "Unit",
    defender: "Unit",
    attack_kind: str,
    *,
    cover_nodes: list | None = None,
    allies: Iterable["Unit"] = (),
) -> AttackContext:
    """Build the exact tactical calculation used by preview and execution."""
    normalized = {"shoot": "fire"}.get(attack_kind, attack_kind)
    stat = "str" if normalized == "melee" else "psi" if normalized == "psi" else "agi"
    attack_value = max(0, int(getattr(attacker.stats, stat, 0))) if attacker.stats else 0
    damage_bonus = 2 if normalized == "missiles" else 0
    accuracy_bonus = 2 if normalized == "missiles" else 0
    attack_value += accuracy_bonus
    base_defense = max(0, int(getattr(defender.stats, "defense", 0))) if defender.stats else 0
    flanking = bool(cover_nodes and is_flanking(attacker, defender, cover_nodes))
    _, facing_bonus = directional_cover(attacker, defender, cover_nodes or [])
    cover_bonus = (
        facing_bonus
        if cover_nodes
        else max(0, int(getattr(defender, "in_cover_bonus", 0)))
    )
    sight_line = trace_sight_line(attacker.position, defender.position, cover_nodes)
    effective_defense = base_defense + cover_bonus
    total = attack_value + effective_defense
    hit_chance = attack_value / total if attack_value > 0 and total > 0 else 0.0
    range_cells = (
        1 if normalized == "melee"
        else 10 if normalized == "psi"
        else max(1, int(getattr(attacker, "attack_range", 1)))
    )
    distance_cells = attacker.distance_to(defender) / GRID_SIZE
    in_range = distance_cells <= range_cells
    normal_damage = attack_value + damage_bonus
    if normalized == "psi" and getattr(defender, "is_psi_defending", False):
        normal_damage = max(0, normal_damage - 1)
    elif normalized != "psi" and getattr(defender, "is_defending", False):
        normal_damage = max(0, normal_damage - 1)
    return AttackContext(
        attack_kind=normalized,
        attack_stat=stat,
        attack_value=attack_value,
        base_defense=base_defense,
        cover_bonus=cover_bonus,
        effective_defense=effective_defense,
        hit_chance=max(0.0, min(1.0, hit_chance)),
        crit_chance=BASE_CRIT_CHANCE,
        normal_damage=normal_damage,
        critical_damage=max(0, normal_damage * 2),
        distance_cells=distance_cells,
        range_cells=range_cells,
        in_range=in_range,
        flanking=flanking,
        line_blocked=not sight_line.clear,
        line_warning=_line_warning(attacker, defender, allies),
        resource_cost=1 if normalized == "missiles" else 0,
    )


def resolve_attack(
    attacker: "Unit",
    defender: "Unit",
    attack_kind: str,
    *,
    cover_nodes: list | None = None,
    allies: Iterable["Unit"] = (),
    rng: Callable[[], float] | None = None,
    spend_ap: bool = True,
) -> AttackResolution:
    """Resolve and apply one attack using the same context shown by the HUD."""
    rng = rng or random.random
    context = build_attack_context(
        attacker, defender, attack_kind, cover_nodes=cover_nodes, allies=allies
    )
    if not attacker.stats or not defender.stats:
        return AttackResolution(False, context, reason="missing_stats")
    if not context.in_range:
        return AttackResolution(False, context, reason="out_of_range")
    if context.line_blocked:
        return AttackResolution(False, context, reason="line_blocked")
    if spend_ap and attacker.action_points < context.ap_cost:
        return AttackResolution(False, context, reason="insufficient_ap")
    if context.resource_cost:
        asset = getattr(attacker, "spec_ops_asset", None)
        if asset is None or int(getattr(asset, "missile_capacity", 0)) < context.resource_cost:
            return AttackResolution(False, context, reason="no_missiles")

    consumed_ap = context.ap_cost if spend_ap else 0
    if spend_ap:
        attacker.action_points -= consumed_ap
    consumed_resource = 0
    if context.resource_cost:
        attacker.spec_ops_asset.missile_capacity -= context.resource_cost
        consumed_resource = context.resource_cost

    hit = rng() < context.hit_chance
    critical = hit and rng() < context.crit_chance
    damage = context.critical_damage if critical else context.normal_damage if hit else 0
    before_hp = defender.stats.hp
    defender.stats.hp = max(0, defender.stats.hp - damage)
    defender.health = defender.stats.hp
    attacker._last_crit = critical
    if hit:
        defender.is_defending = False
        defender.is_psi_defending = False
    return AttackResolution(
        True,
        context,
        hit=hit,
        critical=critical,
        damage=max(0, before_hp - defender.stats.hp),
        defeated=defender.health <= 0,
        consumed_ap=consumed_ap,
        consumed_resource=consumed_resource,
        reason="critical" if critical else "hit" if hit else "miss",
    )
