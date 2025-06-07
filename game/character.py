from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Character:
    name: str
    level: int = 1
    skill_points: int = 0
    talents: Dict[str, int] = field(default_factory=dict)
    equipment: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "level": self.level,
            "skill_points": self.skill_points,
            "talents": self.talents,
            "equipment": self.equipment,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        return cls(
            name=data.get("name", "Unnamed"),
            level=data.get("level", 1),
            skill_points=data.get("skill_points", 0),
            talents=data.get("talents", {}),
            equipment=data.get("equipment", {}),
        )
