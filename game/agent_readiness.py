"""Pre-mission readiness rules for emotionally readable deployments."""

from __future__ import annotations

from .character import Character
from .mission_templates import MissionTemplate


LOW_RISK_STRESS = 35
HIGH_RISK_STRESS = 65
BREAKDOWN_STRESS = 85


def stress_state_label(stress: int) -> str:
    """Translate agent stress into a compact emotional state label."""
    if stress >= BREAKDOWN_STRESS:
        return "breaking"
    if stress >= HIGH_RISK_STRESS:
        return "frayed"
    if stress >= LOW_RISK_STRESS:
        return "rattled"
    return "steady"


def estimate_mission_stress(mission: MissionTemplate | None) -> int:
    """Estimate baseline stress a mission will add before random fallout."""
    risk = max(0, int(getattr(mission, "risk_level", 1)))
    return max(0, risk * 4 - 2)


def projected_stress(character: Character, mission: MissionTemplate | None) -> int:
    """Estimate post-mission stress before complications or defeat."""
    return min(100, character.stress + estimate_mission_stress(mission))


def _risk_note(character: Character, projected: int) -> str:
    if projected >= BREAKDOWN_STRESS:
        return "breakdown risk"
    if projected >= HIGH_RISK_STRESS:
        if character.trauma:
            return f"trauma may resurface: {character.trauma[0]}"
        return "stress likely to linger"
    if character.injuries:
        return f"field injury: {character.injuries[0]}"
    if character.savage_tags:
        return f"tagged by {character.savage_tags[0]}"
    return "cleared for deployment"


def build_agent_readiness_lines(
    characters: list[Character], mission: MissionTemplate | None, limit: int = 4
) -> list[str]:
    """Build readable pre-mission stress warnings for the RPG dashboard."""
    deployable = [character for character in characters if character.stats.hp > 0]
    if not deployable:
        return ["No deployable agents. Recruit or recover someone before launch."]

    ranked = sorted(
        deployable,
        key=lambda character: (
            projected_stress(character, mission),
            len(character.trauma),
            len(character.injuries),
        ),
        reverse=True,
    )
    lines: list[str] = []
    for character in ranked[:limit]:
        projected = projected_stress(character, mission)
        state = stress_state_label(projected)
        note = _risk_note(character, projected)
        stress_range = f"{character.stress}->{projected}"
        lines.append(f"{character.name}: {state} after op ({stress_range}) - {note}.")
    return lines
