"""Role-based agent specialization trees.

The tree is intentionally small and readable:
- each role has a handful of branches
- each unlock grants a simple stat bonus
- the UI can present it as a lightweight RPG progression layer
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .stats import PlayerStats


@dataclass(frozen=True)
class TalentNode:
    """One unlockable talent in a role tree."""

    id: str
    role: str
    name: str
    tier: int
    description: str
    bonuses: dict[str, int]
    prerequisites: tuple[str, ...] = ()


_TALENT_TREES: dict[str, tuple[TalentNode, ...]] = {
    "samurai": (
        TalentNode(
            "samurai_street_blade",
            "samurai",
            "Street Blade",
            1,
            "Sharper close-quarters instincts and faster strikes.",
            {"str": 1},
        ),
        TalentNode(
            "samurai_iron_guard",
            "samurai",
            "Iron Guard",
            1,
            "Frontline discipline that hardens the line.",
            {"defense": 1},
        ),
        TalentNode(
            "samurai_breach_form",
            "samurai",
            "Breach Form",
            2,
            "Refines force and timing for point-blank assaults.",
            {"str": 1, "agi": 1},
            ("samurai_street_blade",),
        ),
        TalentNode(
            "samurai_wall_stance",
            "samurai",
            "Wall Stance",
            2,
            "Turns the agent into a stubborn anchor under pressure.",
            {"defense": 1, "con": 1},
            ("samurai_iron_guard",),
        ),
        TalentNode(
            "samurai_last_cut",
            "samurai",
            "Last Cut",
            3,
            "The final form of a veteran blade specialist.",
            {"str": 1, "defense": 1},
            ("samurai_breach_form", "samurai_wall_stance"),
        ),
    ),
    "sniper": (
        TalentNode(
            "sniper_overwatch_eye",
            "sniper",
            "Overwatch Eye",
            1,
            "Improves patience, timing, and target tracking.",
            {"agi": 1},
        ),
        TalentNode(
            "sniper_silent_step",
            "sniper",
            "Silent Step",
            1,
            "Tighter movement discipline and better positioning.",
            {"defense": 1},
        ),
        TalentNode(
            "sniper_dead_eye",
            "sniper",
            "Dead Eye",
            2,
            "Precision drills that turn long shots into certainties.",
            {"agi": 1},
            ("sniper_overwatch_eye",),
        ),
        TalentNode(
            "sniper_ghost_scope",
            "sniper",
            "Ghost Scope",
            2,
            "Keeps the shooter calm, hidden, and hard to pin down.",
            {"agi": 1, "defense": 1},
            ("sniper_silent_step",),
        ),
        TalentNode(
            "sniper_longshot_mastery",
            "sniper",
            "Longshot Mastery",
            3,
            "The sniper becomes lethal across the whole battlefield.",
            {"agi": 1, "defense": 1},
            ("sniper_dead_eye", "sniper_ghost_scope"),
        ),
    ),
    "psi": (
        TalentNode(
            "psi_mind_focus",
            "psi",
            "Mind Focus",
            1,
            "Strengthens concentration and psychic output.",
            {"psi": 1},
        ),
        TalentNode(
            "psi_warding_shell",
            "psi",
            "Warding Shell",
            1,
            "A mental barrier that improves resilience.",
            {"defense": 1},
        ),
        TalentNode(
            "psi_mind_spike",
            "psi",
            "Mind Spike",
            2,
            "Trains sharper psychic attacks under stress.",
            {"psi": 1},
            ("psi_mind_focus",),
        ),
        TalentNode(
            "psi_veil_step",
            "psi",
            "Veil Step",
            2,
            "Teaches movement and clarity while under pressure.",
            {"agi": 1},
            ("psi_warding_shell",),
        ),
        TalentNode(
            "psi_synapse_burst",
            "psi",
            "Synapse Burst",
            3,
            "A veteran psi operative that shapes the whole room.",
            {"psi": 1, "defense": 1},
            ("psi_mind_spike", "psi_veil_step"),
        ),
    ),
}


def talent_nodes_for_role(role: str) -> tuple[TalentNode, ...]:
    """Return the ordered talent tree for a role."""
    return _TALENT_TREES.get(role, ())


def talent_node_by_id(node_id: str) -> TalentNode | None:
    """Return one node by id across all trees."""
    for nodes in _TALENT_TREES.values():
        for node in nodes:
            if node.id == node_id:
                return node
    return None


def available_talent_nodes(role: str, unlocked: set[str]) -> list[TalentNode]:
    """Return unlockable nodes for the supplied role and unlocked set."""
    candidates = []
    for node in talent_nodes_for_role(role):
        if node.id in unlocked:
            continue
        if all(req in unlocked for req in node.prerequisites):
            candidates.append(node)
    return candidates


def can_unlock_talent(role: str, unlocked: set[str], node_id: str) -> bool:
    """Check whether a node is valid for the current tree state."""
    node = talent_node_by_id(node_id)
    return bool(
        node
        and node.role == role
        and node.id not in unlocked
        and all(req in unlocked for req in node.prerequisites)
    )


def unlock_talent(character, node_id: str) -> bool:
    """Spend one talent point to unlock a specialization node."""
    node = talent_node_by_id(node_id)
    if node is None:
        return False
    unlocked = set(getattr(character, "specializations", []))
    if character.talent_points <= 0:
        return False
    if not can_unlock_talent(character.role, unlocked, node_id):
        return False
    unlocked.add(node_id)
    character.specializations = sorted(unlocked)
    character.talent_points -= 1
    return True


def apply_talent_bonuses(stats: PlayerStats, unlocked_talent_ids: list[str]) -> PlayerStats:
    """Return a stats copy with role-tree bonuses applied."""
    adjusted = replace(stats)
    for node_id in unlocked_talent_ids:
        node = talent_node_by_id(node_id)
        if node is None:
            continue
        for key, bonus in node.bonuses.items():
            if hasattr(adjusted, key):
                setattr(adjusted, key, max(0, getattr(adjusted, key) + bonus))
    adjusted.recalculate_hp()
    adjusted.hp = min(adjusted.hp, adjusted.max_hp)
    return adjusted

