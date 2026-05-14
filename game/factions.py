from __future__ import annotations

from dataclasses import dataclass, field

from .savage_fate import SavageTag, tag_from_library


@dataclass
class Faction:
    """Political, corporate, or street power active in the vertical slice."""

    name: str
    influence: int
    hostility_to_player: int
    public_legitimacy: int
    active_tags: list[SavageTag] = field(default_factory=list)

    def clamp_pressure(self) -> None:
        self.influence = max(0, min(100, self.influence))
        self.hostility_to_player = max(0, min(100, self.hostility_to_player))
        self.public_legitimacy = max(0, min(100, self.public_legitimacy))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "influence": self.influence,
            "hostility_to_player": self.hostility_to_player,
            "public_legitimacy": self.public_legitimacy,
            "active_tags": [tag.to_dict() for tag in self.active_tags],
        }

    @classmethod
    def from_dict(cls, data: dict | "Faction") -> "Faction":
        if isinstance(data, cls):
            return data
        faction = cls(
            name=data.get("name", "Unknown Faction"),
            influence=data.get("influence", 25),
            hostility_to_player=data.get("hostility_to_player", 25),
            public_legitimacy=data.get("public_legitimacy", 25),
            active_tags=[
                SavageTag.from_dict(tag) for tag in data.get("active_tags", [])
            ],
        )
        faction.clamp_pressure()
        return faction


def create_vertical_slice_factions() -> list[Faction]:
    """Build the three factions present in the first playable world slice."""
    return [
        Faction(
            name="Aegis Dynamics",
            influence=72,
            hostility_to_player=18,
            public_legitimacy=54,
            active_tags=[tag_from_library("media_swarm")],
        ),
        Faction(
            name="Warrens Free Clinic",
            influence=34,
            hostility_to_player=8,
            public_legitimacy=81,
            active_tags=[],
        ),
        Faction(
            name="Chrome Jackals",
            influence=49,
            hostility_to_player=62,
            public_legitimacy=19,
            active_tags=[tag_from_library("gang_pressure")],
        ),
    ]
