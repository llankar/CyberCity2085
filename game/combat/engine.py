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

from .state import CombatState

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
    battle: BattleCheckResult = field(default_factory=BattleCheckResult)


class CombatEngine:
    """Own pure combat state transitions for a tactical battle."""

    def __init__(
        self,
        state: CombatState,
        *,
        can_enter: Callable[[int, int], bool] | None = None,
        cover_nodes: list | None = None,
    ) -> None:
        self.state = state
        self.can_enter = can_enter
        self.cover_nodes = cover_nodes

    def start_player_turn(self) -> BattleCheckResult:
        """Reset allied AP/statuses and advance from enemy to player phase."""
        for unit in self.state.allied_units:
            for msg in unit.tick_status_effects():
                if "bleeding" in msg:
                    name = unit.character.name if unit.character else unit.unit_type
                    self.state.logs.append(f"{name} is bleeding (-1 HP)")
            unit.reset_actions()
        if self.state.turn == "enemy":
            self.state.turn_number += 1
        self.state.turn = "player"
        self.state.active_index = 0
        self.state.logs.append(f"── Turn {self.state.turn_number} ──")
        return self.end_battle_check()

    def start_enemy_turn(
        self,
        *,
        defeated_player_units: list[Unit] | None = None,
        on_attack: Callable[[Unit, Unit, int], None] | None = None,
        on_defeated: Callable[[Unit], None] | None = None,
        on_overwatch_shot: Callable[[Unit, Unit, int], None] | None = None,
    ) -> BattleCheckResult:
        """Run the enemy phase without rendering or sound side effects."""
        for enemy in self.state.enemy_units:
            enemy.reset_actions()
        self.state.turn = "enemy"
        run_enemy_ai(
            self.state.allied_units,
            self.state.enemy_units,
            defeated_player_units=defeated_player_units,
            on_attack=on_attack,
            on_defeated=on_defeated,
            on_overwatch_shot=on_overwatch_shot,
            can_enter=self.can_enter,
            cover_nodes=self.cover_nodes,
        )
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
        if actor is None or actor.health <= 0:
            return CombatActionResult(False, "No active allied unit.", action=action_key)

        available = {action.key for action in available_combat_actions(actor)}
        if action_key not in available:
            return CombatActionResult(False, "Action unavailable.", action=action_key, actor=actor)

        before_ap = actor.action_points
        message = ""
        damage = 0
        defeated = False

        if action_key == "move":
            if actor.action_points <= 0 or move_delta is None:
                return CombatActionResult(False, "Move needs AP and a destination.", action=action_key, actor=actor)
            dx, dy = move_delta
            if self.can_enter is not None:
                nx, ny = actor.position[0] + dx, actor.position[1] + dy
                if not self.can_enter(nx, ny):
                    return CombatActionResult(False, "Destination blocked.", action=action_key, actor=actor)
            actor.move(dx, dy)
            message = "Unit moved."
        elif action_key in {"fire", "melee", "psi", "missiles"}:
            if target is None:
                return CombatActionResult(False, "Action needs a target.", action=action_key, actor=actor)
            if action_key == "melee":
                damage = actor.melee_attack(target)
            elif action_key == "psi":
                damage = actor.psi_attack(target)
            else:
                damage = actor.shoot(target)
            defeated = target.health <= 0
            if defeated and target in self.state.enemy_units:
                self.state.enemy_units.remove(target)
            message = f"{action_key.title()} deals {damage} damage."
        elif action_key == "first_aid":
            if actor.action_points <= 0 or not actor.stats:
                return CombatActionResult(False, "First aid needs AP.", action=action_key, actor=actor)
            before_hp = actor.health
            actor.health = min(actor.stats.max_hp, actor.health + 2)
            actor.stats.hp = actor.health
            actor.action_points -= 1
            message = f"First aid restores {actor.health - before_hp} HP."
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

    def end_battle_check(self) -> BattleCheckResult:
        """Return victory/defeat when one side has no living units left."""
        if not any(unit.health > 0 for unit in self.state.allied_units):
            return BattleCheckResult("defeat", "all_allies_down")
        if not any(unit.health > 0 for unit in self.state.enemy_units):
            return BattleCheckResult("victory", "all_enemies_down")
        return BattleCheckResult()
