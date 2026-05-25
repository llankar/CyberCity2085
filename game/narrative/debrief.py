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
    decision_key: str = ""
    risk_taken: str = ""
    heroic_action: str = ""
    rpg_links: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "mission_title": self.mission_title,
            "mission_outcome": self.mission_outcome,
            "lines": [line.to_dict() for line in self.lines],
            "decision_key": self.decision_key,
            "risk_taken": self.risk_taken,
            "heroic_action": self.heroic_action,
            "rpg_links": list(self.rpg_links),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DebriefReport":
        return cls(
            mission_title=str(data.get("mission_title", "Unknown Operation")),
            mission_outcome=str(data.get("mission_outcome", "unknown")),
            lines=[DebriefLine.from_dict(line) for line in data.get("lines", [])],
            decision_key=str(data.get("decision_key", "")),
            risk_taken=str(data.get("risk_taken", "")),
            heroic_action=str(data.get("heroic_action", "")),
            rpg_links=[str(line) for line in data.get("rpg_links", [])],
        )


def _extract_decision_key(lines: list[DebriefLine], mission: MissionTemplate | None) -> str:
    mission_title = mission.title if mission else "Unknown Operation"
    if any(line.consequence_type == "downed" for line in lines):
        return f"Maintenir l'objectif de {mission_title} malgré un agent au sol."
    if any(line.consequence_type == "injured" for line in lines):
        return f"Continuer l'opération {mission_title} sous pression médicale."
    return f"Tenir la formation jusqu'à extraction complète sur {mission_title}."


def _extract_risk_taken(
    lines: list[DebriefLine],
    complication: MissionComplication | None,
) -> str:
    if complication is not None:
        return f"Risque narratif majeur accepté: {complication.name.lower()}."
    if any(line.emotional_tone in {"fractured", "frayed"} for line in lines):
        return "Risque humain: engagement avec escouade sous stress élevé."
    return "Risque mesuré: progression sans complication critique détectée."


def _extract_heroic_action(lines: list[DebriefLine]) -> str:
    heroic_line = next(
        (line for line in lines if line.consequence_type in {"injured", "recovering", "downed"}),
        lines[0] if lines else None,
    )
    if heroic_line is None:
        return "L'escouade a tenu sans perte majeure."
    return f"{heroic_line.agent_name} a tenu la ligne dans les pires conditions."


def _build_rpg_links(characters: list[Character]) -> list[str]:
    if not characters:
        return ["Aucun agent survivant: revue stratégique requise."]

    highest_stress = max(characters, key=lambda c: c.stress)
    strongest_bond = max(
        characters,
        key=lambda c: max(c.relationships.values(), default=0),
    )
    top_level = max(characters, key=lambda c: c.stats.level)
    return [
        f"Stress: {highest_stress.name} à {highest_stress.stress}/100, priorité récupération.",
        (
            "Relations: "
            f"{strongest_bond.name} consolide le lien d'escouade "
            f"(max {max(strongest_bond.relationships.values(), default=0)})."
        ),
        f"Progression: {top_level.name} niveau {top_level.stats.level}, capitaliser sur son rôle.",
    ]


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
        decision_key=_extract_decision_key(lines, mission),
        risk_taken=_extract_risk_taken(lines, complication),
        heroic_action=_extract_heroic_action(lines),
        rpg_links=_build_rpg_links(characters),
    )
