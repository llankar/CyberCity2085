from __future__ import annotations

from .character import Character
from .narrative.temporary_scars import build_temporary_scar_summary


NO_TRAIT = "No notable trait"
NO_WOUND = "No recorded injury or trauma"
NO_HISTORY = "No history logged"


def first_or_default(values: list[str], default: str) -> str:
    """Return the first dossier entry or a readable placeholder."""
    return values[0] if values else default


def first_wound_or_trauma(character: Character) -> str:
    """Prefer visible injuries, then unresolved trauma for the agent dossier."""
    if character.injuries:
        return character.injuries[0]
    if character.trauma:
        return character.trauma[0]
    return NO_WOUND


def build_agent_dossier_lines(character: Character) -> tuple[str, str]:
    """Build concise RPG-view dossier lines for an agent."""
    stats = character.stats
    display_name = (
        f"{character.name} '{character.nickname}'"
        if character.nickname
        else character.name
    )
    summary = (
        f"{display_name} ({character.role}) HP {stats.hp}/{stats.max_hp} "
        f"Stress {character.stress} Loyalty {character.loyalty}"
    )
    detail = (
        f"  Trait: {first_or_default(character.traits, NO_TRAIT)} | "
        f"Scar: {first_wound_or_trauma(character)} | "
        f"Temp: {build_temporary_scar_summary(character)[0]} | "
        f"Rep: {first_or_default(character.reputation, 'No reputation tag')} | "
        f"History: {first_or_default(character.history, NO_HISTORY)}"
    )
    return summary, detail
