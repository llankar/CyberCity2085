"""Deterministic campaign finale and agent epilogues.

The finale deliberately evaluates state the player has already shaped instead
of introducing a last-minute choice disconnected from the campaign.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game.gamestate import GameState


@dataclass
class CampaignEnding:
    """Serializable result of a completed five-act campaign."""

    outcome_id: str
    title: str
    summary: str
    world_lines: list[str] = field(default_factory=list)
    agent_epilogues: list[str] = field(default_factory=list)
    resolved_day: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome_id": self.outcome_id,
            "title": self.title,
            "summary": self.summary,
            "world_lines": list(self.world_lines),
            "agent_epilogues": list(self.agent_epilogues),
            "resolved_day": self.resolved_day,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "CampaignEnding | None":
        if not data or not data.get("outcome_id"):
            return None
        return cls(
            outcome_id=str(data["outcome_id"]),
            title=str(data.get("title", "The City Remembers")),
            summary=str(data.get("summary", "CyberCity survives, changed.")),
            world_lines=[str(line) for line in data.get("world_lines", [])],
            agent_epilogues=[str(line) for line in data.get("agent_epilogues", [])],
            resolved_day=int(data.get("resolved_day", 0)),
        )


def _agent_epilogue(character: object) -> str:
    name = str(getattr(character, "name", "Unknown agent"))
    nickname = str(getattr(character, "nickname", "")).strip()
    display_name = f'{name} "{nickname}"' if nickname else name
    stats = getattr(character, "stats", None)
    alive = bool(stats is None or getattr(stats, "hp", 1) > 0)
    reputation = list(getattr(character, "reputation", []))
    scars = list(getattr(character, "temporary_scars", []))
    relationships = dict(getattr(character, "relationships", {}))

    if not alive:
        return f"{display_name} lives on in the squad's roll of honour."
    if relationships:
        closest = max(relationships, key=relationships.get)
        return f"{display_name} stays in CyberCity, watching {closest}'s back."
    if reputation:
        return f"{display_name} leaves the war known for {reputation[-1]}."
    if scars:
        return f"{display_name} survives with scars that make the truth impossible to forget."
    return f"{display_name} survives, carrying the squad's story into the new city."


def evaluate_campaign_ending(game_state: "GameState") -> CampaignEnding:
    """Resolve the finale from accumulated world, intel, faction, and agent state."""

    campaign = game_state.campaign
    world = campaign.world
    intel_count = len(campaign.discovered_intel)
    living_agents = sum(
        1
        for agent in game_state.characters
        if getattr(getattr(agent, "stats", None), "hp", 1) > 0
    )
    hostile_pressure = sum(
        max(0, int(getattr(faction, "hostility_to_player", 0)))
        for faction in game_state.factions
    )

    hope = intel_count + living_agents * 2
    if world.pharmacorp_secret == "exposed":
        hope += 4
    if world.ai_factions_status == "confirmed":
        hope += 3
    if world.perfs_status == "understood":
        hope += 2
    if world.new_delhi_status == "revealed":
        hope += 3

    crisis = hostile_pressure // 25 + world.hungry_tide_progress // 20
    if world.new_york_status == "siege":
        crisis += 4
    if world.warsaw_status == "three_sevens_controlled":
        crisis += 3

    if living_agents == 0:
        outcome_id = "legacy_in_ashes"
        title = "THE LAST TRANSMISSION"
        summary = "The squad does not return, but its evidence outlives the people who carried it."
    elif hope >= crisis + 8:
        outcome_id = "human_coalition"
        title = "DAWN WITHOUT MASTERS"
        summary = "Truth breaks the emergency regime, and a fragile human coalition claims the future."
    elif hope >= crisis:
        outcome_id = "guarded_survival"
        title = "THE CITY ENDURES"
        summary = "CyberCity survives the siege with its freedom wounded, contested, and still alive."
    else:
        outcome_id = "corporate_hegemony"
        title = "ORDER AT ANY PRICE"
        summary = "The crisis ends beneath corporate authority; survival is secured, but freedom is deferred."

    world_lines = [
        f"New York: {world.new_york_status.replace('_', ' ').title()}.",
        f"Warsaw: {world.warsaw_status.replace('_', ' ').title()}.",
        f"Hungry Tide: {world.hungry_tide_progress}%.",
        f"Intel exposed: {intel_count} fragments.",
    ]
    if world.pharmacorp_secret == "exposed":
        world_lines.append("The P-77 cure can no longer be buried.")
    if world.ai_factions_status == "confirmed":
        world_lines.append("Humanity enters the new era knowing the hidden AIs exist.")

    return CampaignEnding(
        outcome_id=outcome_id,
        title=title,
        summary=summary,
        world_lines=world_lines,
        agent_epilogues=[_agent_epilogue(agent) for agent in game_state.characters],
        resolved_day=game_state.calendar.current_day,
    )
