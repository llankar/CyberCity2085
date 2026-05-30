"""CampaignState and WorldState — serialisable campaign progress tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorldState:
    """Macro world conditions that change as the campaign advances."""

    warsaw_status: str = "open"
    # open | coup_underway | three_sevens_controlled
    hungry_tide_progress: int = 0
    # 0–100; at 100 New York is under siege
    new_york_status: str = "normal"
    # normal | alert | siege
    pharmacorp_secret: str = "hidden"
    # hidden | rumored | exposed
    ai_factions_status: str = "unknown"
    # unknown | suspected | confirmed
    perfs_status: str = "unknown"
    # unknown | sighted | understood
    new_delhi_status: str = "forbidden"
    # forbidden | infiltrated | revealed

    def to_dict(self) -> dict[str, Any]:
        return {
            "warsaw_status": self.warsaw_status,
            "hungry_tide_progress": self.hungry_tide_progress,
            "new_york_status": self.new_york_status,
            "pharmacorp_secret": self.pharmacorp_secret,
            "ai_factions_status": self.ai_factions_status,
            "perfs_status": self.perfs_status,
            "new_delhi_status": self.new_delhi_status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WorldState":
        ws = cls()
        ws.warsaw_status = str(d.get("warsaw_status", ws.warsaw_status))
        ws.hungry_tide_progress = int(d.get("hungry_tide_progress", 0))
        ws.new_york_status = str(d.get("new_york_status", ws.new_york_status))
        ws.pharmacorp_secret = str(d.get("pharmacorp_secret", ws.pharmacorp_secret))
        ws.ai_factions_status = str(d.get("ai_factions_status", ws.ai_factions_status))
        ws.perfs_status = str(d.get("perfs_status", ws.perfs_status))
        ws.new_delhi_status = str(d.get("new_delhi_status", ws.new_delhi_status))
        return ws


# Missions required per act to trigger act-advance
_ACT_MISSIONS_REQUIRED = {1: 3, 2: 4, 3: 5, 4: 5, 5: 3}


@dataclass
class CampaignState:
    """All campaign-level progress — act, intel, world state, faction reveals."""

    current_act: int = 1
    act_progress: int = 0
    act_triggers_seen: list[str] = field(default_factory=list)
    discovered_intel: list[str] = field(default_factory=list)
    world: WorldState = field(default_factory=WorldState)
    # Hidden factions not yet in game_state.factions (keyed by name)
    hidden_faction_hostility: dict[str, int] = field(default_factory=lambda: {
        "Three Sevens Corp": 75,
        "Pharmacorp": 20,
        "Preservationist AIs": 0,
        "Exterminator AIs": 80,
    })

    @property
    def missions_required(self) -> int:
        return _ACT_MISSIONS_REQUIRED.get(self.current_act, 5)

    @property
    def act_complete(self) -> bool:
        return self.act_progress >= self.missions_required

    def record_trigger(self, trigger_id: str) -> bool:
        """Mark a trigger as seen; return True if it was new."""
        if trigger_id in self.act_triggers_seen:
            return False
        self.act_triggers_seen.append(trigger_id)
        return True

    def discover_intel(self, fragment_id: str) -> bool:
        """Record a newly discovered intel fragment; return True if new."""
        if fragment_id in self.discovered_intel:
            return False
        self.discovered_intel.append(fragment_id)
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_act": self.current_act,
            "act_progress": self.act_progress,
            "act_triggers_seen": list(self.act_triggers_seen),
            "discovered_intel": list(self.discovered_intel),
            "world": self.world.to_dict(),
            "hidden_faction_hostility": dict(self.hidden_faction_hostility),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CampaignState":
        cs = cls()
        cs.current_act = int(d.get("current_act", 1))
        cs.act_progress = int(d.get("act_progress", 0))
        cs.act_triggers_seen = list(d.get("act_triggers_seen", []))
        cs.discovered_intel = list(d.get("discovered_intel", []))
        cs.world = WorldState.from_dict(d.get("world", {}))
        cs.hidden_faction_hostility = dict(d.get("hidden_faction_hostility", cs.hidden_faction_hostility))
        return cs
