"""Serializable-ish tactical combat state independent from Arcade rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from game.mission_templates import MissionTemplate
from game.unit import Unit

TurnPhase = Literal["player", "enemy"]


@dataclass
class CombatState:
    """Mutable battle state owned by the pure combat engine.

    The view may mirror a few attributes for legacy rendering, but new turn and
    action rules should read/write this object instead of storing rules directly
    on ``BattleView``.
    """

    mission: MissionTemplate | None
    allied_units: list[Unit]
    enemy_units: list[Unit]
    objective: Any | None = None
    turn: TurnPhase = "player"
    turn_number: int = 1
    active_index: int = 0
    logs: list[str] = field(default_factory=list)
    tactical_flags: dict[str, Any] = field(default_factory=dict)

    @property
    def active_unit(self) -> Unit | None:
        """Return the current living allied unit, if player activation exists."""
        if self.turn != "player":
            return None
        if 0 <= self.active_index < len(self.allied_units):
            unit = self.allied_units[self.active_index]
            if unit.health > 0:
                return unit
        return None
