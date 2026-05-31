"""Compact narrative-only faction rewards granted after successful missions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FactionNarrativeReward:
    """Small narrative beat recorded in campaign memory."""

    kind: str
    text: str

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "text": self.text}


_FACTION_REWARDS: dict[str, list[FactionNarrativeReward]] = {
    "Warrens Free Clinic": [
        FactionNarrativeReward("local_trust", "The clinic spreads a quiet word of trust.")
    ],
    "Chrome Jackals": [
        FactionNarrativeReward("street_rumor", "A street rumor says you broke a trafficking lane.")
    ],
    "Aegis Dynamics": [
        FactionNarrativeReward("contact", "A corporate contact passes along a one-time emergency channel.")
    ],
}

_NEUTRAL_FALLBACK = FactionNarrativeReward(
    "neutral_echo",
    "The district keeps a cautious echo of the operation, with no direct new support.",
)


def rewards_for_faction(faction_name: str) -> list[FactionNarrativeReward]:
    """Return small narrative rewards for a faction with a neutral fallback."""
    rewards = _FACTION_REWARDS.get(faction_name)
    if rewards:
        return list(rewards)
    return [_NEUTRAL_FALLBACK]


def build_reward_log_entries(faction_name: str, mission_title: str) -> list[str]:
    """Build readable campaign-log lines from faction narrative rewards."""
    entries = []
    for reward in rewards_for_faction(faction_name):
        entries.append(
            f"Narrative reward ({reward.kind}) after '{mission_title}': {reward.text}"
        )
    return entries
