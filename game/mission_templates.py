from __future__ import annotations

from dataclasses import dataclass, field

from .consequences import Consequence
from .savage_fate import SavageTag, tag_from_library


@dataclass
class MissionComplication:
    """A battle complication that can become fallout for an active mission."""

    key: str
    name: str
    trigger_text: str
    risk_threshold: int
    tags: list[SavageTag] = field(default_factory=list)
    consequence: Consequence = field(default_factory=Consequence)

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "trigger_text": self.trigger_text,
            "risk_threshold": self.risk_threshold,
            "tags": [tag.to_dict() for tag in self.tags],
            "consequence": self.consequence.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict | "MissionComplication") -> "MissionComplication":
        if isinstance(data, cls):
            return data
        return cls(
            key=data.get("key", "unknown"),
            name=data.get("name", "Unknown Complication"),
            trigger_text=data.get("trigger_text", "The mission twists out of shape."),
            risk_threshold=data.get("risk_threshold", 1),
            tags=[SavageTag.from_dict(tag) for tag in data.get("tags", [])],
            consequence=Consequence.from_dict(data.get("consequence", {})),
        )


@dataclass
class MissionTemplate:
    """A vertical-slice mission seed that drives tactical battle setup and fallout."""

    id: str
    title: str
    objective_text: str
    target_faction: str
    district: str
    district_pressure: dict
    starting_enemy_count: int
    objective_type: str = "eliminate"
    possible_complications: list[MissionComplication] = field(default_factory=list)
    success_consequences: list[Consequence] = field(default_factory=list)
    failure_consequences: list[Consequence] = field(default_factory=list)
    risk_level: int = 1
    fund_reward: int = 0
    tags: list[SavageTag] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "objective_text": self.objective_text,
            "target_faction": self.target_faction,
            "district": self.district,
            "district_pressure": dict(self.district_pressure),
            "starting_enemy_count": self.starting_enemy_count,
            "objective_type": self.objective_type,
            "possible_complications": [
                complication.to_dict() for complication in self.possible_complications
            ],
            "success_consequences": [
                consequence.to_dict() for consequence in self.success_consequences
            ],
            "failure_consequences": [
                consequence.to_dict() for consequence in self.failure_consequences
            ],
            "risk_level": self.risk_level,
            "fund_reward": self.fund_reward,
            "tags": [tag.to_dict() for tag in self.tags],
        }

    @classmethod
    def from_dict(cls, data: dict | "MissionTemplate") -> "MissionTemplate":
        if isinstance(data, cls):
            return data
        return cls(
            id=data.get("id", "unknown"),
            title=data.get("title", "Unknown Mission"),
            objective_text=data.get("objective_text", "Win the tactical engagement."),
            target_faction=data.get("target_faction", "Unknown Faction"),
            district=data.get("district", "Chrome Warrens"),
            district_pressure=dict(data.get("district_pressure", {})),
            starting_enemy_count=data.get("starting_enemy_count", 1),
            objective_type=data.get("objective_type")
            if data.get("objective_type") in {"extract", "sabotage", "data_theft", "eliminate"}
            else "eliminate",
            possible_complications=[
                MissionComplication.from_dict(complication)
                for complication in data.get("possible_complications", [])
            ],
            success_consequences=[
                Consequence.from_dict(consequence)
                for consequence in data.get("success_consequences", [])
            ],
            failure_consequences=[
                Consequence.from_dict(consequence)
                for consequence in data.get("failure_consequences", [])
            ],
            risk_level=data.get("risk_level", 1),
            fund_reward=int(data.get("fund_reward", 0)),
            tags=[SavageTag.from_dict(tag) for tag in data.get("tags", [])],
        )


def create_core_complications(district_name: str) -> list[MissionComplication]:
    """Return complications shared by the first mission layer."""
    return [
        MissionComplication(
            key="media_leak",
            name="Media Leak",
            trigger_text="A pirate news relay leaks the team's route before extraction.",
            risk_threshold=2,
            tags=[tag_from_library("media_leak")],
            consequence=Consequence(
                affected_district=district_name,
                severity=2,
                narrative_text="Media leak: pirate feeds turn the firefight into a public scandal.",
                mechanical_effects={"media_heat": 8, "stability": -2},
                tags=[tag_from_library("media_leak")],
            ),
        ),
        MissionComplication(
            key="civilian_panic",
            name="Civilian Panic",
            trigger_text="Crowds panic as muzzle flashes bounce across the stacked market decks.",
            risk_threshold=3,
            tags=[tag_from_library("civilian_panic")],
            consequence=Consequence(
                affected_district=district_name,
                severity=2,
                narrative_text="Civilian panic: frightened residents jam streets and blame Aegis patrols.",
                mechanical_effects={"unrest": 7, "stability": -4},
                tags=[tag_from_library("civilian_panic")],
            ),
        ),
        MissionComplication(
            key="faction_retaliation",
            name="Faction Retaliation",
            trigger_text="The target faction marks the squad and calls in retaliation crews.",
            risk_threshold=4,
            tags=[tag_from_library("faction_retaliation")],
            consequence=Consequence(
                affected_district=district_name,
                severity=3,
                narrative_text="Faction retaliation: the target faction answers with reprisals and fresh threats.",
                mechanical_effects={"faction_hostility": 9, "unrest": 4},
                tags=[tag_from_library("faction_retaliation")],
            ),
        ),
    ]


