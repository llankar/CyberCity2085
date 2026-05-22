"""Compact morale aggregation for squad-level UI and narrative hooks."""

from __future__ import annotations

from dataclasses import dataclass

from ..character import Character


@dataclass(frozen=True)
class AgentMoraleContribution:
    """One agent contribution to squad morale."""

    name: str
    morale: int
    delta: int


@dataclass(frozen=True)
class SquadMoraleSummary:
    """Aggregated squad morale snapshot used by UI widgets."""

    global_morale: int
    state: str
    trend_delta: int
    contributions: list[AgentMoraleContribution]


def _clamp(value: int, floor: int = 0, ceil: int = 100) -> int:
    return max(floor, min(ceil, int(value)))


def _agent_morale(character: Character) -> int:
    loyalty_component = _clamp(character.loyalty * 10)
    stress_penalty = _clamp(character.stress)
    return _clamp(50 + loyalty_component - stress_penalty)


def morale_state(value: int) -> str:
    """Map morale value to sober command states."""
    if value <= 30:
        return "critical"
    if value <= 50:
        return "declining"
    return "stable"


def aggregate_squad_morale(
    squad: list[Character],
    previous_global_morale: int | None = None,
) -> SquadMoraleSummary:
    """Return global squad morale and per-agent contributions.

    Morale favors high loyalty and low stress while keeping values in [0..100].
    Empty squads return a neutral zero snapshot for robust UI rendering.
    """
    if not squad:
        return SquadMoraleSummary(0, "critical", 0, [])

    contributions = [
        AgentMoraleContribution(
            name=agent.name,
            morale=_agent_morale(agent),
            delta=(_agent_morale(agent) - 50),
        )
        for agent in squad
    ]
    global_morale = _clamp(
        round(sum(contribution.morale for contribution in contributions) / len(contributions))
    )
    trend_delta = (
        0
        if previous_global_morale is None
        else global_morale - _clamp(previous_global_morale)
    )
    return SquadMoraleSummary(
        global_morale=global_morale,
        state=morale_state(global_morale),
        trend_delta=trend_delta,
        contributions=contributions,
    )
