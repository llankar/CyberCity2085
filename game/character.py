from dataclasses import dataclass, field, asdict
from typing import Dict

from .stats import PlayerStats


@dataclass
class Character:
    """Player character with associated statistics."""

    name: str
    role: str = "samurai"
    stats: PlayerStats = field(default_factory=PlayerStats)
    pending_points: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "stats": asdict(self.stats),
            "pending_points": self.pending_points,
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

