from __future__ import annotations

from dataclasses import dataclass
from math import ceil

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
    healing_fraction: float = 0.0
    heal_to_full: bool = False


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
    DowntimeActivity(
        key="rest",
        label="Rest",
        days_cost=1,
        resource_key="credits",
        resource_cost=0,
        morale_delta=0,
        stress_delta=0,
        healing_fraction=0.25,
    ),
    DowntimeActivity(
        key="hospital",
        label="Hospital",
        days_cost=1,
        resource_key="credits",
        resource_cost=8,
        morale_delta=0,
        stress_delta=0,
        heal_to_full=True,
    ),
)


def can_run_activity(gs: GameState, activity: DowntimeActivity) -> bool:
    return (
        gs.strategic_resources.get(activity.resource_key, 0) >= activity.resource_cost
    )


def apply_activity(
    gs: GameState, activity: DowntimeActivity, squad: list[Character]
) -> str:
    if not squad:
        return "Select at least one agent for downtime."
    medical = activity.healing_fraction > 0 or activity.heal_to_full
    if medical:
        squad = [
            agent
            for agent in squad
            if any(agent is member for member in gs.characters)
            and not agent.starver_transformed
            and 0 < agent.stats.hp < agent.stats.max_hp
        ]
        if not squad:
            return "Select a living injured agent for treatment."
    if not can_run_activity(gs, activity):
        return f"Not enough {activity.resource_key} for {activity.label}."

    if activity.resource_cost:
        gs.strategic_resources[activity.resource_key] -= activity.resource_cost
    for _ in range(activity.days_cost):
        gs.advance_days(1, reason=f"downtime:{activity.key}")

    healed = []
    for agent in squad:
        if medical:
            if (
                agent.stats.hp <= 0
                or agent.starver_transformed
                or not any(agent is member for member in gs.characters)
            ):
                continue
            before = agent.stats.hp
            amount = (
                agent.stats.max_hp
                if activity.heal_to_full
                else max(1, ceil(agent.stats.max_hp * activity.healing_fraction))
            )
            agent.stats.hp = min(agent.stats.max_hp, agent.stats.hp + amount)
            healed.append(f"{agent.name} +{agent.stats.hp-before} HP")
        agent.stress = max(0, min(100, agent.stress + activity.stress_delta))
        agent.loyalty = max(-100, min(100, agent.loyalty + activity.morale_delta))
        if activity.add_trait and activity.add_trait not in agent.traits:
            agent.traits.append(activity.add_trait)

    return (
        f"Downtime: {activity.label} (-{activity.resource_cost} {activity.resource_key}, "
        f"{activity.days_cost} day)" + (" · " + ", ".join(healed) if medical else "")
    )
