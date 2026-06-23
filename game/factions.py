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
    category: str = "local"
    revealed: bool = True

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
            "category": self.category,
            "revealed": self.revealed,
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
            category=data.get("category", "local"),
            revealed=bool(data.get("revealed", True)),
        )
        faction.clamp_pressure()
        return faction


def create_vertical_slice_factions() -> list[Faction]:
    """Build the factions visible in the first playable world slice."""
    return [
        Faction(
            name="Aegis Dynamics",
            influence=72,
            hostility_to_player=18,
            public_legitimacy=54,
            active_tags=[tag_from_library("media_swarm")],
            category="corporate",
        ),
        Faction(
            name="Warrens Free Clinic",
            influence=34,
            hostility_to_player=8,
            public_legitimacy=81,
            active_tags=[],
            category="local_city",
        ),
        Faction(
            name="Chrome Jackals",
            influence=49,
            hostility_to_player=62,
            public_legitimacy=19,
            active_tags=[tag_from_library("gang_pressure")],
            category="raider",
        ),
    ]


def create_core_campaign_factions(*, include_hidden: bool = True) -> list[Faction]:
    """Build first-class faction/content entries for the larger campaign."""
    factions = create_vertical_slice_factions()
    factions.extend(
        [
            Faction(
                name="Starvers",
                influence=58,
                hostility_to_player=88,
                public_legitimacy=0,
                active_tags=[],
                category="starver",
            ),
            Faction(
                name="Three Sevens",
                influence=82,
                hostility_to_player=74,
                public_legitimacy=46,
                active_tags=[tag_from_library("media_swarm")],
                category="corporate_antagonist",
            ),
            Faction(
                name="Pharmacorp",
                influence=76,
                hostility_to_player=34,
                public_legitimacy=61,
                active_tags=[],
                category="corporate",
            ),
            Faction(
                name="Novatek",
                influence=68,
                hostility_to_player=48,
                public_legitimacy=44,
                active_tags=[],
                category="corporate",
            ),
            Faction(
                name="Raiders",
                influence=41,
                hostility_to_player=72,
                public_legitimacy=8,
                active_tags=[tag_from_library("gang_pressure")],
                category="raider",
            ),
            Faction(
                name="Mutants",
                influence=39,
                hostility_to_player=66,
                public_legitimacy=4,
                active_tags=[],
                category="mutant",
            ),
            Faction(
                name="Corporate Security",
                influence=64,
                hostility_to_player=42,
                public_legitimacy=35,
                active_tags=[],
                category="security",
            ),
            Faction(
                name="New York Civic Grid",
                influence=52,
                hostility_to_player=12,
                public_legitimacy=58,
                active_tags=[],
                category="local_city",
            ),
        ]
    )
    if include_hidden:
        factions.extend(
            [
                Faction(
                    name="Preservationist AIs",
                    influence=70,
                    hostility_to_player=5,
                    public_legitimacy=0,
                    active_tags=[],
                    category="hidden_ai",
                    revealed=False,
                ),
                Faction(
                    name="Exterminator AIs",
                    influence=70,
                    hostility_to_player=90,
                    public_legitimacy=0,
                    active_tags=[],
                    category="hidden_ai",
                    revealed=False,
                ),
            ]
        )
    return factions
