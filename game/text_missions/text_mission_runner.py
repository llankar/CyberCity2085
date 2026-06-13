"""Skill-check resolution for text missions."""

from __future__ import annotations

import random

from game.agents.sheet_calculations import skill_total


# Result tiers relative to difficulty:
#   total_roll >= difficulty + 2  → "great"
#   total_roll >= difficulty      → "success"
#   total_roll >= difficulty - 2  → "partial"
#   total_roll <  difficulty - 2  → "failure"

RESULT_LABELS: dict[str, str] = {
    "great":   "GREAT SUCCESS",
    "success": "SUCCESS",
    "partial": "PARTIAL FAILURE",
    "failure": "FAILURE",
}

RESULT_COLORS: dict[str, tuple[int, int, int]] = {
    "great":   (100, 220, 150),
    "success": (80,  200, 120),
    "partial": (220, 160, 60),
    "failure": (220, 80,  70),
}


def best_skill_agent(characters, skill_key: str) -> tuple[str, int]:
    """Return (agent_name, best_total) for the agent with the highest skill total."""
    best_name = "—"
    best_total = 0
    for char in characters:
        stats = char.stats
        attrs = {
            "level": int(stats.level),
            "str":   int(stats.str),
            "agi":   int(stats.agi),
            "con":   int(stats.con),
            "cha":   int(stats.cha),
            "psi":   int(stats.psi),
        }
        total = skill_total(skill_key, attrs, char.skills, {})
        if total > best_total:
            best_total = total
            best_name = char.name
    return best_name, best_total


def resolve_skill_check(
    skill_total_score: int,
    difficulty: int,
    *,
    seed: int | None = None,
) -> tuple[str, int, int]:
    """Roll 1d6 + skill_total vs difficulty.

    Returns (result_key, die_roll, total_roll).
    result_key is one of: "great", "success", "partial", "failure".
    """
    rng = random.Random(seed) if seed is not None else random
    roll = rng.randint(1, 6)
    total = skill_total_score + roll
    if total >= difficulty + 2:
        result = "great"
    elif total >= difficulty:
        result = "success"
    elif total >= difficulty - 2:
        result = "partial"
    else:
        result = "failure"
    return result, roll, total
