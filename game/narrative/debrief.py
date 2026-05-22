"""Pure mission debrief narrative mapping for post-mission reporting."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..character import Character
from ..mission_templates import MissionComplication, MissionTemplate


@dataclass(frozen=True)
class DebriefLine:
    """Single emotional line in a mission debrief report."""

    agent_name: str
    emotional_tone: str
    consequence_type: str
    text: str

    def to_dict(self) -> dict[str, str]:
        return {
            "agent_name": self.agent_name,
            "emotional_tone": self.emotional_tone,
            "consequence_type": self.consequence_type,
            "text": self.text,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DebriefLine":
        return cls(
            agent_name=str(data.get("agent_name", "Unknown")),
            emotional_tone=str(data.get("emotional_tone", "steady")),
            consequence_type=str(data.get("consequence_type", "mission_outcome")),
            text=str(data.get("text", "")),
        )


@dataclass(frozen=True)
class DebriefReport:
    """Collection of agent-centric debrief lines."""

    mission_title: str
    mission_outcome: str
    lines: list[DebriefLine] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "mission_title": self.mission_title,
            "mission_outcome": self.mission_outcome,
            "lines": [line.to_dict() for line in self.lines],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DebriefReport":
        return cls(
            mission_title=str(data.get("mission_title", "Unknown Operation")),
            mission_outcome=str(data.get("mission_outcome", "unknown")),
            lines=[DebriefLine.from_dict(line) for line in data.get("lines", [])],
        )


def _stress_tone(stress: int) -> str:
    if stress >= 85:
        return "fractured"
    if stress >= 65:
        return "frayed"
    if stress >= 35:
        return "tense"
    return "steady"


def _injury_type(character: Character) -> str:
    if character.stats.hp <= 0:
        return "downed"
    if character.injuries:
        return "injured"
    if character.recovery_turns > 0:
        return "recovering"
    return "operational"


def _mission_outcome_label(victory: bool) -> str:
    return "victory" if victory else "failure"


def _line_text(
    character: Character,
    mission: MissionTemplate | None,
    victory: bool,
    complication: MissionComplication | None,
) -> tuple[str, str, str]:
    tone = _stress_tone(character.stress)
    consequence_type = _injury_type(character)
    mission_title = mission.title if mission else "Unknown Operation"

    templates: dict[str, dict[str, str]] = {
        "victory": {
            "operational": "{name} garde le cap après {mission}.",
            "recovering": "{name} tient la ligne malgré la récupération post-{mission}.",
            "injured": "{name} revient blessé·e de {mission}, mais reste engagé·e.",
            "downed": "{name} a payé un lourd prix pendant {mission}.",
        },
        "failure": {
            "operational": "{name} encaisse l'échec de {mission} avec discipline.",
            "recovering": "{name} est en récupération après la chute de {mission}.",
            "injured": "{name} sort meurtri·e de {mission} et garde la mission en tête.",
            "downed": "{name} s'effondre sous le choc de {mission}.",
        },
    }
    outcome = _mission_outcome_label(victory)
    base = templates[outcome][consequence_type].format(name=character.name, mission=mission_title)
    if complication:
        base += f" Complication: {complication.name.lower()}."
    return tone, consequence_type, base


def build_mission_debrief_report(
    characters: list[Character],
    mission: MissionTemplate | None,
    victory: bool,
    complication: MissionComplication | None = None,
) -> DebriefReport:
    """Build a deterministic debrief report from post-mission agent states."""
    mission_title = mission.title if mission else "Unknown Operation"
    lines = []
    for character in characters:
        tone, consequence_type, text = _line_text(
            character, mission, victory, complication
        )
        lines.append(
            DebriefLine(
                agent_name=character.name,
                emotional_tone=tone,
                consequence_type=consequence_type,
                text=text,
            )
        )
    return DebriefReport(
        mission_title=mission_title,
        mission_outcome=_mission_outcome_label(victory),
        lines=lines,
    )
