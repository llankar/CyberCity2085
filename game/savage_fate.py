from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SavageTag:
    """Narrative tag used to color missions, outcomes, and consequences."""

    name: str
    description: str
    intensity: int = 1
    source: str = "world"
    expires_after_turns: int | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "intensity": self.intensity,
            "source": self.source,
            "expires_after_turns": self.expires_after_turns,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict | "SavageTag") -> "SavageTag":
        if isinstance(data, cls):
            return data
        return cls(
            name=data.get("name", "unknown"),
            description=data.get("description", ""),
            intensity=data.get("intensity", 1),
            source=data.get("source", "world"),
            expires_after_turns=data.get("expires_after_turns"),
            metadata=dict(data.get("metadata", {})),
        )


SAVAGE_TAG_LIBRARY: dict[str, SavageTag] = {
    "neon_blackout": SavageTag(
        name="neon_blackout",
        description="Rolling power outages make every alley a blind spot.",
        intensity=2,
        source="district",
    ),
    "media_swarm": SavageTag(
        name="media_swarm",
        description="Pirate feeds and corporate journalists are hunting for a scandal.",
        intensity=2,
        source="media",
    ),
    "gang_pressure": SavageTag(
        name="gang_pressure",
        description="Street crews are testing who really owns the district.",
        intensity=1,
        source="faction",
    ),
    "ghost_signal": SavageTag(
        name="ghost_signal",
        description="A hostile signal rides the local mesh and spoofs trusted orders.",
        intensity=3,
        source="operation",
    ),
    "media_leak": SavageTag(
        name="media_leak",
        description="Leaked footage turns tactical choices into public evidence.",
        intensity=2,
        source="complication",
    ),
    "civilian_panic": SavageTag(
        name="civilian_panic",
        description="Noncombatants scatter, block exits, and amplify district unrest.",
        intensity=2,
        source="complication",
    ),
    "faction_retaliation": SavageTag(
        name="faction_retaliation",
        description="A wounded faction answers with reprisal crews and pressure campaigns.",
        intensity=3,
        source="complication",
    ),
}


def tag_from_library(name: str) -> SavageTag:
    """Return a detached copy of a known narrative tag."""
    tag = SAVAGE_TAG_LIBRARY[name]
    return SavageTag.from_dict(tag.to_dict())
