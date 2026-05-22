"""Temporary narrative scars derived from severe battlefield injuries."""

from __future__ import annotations

from dataclasses import dataclass

from ..character import Character


@dataclass(frozen=True)
class TemporaryScarTemplate:
    """Compact narrative-only scar template keyed by severe injury label."""

    key: str
    title: str
    strategic_days: int
    tone: str
    tags: tuple[str, ...]
    log_line: str


SEVERE_INJURY_TO_SCAR: dict[str, TemporaryScarTemplate] = {
    "Critical battle trauma": TemporaryScarTemplate(
        key="critical_battle_trauma",
        title="Nights of Sirens",
        strategic_days=4,
        tone="vigilant",
        tags=("injury", "hypervigilance", "nightmares"),
        log_line="Every distant siren drags the battle back into focus.",
    )
}


def apply_temporary_scar_from_injury(character: Character, injury: str) -> dict | None:
    """Attach or refresh a compact narrative scar when injury is severe."""
    template = SEVERE_INJURY_TO_SCAR.get(injury)
    if template is None:
        return None

    existing = next(
        (scar for scar in character.temporary_scars if scar.get("key") == template.key),
        None,
    )
    if existing is not None:
        existing["days_remaining"] = max(
            int(existing.get("days_remaining", 0)), template.strategic_days
        )
        return existing

    scar = {
        "key": template.key,
        "title": template.title,
        "days_remaining": template.strategic_days,
        "tone": template.tone,
        "tags": list(template.tags),
        "log_line": template.log_line,
    }
    character.temporary_scars.append(scar)
    character.history.append(f"Narrative scar gained: {template.title}.")
    return scar


def tick_temporary_scars(character: Character, days: int = 1) -> list[dict]:
    """Decrease scar duration and remove expired scars."""
    if days <= 0:
        return []

    expired: list[dict] = []
    remaining: list[dict] = []
    for scar in character.temporary_scars:
        updated = dict(scar)
        updated["days_remaining"] = int(updated.get("days_remaining", 0)) - days
        if updated["days_remaining"] <= 0:
            expired.append(updated)
            character.history.append(f"Narrative scar faded: {updated.get('title', 'Unknown')}.")
            continue
        remaining.append(updated)

    character.temporary_scars = remaining
    return expired


def build_temporary_scar_summary(character: Character) -> list[str]:
    """Return readable, render-neutral lines for UI consumers."""
    if not character.temporary_scars:
        return ["Temporary scars: none"]
    lines = []
    for scar in character.temporary_scars:
        tags = ", ".join(scar.get("tags", []))
        lines.append(
            f"{scar.get('title', 'Unknown')} ({scar.get('days_remaining', 0)}d, "
            f"tone {scar.get('tone', 'neutral')}, tags: {tags})"
        )
    return lines
