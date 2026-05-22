"""Mission aftermath rules for agent stress, loyalty, and memory."""

from __future__ import annotations

from .character import Character
from .mission_templates import MissionComplication, MissionTemplate
from .relationships.mentor_history import upsert_mentor_link

MIN_STRESS = 0
MAX_STRESS = 100


def clamp_stress(value: int) -> int:
    """Keep stress in the readable UI range."""
    return max(MIN_STRESS, min(MAX_STRESS, value))


def _mission_title(mission: MissionTemplate | None) -> str:
    return mission.title if mission else "Unknown Operation"


def _risk_level(mission: MissionTemplate | None) -> int:
    return max(0, int(getattr(mission, "risk_level", 1)))


def _complication_intensity(complication: MissionComplication | None) -> int:
    if not complication:
        return 0
    tag_intensity = sum(max(0, tag.intensity) for tag in complication.tags)
    consequence_severity = max(0, complication.consequence.severity)
    return max(4, tag_intensity + consequence_severity)


def _add_unique_savage_tags(
    character: Character, complication: MissionComplication | None
) -> list[str]:
    """Attach complication tag names to a character without duplicating them."""
    if not complication:
        return []

    added_tags: list[str] = []
    for tag in complication.tags:
        if tag.name not in character.savage_tags:
            character.savage_tags.append(tag.name)
            added_tags.append(tag.name)
    return added_tags


def _maybe_add_trauma(
    character: Character,
    mission: MissionTemplate | None,
    complication: MissionComplication | None,
) -> str | None:
    """Add a compact trauma hook when fallout is severe enough to linger."""
    if not complication:
        return None

    risk = _risk_level(mission)
    severity = complication.consequence.severity
    if character.stress < 65 and risk + severity < 6:
        return None

    trauma = f"Haunted by {complication.name}"
    if trauma not in character.trauma:
        character.trauma.append(trauma)
    return trauma


def _update_team_links(characters: list[Character], strategic_day: int, victory: bool) -> None:
    """Increment compact bond levels for agents who share mission fallout."""
    bond_delta = 2 if victory else 1
    for character in characters:
        for teammate in characters:
            if teammate.name == character.name:
                continue
            upsert_mentor_link(
                character.mentor_links,
                agent_id=teammate.name,
                strategic_day=strategic_day,
                bond_delta=bond_delta,
            )


def apply_mission_aftermath(
    characters: list[Character],
    mission: MissionTemplate | None,
    victory: bool,
    triggered_complication: MissionComplication | None = None,
) -> list[str]:
    """Apply emotional aftermath to surviving mission participants.

    The caller is expected to pass only surviving agents who participated in the
    battle. Returned strings are intentionally compact for the event log.
    """
    title = _mission_title(mission)
    risk = _risk_level(mission)
    base_stress = risk * 4
    if victory:
        base_stress = max(0, base_stress - 2)
    else:
        base_stress += 3

    complication_stress = _complication_intensity(triggered_complication)
    outcome_label = "victory" if victory else "defeat"
    aftermath_lines: list[str] = []
    strategic_day = max(0, int(getattr(mission, "duration_days", 1)))
    _update_team_links(characters, strategic_day=strategic_day, victory=victory)

    for character in characters:
        stress_delta = base_stress + complication_stress
        before_stress = character.stress
        character.stress = clamp_stress(character.stress + stress_delta)
        applied_stress = character.stress - before_stress

        clean_victory = victory and triggered_complication is None
        if clean_victory:
            character.loyalty += 1

        character.history.append(
            f"{title}: {outcome_label}, stress {applied_stress:+d}"
        )

        added_tags = _add_unique_savage_tags(character, triggered_complication)
        trauma = _maybe_add_trauma(character, mission, triggered_complication)

        line = (
            f"Aftermath: {character.name} carries {title} "
            f"({outcome_label}, stress {character.stress}/100"
        )
        if clean_victory:
            line += ", loyalty +1"
        if triggered_complication:
            line += f", {triggered_complication.name} +{complication_stress}"
        if trauma:
            line += f", trauma: {trauma}"
        elif added_tags:
            line += f", tag: {added_tags[0]}"
        line += ")."
        aftermath_lines.append(line)

    return aftermath_lines
