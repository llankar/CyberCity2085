"""Small research-management model for campaign upgrades.

Research is intentionally scoped as a light management layer: projects cost
corporate funds, take campaign days, and finish as unlock flags or small stat
modifiers that other systems can read without coupling to a large tech system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..gamestate import GameState


RESEARCH_CATEGORIES = (
    "vehicles",
    "weapons",
    "armor",
    "psy",
    "equipment",
    "robots",
    "power_armor",
)


@dataclass(frozen=True)
class ResearchProject:
    """A fund-and-time gated upgrade project."""

    id: str
    name: str
    category: str
    funds_cost: int
    days_required: int
    description: str = ""
    unlock_flags: tuple[str, ...] = ()
    stat_modifiers: dict[str, int] = field(default_factory=dict)
    requires: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.category not in RESEARCH_CATEGORIES:
            raise ValueError(f"Unsupported research category: {self.category}")
        if self.funds_cost <= 0:
            raise ValueError("Research projects must require positive funds")
        if self.days_required <= 0:
            raise ValueError("Research projects must require at least one day")

    def to_dict(self) -> dict:
        """Serialize project data for tools or future save migration."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "funds_cost": self.funds_cost,
            "days_required": self.days_required,
            "description": self.description,
            "unlock_flags": list(self.unlock_flags),
            "stat_modifiers": dict(self.stat_modifiers),
            "requires": list(self.requires),
        }


