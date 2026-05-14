from __future__ import annotations

from dataclasses import dataclass, field

from .savage_fate import SavageTag, tag_from_library


@dataclass
class Operation:
    """Mission-sized pressure applied to one faction in one district."""

    type: str
    target_faction: str
    district: str
    risk: int
    objective: str
    complications: list[str] = field(default_factory=list)
    outcome_tags: list[SavageTag] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "target_faction": self.target_faction,
            "district": self.district,
            "risk": self.risk,
            "objective": self.objective,
            "complications": list(self.complications),
            "outcome_tags": [tag.to_dict() for tag in self.outcome_tags],
        }

    @classmethod
    def from_dict(cls, data: dict | "Operation") -> "Operation":
        if isinstance(data, cls):
            return data
        return cls(
            type=data.get("type", "intel"),
            target_faction=data.get("target_faction", "Unknown Faction"),
            district=data.get("district", "Chrome Warrens"),
            risk=data.get("risk", 1),
            objective=data.get("objective", "Stabilize the district."),
            complications=list(data.get("complications", [])),
            outcome_tags=[
                SavageTag.from_dict(tag) for tag in data.get("outcome_tags", [])
            ],
        )


def create_operation_templates(
    district_name: str = "Chrome Warrens",
) -> list[Operation]:
    """Return a handful of reusable vertical-slice operation seeds."""
    return [
        Operation(
            type="hearts_and_minds",
            target_faction="Warrens Free Clinic",
            district=district_name,
            risk=2,
            objective="Escort medtechs through blackout alleys and win visible trust.",
            complications=[
                "Power failures hide ambush routes",
                "Cameras may frame the team as occupiers",
            ],
            outcome_tags=[tag_from_library("media_swarm")],
        ),
        Operation(
            type="counter_gang_raid",
            target_faction="Chrome Jackals",
            district=district_name,
            risk=4,
            objective="Break a Jackal weapons handoff before it floods the Warrens.",
            complications=[
                "Civilian lookouts protect the drop",
                "The Jackals wired the crates to burn evidence",
            ],
            outcome_tags=[tag_from_library("gang_pressure")],
        ),
        Operation(
            type="signal_trace",
            target_faction="Aegis Dynamics",
            district=district_name,
            risk=3,
            objective="Trace a spoofed corporate order without triggering Aegis auditors.",
            complications=[
                "Ghost packets mimic friendly command",
                "A media drone is already on scene",
            ],
            outcome_tags=[tag_from_library("ghost_signal")],
        ),
    ]
