"""Compact objective-phase branching rules for mission progression."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

BranchCondition = Callable[[dict], bool]


@dataclass(frozen=True)
class ObjectivePhase:
    phase_id: str
    condition: BranchCondition
    on_success: str
    on_failure: str
    next_on_success: str | None = None
    next_on_failure: str | None = None


@dataclass(frozen=True)
class ObjectiveBranchTemplate:
    template_id: str
    label: str
    start_phase: str
    phases: dict[str, ObjectivePhase]


@dataclass(frozen=True)
class ObjectivePhaseResult:
    phase_id: str
    succeeded: bool
    issue_text: str
    next_phase_id: str | None
    finished: bool


_BRANCHES: dict[str, ObjectiveBranchTemplate] = {
    "safe_extraction": ObjectiveBranchTemplate(
        template_id="safe_extraction",
        label="Witness corridor",
        start_phase="reach_witness",
        phases={
            "reach_witness": ObjectivePhase(
                phase_id="reach_witness",
                condition=lambda state: state.get("reached_witness", False),
                on_success="The witness is secure.",
                on_failure="The witness remains missing.",
                next_on_success="escort_zone",
                next_on_failure="mission_failed",
            ),
            "escort_zone": ObjectivePhase(
                phase_id="escort_zone",
                condition=lambda state: state.get("witness_escorted", False),
                on_success="Clean extraction confirmed.",
                on_failure="The witness was lost during the escort.",
                next_on_success="mission_success",
                next_on_failure="mission_failed",
            ),
        },
    ),
    "data_with_detour": ObjectiveBranchTemplate(
        template_id="data_with_detour",
        label="Ghost cache route",
        start_phase="breach_terminal",
        phases={
            "breach_terminal": ObjectivePhase(
                phase_id="breach_terminal",
                condition=lambda state: state.get("terminal_breached", False),
                on_success="Terminal access secured.",
                on_failure="Main access blocked; alternate route engaged.",
                next_on_success="extract_data",
                next_on_failure="field_proxy",
            ),
            "field_proxy": ObjectivePhase(
                phase_id="field_proxy",
                condition=lambda state: state.get("proxy_reached", False),
                on_success="Tactical proxy established; extraction resumed.",
                on_failure="The proxy collapsed under pressure.",
                next_on_success="extract_data",
                next_on_failure="mission_failed",
            ),
            "extract_data": ObjectivePhase(
                phase_id="extract_data",
                condition=lambda state: state.get("cache_extracted", False),
                on_success="The Ghost Order cache was recovered.",
                on_failure="The cache was corrupted before transfer.",
                next_on_success="mission_success",
                next_on_failure="mission_failed",
            ),
        },
    ),
    "sabotage_window": ObjectiveBranchTemplate(
        template_id="sabotage_window",
        label="Relay demolition window",
        start_phase="plant_charge",
        phases={
            "plant_charge": ObjectivePhase(
                phase_id="plant_charge",
                condition=lambda state: state.get("charge_armed", False),
                on_success="Charges planted on the relay.",
                on_failure="The relay alerted reinforcements.",
                next_on_success="detonation",
                next_on_failure="mission_failed",
            ),
            "detonation": ObjectivePhase(
                phase_id="detonation",
                condition=lambda state: state.get("detonation_confirmed", False),
                on_success="Relay destroyed; strategic window secured.",
                on_failure="Detonation interrupted before impact.",
                next_on_success="mission_success",
                next_on_failure="mission_failed",
            ),
        },
    ),
}


def get_objective_branch(template_id: str) -> ObjectiveBranchTemplate | None:
    return _BRANCHES.get(template_id)


def evaluate_objective_phase(
    branch: ObjectiveBranchTemplate,
    phase_id: str,
    objective_state: dict,
) -> ObjectivePhaseResult:
    phase = branch.phases[phase_id]
    succeeded = bool(phase.condition(objective_state))
    next_phase = phase.next_on_success if succeeded else phase.next_on_failure
    issue = phase.on_success if succeeded else phase.on_failure
    finished = next_phase in {None, "mission_success", "mission_failed"}
    return ObjectivePhaseResult(
        phase_id=phase.phase_id,
        succeeded=succeeded,
        issue_text=issue,
        next_phase_id=next_phase,
        finished=finished,
    )


def branch_summary_lines(template_id: str) -> list[str]:
    branch = get_objective_branch(template_id)
    if not branch:
        return []
    lines = [f"{branch.label} ({branch.template_id})"]
    for phase in branch.phases.values():
        lines.append(
            f"- {phase.phase_id}: success -> {phase.next_on_success}, failure -> {phase.next_on_failure}"
        )
    return lines
