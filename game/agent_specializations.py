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


# ──────────────────────────────────────────────────────────────────────────────
# Role signatures — Visual and behavioral identity per role tree
# ──────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass
from typing import Literal
from enum import Enum


@dataclass(frozen=True)
class RoleSignature:
    """Visual and behavioral identity for a role."""
    
    key: str
    name: str
    primary_color: tuple[int, int, int]
    secondary_color: tuple[int, int, int]
    accent_color: tuple[int, int, int]
    description: str
    
    # Visual indicators
    has_mode_switch: bool = False  # e.g., breach/guard stance
    mode_names: tuple[str, str] = ("", "")  # (active, passive)
    
    # Combat behaviors that trigger automatically
    auto_behaviors: list[str] = None
    
    @property
    def mode_colors(self) -> dict[str, tuple[int, int, int]]:
        """Return colors for stance-based visual toggles."""
        return {
            "breach": (*self.accent_color[:3], 200),
            "guard": (*self.primary_color[:3], 200),
        }


_ROLE_SIGNATURES: dict[str, RoleSignature] = {
    "samurai": RoleSignature(
        key="samurai",
        name="SAMURAI",
        primary_color=(80, 190, 255),
        secondary_color=(140, 60, 30),
        accent_color=(255, 70, 30),  # Red for breach charge
        description="Close-combat specialist. Breach walls and guard choke points.",
        has_mode_switch=True,
        mode_names=("BREACH", "GUARD"),
        auto_behaviors=["breath_stance_detection"],
    ),
    "sniper": RoleSignature(
        key="sniper",
        name="SNIPER",
        primary_color=(100, 200, 60),
        secondary_color=(40, 80, 40),
        accent_color=(180, 255, 120),
        description="Long-range precision. Overwatch and eliminate high-value targets.",
        auto_behaviors=["sniper_scope_highlight", "overwatch_indication"],
    ),
    "psi": RoleSignature(
        key="psi",
        name="PSI",
        primary_color=(180, 50, 200),
        secondary_color=(60, 20, 100),
        accent_color=(240, 100, 255),
        description="Psychic warfare. Control minds and destabilize enemies.",
        has_mode_switch=True,
        mode_names=("CONTROL", "RISK"),
        auto_behaviors=["psi_pulse_ring"],
    ),
    "medic": RoleSignature(
        key="medic",
        name="MEDIC",
        primary_color=(60, 200, 100),
        secondary_color=(30, 70, 40),
        accent_color=(255, 200, 80),
        description="Field surgeon. Stabilize and cleanse wounds under fire.",
        auto_behaviors=["stabilization_indicator"],
    ),
    "robot": RoleSignature(
        key="robot",
        name="ROBOT",
        primary_color=(150, 150, 150),
        secondary_color=(80, 80, 80),
        accent_color=(200, 200, 200),
        description="Asset unit. Heat/ammunition management.",
        auto_behaviors=["heat_warning"],
    ),
}


def signature_for_role(role: str) -> RoleSignature | None:
    """Get the signature data for a role."""
    key = role.lower() if isinstance(role, str) else str(role).lower()
    return _ROLE_SIGNATURES.get(key)


# ──────────────────────────────────────────────────────────────────────────────
# Stance/Psi state management — per-unit tactical modes
# ──────────────────────────────────────────────────────────────────────────────

class Stance(Enum):
    """Samurai stance: BREACH (offensive charge) or GUARD (defensive anchor)."""
    BREACH = "breach"
    GUARD = "guard"


class PsiState(Enum):
    """Psi state: CONTROL (focused) or RISK (unstable/overdriven)."""
    CONTROL = "control"
    RISK = "risk"


def default_stance_for_unit(unit) -> Stance:
    """Determine the appropriate stance for a samurai unit."""
    character = getattr(unit, "character", None)
    if not character:
        return Stance.GUARD
    
    role = str(character.role).lower()
    if role != "samurai":
        return Stance.GUARD
    
    # Breach when at close range with enemies
    enemy_units = getattr(unit, "_combat_context", {}).get("enemy_units", [])
    living_enemies = [e for e in enemy_units if getattr(e, "health", 0) > 0]
    
    if not living_enemies:
        return Stance.GUARD
    
    nearest_dist = float("inf")
    for enemy in living_enemies:
        dist = unit.distance_to(enemy) if hasattr(unit, "distance_to") else getattr(enemy, "x", None)
        if dist is None:
            # Fallback: check grid coordinates
            ux, uy = getattr(unit, "x", 0), getattr(unit, "y", 0)
            ex, ey = getattr(enemy, "x", 0), getattr(enemy, "y", 0)
            dist = ((ux - ex) ** 2 + (uy - ey) ** 2) ** 0.5
        nearest_dist = min(nearest_dist, dist)
    
    # 32 pixels is approx 1 tile — switch to breach when very close
    return Stance.BREACH if nearest_dist < 48 else Stance.GUARD


