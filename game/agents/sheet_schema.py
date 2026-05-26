"""Typed schema helpers for agent sheet payloads.

Keeps recruitment/new-character creation and save migration aligned.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from game.stats import PlayerStats

SKILL_MIN_RANK = 0
SKILL_MAX_RANK = 10


@dataclass
class AgentSheet:
    attributes: dict[str, int] = field(default_factory=dict)
    skills: dict[str, int] = field(default_factory=dict)
    derived_stats: dict[str, int] = field(default_factory=dict)


def _clamp_rank(value: Any) -> int:
    rank = int(value) if isinstance(value, (int, float)) else SKILL_MIN_RANK
    return max(SKILL_MIN_RANK, min(SKILL_MAX_RANK, rank))


def build_default_attributes(stats: PlayerStats | None = None) -> dict[str, int]:
    base = stats or PlayerStats()
    return {
        "level": int(base.level),
        "str": int(base.str),
        "agi": int(base.agi),
        "con": int(base.con),
        "cha": int(base.cha),
        "psi": int(base.psi),
        "defense": int(base.defense),
    }


def build_default_skills() -> dict[str, int]:
    return {
        "firearms": 0,
        "close_combat": 0,
        "tactics": 0,
        "tech": 0,
        "medicine": 0,
        "influence": 0,
        "stealth": 0,
        "composure": 0,
        "psychokinesis": 0,
        "pyrokinesis": 0,
        "cryokinesis": 0,
        "telepathy": 0,
    }


def build_default_derived_stats(stats: PlayerStats | None = None) -> dict[str, int]:
    base = stats or PlayerStats()
    return {
        "hp": int(base.hp),
        "aim": int(base.agi + base.level),
        "defense": int(base.defense),
        "crit": int(max(0, base.agi // 2)),
        "initiative": int(base.agi + base.cha),
        "stress_cap": int(10 + base.con + base.cha),
        "recovery_rate": int(max(1, 1 + base.con // 2)),
        "resolve": int(base.psi + base.cha),
    }


def default_agent_sheet(stats: PlayerStats | None = None) -> AgentSheet:
    return AgentSheet(
        attributes=build_default_attributes(stats),
        skills=build_default_skills(),
        derived_stats=build_default_derived_stats(stats),
    )


def normalize_agent_sheet(
    *,
    stats: PlayerStats,
    attributes: dict[str, Any] | None,
    skills: dict[str, Any] | None,
    derived_stats: dict[str, Any] | None,
) -> AgentSheet:
    defaults = default_agent_sheet(stats)
    normalized_attributes = dict(defaults.attributes)
    normalized_attributes.update({k: int(v) for k, v in (attributes or {}).items() if isinstance(v, (int, float))})

    normalized_skills = dict(defaults.skills)
    for key, value in (skills or {}).items():
        if key in normalized_skills:
            normalized_skills[key] = _clamp_rank(value)

    normalized_derived = dict(defaults.derived_stats)
    normalized_derived.update({k: int(v) for k, v in (derived_stats or {}).items() if isinstance(v, (int, float))})

    return AgentSheet(
        attributes=normalized_attributes,
        skills=normalized_skills,
        derived_stats=normalized_derived,
    )
