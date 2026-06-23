from dataclasses import dataclass, field, asdict


from .agents.sheet_schema import default_agent_sheet, normalize_agent_sheet
from .management.equipment import AgentLoadout
from .stats import PlayerStats
from .relationships.mentor_history import serialize_links


@dataclass
class Character:
    """Player character with associated statistics and agent dossier details."""

    name: str
    role: str = "samurai"
    stats: PlayerStats = field(default_factory=PlayerStats)
    pending_points: int = 0
    talent_points: int = 0
    specializations: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    addictions: list[str] = field(default_factory=list)
    fears: list[str] = field(default_factory=list)
    ambition: str = ""
    loyalty: int = 0
    stress: int = 0
    trauma: list[str] = field(default_factory=list)
    injuries: list[str] = field(default_factory=list)
    nickname: str = ""
    reputation: list[str] = field(default_factory=list)
    relationships: dict[str, int] = field(default_factory=dict)
    mentor_links: dict[str, dict] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)
    savage_tags: list[str] = field(default_factory=list)
    temporary_scars: list[dict] = field(default_factory=list)
    recovery_turns: int = 0
    loadout: AgentLoadout = field(default_factory=AgentLoadout)
    personality_primary_trait: str = ""
    personality_secondary_trait: str = ""
    sex: str = ""
    attributes: dict[str, int] = field(default_factory=lambda: default_agent_sheet().attributes)
    skills: dict[str, int] = field(default_factory=lambda: default_agent_sheet().skills)
    derived_stats: dict[str, int] = field(default_factory=lambda: default_agent_sheet().derived_stats)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "stats": asdict(self.stats),
            "pending_points": self.pending_points,
            "talent_points": self.talent_points,
            "specializations": list(self.specializations),
            "traits": list(self.traits),
            "addictions": list(self.addictions),
            "fears": list(self.fears),
            "ambition": self.ambition,
            "loyalty": self.loyalty,
            "stress": self.stress,
            "trauma": list(self.trauma),
            "injuries": list(self.injuries),
            "nickname": self.nickname,
            "reputation": list(self.reputation),
            "relationships": dict(self.relationships),
            "mentor_links": serialize_links(self.mentor_links),
            "history": list(self.history),
            "savage_tags": list(self.savage_tags),
            "temporary_scars": [dict(scar) for scar in self.temporary_scars],
            "recovery_turns": self.recovery_turns,
            "loadout": self.loadout.to_dict(),
            "personality_primary_trait": self.personality_primary_trait,
            "personality_secondary_trait": self.personality_secondary_trait,
            "sex": self.sex,
            "attributes": dict(self.attributes),
            "skills": dict(self.skills),
            "derived_stats": dict(self.derived_stats),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        stats_data = data.get("stats", {})
        stats = PlayerStats(**stats_data)
        sheet = normalize_agent_sheet(
            stats=stats,
            attributes=data.get("attributes"),
            skills=data.get("skills"),
            derived_stats=data.get("derived_stats"),
        )
        return cls(
            name=data.get("name", "Unnamed"),
            role=data.get("role", "samurai"),
            stats=stats,
            pending_points=data.get("pending_points", 0),
            talent_points=data.get("talent_points", 0),
            specializations=list(data.get("specializations", [])),
            traits=list(data.get("traits", [])),
            addictions=list(data.get("addictions", [])),
            fears=list(data.get("fears", [])),
            ambition=data.get("ambition", ""),
            loyalty=data.get("loyalty", 0),
            stress=data.get("stress", 0),
            trauma=list(data.get("trauma", [])),
            injuries=list(data.get("injuries", [])),
            nickname=str(data.get("nickname", "")),
            reputation=list(data.get("reputation", [])),
            relationships=dict(data.get("relationships", {})),
            mentor_links=serialize_links(dict(data.get("mentor_links", {}))),
            history=list(data.get("history", [])),
            savage_tags=list(data.get("savage_tags", [])),
            temporary_scars=[dict(scar) for scar in data.get("temporary_scars", [])],
            recovery_turns=data.get("recovery_turns", 0),
            loadout=AgentLoadout.from_dict(data.get("loadout")),
            personality_primary_trait=str(data.get("personality_primary_trait", "")),
            personality_secondary_trait=str(data.get("personality_secondary_trait", "")),
            sex=str(data.get("sex", "")),
            attributes=sheet.attributes,
            skills=sheet.skills,
            derived_stats=sheet.derived_stats,
        )

    def gain_xp(self, amount: int) -> None:
        """Add experience and handle level ups."""
        self.stats.xp += amount
        while self.stats.xp >= 100 * (self.stats.level ** 2):
            self.stats.xp -= 100 * (self.stats.level ** 2)
            self.stats.level += 1
            # Recompute max HP based on CON and level
            self.stats.recalculate_hp()
            self.stats.hp = min(self.stats.hp + 10, self.stats.max_hp)
            self.pending_points += 5
            self.talent_points += 1


def is_deployable(character: Character) -> bool:
    """Return whether an agent can currently be assigned to a mission."""
    return character.stats.hp > 0 and character.recovery_turns <= 0
