"""Recruitment helpers for creating player agents."""

from .character import Character
from .stats import PlayerStats
from .relationships.mentor_history import upsert_mentor_link

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
    seed_roster_mentor_links(roster, agent)
    roster.append(agent)
    return agent


def seed_roster_mentor_links(roster: list[Character], new_agent: Character, strategic_day: int = 0) -> None:
    """Initialize lightweight social ties between a recruit and the current roster."""
    for teammate in roster:
        if teammate.name == new_agent.name:
            continue
        upsert_mentor_link(new_agent.mentor_links, agent_id=teammate.name, strategic_day=strategic_day, bond_delta=1)
        upsert_mentor_link(teammate.mentor_links, agent_id=new_agent.name, strategic_day=strategic_day, bond_delta=1)
