"""Read-only dossier projections. All calculations/unlock rules stay in the game."""

from dataclasses import dataclass
from game.agents.sheet_calculations import compute_derived_stats, skill_total
from game.agents.sheet_schema import build_default_attributes, SKILL_MAX_RANK
from game.progression import ALLOWED_SKILL_KEYS
from game.agent_specializations import (
    talent_nodes_for_role,
    can_unlock_talent,
    talent_node_by_id,
)

SKILL_ATTRIBUTES = {
    "firearms": "agi",
    "close_combat": "str",
    "tactics": "cha",
    "tech": "psi",
    "medicine": "cha",
    "influence": "cha",
    "stealth": "agi",
    "composure": "con",
    "psychokinesis": "psi",
    "pyrokinesis": "psi",
    "cryokinesis": "psi",
    "telepathy": "psi",
}
ATTRIBUTE_ORDER = (
    ("str", "STR"),
    ("agi", "AGI"),
    ("psi", "PSI"),
    ("def", "DEF"),
    ("con", "CON"),
)
READINESS_ORDER = (
    ("hp", "HP"),
    ("aim", "AIM"),
    ("defense", "DEF"),
    ("initiative", "INIT"),
    ("resolve", "RES"),
    ("recovery_rate", "REC"),
)


@dataclass(frozen=True)
class SkillDisplay:
    key: str
    attribute: str
    attribute_value: int
    rank: int
    total: int
    can_spend: bool


@dataclass(frozen=True)
class TalentDisplay:
    node: object
    state: str
    missing_names: tuple[str, ...]
    needs_point: bool


@dataclass(frozen=True)
class CharacterSheetData:
    attributes: dict
    derived: dict
    stress_state: str
    xp_target: int
    skills: tuple[SkillDisplay, ...]
    talents: tuple[TalentDisplay, ...]


def build_character_sheet_data(character):
    attributes = build_default_attributes(character.stats)
    stress = int(character.stress)
    stress_state = (
        "steady"
        if stress < 35
        else "rattled" if stress < 65 else "frayed" if stress < 85 else "breaking"
    )
    derived = compute_derived_stats(
        attributes,
        character.skills,
        character.loadout.total_stat_bonuses(),
        stress_state,
    )
    skills = []
    for key in ALLOWED_SKILL_KEYS:
        linked = SKILL_ATTRIBUTES[key]
        rank = int(character.skills.get(key, 0))
        skills.append(
            SkillDisplay(
                key,
                linked,
                attributes[linked],
                rank,
                skill_total(key, attributes, character.skills, {}),
                character.pending_points > 0 and rank < SKILL_MAX_RANK,
            )
        )
    unlocked = set(character.specializations)
    talents = []
    for node in talent_nodes_for_role(character.role):
        owned = node.id in unlocked
        allowed = can_unlock_talent(character.role, unlocked, node.id)
        state = (
            "UNLOCKED"
            if owned
            else "AVAILABLE" if allowed and character.talent_points > 0 else "LOCKED"
        )
        missing = tuple(
            (talent_node_by_id(req).name if talent_node_by_id(req) else req)
            for req in node.prerequisites
            if req not in unlocked
        )
        talents.append(
            TalentDisplay(
                node, state, missing, not owned and character.talent_points <= 0
            )
        )
    # This is the exact existing Character.gain_xp threshold, not the mockup's XP.
    return CharacterSheetData(
        attributes,
        derived,
        stress_state,
        100 * character.stats.level**2,
        tuple(skills),
        tuple(talents),
    )
