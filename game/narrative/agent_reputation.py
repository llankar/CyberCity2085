"""Small post-mission nickname and reputation award helpers."""

from __future__ import annotations

from dataclasses import dataclass

from ..character import Character
from ..mission_templates import MissionComplication, MissionTemplate


@dataclass(frozen=True)
class AgentReputationAward:
    agent_name: str
    tag: str
    nickname: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "agent_name": self.agent_name,
            "tag": self.tag,
            "nickname": self.nickname,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentReputationAward":
        return cls(
            agent_name=str(data.get("agent_name", "Unknown")),
            tag=str(data.get("tag", "")),
            nickname=str(data.get("nickname", "")),
            reason=str(data.get("reason", "")),
        )


def _objective_type(mission: MissionTemplate | None, performance: dict) -> str:
    return str(
        performance.get("objective_type")
        or getattr(mission, "objective_type", "")
        or ""
    ).lower()


def _award_for_agent(
    character: Character,
    performance: dict,
    victory: bool,
    mission: MissionTemplate | None,
    complication: MissionComplication | None,
) -> AgentReputationAward | None:
    kills = int(performance.get("kills", 0) or 0)
    damage_taken = int(performance.get("damage_taken", 0) or 0)
    saved_civilian = bool(performance.get("saved_civilian", False))
    objective_type = _objective_type(mission, performance)
    reason_mission = getattr(mission, "title", "the mission") if mission else "the mission"

    if kills >= 3:
        return AgentReputationAward(
            character.name,
            "elite_breaker",
            "" if character.nickname else "Breaker",
            f"eliminated {kills} hostiles during {reason_mission}",
        )
    if damage_taken >= 30 and not bool(performance.get("kia", False)):
        return AgentReputationAward(
            character.name,
            "critical_survivor",
            "" if character.nickname else "Last Light",
            f"survived {damage_taken} damage and extracted",
        )
    if saved_civilian or objective_type in {"civilian_rescue", "rescue"}:
        return AgentReputationAward(
            character.name,
            "civilian_shield",
            "" if character.nickname else "Shield",
            f"protected civilians or cured Starvers during {reason_mission}",
        )
    if not victory and (character.stress >= 75 or complication is not None):
        return AgentReputationAward(
            character.name,
            "trauma_witness",
            "" if character.nickname else "Witness",
            f"carried the memory of a failed objective during {reason_mission}",
        )
    return None


def build_agent_reputation_awards(
    characters: list[Character],
    performance_by_agent: dict[str, dict] | None,
    victory: bool,
    mission: MissionTemplate | None = None,
    complication: MissionComplication | None = None,
) -> list[AgentReputationAward]:
    """Return deterministic standout awards without mutating agents."""
    awards: list[AgentReputationAward] = []
    performance_by_agent = performance_by_agent or {}
    for character in characters:
        performance = performance_by_agent.get(character.name, {})
        award = _award_for_agent(character, performance, victory, mission, complication)
        if award is None:
            continue
        if award.tag in character.reputation:
            continue
        awards.append(award)
    return awards


def apply_agent_reputation_awards(
    characters: list[Character],
    awards: list[AgentReputationAward],
) -> list[str]:
    """Apply awards once and return event-log ready summary lines."""
    by_name = {character.name: character for character in characters}
    lines: list[str] = []
    for award in awards:
        character = by_name.get(award.agent_name)
        if character is None:
            continue
        if award.tag not in character.reputation:
            character.reputation.append(award.tag)
        if award.nickname and not character.nickname:
            character.nickname = award.nickname
        history_line = f"Earned {award.tag}: {award.reason}."
        if history_line not in character.history:
            character.history.append(history_line)
        label = f"'{character.nickname}' " if character.nickname else ""
        lines.append(
            f"Reputation: {character.name} {label}earned {award.tag} ({award.reason})."
        )
    return lines
