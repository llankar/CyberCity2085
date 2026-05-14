from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from .consequences import Consequence, create_opening_consequence
from .factions import Faction, create_vertical_slice_factions
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
    recent_consequences: list[Consequence] = field(
        default_factory=lambda: [create_opening_consequence()]
    )
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
        """Move to the next turn and refresh the budget."""
        self.turn += 1
        self.budget_pool = self.compute_budget()
        self.add_event(
            f"Turn {self.turn}: Corporate budget refreshed for {self.base_name}."
        )

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
            "recent_consequences": [
                consequence.to_dict() for consequence in self.recent_consequences
            ],
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
        gs.recent_consequences = [
            Consequence.from_dict(consequence)
            for consequence in data.get("recent_consequences", [])
        ] or [create_opening_consequence(gs.district.name)]
        gs.event_log = list(data.get("event_log", gs.event_log))
        from .character import Character

        gs.characters = [Character.from_dict(c) for c in data.get("characters", [])]
        return gs
