import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class GameState:
    corp_budget: dict = field(default_factory=lambda: {
        "research": 0,
        "security": 0,
        "politics": 0,
        "black_ops": 0,
    })
    city_budget: dict = field(default_factory=lambda: {
        "armaments": 0,
        "garrisons": 0,
        "defense_zones": 0,
    })
    characters: List["Character"] = field(default_factory=list)

    def save(self, path: str):
        data = {
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
        from .character import Character
        gs.characters = [Character.from_dict(c) for c in data.get("characters", [])]
        return gs