def create_mission_templates(
    district_name: str = "Chrome Warrens",
) -> list[MissionTemplate]:
    """Build the three playable vertical-slice missions before entering battle."""
    complications = create_core_complications(district_name)
    return [
        MissionTemplate(
            id="extraction",
            title="Extraction: Neon Witness",
            objective_text="Extract a clinic witness from the east-rail blackout before gangs sell them to Aegis auditors.",
            target_faction="Chrome Jackals",
            district=district_name,
            district_pressure={"unrest": 3, "media_heat": 2},
            starting_enemy_count=2,
            objective_type="extract",
            possible_complications=[complications[0], complications[1]],
            success_consequences=[
                Consequence(
                    affected_district=district_name,
                    affected_faction="Warrens Free Clinic",
                    severity=1,
                    narrative_text="Extraction success: the witness reaches the clinic and locals share safehouse routes.",
                    mechanical_effects={"stability": 5, "unrest": -4, "faction_hostility": -3},
                    tags=[tag_from_library("civilian_panic")],
                )
            ],
            failure_consequences=[
                Consequence(
                    affected_district=district_name,
                    affected_faction="Chrome Jackals",
                    severity=3,
                    narrative_text="Extraction failure: the witness disappears and Jackal recruiters own the rumor mill.",
                    mechanical_effects={"unrest": 8, "media_heat": 4, "faction_hostility": 6},
                    tags=[tag_from_library("gang_pressure")],
                )
            ],
            risk_level=2,
            fund_reward=40,
            tags=[tag_from_library("neon_blackout")],
        ),
        MissionTemplate(
            id="sabotage",
            title="Sabotage: Jackal Relay Burn",
            objective_text="Destroy the Chrome Jackals' relay van before it coordinates raids on the defense zones.",
            target_faction="Chrome Jackals",
            district=district_name,
            district_pressure={"unrest": 5, "media_heat": 1},
            starting_enemy_count=3,
            objective_type="sabotage",
            possible_complications=[complications[1], complications[2]],
            success_consequences=[
                Consequence(
                    affected_district=district_name,
                    affected_faction="Chrome Jackals",
                    severity=2,
                    narrative_text="Sabotage success: the Jackal relay goes dark and their raid clock slips.",
                    mechanical_effects={"unrest": -6, "stability": 3, "faction_influence": -5},
                    tags=[tag_from_library("gang_pressure")],
                )
            ],
            failure_consequences=[
                Consequence(
                    affected_district=district_name,
                    affected_faction="Chrome Jackals",
                    severity=3,
                    narrative_text="Sabotage failure: the relay survives and Jackal retaliation teams flood the alleys.",
                    mechanical_effects={"unrest": 9, "faction_hostility": 8, "stability": -5},
                    tags=[tag_from_library("faction_retaliation")],
                )
            ],
            risk_level=4,
            fund_reward=70,
            tags=[tag_from_library("gang_pressure")],
        ),
        MissionTemplate(
            id="data_theft",
            title="Data Theft: Ghost Order Cache",
            objective_text="Steal the spoofed Aegis order cache without letting corporate counterintel trace the breach.",
            target_faction="Aegis Dynamics",
            district=district_name,
            district_pressure={"media_heat": 4, "stability": -1},
            starting_enemy_count=2,
            objective_type="data_theft",
            possible_complications=[complications[0], complications[2]],
            success_consequences=[
                Consequence(
                    affected_district=district_name,
                    affected_faction="Aegis Dynamics",
                    severity=2,
                    narrative_text="Data theft success: the ghost order cache exposes a false-flag command chain.",
                    mechanical_effects={"media_heat": -3, "stability": 4, "faction_influence": -4},
                    tags=[tag_from_library("ghost_signal")],
                )
            ],
            failure_consequences=[
                Consequence(
                    affected_district=district_name,
                    affected_faction="Aegis Dynamics",
                    severity=3,
                    narrative_text="Data theft failure: Aegis counterintel frames the squad as rogue assets.",
                    mechanical_effects={"media_heat": 9, "faction_hostility": 7, "stability": -4},
                    tags=[tag_from_library("media_leak")],
                )
            ],
            risk_level=3,
            fund_reward=60,
            tags=[tag_from_library("ghost_signal"), tag_from_library("media_swarm")],
        ),
    ]
