from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mission_templates import MissionTemplate

GRID_SIZE = 32
DEFAULT_OBJECTIVE_POSITION = (448, 320)
FALLBACK_OBJECTIVE_TYPE = "eliminate"
SUPPORTED_OBJECTIVE_TYPES = {"extract", "sabotage", "data_theft", "defend", "assassination", FALLBACK_OBJECTIVE_TYPE}

_OBJECTIVE_PROTOTYPES = {
    "extract": {
        "label": "WITNESS",
        "description": "reach WITNESS extraction point",
        "completion_message": "Witness secured. Extraction complete.",
    },
    "sabotage": {
        "label": "RELAY",
        "description": "sabotage RELAY at close range",
        "completion_message": "Relay burned. Sabotage complete.",
    },
    "data_theft": {
        "label": "CACHE",
        "description": "steal CACHE data at close range",
        "completion_message": "Cache copied. Data theft complete.",
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

    @property
    def status_text(self) -> str:
        state = "complete" if self.completed else self.description
        return f"Objective: {state}"


def normalize_objective_type(objective_type: str | None) -> str:
    """Return a supported objective type, preserving old saves with safe elimination."""
    if objective_type in SUPPORTED_OBJECTIVE_TYPES:
        return objective_type
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
        return False, f"Move within one grid cell of {objective.label} to interact."
    objective.completed = True
    objective.progress = 1
    return True, objective.completion_message
