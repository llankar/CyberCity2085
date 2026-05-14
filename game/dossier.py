from __future__ import annotations

from .character import Character


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
    summary = (
        f"{character.name} ({character.role}) HP {stats.hp}/{stats.max_hp} "
        f"Stress {character.stress} Loyalty {character.loyalty}"
    )
    detail = (
        f"  Trait: {first_or_default(character.traits, NO_TRAIT)} | "
        f"Scar: {first_wound_or_trauma(character)} | "
        f"History: {first_or_default(character.history, NO_HISTORY)}"
    )
    return summary, detail
