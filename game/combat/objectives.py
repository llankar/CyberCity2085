"""Pure lifecycle and contribution rules for tactical mission objectives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from game.mission_objectives import (
    BattleObjective,
    interact_with_objective,
    objective_failed_by_enemy_positions,
)

ObjectiveStatus = Literal["ongoing", "victory", "defeat"]


@dataclass(frozen=True)
class ObjectiveResult:
    status: ObjectiveStatus
    reason: str
    message: str
    objective_kind: str
    progress: int = 0
    required: int = 0
    phase: str = ""
    actor_name: str = ""

    @property
    def ended(self) -> bool:
        return self.status != "ongoing"


def _result(
    objective: BattleObjective | None,
    status: ObjectiveStatus,
    reason: str,
    message: str,
    *,
    actor_name: str = "",
) -> ObjectiveResult:
    return ObjectiveResult(
        status,
        reason,
        message,
        objective.kind if objective else "eliminate",
        objective.progress if objective else 0,
        objective.required_interactions if objective else 0,
        objective.phase_text if objective else "ELIMINATE HOSTILES",
        actor_name,
    )


def interact_objective(
    objective: BattleObjective | None,
    actor,
    *,
    turn_number: int,
    enemy_units: list | None = None,
) -> ObjectiveResult:
    """Advance one objective beat, at most once per tactical turn."""
    if objective is None:
        return _result(None, "ongoing", "no_interactable_objective", "No interactable objective.")
    actor_name = (
        actor.character.name if getattr(actor, "character", None)
        else actor.spec_ops_asset.name if getattr(actor, "spec_ops_asset", None)
        else getattr(actor, "unit_type", "Unit")
    )
    if objective.failed:
        return _result(objective, "defeat", "objective_failed", objective.failure_message, actor_name=actor_name)
    if objective.completed:
        return _result(objective, "ongoing", "objective_already_complete", objective.completion_message, actor_name=actor_name)
    if objective.interaction_turns and objective.interaction_turns[-1] == turn_number:
        return _result(
            objective,
            "ongoing",
            "interaction_already_used_this_turn",
            f"{objective.label} requires another turn to advance.",
            actor_name=actor_name,
        )

    living_enemies = [unit for unit in (enemy_units or []) if unit.health > 0]
    ox, oy = objective.position
    if any(
        (unit.position[0] - ox) ** 2 + (unit.position[1] - oy) ** 2 <= 32**2
        for unit in living_enemies
    ):
        return _result(
            objective,
            "ongoing",
            "objective_contested",
            f"{objective.label} is contested. Clear nearby hostiles first.",
            actor_name=actor_name,
        )

    previous_progress = objective.progress
    completed, message = interact_with_objective(actor.position, objective)
    advanced = objective.progress > previous_progress
    if advanced:
        objective.interaction_turns.append(turn_number)
    if completed and objective.hold_turns_after_interaction:
        objective.hold_until_turn = turn_number + objective.hold_turns_after_interaction
        message = f"{message} Hold until turn {objective.hold_until_turn}."
    status: ObjectiveStatus = (
        "victory" if completed and objective.hold_until_turn is None else "ongoing"
    )
    return _result(
        objective,
        status,
        (
            "objective_completed"
            if status == "victory"
            else "objective_progress"
            if advanced
            else "interaction_blocked"
        ),
        message,
        actor_name=actor_name,
    )


def evaluate_objective(
    objective: BattleObjective | None,
    *,
    turn_number: int,
    allied_units: list,
    enemy_units: list,
    assassination_target=None,
    defend_turns_required: int = 4,
) -> ObjectiveResult:
    """Evaluate the authoritative success/failure state for one battle."""
    if not any(unit.health > 0 for unit in allied_units):
        return _result(objective, "defeat", "all_allies_down", "All allied operatives are down.")

    living_enemies = [unit for unit in enemy_units if unit.health > 0]
    if objective is None:
        if not living_enemies:
            return _result(None, "victory", "all_enemies_down", "All hostiles neutralized.")
        return _result(None, "ongoing", "elimination_in_progress", "Neutralize remaining hostiles.")

    failed, failure = objective_failed_by_enemy_positions(
        [unit.position for unit in living_enemies], objective
    )
    if failed:
        objective.failed = True
        objective.failure_message = failure
        return _result(objective, "defeat", "objective_breached", failure)

    if objective.kind == "assassination":
        target_alive = assassination_target is not None and assassination_target.health > 0
        if assassination_target is not None and not target_alive:
            objective.completed = True
            return _result(objective, "victory", "target_eliminated", objective.completion_message)
        return _result(objective, "ongoing", "target_alive", "High-value target remains active.")

    if objective.kind == "defend":
        if turn_number > defend_turns_required:
            objective.completed = True
            return _result(objective, "victory", "position_held", objective.completion_message)
        return _result(
            objective,
            "ongoing",
            "hold_in_progress",
            f"Hold position: turn {turn_number}/{defend_turns_required}.",
        )

    if objective.completed:
        if objective.hold_until_turn is not None and turn_number < objective.hold_until_turn:
            return _result(
                objective,
                "ongoing",
                "counterpush_active",
                f"Counterpush active until turn {objective.hold_until_turn}.",
            )
        return _result(objective, "victory", "objective_completed", objective.completion_message)

    if not living_enemies and objective.kind in {"containment"}:
        objective.completed = True
        return _result(objective, "victory", "threat_contained", objective.completion_message)

    return _result(objective, "ongoing", "objective_in_progress", objective.progress_text)
