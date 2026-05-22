"""Utilities for lightweight mentor-link tracking between agents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MentorLink:
    """Compact relationship link persisted on each agent."""

    agent_id: str
    bond_level: int
    strategic_day: int

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "bond_level": self.bond_level,
            "strategic_day": self.strategic_day,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MentorLink":
        return cls(
            agent_id=str(data.get("agent_id", "")),
            bond_level=max(0, int(data.get("bond_level", 0))),
            strategic_day=max(0, int(data.get("strategic_day", 0))),
        )


def upsert_mentor_link(
    links: dict[str, dict],
    *,
    agent_id: str,
    strategic_day: int,
    bond_delta: int = 1,
) -> dict[str, dict]:
    """Create or update one relationship link while keeping payload minimal."""
    if not agent_id:
        return links

    previous = MentorLink.from_dict(links.get(agent_id, {}))
    next_bond = previous.bond_level + max(0, int(bond_delta))
    links[agent_id] = MentorLink(
        agent_id=agent_id,
        bond_level=next_bond,
        strategic_day=max(previous.strategic_day, int(strategic_day)),
    ).to_dict()
    return links


def serialize_links(links: dict[str, dict]) -> dict[str, dict]:
    """Normalize links into a persistable dictionary of primitive values."""
    normalized: dict[str, dict] = {}
    for key, payload in links.items():
        link = MentorLink.from_dict(payload)
        if not link.agent_id:
            continue
        normalized[key] = link.to_dict()
    return normalized