def default_psi_state_for_unit(unit) -> PsiState:
    """Determine the appropriate psi state for a psi unit."""
    character = getattr(unit, "character", None)
    if not character:
        return PsiState.CONTROL
    
    role = str(character.role).lower()
    if role != "psi":
        return PsiState.CONTROL
    
    # Risk when using psi powers frequently or under stress
    psi_stamina = getattr(unit, "psi_stamina", 10)
    psi_max = getattr(unit, "psi_max", 10)
    
    # Higher risk when low stamina (overdriving) and stressed character
    if psi_stamina < psi_max * 0.4 or unit.character.stress > 8:
        return PsiState.RISK
    
    return PsiState.CONTROL


def update_unit_stance(unit, stance_override=None) -> Stance:
    """Update a samurai's stance based on tactical situation."""
    if stance_override is not None:
        return stance_override
    
    return default_stance_for_unit(unit)


def update_unit_psi_state(unit, psi_override=None) -> PsiState:
    """Update a psi unit's state based on mental load."""
    if psi_override is not None:
        return psi_override
    
    return default_psi_state_for_unit(unit)


# ──────────────────────────────────────────────────────────────────────────────


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


# ──────────────────────────────────────────────────────────────────────────────
# Role signatures — Visual and behavioral identity per role tree
# ──────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class RoleSignature:
    """Visual and behavioral identity for a role."""
    
    key: str
    name: str
    primary_color: tuple[int, int, int]
    secondary_color: tuple[int, int, int]
    accent_color: tuple[int, int, int]
    description: str
    
    # Visual indicators
    has_mode_switch: bool = False  # e.g., breach/guard stance
    mode_names: tuple[str, str] = ("", "")  # (active, passive)
    
    # Combat behaviors that trigger automatically
    auto_behaviors: list[str] = None
    
    @property
    def mode_colors(self) -> dict[str, tuple[int, int, int]]:
        """Return colors for stance-based visual toggles."""
        return {
            "breach": (*self.accent_color[:3], 200),
            "guard": (*self.primary_color[:3], 200),
        }


_ROLE_SIGNATURES: dict[str, RoleSignature] = {
    "samurai": RoleSignature(
        key="samurai",
        name="SAMURAI",
        primary_color=(80, 190, 255),
        secondary_color=(140, 60, 30),
        accent_color=(255, 70, 30),  # Red for breach charge
        description="Close-combat specialist. Breach walls and guard choke points.",
        has_mode_switch=True,
        mode_names=("BREACH", "GUARD"),
        auto_behaviors=["breath_stance_detection"],
    ),
    "sniper": RoleSignature(
        key="sniper",
        name="SNIPER",
        primary_color=(100, 200, 60),
        secondary_color=(40, 80, 40),
        accent_color=(180, 255, 120),
        description="Long-range precision. Overwatch and eliminate high-value targets.",
        auto_behaviors=["sniper_scope_highlight", "overwatch_indication"],
    ),
    "psi": RoleSignature(
        key="psi",
        name="PSI",
        primary_color=(180, 50, 200),
        secondary_color=(60, 20, 100),
        accent_color=(240, 100, 255),
        description="Psychic warfare. Control minds and destabilize enemies.",
        has_mode_switch=True,
        mode_names=("CONTROL", "RISK"),
        auto_behaviors=["psi_pulse_ring"],
    ),
    "medic": RoleSignature(
        key="medic",
        name="MEDIC",
        primary_color=(60, 200, 100),
        secondary_color=(30, 70, 40),
        accent_color=(255, 200, 80),
        description="Field surgeon. Stabilize and cleanse wounds under fire.",
        auto_behaviors=["stabilization_indicator"],
    ),
    "robot": RoleSignature(
        key="robot",
        name="ROBOT",
        primary_color=(150, 150, 150),
        secondary_color=(80, 80, 80),
        accent_color=(200, 200, 200),
        description="Asset unit. Heat/ammunition management.",
        auto_behaviors=["heat_warning"],
    ),
}


def signature_for_role(role: str) -> RoleSignature | None:
    """Get the signature data for a role."""
    key = role.lower() if isinstance(role, str) else str(role).lower()
    return _ROLE_SIGNATURES.get(key)

