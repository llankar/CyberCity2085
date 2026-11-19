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
    attack_stance_bonus: int = 0  # BREACH:+20 dmg/+5 hit, GUARD:-30 agi
    psi_state_penalty: float = 0.0  # RISK state reduces effectiveness


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
    infection_transmitted: bool = False
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
    
    # Import stance/pstate system here to avoid circular imports
    from game.agent_specializations import (
        default_stance_for_unit, 
        default_psi_state_for_unit, 
        Stance, 
        PsiState
    )
    
    # Determine attacker's active stance and psi state for combat effects
    attack_stance = default_stance_for_unit(attacker)
    active_psi_state = default_psi_state_for_unit(attacker)
    
    # Calculate stance bonuses (Samurai-specific, applied to relevant stats)
    stance_bonus = 0
    stance_penalty = 0
    
    if attack_stance == Stance.BREACH:
        # BREACH mode: +20% damage and hit chance for offensive actions
        # Base values on typical samurai str/agi (around 6-8), scaled by role
        from game.stats import PlayerStats
        melee_stat = max(1, int(getattr(attacker.stats, "str", 6))) if attacker.stats else 6
        stance_bonus = max(0, int(melee_stat * 0.25))  # Up to +25% damage bonus
    elif attack_stance == Stance.GUARD:
        # GUARD mode: -30% agility (movement/precision tradeoff), no offensive penalty in calculation
        # Note: this affects movement costs and could affect hit chance for agi-based attacks
        from game.stats import PlayerStats
        melee_stat = max(1, int(getattr(attacker.stats, "str", 6))) if attacker.stats else 6
        stance_penalty = max(0, int(melee_stat * 0.25))  # Up to -25% effective damage
    
    # Calculate psi state penalties (Psi-specific)
    psi_state_factor = 1.0
    if active_psi_state == PsiState.RISK:
        # RISK state: -15% effectiveness per turn of overdrive/stress overload
        psi_state_factor = 0.85
    elif active_psi_state == PsiState.CONTROL:
        # CONTROL state: +10% bonus for well-calibrated psi use
        psi_state_factor = 1.10
    
    precision = attack_kind == "precision"
    normalized = {"shoot": "fire", "precision": "fire"}.get(attack_kind, attack_kind)
    stat = "str" if normalized == "melee" else "psi" if normalized == "psi" else "agi"
    
    # Apply stance bonuses to attack value (BREACH boosts, GUARD reduces for precision trades)
    base_attack_value = max(0, int(getattr(attacker.stats, stat, 0))) if attacker.stats else 0
    adjusted_attack_value = base_attack_value + stance_bonus - stance_penalty
    
    damage_bonus = 2 if normalized == "missiles" else 0
    accuracy_bonus = 2 if normalized == "missiles" else 0
    adjusted_attack_value += accuracy_bonus
    
    # Apply psi state multiplier to attack effectiveness
    if adjusted_attack_value > 0 and psi_state_factor != 1.0:
        adjusted_attack_value = max(1, int(adjusted_attack_value * psi_state_factor))
    if precision:
        adjusted_attack_value += 2
    
    base_defense = max(0, int(getattr(defender.stats, "defense", 0))) if defender.stats else 0
    flanking = bool(cover_nodes and is_flanking(attacker, defender, cover_nodes))
    _, facing_bonus = directional_cover(attacker, defender, cover_nodes or [])
    cover_bonus = (
        facing_bonus
        if cover_nodes
        else max(0, int(getattr(defender, "in_cover_bonus", 0)))
    )
    sight_line = trace_sight_line(attacker.position, defender.position, cover_nodes)
    
    # Calculate hit chance with stance effects
    effective_defense = base_defense + cover_bonus
    
    # Stance affects hit calculation based on stat type:
    # BREACH boosts melee/physical attacks, GUARD slightly hinders them (precision tradeoff)
    total = adjusted_attack_value + effective_defense
    hit_chance = adjusted_attack_value / total if adjusted_attack_value > 0 and total > 0 else 0.0
    
    range_cells = (
        1 if normalized == "melee"
        else 10 if normalized == "psi"
        else max(1, int(getattr(attacker, "attack_range", 1)))
    )
    distance_cells = attacker.distance_to(defender) / GRID_SIZE
    in_range = distance_cells <= range_cells
    
    # Calculate damage with stance multipliers
    normal_damage = adjusted_attack_value + damage_bonus
    from game.enemy_themes import normalize_enemy_theme
    if normalized == "melee" and attacker.unit_type == "enemy" and normalize_enemy_theme(attacker.enemy_theme) == "starver":
        normal_damage += max(2, (normal_damage + 3) // 4)
    if normalized == "psi" and getattr(defender, "is_psi_defending", False):
        normal_damage = max(0, int(normal_damage * 0.9))
    elif normalized != "psi" and getattr(defender, "is_defending", False):
        normal_damage = max(0, int(normal_damage * 0.9))
    
    return AttackContext(
        attack_kind=normalized,
        attack_stat=stat,
        attack_value=adjusted_attack_value,  # Use stance-adjusted value
        base_defense=base_defense,
        cover_bonus=cover_bonus,
        effective_defense=effective_defense,
        hit_chance=max(0.0, min(1.0, hit_chance)),
        crit_chance=0.30 if precision else BASE_CRIT_CHANCE,
        normal_damage=normal_damage,  # Already applies psi RISK factor via adjusted_attack_value
        critical_damage=max(0, int(normal_damage * 2)),
        distance_cells=distance_cells,
        range_cells=range_cells,
        in_range=in_range,
        flanking=flanking,
        line_blocked=not sight_line.clear,
        line_warning=_line_warning(attacker, defender, allies),
        resource_cost=1 if normalized == "missiles" else 0,
        ap_cost=2 if precision else 1,
        attack_stance_bonus=stance_bonus,
        psi_state_penalty=max(0.0, 1.0 - psi_state_factor),
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
    infected = False
    if hit and damage > 0 and context.attack_kind == "melee":
        from game.starver_infection import transmit_bite
        infected = transmit_bite(attacker, defender, rng)
    return AttackResolution(
        True,
        context,
        hit=hit,
        critical=critical,
        damage=max(0, before_hp - defender.stats.hp),
        defeated=defender.health <= 0,
        consumed_ap=consumed_ap,
        consumed_resource=consumed_resource,
        infection_transmitted=infected,
        reason="critical" if critical else "hit" if hit else "miss",
    )