@dataclass
class ActiveResearch:
    """Progress record for a started research project."""

    project_id: str
    days_remaining: int
    days_elapsed: int = 0

    def advance_day(self) -> bool:
        """Advance one day and return whether the project is complete."""
        if self.days_remaining <= 0:
            return True
        self.days_remaining -= 1
        self.days_elapsed += 1
        return self.days_remaining <= 0

    @property
    def is_complete(self) -> bool:
        """Return whether no more days are required."""
        return self.days_remaining <= 0

    def to_dict(self) -> dict:
        """Serialize active progress for save files."""
        return {
            "project_id": self.project_id,
            "days_remaining": self.days_remaining,
            "days_elapsed": self.days_elapsed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActiveResearch":
        """Restore active research progress from save data."""
        return cls(
            project_id=str(data.get("project_id", "")),
            days_remaining=max(0, int(data.get("days_remaining", 0))),
            days_elapsed=max(0, int(data.get("days_elapsed", 0))),
        )


@dataclass(frozen=True)
class ResearchTree:
    """A compact catalog of available research projects."""

    projects: dict[str, ResearchProject]

    def project(self, project_id: str) -> ResearchProject | None:
        """Return a project by id if it exists."""
        return self.projects.get(project_id)

    def projects_for_category(self, category: str) -> list[ResearchProject]:
        """Return projects in stable category order."""
        return [p for p in self.projects.values() if p.category == category]

    def available_projects(
        self,
        completed_project_ids: set[str],
        active_project_ids: set[str] | None = None,
    ) -> list[ResearchProject]:
        """Return projects whose prerequisites are met and are not already active."""
        active_project_ids = active_project_ids or set()
        return [
            project
            for project in self.projects.values()
            if project.id not in completed_project_ids
            and project.id not in active_project_ids
            and all(required in completed_project_ids for required in project.requires)
        ]


def create_starter_research_tree() -> ResearchTree:
    """Create a compact 3X-style tech tree with clear progression branches."""
    starter_projects = [
        # Vehicles branch
        ResearchProject(
            id="vehicle_silent_wheels",
            name="Silent Wheels Retrofit",
            category="vehicles",
            funds_cost=25,
            days_required=2,
            description="Muffled drive trains make extraction vehicles harder to track.",
            unlock_flags=("vehicles.silent_wheels",),
            stat_modifiers={"vehicle_stealth": 1},
        ),
        ResearchProject(
            id="vehicle_black_channel_logistics",
            name="Black Channel Logistics",
            category="vehicles",
            funds_cost=45,
            days_required=4,
            requires=("vehicle_silent_wheels",),
            description="Ghost routing through shell corps improves drop reliability and budget control.",
            unlock_flags=("vehicles.black_channel_logistics",),
            stat_modifiers={"mission_budget_efficiency": 1},
        ),
        ResearchProject(
            id="vehicle_ghost_convoy_doctrine",
            name="Ghost Convoy Doctrine",
            category="vehicles",
            funds_cost=70,
            days_required=6,
            requires=("vehicle_black_channel_logistics",),
            description="Layered decoy convoys preserve extraction lanes under surveillance pressure.",
            unlock_flags=("vehicles.ghost_convoy_doctrine",),
            stat_modifiers={"vehicle_survivability": 1},
        ),
        # Weapons branch
        ResearchProject(
            id="weapon_smartlink_mk1",
            name="Smartlink Mk I",
            category="weapons",
            funds_cost=30,
            days_required=2,
            description="Cheap targeting mesh for agents who still trust a trigger.",
            unlock_flags=("weapons.smartlink_mk1",),
            stat_modifiers={"weapon_accuracy": 1},
        ),
        ResearchProject(
            id="weapon_corporate_rail_lattice",
            name="Corporate Rail Lattice",
            category="weapons",
            funds_cost=50,
            days_required=4,
            requires=("weapon_smartlink_mk1",),
            description="Weapon rails standardize hardpoint calibration for heavier loadouts.",
            unlock_flags=("weapons.corporate_rail_lattice",),
            stat_modifiers={"weapon_damage": 1},
        ),
        ResearchProject(
            id="weapon_oracle_killchain",
            name="Oracle Killchain Targeting",
            category="weapons",
            funds_cost=75,
            days_required=6,
            requires=("weapon_corporate_rail_lattice",),
            description="Cross-squad telemetry chains improve first-volley certainty on priority threats.",
            unlock_flags=("weapons.oracle_killchain",),
            stat_modifiers={"weapon_crit_window": 1},
        ),
        # Armor branch
        ResearchProject(
            id="armor_reactive_lining",
            name="Reactive Armor Lining",
            category="armor",
            funds_cost=35,
            days_required=3,
            description="Thin reactive plates reduce the first hit before medbay is needed.",
            unlock_flags=("armor.reactive_lining",),
            stat_modifiers={"armor_defense": 1},
        ),
        ResearchProject(
            id="armor_aegis_weave",
            name="Aegis Weave Shell",
            category="armor",
            funds_cost=55,
            days_required=5,
            requires=("armor_reactive_lining",),
            description="Layered weave plates trade speed for emotional survivability.",
            unlock_flags=("armor.aegis_weave",),
            stat_modifiers={"armor_resilience": 1},
        ),
        ResearchProject(
            id="armor_memorial_plating",
            name="Memorial Plating Grid",
            category="armor",
            funds_cost=80,
            days_required=7,
            requires=("armor_aegis_weave",),
            description="Field-tuned plating profiles absorb breach shock during retreat windows.",
            unlock_flags=("armor.memorial_plating",),
            stat_modifiers={"armor_breach_guard": 1},
        ),
        # Psy branch
        ResearchProject(
            id="psy_echo_discipline",
            name="Echo Discipline",
            category="psy",
            funds_cost=30,
            days_required=3,
            description="A controlled psi cadence that keeps gifted agents present.",
            unlock_flags=("psy.echo_discipline",),
            stat_modifiers={"psi_focus": 1},
        ),
        ResearchProject(
            id="psy_choir_firebreak",
            name="Choir Firebreak",
            category="psy",
            funds_cost=45,
            days_required=4,
            requires=("psy_echo_discipline",),
            description="Squad resonance drills reduce cascade panic during high-pressure ops.",
            unlock_flags=("psy.choir_firebreak",),
            stat_modifiers={"stress_resistance": 1},
        ),
        ResearchProject(
            id="psy_memory_anchor_ritual",
            name="Memory Anchor Rituals",
            category="psy",
            funds_cost=70,
            days_required=6,
            requires=("psy_choir_firebreak",),
            description="Guided anchor rites help operatives retain mission identity after psychic spillover.",
            unlock_flags=("psy.memory_anchor_ritual",),
            stat_modifiers={"psi_recovery": 1},
        ),
        # Equipment branch
        ResearchProject(
            id="equipment_field_mender",
            name="Field Mender Kit",
            category="equipment",
            funds_cost=20,
            days_required=2,
            description="Disposable trauma foam and a tiny diagnostic saint in a box.",
            unlock_flags=("equipment.field_mender",),
            stat_modifiers={"medkit_quality": 1},
        ),
        ResearchProject(
            id="equipment_tactical_fabricator",
            name="Tactical Fabricator Cache",
            category="equipment",
            funds_cost=40,
            days_required=4,
            requires=("equipment_field_mender",),
            description="Rapid-print utility pods increase mission adaptability.",
            unlock_flags=("equipment.tactical_fabricator",),
            stat_modifiers={"utility_capacity": 1},
        ),
        ResearchProject(
            id="equipment_lastlight_pack",
            name="Lastlight Sustainment Pack",
            category="equipment",
            funds_cost=60,
            days_required=5,
            requires=("equipment_tactical_fabricator",),
            description="Miniaturized reserve kits keep squads operation-ready across longer deployments.",
            unlock_flags=("equipment.lastlight_pack",),
            stat_modifiers={"mission_endurance": 1},
        ),
        # Robots branch
        ResearchProject(
            id="robot_loyalty_kernel",
            name="Loyalty Kernel Patch",
            category="robots",
            funds_cost=35,
            days_required=3,
            description="A patched obedience kernel for drones that heard too many ghosts.",
            unlock_flags=("robots.loyalty_kernel",),
            stat_modifiers={"robot_reliability": 1},
        ),
        ResearchProject(
            id="robot_hunter_killer_doctrine",
            name="Hunter-Killer Doctrine",
            category="robots",
            funds_cost=55,
            days_required=5,
            requires=("robot_loyalty_kernel", "weapon_smartlink_mk1"),
            description="Autonomous threat prioritization improves robot lethality and suppression.",
            unlock_flags=("robots.hunter_killer_doctrine",),
            stat_modifiers={"robot_firepower": 1},
        ),
        ResearchProject(
            id="robot_oathfire_command_net",
            name="Oathfire Command Net",
            category="robots",
            funds_cost=80,
            days_required=7,
            requires=("robot_hunter_killer_doctrine", "psy_choir_firebreak"),
            description="Human-robot trust loops improve allied coordination under fear-heavy scenarios.",
            unlock_flags=("robots.oathfire_command_net",),
            stat_modifiers={"robot_command_sync": 1},
        ),
        # Power-armor branch
        ResearchProject(
            id="power_armor_servo_prayer",
            name="Servo Prayer Loop",
            category="power_armor",
            funds_cost=40,
            days_required=4,
            description="Predictive servo chants make heavy armor feel almost human.",
            unlock_flags=("power_armor.servo_prayer",),
            stat_modifiers={"power_armor_mobility": 1},
        ),
        ResearchProject(
            id="power_armor_praetorian_frame",
            name="Praetorian Frame Contract",
            category="power_armor",
            funds_cost=65,
            days_required=6,
            requires=("power_armor_servo_prayer", "armor_reactive_lining"),
            description="Corporate-backed frame reinforcement unlocks elite suit survivability.",
            unlock_flags=("power_armor.praetorian_frame", "corp.contract.praetorian"),
            stat_modifiers={"power_armor_durability": 1, "corp_budget_bonus": 1},
        ),
        ResearchProject(
            id="power_armor_bastion_overdrive",
            name="Bastion Overdrive Suite",
            category="power_armor",
            funds_cost=90,
            days_required=8,
            requires=("power_armor_praetorian_frame", "robot_hunter_killer_doctrine"),
            description="Integrated pilot-assist and threat AI boosts suit tempo without replacing the pilot.",
            unlock_flags=("power_armor.bastion_overdrive",),
            stat_modifiers={"power_armor_response": 1},
        ),
    ]
    return ResearchTree({project.id: project for project in starter_projects})


def active_research_ids(game_state: "GameState") -> set[str]:
    """Return project ids currently being researched."""
    return {active.project_id for active in game_state.active_research}


def completed_research_ids(game_state: "GameState") -> set[str]:
    """Return completed project ids as a set."""
    return set(game_state.completed_research)


def can_start_research(
    game_state: "GameState", project_id: str, tree: ResearchTree | None = None
) -> bool:
    """Return whether a project can start right now."""
    tree = tree or create_starter_research_tree()
    project = tree.project(project_id)
    if project is None:
        return False
    completed = completed_research_ids(game_state)
    if project_id in completed or project_id in active_research_ids(game_state):
        return False
    if not all(required in completed for required in project.requires):
        return False
    return game_state.can_afford(project.funds_cost)


def start_research(
    game_state: "GameState", project_id: str, tree: ResearchTree | None = None
) -> bool:
    """Pay for a project and add it to active research when possible."""
    tree = tree or create_starter_research_tree()
    project = tree.project(project_id)
    if project is None or not can_start_research(game_state, project_id, tree):
        return False
    if not game_state.spend_funds(
        project.funds_cost,
        "research",
        f"Started {project.name} ({project.days_required}d).",
    ):
        return False
    game_state.active_research.append(
        ActiveResearch(project.id, project.days_required, days_elapsed=0)
    )
    game_state.add_event(
        f"Research started: {project.name} ({project.category.replace('_', ' ')}, "
        f"{project.days_required}d)."
    )
    return True


def apply_completed_research(game_state: "GameState", project: ResearchProject) -> None:
    """Apply a completed project's unlock flags and stat modifiers."""
    if project.id not in game_state.completed_research:
        game_state.completed_research.append(project.id)
    for flag in project.unlock_flags:
        if flag not in game_state.research_unlock_flags:
            game_state.research_unlock_flags.append(flag)
    for key, value in project.stat_modifiers.items():
        game_state.research_stat_modifiers[key] = (
            game_state.research_stat_modifiers.get(key, 0) + value
        )


def advance_research_days(
    game_state: "GameState", days: int = 1, tree: ResearchTree | None = None
) -> list[ResearchProject]:
    """Advance active research by campaign days and apply completions."""
    if days < 0:
        raise ValueError("days must be non-negative")
    tree = tree or create_starter_research_tree()
    completed_projects: list[ResearchProject] = []
    for _ in range(days):
        still_active: list[ActiveResearch] = []
        for active in game_state.active_research:
            if active.advance_day():
                project = tree.project(active.project_id)
                if project is not None:
                    apply_completed_research(game_state, project)
                    completed_projects.append(project)
                    game_state.add_event(f"Research complete: {project.name}.")
            else:
                still_active.append(active)
        game_state.active_research = still_active
    return completed_projects
