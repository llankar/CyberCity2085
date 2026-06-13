"""Recruitment helpers for creating player agents."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
import random

from .agents.sheet_schema import build_default_skills, normalize_agent_sheet
from .character import Character
from .narrative.personality_traits import assign_personality_traits
from .relationships.mentor_history import upsert_mentor_link
from .stats import PlayerStats
from .ui.portraits import portrait_path_for_agent, portrait_path_for_robot, portrait_sex_for_agent

ROLE_STAT_BONUSES = {
    "samurai": "str",
    "sniper": "agi",
    "psi": "psi",
    "robot": "con",
}

ROLE_SKILL_POOLS: dict[str, tuple[str, ...]] = {
    "samurai": (
        "close_combat",
        "firearms",
        "tactics",
        "composure",
        "medicine",
    ),
    "sniper": (
        "firearms",
        "stealth",
        "tactics",
        "composure",
        "influence",
    ),
    "psi": (
        "psychokinesis",
        "telepathy",
        "composure",
        "influence",
        "stealth",
    ),
    "robot": (
        "close_combat",
        "firearms",
        "tactics",
        "composure",
        "tech",
    ),
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
    "robot": (
        "Bastion", "Forger", "Colossus", "Sentinel", "Rampart",
        "Vector", "Titan", "Wraith-7",
    ),
}

ROLE_TAGLINES = {
    "samurai": "Close-range breach specialist.",
    "sniper": "Long-range strike and overwatch expert.",
    "psi": "Psychic disruption and battlefield control.",
    "robot": "Heavy combat chassis — frontline suppression unit.",
}

ROLE_FUNCTIONS = {
    "samurai": "Breach / front line",
    "sniper": "Overwatch / precision",
    "psi": "Disruption / control",
    "robot": "Heavy assault / suppression",
}

ROLE_BACKGROUNDS = {
    "samurai": (
        "Dock security veteran who learned to survive the worst calls.",
        "Transit enforcer with a habit of standing between others and fire.",
        "Street duelist forged in night-market disputes.",
        "Ex-courier who grew into a shield after too many ambushes.",
    ),
    "sniper": (
        "Rooftop spotter raised on line-of-sight and patience.",
        "Transit tower look-out who never missed a moving target.",
        "Contract shooter with a clean record and a dirty past.",
        "Former survey drone operator who learned to own the horizon.",
    ),
    "psi": (
        "Clinic runaway whose instincts became a weapon.",
        "Corporate lab survivor with a discipline problem turned advantage.",
        "Street mystic who treats fear like data.",
        "Quiet analyst whose mind moves before the body does.",
    ),
    "robot": (
        "Reclaimed military chassis, reprogrammed for squad deployment.",
        "Industrial labour unit retrofitted with combat firmware.",
        "Corporate prototype acquired through a black-market broker.",
        "Decommissioned perimeter security drone, field-modified for ops.",
    ),
}

ROLE_ADVANTAGES = {
    "samurai": (
        "High opening STR",
        "Close-quarters pressure",
        "Armor discipline",
        "Front line anchor",
    ),
    "sniper": (
        "High opening AGI",
        "Long-range accuracy",
        "Early initiative",
        "Overwatch control",
    ),
    "psi": (
        "High opening PSI",
        "Resolve pressure",
        "Battlefield disruption",
        "Crowd control",
    ),
    "robot": (
        "Giant combat token",
        "High HP pool",
        "Immune to stress",
        "Heavy suppression",
    ),
}

PLACEHOLDER_NAME_RE = re.compile(r"^(?:agent|recruit|operative|unit)[\s_-]*\d+$", re.IGNORECASE)


@dataclass(frozen=True)
class RecruitCandidate:
    """One candidate in the recruit chooser."""

    name: str
    role: str
    function: str
    background: str
    advantages: tuple[str, ...]
    stats: PlayerStats
    preview_stats: dict[str, int]
    skill_ranks: dict[str, int]
    price: int
    sex: str
    portrait_path: str

    @property
    def tagline(self) -> str:
        """Backwards-compatible short descriptor used by older UI code."""
        return self.function

    def stat_line(self) -> str:
        """Return a compact, UI-friendly stat summary for the chooser."""
        stats = self.preview_stats
        return (
            f"LV {stats.get('level', 1)}  HP {stats.get('hp', 0)}  STR {stats.get('str', 0)}  "
            f"AGI {stats.get('agi', 0)}  PSI {stats.get('psi', 0)}  DEF {stats.get('defense', 0)}  "
            f"CHA {stats.get('cha', 0)}"
        )

    def skill_line(self) -> str:
        """Return the highest ranked recruit skills as a compact label."""
        ranked = sorted(
            ((skill, int(rank)) for skill, rank in self.skill_ranks.items() if int(rank) > 0),
            key=lambda item: (-item[1], item[0]),
        )
        if not ranked:
            return "SKILLS none"
        snippet = " | ".join(f"{skill[:4].upper()} {rank}" for skill, rank in ranked[:3])
        return f"SKILLS {snippet}"


def create_character(
    name: str,
    role: str,
    *,
    stats: PlayerStats | None = None,
    skills: dict[str, int] | None = None,
    sex: str | None = None,
    attributes: dict[str, int] | None = None,
    derived_stats: dict[str, int] | None = None,
) -> Character:
    """Create a new player character, optionally using a prebuilt recruit profile."""
    if stats is None:
        stats = PlayerStats()
        bonus_stat = ROLE_STAT_BONUSES.get(role)
        if bonus_stat:
            setattr(stats, bonus_stat, getattr(stats, bonus_stat) + 5)
    else:
        stats = PlayerStats(**asdict(stats))
    stats.recalculate_hp()
    cleaned_name = normalize_agent_name(name, [], role)
    primary_trait, secondary_trait = assign_personality_traits(cleaned_name, role, roster_index=0)
    sheet = normalize_agent_sheet(
        stats=stats,
        attributes=attributes,
        skills=skills,
        derived_stats=derived_stats,
    )
    sex = sex if sex is not None else ("" if role == "robot" else portrait_sex_for_agent(cleaned_name, role))
    return Character(
        name=cleaned_name,
        role=role,
        stats=stats,
        talent_points=1,
        personality_primary_trait=primary_trait,
        personality_secondary_trait=secondary_trait or "",
        sex=sex,
        attributes=sheet.attributes,
        skills=sheet.skills,
        derived_stats=sheet.derived_stats,
    )


def _existing_names(roster: list[Character]) -> set[str]:
    return {character.name for character in roster}


def _clamp_attribute(value: int) -> int:
    return max(1, min(10, int(value)))


def _candidate_stats_for_role(role: str, rng: random.Random) -> PlayerStats:
    if role == "robot":
        stats = PlayerStats(
            level=rng.randint(2, 5),
            defense=rng.randint(3, 6),
            str=rng.randint(5, 8),
            agi=rng.randint(2, 4),
            con=rng.randint(5, 8),
            cha=1,
            psi=1,
        )
        stats.recalculate_hp()
        return stats
    base_levels = {
        "samurai": (1, 3),
        "sniper": (1, 3),
        "psi": (1, 4),
    }
    level_min, level_max = base_levels.get(role, (1, 3))
    stats = PlayerStats(
        level=rng.randint(level_min, level_max),
        defense=rng.randint(1, 4),
        psi=rng.randint(1, 4),
        str=rng.randint(2, 6),
        agi=rng.randint(2, 6),
        con=rng.randint(2, 6),
        cha=rng.randint(1, 5),
    )
    bonus_stat = ROLE_STAT_BONUSES.get(role)
    if bonus_stat:
        setattr(stats, bonus_stat, _clamp_attribute(getattr(stats, bonus_stat) + rng.randint(2, 4)))
    for stat_name in rng.sample(["str", "agi", "con", "cha", "psi", "defense"], 2):
        setattr(stats, stat_name, _clamp_attribute(getattr(stats, stat_name) + rng.randint(0, 2)))
    stats.recalculate_hp()
    return stats


def _candidate_skill_ranks(role: str, rng: random.Random) -> dict[str, int]:
    skills = build_default_skills()
    preferred = list(ROLE_SKILL_POOLS.get(role, tuple(skills.keys())))
    rng.shuffle(preferred)

    for index, skill_key in enumerate(preferred):
        if index < 2:
            skills[skill_key] = rng.randint(3, 6)
        elif index < 4:
            skills[skill_key] = rng.randint(1, 4)

    filler_pool = [skill for skill in skills if skill not in preferred[:4]]
    if filler_pool:
        for skill_key in rng.sample(filler_pool, k=min(2, len(filler_pool))):
            skills[skill_key] = rng.randint(1, 3)
    return skills


def _candidate_price(role: str, stats: PlayerStats, skills: dict[str, int]) -> int:
    stat_total = stats.str + stats.agi + stats.con + stats.cha + stats.psi + stats.defense
    skill_total = sum(int(rank) for rank in skills.values())
    role_bias = {"samurai": 2, "sniper": 3, "psi": 4, "robot": 10}.get(role, 2)
    price = 6 + stats.level * 3 + stat_total // 4 + skill_total // 2 + role_bias
    return max(8, price)


def _candidate_profile(role: str, name: str, rng: random.Random) -> tuple[PlayerStats, dict[str, int], int, str, str, tuple[str, ...], str]:
    stats = _candidate_stats_for_role(role, rng)
    skills = _candidate_skill_ranks(role, rng)
    price = _candidate_price(role, stats, skills)
    backgrounds = ROLE_BACKGROUNDS.get(role, ("Field operator.",))
    advantages = ROLE_ADVANTAGES.get(role, ("Reliable field presence",))
    background = rng.choice(backgrounds)
    shuffled_advantages = list(advantages)
    rng.shuffle(shuffled_advantages)
    candidate_advantages = tuple(shuffled_advantages[:2]) if len(shuffled_advantages) > 1 else (shuffled_advantages[0],)
    if role == "robot":
        sex = ""
        portrait = portrait_path_for_robot(name, role)
    else:
        sex = rng.choice(("female", "male"))
        portrait = portrait_path_for_agent(name, role, sex)
    return stats, skills, price, background, sex, candidate_advantages, portrait


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
    roles: tuple[str, ...] = ("samurai", "sniper", "psi", "robot"),
    count: int | None = None,
    rng: random.Random | None = None,
) -> list[RecruitCandidate]:
    """Build a readable recruit list with randomised profiles and pricing."""
    rng = rng or random.SystemRandom()
    used = _existing_names(roster)
    candidates: list[RecruitCandidate] = []
    role_pool = [role for role in roles if role] or ["samurai"]
    target_count = max(6, int(count) if count is not None else rng.randint(6, 9))

    role_sequence = list(role_pool)
    while len(role_sequence) < target_count:
        role_sequence.append(rng.choice(role_pool))
    rng.shuffle(role_sequence)

    for index, role in enumerate(role_sequence[:target_count]):
        pool = [name for name in ROLE_NAME_POOLS.get(role, ()) if name not in used]
        if pool:
            name = rng.choice(pool)
        else:
            suffix = len(roster) + index + 1
            name = f"{role.title()}-{suffix}"
            while name in used:
                suffix += 1
                name = f"{role.title()}-{suffix}"
        stats, skills, price, background, sex, advantages, portrait_path = _candidate_profile(role, name, rng)
        preview_sheet = normalize_agent_sheet(stats=stats, attributes=None, skills=skills, derived_stats=None)
        candidates.append(
            RecruitCandidate(
                name=name,
                role=role,
                function=ROLE_FUNCTIONS.get(role, "Field operator."),
                background=background,
                advantages=advantages,
                stats=stats,
                preview_stats={
                    "level": int(preview_sheet.attributes.get("level", stats.level)),
                    "hp": int(preview_sheet.derived_stats.get("hp", stats.hp)),
                    "str": int(preview_sheet.attributes.get("str", stats.str)),
                    "agi": int(preview_sheet.attributes.get("agi", stats.agi)),
                    "psi": int(preview_sheet.attributes.get("psi", stats.psi)),
                    "con": int(preview_sheet.attributes.get("con", stats.con)),
                    "cha": int(preview_sheet.attributes.get("cha", stats.cha)),
                    "defense": int(preview_sheet.attributes.get("defense", stats.defense)),
                },
                skill_ranks=skills,
                price=price,
                sex=sex,
                portrait_path=portrait_path,
            )
        )
        used.add(name)

    return candidates


def recruit_agent(
    roster: list[Character],
    role: str,
    name: str | None = None,
    *,
    stats: PlayerStats | None = None,
    skills: dict[str, int] | None = None,
    sex: str | None = None,
    attributes: dict[str, int] | None = None,
    derived_stats: dict[str, int] | None = None,
) -> Character:
    """Create a named recruit and append them to the supplied roster."""
    next_name = normalize_agent_name(name, roster, role) if name else unique_recruit_name(roster, role)
    agent = create_character(
        next_name,
        role,
        stats=stats,
        skills=skills,
        sex=sex,
        attributes=attributes,
        derived_stats=derived_stats,
    )
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
