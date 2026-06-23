from __future__ import annotations

from dataclasses import dataclass, field
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
    "civilian_rescue",
    "containment",
    "extract",
    "sabotage",
    "data_theft",
    "defend",
    "recon_scan",
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
    "containment": {
        "label": "BREACH LINE",
        "description": "hold the containment line and prevent Starvers or mutants from crossing",
        "interaction_prompt": "Hold enemies north of the breach line.",
        "success_condition": "Win while no enemy crosses the containment threshold.",
        "failure_condition": "Containment fails if an enemy crosses the breach line.",
        "completion_message": "Containment line held. Threat contained.",
        "required_interactions": 1,
        "breach_y": 192,
    },
    "civilian_rescue": {
        "label": "CIVILIANS",
        "description": "rescue multiple civilians or cured Starvers before they are lost",
        "interaction_prompt": "Press E near CIVILIANS to extract the next group.",
        "success_condition": "Three civilian groups are extracted.",
        "failure_condition": "Rescue fails if the squad is wiped before extraction completes.",
        "completion_message": "Civilian groups extracted. Rescue complete.",
        "required_interactions": 3,
        "marker_offsets": [(0, 0), (64, 32), (-64, 64)],
    },
    "recon_scan": {
        "label": "SCAN",
        "description": "scan several points and extract without eliminating every enemy",
        "interaction_prompt": "Press E near SCAN to complete this sweep point.",
        "success_condition": "Three scan points are completed.",
        "failure_condition": "Recon fails if the squad is wiped before all scan points are complete.",
        "completion_message": "Scan sweep complete. Recon objective achieved.",
        "required_interactions": 3,
        "marker_offsets": [(0, 0), (96, 0), (32, 96)],
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
    marker_positions: list[tuple[int, int]] = field(default_factory=list)
    breach_y: int | None = None

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
    marker_positions = [
        (position[0] + offset[0], position[1] + offset[1])
        for offset in prototype.get("marker_offsets", [(0, 0)])
    ]
    return BattleObjective(
        kind=kind,
        position=marker_positions[0],
        label=prototype["label"],
        description=prototype["description"],
        completion_message=prototype["completion_message"],
        interaction_prompt=prototype.get("interaction_prompt", "Press E to interact."),
        success_condition=prototype.get("success_condition", "Complete the marker."),
        failure_condition=prototype.get("failure_condition", "Squad wipe before completion."),
        required_interactions=int(prototype.get("required_interactions", 1)),
        marker_positions=marker_positions,
        breach_y=prototype.get("breach_y"),
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
    if objective.marker_positions and objective.progress < len(objective.marker_positions):
        objective.position = objective.marker_positions[objective.progress]
    return False, f"{objective.label} progress {objective.progress}/{objective.required_interactions}. Hold position."


def objective_failed_by_enemy_positions(
    enemy_positions: list[tuple[int, int]],
    objective: BattleObjective | None,
    *,
    grid_size: int = GRID_SIZE,
) -> tuple[bool, str]:
    """Return whether enemy movement has failed a defensive objective."""
    if objective is None or objective.completed:
        return False, ""
    if objective.kind == "containment" and objective.breach_y is not None:
        if any(y <= objective.breach_y for _, y in enemy_positions):
            return True, objective.failure_condition
    if objective.kind == "defend":
        ox, oy = objective.position
        for x, y in enemy_positions:
            if abs(x - ox) <= grid_size and abs(y - oy) <= grid_size:
                return True, objective.failure_condition
    return False, ""
