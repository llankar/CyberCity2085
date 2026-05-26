"""Compact progression helpers for level-up choices and UI projections."""

from __future__ import annotations

from dataclasses import dataclass

from .agents.sheet_calculations import compute_derived_stats
from .agents.sheet_schema import SKILL_MAX_RANK
from .character import Character

ATTRIBUTE_MAX = 10
ATTRIBUTE_KEYS = ("psi", "str", "agi", "con", "cha")
ALLOWED_SKILL_KEYS = (
    "firearms",
    "close_combat",
    "tactics",
    "tech",
    "medicine",
    "influence",
    "stealth",
    "composure",
    "psychokinesis",
    "pyrokinesis",
    "cryokinesis",
    "telepathy",
)


@dataclass(frozen=True)
class ProgressionProjection:
    stats_delta: dict[str, int]
    skills_delta: dict[str, int]
    derived_delta: dict[str, int]


def _derived_for(character: Character, stats_override: dict[str, int] | None = None, skills_override: dict[str, int] | None = None) -> dict[str, int]:
    attrs = dict(character.attributes)
    attrs.update(
        {
            "level": int(character.stats.level),
            "str": int((stats_override or {}).get("str", character.stats.str)),
            "agi": int((stats_override or {}).get("agi", character.stats.agi)),
            "con": int((stats_override or {}).get("con", character.stats.con)),
            "cha": int((stats_override or {}).get("cha", character.stats.cha)),
            "psi": int((stats_override or {}).get("psi", character.stats.psi)),
            "defense": int(character.stats.defense),
        }
    )
    skills = dict(character.skills)
    if skills_override:
        skills.update(skills_override)
    return compute_derived_stats(attrs, skills, {}, "steady")


def option_a_projection(character: Character, stat_key: str) -> ProgressionProjection:
    current = int(getattr(character.stats, stat_key))
    next_value = min(ATTRIBUTE_MAX, current + 1)
    stat_delta = next_value - current
    before = _derived_for(character)
    after = _derived_for(character, {stat_key: next_value})
    return ProgressionProjection(
        stats_delta={stat_key: stat_delta},
        skills_delta={},
        derived_delta={k: after.get(k, 0) - before.get(k, 0) for k in after},
    )


def option_b_plan(character: Character) -> dict[str, int]:
    remaining = 2
    updates: dict[str, int] = {}
    for skill_key in ALLOWED_SKILL_KEYS:
        if remaining <= 0:
            break
        current = int(character.skills.get(skill_key, 0))
        can_add = max(0, SKILL_MAX_RANK - current)
        if can_add <= 0:
            continue
        add = min(remaining, can_add)
        updates[skill_key] = current + add
        remaining -= add
    return updates


def option_b_projection(character: Character) -> ProgressionProjection:
    before = _derived_for(character)
    updates = option_b_plan(character)
    after = _derived_for(character, skills_override=updates)
    return ProgressionProjection(
        stats_delta={},
        skills_delta={k: updates[k] - int(character.skills.get(k, 0)) for k in updates},
        derived_delta={k: after.get(k, 0) - before.get(k, 0) for k in after},
    )
