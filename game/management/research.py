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
    """Create one memorable starter project for each requested category."""
    starter_projects = [
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
            id="power_armor_servo_prayer",
            name="Servo Prayer Loop",
            category="power_armor",
            funds_cost=40,
            days_required=4,
            description="Predictive servo chants make heavy armor feel almost human.",
            unlock_flags=("power_armor.servo_prayer",),
            stat_modifiers={"power_armor_mobility": 1},
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
