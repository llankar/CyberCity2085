"""Compact agent personality traits used to modulate mission narrative tone."""

from __future__ import annotations

import random

TRAIT_TONE_MODULATORS: dict[str, dict[str, str]] = {
    "steadfast": {
        "prefix": "Steady voice:",
        "suffix": "Holds formation under pressure.",
        "stress_reaction": "turns fear into procedure",
    },
    "reckless": {
        "prefix": "Hot-blooded report:",
        "suffix": "Pushes ahead before the smoke clears.",
        "stress_reaction": "answers panic with motion",
    },
    "empathetic": {
        "prefix": "Human-focused brief:",
        "suffix": "Keeps civilians and squad morale in sight.",
        "stress_reaction": "checks who is still breathing first",
    },
    "cunning": {
        "prefix": "Sharp-angle debrief:",
        "suffix": "Finds leverage in chaos.",
        "stress_reaction": "starts bargaining with the chaos",
    },
}


NEUTRAL_TRAIT = "neutral"


def list_personality_traits() -> list[str]:
    """Return available trait keys for assignment and UI display."""
    return list(TRAIT_TONE_MODULATORS.keys())


def assign_personality_traits(
    name: str,
    role: str,
    roster_index: int,
    seed: int | None = None,
) -> tuple[str, str | None]:
    """Deterministically assign one primary trait and optional secondary trait."""
    trait_pool = list_personality_traits()
    rng_seed = seed if seed is not None else f"{name}:{role}:{roster_index}"
    rng = random.Random(rng_seed)
    primary = rng.choice(trait_pool)

    if len(trait_pool) < 2 or rng.random() < 0.45:
        return primary, None

    secondary_pool = [trait for trait in trait_pool if trait != primary]
    return primary, rng.choice(secondary_pool)


def modulate_mission_log_tone(
    text: str,
    primary_trait: str | None,
    secondary_trait: str | None = None,
) -> str:
    """Return mission log text with personality-tone wrappers.

    Fallback is fully neutral for old saves with no trait metadata.
    """
    primary = TRAIT_TONE_MODULATORS.get(primary_trait or "")
    if not primary:
        return text

    secondary = TRAIT_TONE_MODULATORS.get(secondary_trait or "")
    suffix = primary["suffix"]
    if secondary:
        suffix = f"{suffix} {secondary['suffix']}"

    return f"{primary['prefix']} {text} {suffix}"


def personality_stress_reaction(
    name: str,
    stress: int,
    primary_trait: str | None,
) -> str:
    """Return a compact trait-specific stress reaction line."""
    if stress < 65:
        return ""
    trait = TRAIT_TONE_MODULATORS.get(primary_trait or "")
    if not trait:
        return f"{name} shows visible strain but stays functional."
    return f"{name} {trait['stress_reaction']}."
