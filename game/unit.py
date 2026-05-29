from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Tuple

from .character import Character
from .management.spec_ops_assets import SpecOpsAsset
from .stats import PlayerStats, EnemyStats, perform_attack

if TYPE_CHECKING:
    import arcade

# Status effect keys
STATUS_SUPPRESSED = "suppressed"  # -2 movement AP next turn (triggered by overwatch fire)
STATUS_BLEEDING   = "bleeding"    # -1 HP at start of next player turn; cleared by first-aid
STATUS_STUNNED    = "stunned"     # skip next action; triggered by heavy melee


@dataclass
class Unit:
    position: Tuple[int, int]
    stats: PlayerStats | EnemyStats | None = None
    character: Character | None = None
    spec_ops_asset: SpecOpsAsset | None = None
    unit_type: str = "agent"
    equipment_summary: list[str] | None = None
    attack_range: int = 1
    health: int = 3
    action_points: int = 2
    available_actions: list[str] | None = None
    sprite: arcade.Sprite | None = None
    is_defending: bool = False
    is_psi_defending: bool = False
    # XCOM-style tactical state
    on_overwatch: bool = False       # unit fires automatically when enemy enters range
    in_cover: bool = False           # standing in cover (visual flag, bonus computed by cover_system)
    has_moved: bool = False          # moved this turn (disables overwatch if re-activated)
    enemy_subtype: str = "grunt"     # for enemy units: grunt / heavy / elite / commander
    visible: bool = True             # hidden by fog of war when False (enemies only)
    in_cover_bonus: int = 0          # defense bonus from cover nodes; updated each frame by BattleView
    # Phase 3-G04: status effects
    status_effects: list[str] = field(default_factory=list)

    # ── Status effect helpers ──────────────────────────────────────────────

    def apply_status(self, effect: str) -> None:
        """Add a status effect if not already present."""
        if effect not in self.status_effects:
            self.status_effects.append(effect)

    def clear_status(self, effect: str) -> None:
        """Remove a status effect."""
        if effect in self.status_effects:
            self.status_effects.remove(effect)

    def has_status(self, effect: str) -> bool:
        return effect in self.status_effects

    def tick_status_effects(self) -> list[str]:
        """Apply and expire turn-based status effects. Returns messages."""
        messages: list[str] = []
        # Bleeding: lose 1 HP this turn then the effect persists until healed
        if STATUS_BLEEDING in self.status_effects and self.stats:
            self.stats.hp = max(0, self.stats.hp - 1)
            self.health = self.stats.hp
            messages.append("bleeding")
        # Suppressed / stunned clear after one turn
        for effect in (STATUS_SUPPRESSED, STATUS_STUNNED):
            if effect in self.status_effects:
                self.status_effects.remove(effect)
                messages.append(f"{effect} cleared")
        return messages

    def move(self, dx: int, dy: int):
        x, y = self.position
        self.position = (x + dx, y + dy)
        if self.sprite:
            self.sprite.center_x = self.position[0]
            self.sprite.center_y = self.position[1]
        self.action_points -= 1
        self.has_moved = True
        self.on_overwatch = False  # moving cancels your overwatch

    def reset_actions(self):
        # Suppressed units get reduced AP next turn
        base_ap = 2
        if STATUS_SUPPRESSED in self.status_effects:
            base_ap = max(0, base_ap - 2)
        # Stunned units get 0 AP next turn
        if STATUS_STUNNED in self.status_effects:
            base_ap = 0
        self.action_points = base_ap
        self.is_defending = False
        self.is_psi_defending = False
        self.has_moved = False
        # Keep on_overwatch until the unit acts — it clears itself on any action

    def distance_to(self, other: "Unit") -> float:
        return (
            (self.position[0] - other.position[0]) ** 2
            + (self.position[1] - other.position[1]) ** 2
        ) ** 0.5

    def _perform_attack(self, other: "Unit", stat: str, range_: int) -> int:
        if self.action_points <= 0 or not self.stats or not other.stats:
            return 0
        if self.distance_to(other) <= range_ * 32:
            before = other.stats.hp
            hit = perform_attack(
                self.stats,
                other.stats,
                stat,
                phys_def=other.is_defending,
                psi_def=other.is_psi_defending,
                extra_defense=other.in_cover_bonus,
            )
            damage = max(0, before - other.stats.hp) if hit else 0
            other.health = other.stats.hp
            self.action_points -= 1
            other.is_defending = False
            other.is_psi_defending = False
            return damage
        return 0

    def attack(self, other: "Unit") -> int:
        """Backward compatible melee attack."""
        return self.melee_attack(other)

    def melee_attack(self, other: "Unit") -> int:
        return self._perform_attack(other, stat="str", range_=1)

    def shoot(self, other: "Unit") -> int:
        """Ranged attack using agility and equipped weapon reach."""
        return self._perform_attack(other, stat="agi", range_=max(1, self.attack_range))

    def psi_attack(self, other: "Unit") -> int:
        """Psi attack with a 10 cell range."""
        return self._perform_attack(other, stat="psi", range_=10)

    def defend(self) -> bool:
        if self.action_points <= 0:
            return False
        self.is_defending = True
        self.action_points -= 1
        return True

    def psi_defend(self) -> bool:
        if self.action_points <= 0:
            return False
        self.is_psi_defending = True
        self.action_points -= 1
        return True

    def set_overwatch(self) -> bool:
        """Put this unit on overwatch: fires automatically when enemy enters range."""
        if self.action_points <= 0 or self.has_moved:
            return False
        self.on_overwatch = True
        self.action_points -= 1
        return True

    def trigger_overwatch_shot(self, other: "Unit") -> int:
        """Fire one overwatch shot at *other* (does not cost AP — already spent).

        Returns damage dealt (0 on miss).
        """
        if not self.on_overwatch or not self.stats or not other.stats:
            return 0
        self.on_overwatch = False
        before = other.stats.hp
        hit = perform_attack(
            self.stats, other.stats, "agi",
            phys_def=other.is_defending,
            psi_def=other.is_psi_defending,
        )
        damage = max(0, before - other.stats.hp) if hit else 0
        other.health = other.stats.hp
        return damage
