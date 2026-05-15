from dataclasses import dataclass, field, asdict


from .management.equipment import AgentLoadout
from .stats import PlayerStats


@dataclass
class Character:
    """Player character with associated statistics and agent dossier details."""

    name: str
    role: str = "samurai"
    stats: PlayerStats = field(default_factory=PlayerStats)
    pending_points: int = 0
    traits: list[str] = field(default_factory=list)
    addictions: list[str] = field(default_factory=list)
    fears: list[str] = field(default_factory=list)
    ambition: str = ""
    loyalty: int = 0
    stress: int = 0
    trauma: list[str] = field(default_factory=list)
    injuries: list[str] = field(default_factory=list)
    reputation: list[str] = field(default_factory=list)
    relationships: dict[str, int] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)
    savage_tags: list[str] = field(default_factory=list)
    recovery_turns: int = 0
    loadout: AgentLoadout = field(default_factory=AgentLoadout)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "stats": asdict(self.stats),
            "pending_points": self.pending_points,
            "traits": list(self.traits),
            "addictions": list(self.addictions),
            "fears": list(self.fears),
            "ambition": self.ambition,
            "loyalty": self.loyalty,
            "stress": self.stress,
            "trauma": list(self.trauma),
            "injuries": list(self.injuries),
            "reputation": list(self.reputation),
            "relationships": dict(self.relationships),
            "history": list(self.history),
            "savage_tags": list(self.savage_tags),
            "recovery_turns": self.recovery_turns,
            "loadout": self.loadout.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        stats_data = data.get("stats", {})
        stats = PlayerStats(**stats_data)
        return cls(
            name=data.get("name", "Unnamed"),
            role=data.get("role", "samurai"),
            stats=stats,
            pending_points=data.get("pending_points", 0),
            traits=list(data.get("traits", [])),
            addictions=list(data.get("addictions", [])),
            fears=list(data.get("fears", [])),
            ambition=data.get("ambition", ""),
            loyalty=data.get("loyalty", 0),
            stress=data.get("stress", 0),
            trauma=list(data.get("trauma", [])),
            injuries=list(data.get("injuries", [])),
            reputation=list(data.get("reputation", [])),
            relationships=dict(data.get("relationships", {})),
            history=list(data.get("history", [])),
            savage_tags=list(data.get("savage_tags", [])),
            recovery_turns=data.get("recovery_turns", 0),
            loadout=AgentLoadout.from_dict(data.get("loadout")),
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


def is_deployable(character: Character) -> bool:
    """Return whether an agent can currently be assigned to a mission."""
    return character.stats.hp > 0 and character.recovery_turns <= 0
