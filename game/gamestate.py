from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from .consequences import Consequence, create_opening_consequence
from .factions import Faction, create_vertical_slice_factions
from .mission_templates import MissionTemplate, create_mission_templates
from .operations import Operation, create_operation_templates
from .world import District, create_vertical_slice_district

if TYPE_CHECKING:
    from .character import Character


@dataclass
class GameState:
    """Holds the state of the current game."""

    # Corporation values accumulated over all turns
    corp_budget: dict = field(
        default_factory=lambda: {
            "research": 0,
            "security": 0,
            "politics": 0,
            "black_ops": 0,
        }
    )

    # Management data for the city phase
    city_budget: dict = field(
        default_factory=lambda: {
            "armaments": 0,
            "garrisons": 0,
            "defense_zones": 0,
        }
    )

    # List of recruited characters
    characters: List[Character] = field(default_factory=list)

    # First vertical-slice world model: one district, one base, and three factions
    base_name: str = "Aegis Forward Base Kilo"
    district: District = field(default_factory=create_vertical_slice_district)
    factions: list[Faction] = field(default_factory=create_vertical_slice_factions)
    active_operations: list[Operation] = field(
        default_factory=create_operation_templates
    )
    mission_templates: list[MissionTemplate] = field(
        default_factory=create_mission_templates
    )
    active_mission: MissionTemplate | None = None
    selected_mission_index: int = 0
    recent_consequences: list[Consequence] = field(
        default_factory=lambda: [create_opening_consequence()]
    )
    latest_agent_aftermath: list[str] = field(default_factory=list)
    event_log: list[str] = field(
        default_factory=lambda: [
            "Turn 1: Forward Base Kilo establishes overwatch in the Chrome Warrens."
        ]
    )

    # Experience points gained through battles
    x: int = 0

    # Turn management
    turn: int = 1
    budget_pool: int = 0

    def __post_init__(self) -> None:
        if not self.budget_pool:
            self.budget_pool = self.compute_budget()

    # ------------------------------------------------------------------
    # Turn and budget management
    # ------------------------------------------------------------------
    def compute_budget(self) -> int:
        """Compute the budget for the next turn based on current corp values."""
        return 100 + sum(self.corp_budget.values()) // 10

    def allocate_corp_funds(self, key: str, amount: int) -> bool:
        """Attempt to allocate funds from the current budget."""
        if key in self.corp_budget and self.budget_pool >= amount:
            self.corp_budget[key] += amount
            self.budget_pool -= amount
            return True
        return False

    def advance_turn(self) -> None:
        """Move to the next turn, tick recovery timers, and refresh the budget."""
        recovered_agents = []
        for character in self.characters:
            if character.recovery_turns > 0:
                character.recovery_turns -= 1
                if character.recovery_turns == 0:
                    recovered_agents.append(character.name)

        self.turn += 1
        self.budget_pool = self.compute_budget()
        self.add_event(
            f"Turn {self.turn}: Corporate budget refreshed for {self.base_name}."
        )
        for name in recovered_agents:
            self.add_event(f"Turn {self.turn}: {name} is deployable after recovery.")

    def add_event(self, text: str) -> None:
        """Append a compact event-log entry and retain only the latest beats."""
        self.event_log.append(text)
        self.event_log = self.event_log[-12:]

    def record_consequence(self, consequence: Consequence) -> None:
        """Store recent fallout and add it to the event log."""
        self.recent_consequences.append(consequence)
        self.recent_consequences = self.recent_consequences[-6:]
        if consequence.narrative_text:
            self.add_event(consequence.narrative_text)

    def apply_consequence(self, consequence: Consequence) -> None:
        """Apply district and faction effects from a mission consequence."""
        effects = consequence.mechanical_effects
        for key in ("stability", "unrest", "media_heat"):
            if key in effects and hasattr(self.district, key):
                setattr(self.district, key, getattr(self.district, key) + effects[key])
        self.district.clamp_pressure()

        if consequence.affected_faction:
            faction = self.get_faction(consequence.affected_faction)
            if faction:
                if "faction_hostility" in effects:
                    faction.hostility_to_player += effects["faction_hostility"]
                if "faction_influence" in effects:
                    faction.influence += effects["faction_influence"]
                if "faction_legitimacy" in effects:
                    faction.public_legitimacy += effects["faction_legitimacy"]
                for tag in consequence.tags:
                    if all(existing.name != tag.name for existing in faction.active_tags):
                        faction.active_tags.append(tag)
                faction.clamp_pressure()

        for tag in consequence.tags:
            if all(existing.name != tag.name for existing in self.district.tags):
                self.district.tags.append(tag)
        self.record_consequence(consequence)

    def apply_active_mission_pressure(self) -> None:
        """Apply up-front district pressure from the selected active mission."""
        if not self.active_mission:
            return
        for key, amount in self.active_mission.district_pressure.items():
            if hasattr(self.district, key):
                setattr(self.district, key, getattr(self.district, key) + amount)
        self.district.clamp_pressure()
        self.add_event(
            f"Mission launched: {self.active_mission.title} against "
            f"{self.active_mission.target_faction}."
        )

    def get_faction(self, name: str) -> Faction | None:
        """Find a faction by name in the current world slice."""
        for faction in self.factions:
            if faction.name == name:
                return faction
        return None

    def adjust_corp_budget(self, key: str, amount: int) -> None:
        """Backward compatible wrapper around :py:meth:`allocate_corp_funds`."""
        self.allocate_corp_funds(key, amount)

    def adjust_city_budget(self, key: str, amount: int) -> None:
        if key in self.city_budget:
            self.city_budget[key] += amount

    def save(self, path: str):
        data = {
            "turn": self.turn,
            "budget_pool": self.budget_pool,
            "corp_budget": self.corp_budget,
            "city_budget": self.city_budget,
            "characters": [c.to_dict() for c in self.characters],
            "x": self.x,
            "base_name": self.base_name,
            "district": self.district.to_dict(),
            "factions": [faction.to_dict() for faction in self.factions],
            "active_operations": [
                operation.to_dict() for operation in self.active_operations
            ],
            "mission_templates": [
                mission.to_dict() for mission in self.mission_templates
            ],
            "active_mission": (
                self.active_mission.to_dict() if self.active_mission else None
            ),
            "selected_mission_index": self.selected_mission_index,
            "recent_consequences": [
                consequence.to_dict() for consequence in self.recent_consequences
            ],
            "latest_agent_aftermath": list(self.latest_agent_aftermath),
            "event_log": list(self.event_log),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str) -> "GameState":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        gs = cls()
        gs.corp_budget.update(data.get("corp_budget", {}))
        gs.city_budget.update(data.get("city_budget", {}))
        gs.turn = data.get("turn", 1)
        gs.budget_pool = data.get("budget_pool", gs.compute_budget())
        gs.x = data.get("x", 0)
        gs.base_name = data.get("base_name", gs.base_name)
        gs.district = District.from_dict(data.get("district", gs.district.to_dict()))
        gs.factions = [
            Faction.from_dict(faction) for faction in data.get("factions", [])
        ] or create_vertical_slice_factions()
        gs.active_operations = [
            Operation.from_dict(operation)
            for operation in data.get("active_operations", [])
        ] or create_operation_templates(gs.district.name)
        gs.mission_templates = [
            MissionTemplate.from_dict(mission)
            for mission in data.get("mission_templates", [])
        ] or create_mission_templates(gs.district.name)
        active_mission_data = data.get("active_mission")
        gs.active_mission = (
            MissionTemplate.from_dict(active_mission_data)
            if active_mission_data
            else None
        )
        gs.selected_mission_index = data.get("selected_mission_index", 0)
        gs.recent_consequences = [
            Consequence.from_dict(consequence)
            for consequence in data.get("recent_consequences", [])
        ] or [create_opening_consequence(gs.district.name)]
        gs.latest_agent_aftermath = list(data.get("latest_agent_aftermath", []))
        gs.event_log = list(data.get("event_log", gs.event_log))
        from .character import Character

        gs.characters = [Character.from_dict(c) for c in data.get("characters", [])]
        return gs
