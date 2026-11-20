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
STATUS_BURNING = "burning"        # -2 HP at start of turn until cleared
STATUS_CONTAMINATED = "contaminated"  # -1 HP at start of turn until cleared
STATUS_PANICKED = "panicked"      # skip next action, then clears

ALL_STATUS_EFFECTS = (
    STATUS_SUPPRESSED,
    STATUS_BLEEDING,
    STATUS_STUNNED,
    STATUS_BURNING,
    STATUS_CONTAMINATED,
    STATUS_PANICKED,
)


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
    enemy_theme: str = "generic"     # for enemy units: themed roster key
    visible: bool = True             # hidden by fog of war when False (enemies only)
    in_cover_bonus: int = 0          # defense bonus from cover nodes; updated each frame by BattleView
    
    # Phase 3-G04: status effects
    status_effects: list[str] = field(default_factory=list)
    
    # Phase 4: Role state management (stances, Psi states, cooldowns)
    stance_override: str | None = None      # Manual stance selection override (BREACH/GUARD)
    psi_state_override: str | None = None   # Manual Psi state toggle override (CONTROL/RISK)
    
    # Cooldown tracking for role abilities and state changes
    stance_change_cooldown: int = 0         # Turns until next stance change allowed
    psi_state_change_cooldown: int = 0      # Turns until next Psi state toggle allowed
    breach_ability_cooldown: int = 0        # Turns until BREACH mode can be manually activated
    psi_ability_cooldown: int = 0           # Turns until Psi abilities can be used
    
    # Ability usage counters (for player choice)
    manual_breach_used_this_turn: bool = False  # Track if player forced breach this turn
    psi_overdrive_active_this_turn: bool = False  # Track if player used overdrive this turn
    bonus_move_points: int = 0
    control_cooldown: int = 0

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
        
        # First handle role state cooldowns (stance, Psi changes)
        self.stance_change_cooldown = max(0, self.stance_change_cooldown - 1)
        self.psi_state_change_cooldown = max(0, self.psi_state_change_cooldown - 1)
        self.breach_ability_cooldown = max(0, self.breach_ability_cooldown - 1)
        self.psi_ability_cooldown = max(0, self.psi_ability_cooldown - 1)
        
        # Clear manual state flags at end of turn
        self.manual_breach_used_this_turn = False
        self.psi_overdrive_active_this_turn = False
        
        # Persistent damage-over-time effects stay until another action clears them.
        if STATUS_BLEEDING in self.status_effects and self.stats:
            self.stats.hp = max(0, self.stats.hp - 1)
            self.health = self.stats.hp
            messages.append("bleeding")
        if STATUS_BURNING in self.status_effects and self.stats:
            self.stats.hp = max(0, self.stats.hp - 2)
            self.health = self.stats.hp
            messages.append("burning")
        if STATUS_CONTAMINATED in self.status_effects and self.stats:
            self.stats.hp = max(0, self.stats.hp - 1)
            self.health = self.stats.hp
            messages.append("contaminated")
        # Suppressed / stunned / panicked clear after one turn.
        for effect in (STATUS_SUPPRESSED, STATUS_STUNNED, STATUS_PANICKED):
            if effect in self.status_effects:
                self.status_effects.remove(effect)
                messages.append(f"{effect} cleared")
        
        return messages

    # ── Role state management methods ──────────────────────────────────────

    def can_change_stance(self) -> bool:
        """Check if unit can change stance (cooldown not active)."""
        return self.stance_change_cooldown == 0
    
    def can_use_breach(self) -> bool:
        """Check if breach ability is available (cooldown not active)."""
        return self.breach_ability_cooldown == 0
    
    def activate_stance(self, new_stance: str) -> bool:
        """Manually set stance. Returns True if successful."""
        from game.agent_specializations import Stance
        
        if new_stance not in ("BREACH", "GUARD"):
            return False
        
        if not self.can_change_stance():
            # If cooldown is active, revert to auto-detection (remove override)
            if self.stance_override == new_stance:
                self.stance_override = None
                return True
            return False
        
        self.stance_override = new_stance
        self.stance_change_cooldown = 2  # 2 turn cooldown after manual change
        return True
    
    def clear_stance_override(self) -> bool:
        """Clear stance override, reverting to automatic detection."""
        if self.stance_override is not None:
            self.stance_override = None
            self.stance_change_cooldown += 1  # Add a turn for the clearance action
            return True
        return False
    
    def can_toggle_psi_state(self) -> bool:
        """Check if unit can toggle Psi state (cooldown not active)."""
        return self.psi_state_change_cooldown == 0
    
    def activate_psi_state(self, new_state: str) -> bool:
        """Manually set Psi state. Returns True if successful."""
        from game.agent_specializations import PsiState
        
        if new_state not in ("CONTROL", "RISK"):
            return False
        
        if not self.can_toggle_psi_state():
            return False
        
        self.psi_state_override = new_state
        self.psi_state_change_cooldown = 2  # 2 turn cooldown after manual toggle
        self.psi_ability_cooldown = 2      # Also triggers Psi ability cooldown
        
        if new_state == "RISK":
            # Using overdrive - activate this turn flag for combat penalty tracking
            self.psi_overdrive_active_this_turn = True
        else:
            self.psi_overdrive_active_this_turn = False
        
        return True
    
    def clear_psi_override(self) -> bool:
        """Clear Psi state override, reverting to automatic detection."""
        if self.psi_state_override is not None:
            self.psi_state_override = None
            self.psi_state_change_cooldown += 1
            return True
        return False

    def spend_action_points(self, amount: int) -> None:
        self.action_points -= amount
        self._actions_used = getattr(self, "_actions_used", 0) + amount

    def move(self, dx: int, dy: int):
        x, y = self.position
        self.position = (x + dx, y + dy)
        if self.sprite:
            self.sprite.center_x = self.position[0]
            self.sprite.center_y = self.position[1]
        if self.bonus_move_points > 0:
            self.bonus_move_points -= 1
        else:
            self.spend_action_points(1)
        self.has_moved = True
        self.on_overwatch = False  # moving cancels your overwatch

    def reset_actions(self):
        self.control_cooldown = max(0, self.control_cooldown - 1)
        # Suppressed units get reduced AP next turn
        base_ap = 2
        if STATUS_SUPPRESSED in self.status_effects:
            base_ap = max(0, base_ap - 2)
        # Stunned units get 0 AP next turn
        if STATUS_STUNNED in self.status_effects:
            base_ap = 0
        if STATUS_PANICKED in self.status_effects:
            base_ap = 0
        self.action_points = base_ap
        from .enemy_themes import normalize_enemy_theme
        self.bonus_move_points = int(base_ap > 0 and self.unit_type == "enemy" and normalize_enemy_theme(self.enemy_theme) == "starver")
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
        """Return damage dealt (0 on miss).  Sets self._last_crit flag."""
        self._last_crit = False
        if self.action_points <= 0 or not self.stats or not other.stats:
            return 0
        if self.distance_to(other) <= range_ * 32:
            before = other.stats.hp
            hit, crit = perform_attack(
                self.stats,
                other.stats,
                stat,
                phys_def=other.is_defending,
                psi_def=other.is_psi_defending,
                extra_defense=other.in_cover_bonus,
            )
            damage = max(0, before - other.stats.hp) if hit else 0
            self._last_crit = crit
            other.health = other.stats.hp
            self.spend_action_points(1)
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
        self.spend_action_points(1)
        return True

    def psi_defend(self) -> bool:
        if self.action_points <= 0:
            return False
        self.is_psi_defending = True
        self.spend_action_points(1)
        return True

    def set_overwatch(self) -> bool:
        """Put this unit on overwatch: fires automatically when enemy enters range."""
        if self.action_points <= 0 or self.has_moved:
            return False
        self.on_overwatch = True
        self.spend_action_points(1)
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
