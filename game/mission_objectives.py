from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mission_templates import MissionTemplate

GRID_SIZE = 32
DEFAULT_OBJECTIVE_POSITION = (448, 320)
FALLBACK_OBJECTIVE_TYPE = "eliminate"
OBJECTIVE_TYPE_ALIASES = {
    "safe_extraction": "extract",
    "sabotage_window": "sabotage",
    "data_with_detour": "data_theft",
}
SUPPORTED_OBJECTIVE_TYPES = {
    "extract",
    "sabotage",
    "data_theft",
    "defend",
    "assassination",
    FALLBACK_OBJECTIVE_TYPE,
}

_OBJECTIVE_PROTOTYPES = {
    "extract": {
        "label": "WITNESS",
        "description": "reach WITNESS extraction point, secure them, then evacuate",
        "interaction_prompt": "Press E near WITNESS to secure extraction.",
        "success_condition": "Squad reaches the marker and confirms extraction.",
        "failure_condition": "Extraction fails if the squad is wiped before securing WITNESS.",
        "completion_message": "Witness secured. Extraction complete.",
        "required_interactions": 1,
    },
    "sabotage": {
        "label": "RELAY",
        "description": "plant a charge or hack RELAY, then survive the counterpush",
        "interaction_prompt": "Press E near RELAY to plant the sabotage charge.",
        "success_condition": "Charge is planted or device is hacked.",
        "failure_condition": "Sabotage fails if the squad is wiped before arming RELAY.",
        "completion_message": "Relay burned. Sabotage complete.",
        "required_interactions": 1,
    },
    "data_theft": {
        "label": "CACHE",
        "description": "hold CACHE for two interaction turns while the team protects the runner",
        "interaction_prompt": "Press E near CACHE to copy data and maintain the link.",
        "success_condition": "Two CACHE interaction turns complete.",
        "failure_condition": "Data theft fails if the squad is wiped before download finishes.",
        "completion_message": "Cache copied. Data theft complete.",
        "required_interactions": 2,
    },
    "defend": {
        "label": "POSITION",
        "description": "hold POSITION until extraction window",
        "completion_message": "Position held. Extraction inbound.",
    },
    "assassination": {
        "label": "TARGET",
        "description": "eliminate HIGH-VALUE TARGET",
        "completion_message": "Target eliminated. Mission accomplished.",
    },
}


@dataclass
class BattleObjective:
    """Small interactable mission objective placed on the tactical battlefield."""

    kind: str
    position: tuple[int, int]
    label: str
    completed: bool = False
    progress: int = 0
    description: str = "complete the battlefield objective"
    completion_message: str = "Objective complete."
    interaction_prompt: str = "Press E near the marker to interact."
    success_condition: str = "Complete the objective marker."
    failure_condition: str = "Mission fails if the squad is wiped before completion."
    required_interactions: int = 1

    @property
    def status_text(self) -> str:
        state = "complete" if self.completed else self.description
        return f"Objective: {state}"

    @property
    def progress_text(self) -> str:
        if self.completed:
            return "Progress: complete"
        total = max(1, self.required_interactions)
        return f"Progress: {self.progress}/{total}"


def normalize_objective_type(objective_type: str | None) -> str:
    """Return a supported objective type, preserving old saves with safe elimination."""
    normalized = OBJECTIVE_TYPE_ALIASES.get(str(objective_type or ""), objective_type)
    if normalized in SUPPORTED_OBJECTIVE_TYPES:
        return str(normalized)
    return FALLBACK_OBJECTIVE_TYPE


def create_battle_objective(
    mission: "MissionTemplate | None",
    position: tuple[int, int] = DEFAULT_OBJECTIVE_POSITION,
) -> BattleObjective | None:
    """Build the battlefield objective prototype for a mission, if it has one."""
    kind = normalize_objective_type(getattr(mission, "objective_type", None))
    prototype = _OBJECTIVE_PROTOTYPES.get(kind)
    if prototype is None:
        return None
    return BattleObjective(
        kind=kind,
        position=position,
        label=prototype["label"],
        description=prototype["description"],
        completion_message=prototype["completion_message"],
        interaction_prompt=prototype.get("interaction_prompt", "Press E to interact."),
        success_condition=prototype.get("success_condition", "Complete the marker."),
        failure_condition=prototype.get("failure_condition", "Squad wipe before completion."),
        required_interactions=int(prototype.get("required_interactions", 1)),
    )


def is_in_interaction_range(
    actor_position: tuple[int, int],
    objective: BattleObjective,
    *,
    grid_size: int = GRID_SIZE,
    max_cells: int = 1,
) -> bool:
    """Return whether an actor is within the allowed grid-cell interaction range."""
    max_distance = grid_size * max_cells
    return (
        (actor_position[0] - objective.position[0]) ** 2
        + (actor_position[1] - objective.position[1]) ** 2
    ) ** 0.5 <= max_distance


def interact_with_objective(
    actor_position: tuple[int, int], objective: BattleObjective
) -> tuple[bool, str]:
    """Try to complete an objective and return success plus a readable message."""
    if objective.completed:
        return True, objective.completion_message
    if not is_in_interaction_range(actor_position, objective):
        return False, f"Move within one grid cell of {objective.label} to interact. {objective.interaction_prompt}"
    objective.progress = min(
        max(1, objective.required_interactions),
        objective.progress + 1,
    )
    if objective.progress >= max(1, objective.required_interactions):
        objective.completed = True
        return True, objective.completion_message
    return False, f"{objective.label} progress {objective.progress}/{objective.required_interactions}. Hold position."
