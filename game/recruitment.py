"""Recruitment helpers for creating player agents."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .agents.sheet_schema import default_agent_sheet
from .character import Character
from .stats import PlayerStats
from .relationships.mentor_history import upsert_mentor_link
from .narrative.personality_traits import assign_personality_traits

ROLE_STAT_BONUSES = {
    "samurai": "str",
    "sniper": "agi",
    "psi": "psi",
}

ROLE_NAME_POOLS: dict[str, tuple[str, ...]] = {
    "samurai": (
        "Rook", "Katana", "Sable", "Mantis", "Ash", "Warden", "Viper", "Kestrel",
    ),
    "sniper": (
        "Longshot", "Vanta", "Iris", "Ghost", "Echo", "Static", "Pulse", "Lumen",
    ),
    "psi": (
        "Oracle", "Wisp", "Hex", "Veil", "Null", "Siren", "Nova", "Morrow",
    ),
}

ROLE_TAGLINES = {
    "samurai": "Close-range breach specialist.",
    "sniper": "Long-range strike and overwatch expert.",
    "psi": "Psychic disruption and battlefield control.",
}

PLACEHOLDER_NAME_RE = re.compile(r"^(?:agent|recruit|operative|unit)[\s_-]*\d+$", re.IGNORECASE)


@dataclass(frozen=True)
class RecruitCandidate:
    """One candidate in the recruit chooser."""

    name: str
    role: str
    tagline: str


def create_character(name: str, role: str) -> Character:
    """Create a new player character with the stat bonus for their role."""
    stats = PlayerStats()
    bonus_stat = ROLE_STAT_BONUSES.get(role)
    if bonus_stat:
        setattr(stats, bonus_stat, getattr(stats, bonus_stat) + 5)
    stats.recalculate_hp()
    cleaned_name = normalize_agent_name(name, [], role)
    primary_trait, secondary_trait = assign_personality_traits(cleaned_name, role, roster_index=0)
    sheet = default_agent_sheet(stats)
    return Character(
        name=cleaned_name,
        role=role,
        stats=stats,
        talent_points=1,
        personality_primary_trait=primary_trait,
        personality_secondary_trait=secondary_trait or "",
        attributes=sheet.attributes,
        skills=sheet.skills,
        derived_stats=sheet.derived_stats,
    )


def _existing_names(roster: list[Character]) -> set[str]:
    return {character.name for character in roster}


def is_placeholder_agent_name(name: str) -> bool:
    """Return whether a name is one of the generic placeholder labels."""
    cleaned = " ".join(name.split())
    return not cleaned or bool(PLACEHOLDER_NAME_RE.match(cleaned))


def unique_recruit_name(roster: list[Character], role: str) -> str:
    """Return the next cool recruit codename for a role."""
    used = _existing_names(roster)
    for candidate in ROLE_NAME_POOLS.get(role, ()):
        if candidate not in used:
            return candidate
    suffix = len(roster) + 1
    while f"{role.title()}-{suffix}" in used:
        suffix += 1
    return f"{role.title()}-{suffix}"


def normalize_agent_name(name: str, roster: list[Character], role: str) -> str:
    """Normalize placeholder roster labels into a role-appropriate codename."""
    cleaned = " ".join(name.split())
    if cleaned and not is_placeholder_agent_name(cleaned) and cleaned not in _existing_names(roster):
        return cleaned
    return unique_recruit_name(roster, role)


def build_recruitment_candidates(
    roster: list[Character],
    *,
    roles: tuple[str, ...] = ("samurai", "sniper", "psi"),
    count: int = 6,
) -> list[RecruitCandidate]:
    """Build a small, readable list of named recruits for the UI."""
    used = _existing_names(roster)
    candidates: list[RecruitCandidate] = []
    per_role = max(1, count // max(1, len(roles)))
    for role in roles:
        pool = [name for name in ROLE_NAME_POOLS.get(role, ()) if name not in used]
        while len(pool) < per_role:
            pool.append(f"{role.title()}-{len(roster) + len(pool) + 1}")
        for name in pool[:per_role]:
            candidates.append(RecruitCandidate(name=name, role=role, tagline=ROLE_TAGLINES.get(role, "Field operator.")))
            used.add(name)
    return candidates[:count]


def recruit_agent(roster: list[Character], role: str, name: str | None = None) -> Character:
    """Create a named recruit and append them to the supplied roster."""
    next_name = normalize_agent_name(name, roster, role) if name else unique_recruit_name(roster, role)
    agent = create_character(next_name, role)
    next_index = len(roster) + 1
    primary_trait, secondary_trait = assign_personality_traits(agent.name, role, roster_index=next_index)
    agent.personality_primary_trait = primary_trait
    agent.personality_secondary_trait = secondary_trait or ""
    seed_roster_mentor_links(roster, agent)
    roster.append(agent)
    return agent


def seed_roster_mentor_links(roster: list[Character], new_agent: Character, strategic_day: int = 0) -> None:
    """Initialize lightweight social ties between a recruit and the current roster."""
    for teammate in roster:
        if teammate.name == new_agent.name:
            continue
        upsert_mentor_link(new_agent.mentor_links, agent_id=teammate.name, strategic_day=strategic_day, bond_delta=1)
        upsert_mentor_link(teammate.mentor_links, agent_id=new_agent.name, strategic_day=strategic_day, bond_delta=1)
