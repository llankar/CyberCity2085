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
        FactionNarrativeReward("local_trust", "La clinique diffuse un mot de confiance discret.")
    ],
    "Chrome Jackals": [
        FactionNarrativeReward("street_rumor", "Une rumeur de rue affirme que vous avez brisé une ligne de trafic.")
    ],
    "Aegis Dynamics": [
        FactionNarrativeReward("contact", "Un contact d'entreprise transmet un canal de secours à usage unique.")
    ],
}

_NEUTRAL_FALLBACK = FactionNarrativeReward(
    "neutral_echo",
    "Le district retient un écho prudent de l'opération, sans nouvel appui direct.",
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
            f"Récompense narrative ({reward.kind}) après '{mission_title}': {reward.text}"
        )
    return entries
