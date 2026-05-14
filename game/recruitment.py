"""Recruitment helpers for creating player agents."""

from .character import Character
from .stats import PlayerStats

ROLE_STAT_BONUSES = {
    "samurai": "str",
    "sniper": "agi",
    "psi": "psi",
}


def create_character(name: str, role: str) -> Character:
    """Create a new player character with the stat bonus for their role."""
    stats = PlayerStats()
    bonus_stat = ROLE_STAT_BONUSES.get(role)
    if bonus_stat:
        setattr(stats, bonus_stat, getattr(stats, bonus_stat) + 5)
    stats.recalculate_hp()
    return Character(name=name, role=role, stats=stats)


def recruit_agent(roster: list[Character], role: str) -> Character:
    """Create the next numbered agent and append them to the supplied roster."""
    agent = create_character(f"Agent {len(roster) + 1}", role)
    roster.append(agent)
    return agent
