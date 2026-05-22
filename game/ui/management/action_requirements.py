"""Management action requirement checks.

Small focused helpers for blocked-action reasons so UI flows stay readable.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionBlockReason:
    action: str
    missing_requirement: str
    guidance: str

    def to_ui_text(self) -> str:
        return (
            f"Action blocked: {self.action}. Missing {self.missing_requirement}. "
            f"Requirement: {self.guidance}."
        )


def blocked_recruit_reason(available_funds: int, recruit_cost: int = 5) -> ActionBlockReason | None:
    if available_funds >= recruit_cost:
        return None
    return ActionBlockReason(
        action="Recruit agent",
        missing_requirement="corporate funds",
        guidance=f"need at least {recruit_cost} funds (current {available_funds})",
    )


def blocked_launch_reason(
    has_deployable_agent: bool,
    selected_count: int,
    mission_unavailable: bool,
    mission_title: str,
) -> ActionBlockReason | None:
    if not has_deployable_agent:
        return ActionBlockReason(
            action="Launch mission",
            missing_requirement="deployable agent",
            guidance="recruit or recover at least one deployable agent",
        )
    if selected_count <= 0:
        return ActionBlockReason(
            action="Launch mission",
            missing_requirement="selected squad",
            guidance="toggle at least one deployable agent into the squad",
        )
    if mission_unavailable:
        return ActionBlockReason(
            action=f"Launch {mission_title}",
            missing_requirement="mission availability",
            guidance="advance day or select another mission",
        )
    return None
