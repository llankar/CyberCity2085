"""Small, idempotent relationship changes caused by factual tactical moments."""

from __future__ import annotations

from ..character import Character


def apply_tactical_relationship_consequences(
    characters: list[Character],
    tactical_moments: list[dict] | None,
) -> list[dict[str, object]]:
    """Apply only explicit two-agent moments and return debrief-ready changes."""
    by_name = {character.name: character for character in characters}
    changes: list[dict[str, object]] = []
    for moment in tactical_moments or []:
        if moment.get("kind") != "rescue":
            continue
        helper = by_name.get(str(moment.get("agent_name", "")))
        patient = by_name.get(str(moment.get("patient_name", "")))
        if helper is None or patient is None or helper is patient:
            continue
        marker = f"Bond strengthened: {helper.name} rescued {patient.name} under fire."
        if marker in helper.history or marker in patient.history:
            continue
        helper.relationships[patient.name] = helper.relationships.get(patient.name, 0) + 1
        patient.relationships[helper.name] = patient.relationships.get(helper.name, 0) + 1
        helper.history.append(marker)
        patient.history.append(marker)
        changes.append(
            {
                "kind": "rescue_bond",
                "source": helper.name,
                "target": patient.name,
                "delta": 1,
                "text": f"Relationship: {helper.name} and {patient.name} gained +1 bond after the rescue.",
            }
        )
    return changes
