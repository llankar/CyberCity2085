from __future__ import annotations

from dataclasses import dataclass

from game.character import Character
from game.gamestate import GameState


@dataclass(frozen=True)
class DowntimeActivity:
    key: str
    label: str
    days_cost: int
    resource_key: str
    resource_cost: int
    morale_delta: int
    stress_delta: int
    add_trait: str | None = None


DOWNTIME_ACTIVITIES: tuple[DowntimeActivity, ...] = (
    DowntimeActivity(
        key="shore_leave",
        label="Shore Leave",
        days_cost=1,
        resource_key="credits",
        resource_cost=8,
        morale_delta=10,
        stress_delta=-12,
        add_trait="grounded",
    ),
    DowntimeActivity(
        key="sim_drills",
        label="Sim Drills",
        days_cost=1,
        resource_key="intel",
        resource_cost=2,
        morale_delta=4,
        stress_delta=6,
        add_trait="disciplined",
    ),
    DowntimeActivity(
        key="group_therapy",
        label="Group Therapy",
        days_cost=1,
        resource_key="influence",
        resource_cost=1,
        morale_delta=6,
        stress_delta=-18,
        add_trait="vulnerable",
    ),
)


def can_run_activity(gs: GameState, activity: DowntimeActivity) -> bool:
    return gs.strategic_resources.get(activity.resource_key, 0) >= activity.resource_cost


def apply_activity(gs: GameState, activity: DowntimeActivity, squad: list[Character]) -> str:
    if not squad:
        return "Select at least one agent for downtime."
    if not can_run_activity(gs, activity):
        return f"Not enough {activity.resource_key} for {activity.label}."

    gs.strategic_resources[activity.resource_key] -= activity.resource_cost
    for _ in range(activity.days_cost):
        gs.advance_days(1, reason=f"downtime:{activity.key}")

    for agent in squad:
        agent.stress = max(0, min(100, agent.stress + activity.stress_delta))
        agent.loyalty = max(-100, min(100, agent.loyalty + activity.morale_delta))
        if activity.add_trait and activity.add_trait not in agent.traits:
            agent.traits.append(activity.add_trait)

    return (
        f"Downtime: {activity.label} (-{activity.resource_cost} {activity.resource_key}, "
        f"{activity.days_cost} day)"
    )
