import json
from dataclasses import dataclass, field
from typing import List


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
    characters: List["Character"] = field(default_factory=list)

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
        from .character import Character

        gs.characters = [Character.from_dict(c) for c in data.get("characters", [])]
        return gs
