from __future__ import annotations

from dataclasses import dataclass, field

from .savage_fate import SavageTag, tag_from_library


@dataclass
class District:
    """A single playable slice of CyberCity's wider urban sprawl."""

    name: str
    stability: int
    control_faction: str
    unrest: int
    media_heat: int
    tags: list[SavageTag] = field(default_factory=list)

    def clamp_pressure(self) -> None:
        """Keep mutable district pressure values within readable 0-100 bands."""
        self.stability = max(0, min(100, self.stability))
        self.unrest = max(0, min(100, self.unrest))
        self.media_heat = max(0, min(100, self.media_heat))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "stability": self.stability,
            "control_faction": self.control_faction,
            "unrest": self.unrest,
            "media_heat": self.media_heat,
            "tags": [tag.to_dict() for tag in self.tags],
        }

    @classmethod
    def from_dict(cls, data: dict | "District") -> "District":
        if isinstance(data, cls):
            return data
        district = cls(
            name=data.get("name", "Chrome Warrens"),
            stability=data.get("stability", 45),
            control_faction=data.get("control_faction", "Aegis Dynamics"),
            unrest=data.get("unrest", 35),
            media_heat=data.get("media_heat", 20),
            tags=[SavageTag.from_dict(tag) for tag in data.get("tags", [])],
        )
        district.clamp_pressure()
        return district


def create_vertical_slice_district() -> District:
    """Build the one district used by the first vertical-slice world model."""
    return District(
        name="Chrome Warrens",
        stability=45,
        control_faction="Aegis Dynamics",
        unrest=38,
        media_heat=24,
        tags=[tag_from_library("neon_blackout"), tag_from_library("gang_pressure")],
    )
