"""Pure tactical combat transitions.

This module deliberately avoids Arcade, sound, view navigation, and campaign
fallout.  It mutates ``CombatState`` and returns compact results so the battle
view can decide how to render, animate, and route between screens.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from game.combat_actions import available_combat_actions
from game.combat_system import run_enemy_ai
from game.unit import Unit
from game.unit import STATUS_BLEEDING

from .attack_resolution import AttackResolution, resolve_attack
from .events import (
    CombatEventResult,
    events_from_mission,
    resolve_combat_events as resolve_event_results,
)
from .state import CombatState
from .objectives import ObjectiveResult, evaluate_objective, interact_objective

BattleOutcome = Literal["victory", "defeat"]


@dataclass(frozen=True)
class BattleCheckResult:
    """Result of checking whether battle-ending conditions are met."""

    outcome: BattleOutcome | None = None
    reason: str = ""

    @property
    def ended(self) -> bool:
        return self.outcome is not None


@dataclass(frozen=True)
class CombatActionResult:
    """Inspectable outcome for one player-facing tactical action."""

    success: bool
    message: str = ""
    action: str = ""
    actor: Unit | None = None
    target: Unit | None = None
    damage: int = 0
    defeated_target: bool = False
    consumed_ap: int = 0
    consumed_resource: int = 0
    attack_resolution: AttackResolution | None = None
    battle: BattleCheckResult = field(default_factory=BattleCheckResult)


class CombatEngine:
    """Own pure combat state transitions for a tactical battle."""

    def __init__(
        self,
        state: CombatState,
        *,
        can_enter: Callable[[int, int], bool] | None = None,
        cover_nodes: list | None = None,
        terrain_profile=None,
    ) -> None:
        self.state = state
        self.can_enter = can_enter
        self.cover_nodes = cover_nodes
        self.terrain_profile = terrain_profile
        self._memory_participants = tuple(unit for unit in state.allied_units if unit.health > 0)
        from .enemy_orders import EnemyOrders
        self.enemy_orders = EnemyOrders()

    def enemy_intents(self):
        """Return the same reservations consumed by the enemy activation."""
        self.refresh_cover()
        self.enemy_orders.reconcile(
            self.state.enemy_units, self.state.allied_units, self.state.objective,
            self.cover_nodes, self.state.logs,
            can_enter=self.can_enter,
            terrain_profile=self.terrain_profile,
        )
        return self.enemy_orders.intents(self.state.enemy_units)

    def refresh_cover(self):
        if self.cover_nodes is not None:
            from game.cover_system import cover_defense_bonus
            for unit in [*self.state.allied_units, *self.state.enemy_units]:
                unit.in_cover_bonus = cover_defense_bonus(unit, self.cover_nodes)

    def interrupt_enemy_plan(self, enemy, reason):
        self.enemy_orders.interrupt(
            enemy, reason, self.state.allied_units, self.state.objective,
            self.cover_nodes, self.state.logs,
            can_enter=self.can_enter,
            terrain_profile=self.terrain_profile,
        )

    def release_enemy_projection(self, enemy, position) -> None:
        from .battlefield import HazardZone

        zones = list(self.state.tactical_flags.get("hazards", ()))
        zones.append(HazardZone("sludge", tuple(position), radius_cells=0,
                                expires_after_turn=self.state.turn_number + 1))
        self.state.tactical_flags["hazards"] = zones
        self.state.logs.append(f"Mutant projection at {position}: 2 AP committed; sludge lasts one round.")

    def apply_battlefield_exposure(self, units: list[Unit]) -> None:
        """Resolve environmental exposure once when a side starts its phase."""
        from .battlefield import apply_hazard

        zones = [zone for zone in self.state.tactical_flags.get("hazards", ())
                 if zone.expires_after_turn is None or self.state.turn_number <= zone.expires_after_turn]
        self.state.tactical_flags["hazards"] = zones
        for unit in units:
            sludge_applied = False
            for zone in zones:
                # Several specialists cannot multiply the same tile's punishment.
                if zone.kind == "sludge" and sludge_applied:
                    continue
                effect = apply_hazard(unit, zone)
                if zone.kind == "sludge" and (effect.damage or effect.ap_lost):
                    sludge_applied = True
                if effect.damage or effect.ap_lost:
                    name = unit.character.name if unit.character else unit.unit_type
                    self.state.logs.append(
                        f"{name}: {effect.kind.upper()} -{effect.damage} HP / -{effect.ap_lost} AP"
                    )

    def start_player_turn(self) -> BattleCheckResult:
        """Reset allied AP/statuses and advance from enemy to player phase."""
        from .agent_moments import record_panic
        for unit in self.state.allied_units:
            record_panic(self.state, unit)
            unit.reset_actions()
            for msg in unit.tick_status_effects():
                if msg in {"bleeding", "burning", "contaminated"}:
                    name = unit.character.name if unit.character else unit.unit_type
                    damage = 2 if msg == "burning" else 1
                    self.state.logs.append(f"{name} is {msg} (-{damage} HP)")
        if self.state.turn == "enemy":
            self.state.turn_number += 1
        self.state.turn = "player"
        self.state.active_index = 0
        self.apply_battlefield_exposure(self.state.allied_units)
        self.refresh_cover()
        self.enemy_orders.reserve(
            self.state.enemy_units, self.state.allied_units, self.state.objective,
            self.cover_nodes, refresh=True,
            can_enter=self.can_enter,
            terrain_profile=self.terrain_profile,
        )
        self.state.logs.append(f"── Turn {self.state.turn_number} ──")
        return self.end_battle_check()

    def resolve_combat_events(
        self,
        *,
        battlefield_size: tuple[int, int] = (1280, 720),
    ) -> list[CombatEventResult]:
        """Resolve newly active mid-battle events without rendering side effects."""
        triggered = self.state.tactical_flags.get("triggered_combat_event_keys", set())
        results, updated_triggered = resolve_event_results(
            events_from_mission(self.state.mission),
            turn_number=self.state.turn_number,
            triggered_keys=triggered,
            battlefield_size=battlefield_size,
        )
        self.state.tactical_flags["triggered_combat_event_keys"] = updated_triggered
        return results

    def start_enemy_turn(
        self,
        *,
        defeated_player_units: list[Unit] | None = None,
        on_attack: Callable[[Unit, Unit, int], None] | None = None,
        on_defeated: Callable[[Unit], None] | None = None,
        on_overwatch_shot: Callable[[Unit, Unit, int], None] | None = None,
    ) -> BattleCheckResult:
        """Run the enemy phase without rendering or sound side effects."""
        self.enemy_intents()
        for enemy in self.state.enemy_units:
            enemy.reset_actions()
            for status in enemy.tick_status_effects():
                if status in {"bleeding", "burning", "contaminated"}:
                    self.state.logs.append(f"{enemy.unit_type} is {status}")
        self.state.turn = "enemy"
        self.apply_battlefield_exposure(self.state.enemy_units)
        results = run_enemy_ai(
            self.state.allied_units,
            self.state.enemy_units,
            defeated_player_units=defeated_player_units,
            on_attack=on_attack,
            on_defeated=on_defeated,
            on_overwatch_shot=on_overwatch_shot,
            can_enter=self.can_enter,
            cover_nodes=self.cover_nodes,
            terrain_profile=self.terrain_profile,
            movement_mode=self.state.movement_mode,
            objective=self.state.objective,
            reserved_orders=self.enemy_orders.orders,
            on_plan_interrupted=self.interrupt_enemy_plan,
            on_projection=self.release_enemy_projection,
        )
        for result in results:
            if result.decision_reason in {"precision_lock", "precision_missed"}:
                name = getattr(getattr(result.target, "character", None), "name", "agent")
                self.state.logs.append(f"{name}: {result.decision_reason.upper()} / specialist committed 2 AP")
            if result.infection_transmitted:
                name = getattr(getattr(result.target, "character", None), "name", "agent")
                self.state.logs.append(f"{name}: STARVER INFECTION — INCURABLE. Conversion in 3 strategic days.")
            if result.decision_reason in {"suppressing_fire", "suppression_missed"}:
                name = getattr(getattr(result.target, "character", None), "name", "agent")
                effect = "SUPPRESSED" if result.decision_reason == "suppressing_fire" else "suppression missed"
                self.state.logs.append(f"{name}: {effect} / linked heavy committed 2 AP")
        return self.end_battle_check()

    def perform_action(
        self,
        action_key: str,
        *,
        actor: Unit | None = None,
        target: Unit | None = None,
        move_delta: tuple[int, int] | None = None,
    ) -> CombatActionResult:
        """Apply one player action when it can be resolved without view input."""
        if self.state.turn != "player":
            return CombatActionResult(False, "Not the player turn.", action=action_key)
        actor = actor or self.state.active_unit
        if actor is None or actor.health <= 0 or not any(actor is unit for unit in self.state.allied_units):
            return CombatActionResult(False, "No active allied unit.", action=action_key)
        self.enemy_intents()

        available = {action.key for action in available_combat_actions(actor)}
        if action_key not in available:
            return CombatActionResult(False, "Action unavailable.", action=action_key, actor=actor)

        before_ap = actor.action_points
        message = ""
        damage = 0
        defeated = False
        consumed_resource = 0
        attack_resolution = None

        if action_key == "move":
            if actor.action_points <= 0 or move_delta is None:
                return CombatActionResult(False, "Move needs AP and a destination.", action=action_key, actor=actor)
            dx, dy = move_delta
            from .movement import CELL_SIZE, can_enter_cell
            if self.state.movement_mode == "tactical_grid" and (dx,dy) not in (
                    (CELL_SIZE,0),(-CELL_SIZE,0),(0,CELL_SIZE),(0,-CELL_SIZE)):
                return CombatActionResult(False, "Move one cardinal grid cell.", action=action_key, actor=actor)
            nx, ny = actor.position[0]+dx, actor.position[1]+dy
            if not can_enter_cell(nx,ny,terrain_profile=self.terrain_profile,
                                  allied_units=self.state.allied_units,enemy_units=self.state.enemy_units,
                                  exclude=actor,movement_mode=self.state.movement_mode):
                return CombatActionResult(False, "Destination blocked.", action=action_key, actor=actor)
            if any(not node.passable and (node.world_x,node.world_y)==(nx,ny) for node in self.cover_nodes or []):
                return CombatActionResult(False, "Destination blocked.", action=action_key, actor=actor)
            if self.can_enter is not None:
                nx, ny = actor.position[0] + dx, actor.position[1] + dy
                if not self.can_enter(nx, ny):
                    return CombatActionResult(False, "Destination blocked.", action=action_key, actor=actor)
            actor.move(dx, dy)
            message = "Unit moved."
        elif action_key in {"fire", "melee", "psi", "missiles"}:
            if target is None or target.health <= 0 or not any(target is unit for unit in self.state.enemy_units):
                return CombatActionResult(False, "Action needs a living hostile target.", action=action_key, actor=actor)
            attack_resolution = resolve_attack(
                actor,
                target,
                action_key,
                cover_nodes=self.cover_nodes,
                allies=self.state.allied_units,
            )
            if not attack_resolution.success:
                readable_reason = attack_resolution.reason.replace("_", " ")
                return CombatActionResult(
                    False,
                    f"Attack unavailable: {readable_reason}.",
                    action=action_key,
                    actor=actor,
                    target=target,
                    attack_resolution=attack_resolution,
                )
            damage = attack_resolution.damage
            defeated = attack_resolution.defeated
            consumed_resource = attack_resolution.consumed_resource
            from .agent_moments import record_last_stand
            record_last_stand(self.state, actor, target, defeated=defeated)
            if defeated and target in self.state.enemy_units:
                self.state.enemy_units.remove(target)
            outcome = "CRITICAL" if attack_resolution.critical else "HIT" if attack_resolution.hit else "MISS"
            flank = " · FLANK" if attack_resolution.context.flanking else ""
            resource = " · 1 missile" if consumed_resource else ""
            message = f"{action_key.title()} {outcome}: {damage} damage{flank}{resource}."
        elif action_key == "first_aid":
            if actor.action_points <= 0 or not actor.stats:
                return CombatActionResult(False, "First aid needs AP.", action=action_key, actor=actor)
            aid_target = target or actor
            if (aid_target.health <= 0 or not any(aid_target is unit for unit in self.state.allied_units)
                    or not aid_target.stats or actor.distance_to(aid_target) > 32):
                return CombatActionResult(False, "First aid target is out of reach.", action=action_key, actor=actor)
            before_hp = aid_target.health
            aid_target.health = min(aid_target.stats.max_hp, aid_target.health + 2)
            aid_target.stats.hp = aid_target.health
            cleared_bleeding = aid_target.has_status(STATUS_BLEEDING)
            aid_target.clear_status(STATUS_BLEEDING)
            actor.spend_action_points(1)
            from .agent_moments import record_rescue
            record_rescue(self.state, actor, aid_target, before_hp=before_hp, cleared_bleeding=cleared_bleeding)
            suffix = " and clears BLEEDING" if cleared_bleeding else ""
            message = f"First aid restores {aid_target.health - before_hp} HP{suffix}."
        elif action_key == "overwatch":
            if not actor.set_overwatch():
                return CombatActionResult(False, "Overwatch unavailable.", action=action_key, actor=actor)
            message = "Unit is on OVERWATCH."
        elif action_key == "defend":
            if not actor.defend():
                return CombatActionResult(False, "Defend needs AP.", action=action_key, actor=actor)
            message = "Unit is defending."
        elif action_key == "end_turn":
            actor.action_points = 0
            message = "Unit ends turn."
        else:
            return CombatActionResult(False, "Action is handled by the view.", action=action_key, actor=actor)

        consumed = max(0, before_ap - actor.action_points)
        battle = self.end_battle_check()
        return CombatActionResult(
            True,
            message,
            action=action_key,
            actor=actor,
            target=target,
            damage=damage,
            defeated_target=defeated,
            consumed_ap=consumed,
            consumed_resource=consumed_resource,
            attack_resolution=attack_resolution,
            battle=battle,
        )

    def advance_active_player(self) -> BattleCheckResult:
        """Skip inactive/dead allies and start enemy phase when none can act."""
        while self.state.active_index < len(self.state.allied_units) and (
            self.state.allied_units[self.state.active_index].action_points <= 0
            or self.state.allied_units[self.state.active_index].health <= 0
        ):
            self.state.active_index += 1
        if self.state.active_index >= len(self.state.allied_units):
            return self.start_enemy_turn()
        return self.end_battle_check()

    def interact_with_objective(self, actor: Unit | None = None) -> ObjectiveResult:
        """Advance the active mission objective through the pure lifecycle."""
        actor = actor or self.state.active_unit
        if self.state.turn != "player" or (actor is not None and not any(actor is unit for unit in self.state.allied_units)):
            return ObjectiveResult("ongoing", "interaction_unavailable", "Only allied operatives may interact during the player phase.",
                                   getattr(self.state.objective, "kind", "eliminate"))
        if actor is None:
            return ObjectiveResult(
                "ongoing",
                "no_active_unit",
                "No active allied unit.",
                getattr(self.state.objective, "kind", "eliminate"),
            )
        result = interact_objective(
            self.state.objective,
            actor,
            turn_number=self.state.turn_number,
            enemy_units=self.state.enemy_units,
        )
        contributions = self.state.tactical_flags.setdefault("objective_contributions", {})
        if result.reason in {"objective_progress", "objective_completed"} and result.actor_name:
            contributions[result.actor_name] = contributions.get(result.actor_name, 0) + 1
        return result

    def objective_result(self) -> ObjectiveResult:
        """Return the current mission result without rendering side effects."""
        return evaluate_objective(
            self.state.objective,
            turn_number=self.state.turn_number,
            allied_units=self.state.allied_units,
            enemy_units=self.state.enemy_units,
            assassination_target=self.state.tactical_flags.get("assassination_target"),
            defend_turns_required=int(
                self.state.tactical_flags.get("defend_turns_required", 4)
            ),
        )

    def end_battle_check(self) -> BattleCheckResult:
        """Return victory/defeat from the authoritative objective lifecycle."""
        from .agent_moments import record_losses
        record_losses(self.state, self._memory_participants)
        objective = self.objective_result()
        if objective.status == "victory":
            return BattleCheckResult("victory", objective.reason)
        if objective.status == "defeat":
            return BattleCheckResult("defeat", objective.reason)
        return BattleCheckResult()
