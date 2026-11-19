from __future__ import annotations

from dataclasses import dataclass, field

from .savage_fate import SavageTag


@dataclass
class Consequence:
    """Narrative and mechanical fallout from a battle or operation."""

    affected_district: str | None = None
    affected_faction: str | None = None
    affected_agent: str | None = None
    severity: int = 1
    narrative_text: str = ""
    mechanical_effects: dict = field(default_factory=dict)
    tags: list[SavageTag] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "affected_district": self.affected_district,
            "affected_faction": self.affected_faction,
            "affected_agent": self.affected_agent,
            "severity": self.severity,
            "narrative_text": self.narrative_text,
            "mechanical_effects": self.mechanical_effects,
            "tags": [tag.to_dict() for tag in self.tags],
        }

    @classmethod
    def from_dict(cls, data: dict | "Consequence") -> "Consequence":
        if isinstance(data, cls):
            return data
        return cls(
            affected_district=data.get("affected_district"),
            affected_faction=data.get("affected_faction"),
            affected_agent=data.get("affected_agent"),
            severity=data.get("severity", 1),
            narrative_text=data.get("narrative_text", ""),
            mechanical_effects=dict(data.get("mechanical_effects", {})),
            tags=[SavageTag.from_dict(tag) for tag in data.get("tags", [])],
        )


def create_opening_consequence(district_name: str = "Chrome Warrens") -> Consequence:
    """Seed fallout that tells the player the district is already unstable."""
    return Consequence(
        affected_district=district_name,
        severity=1,
        narrative_text="Blackout rumors spike after an Aegis patrol vanishes under the east rail.",
        mechanical_effects={"unrest": 3, "media_heat": 2},
    )
