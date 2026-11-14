"""Enemy intent plans with explicit disruption conditions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol

from game.enemy_themes import normalize_enemy_theme


# =============================================================================
# Enums: Disruption Types and Plan States
# =============================================================================

class DisruptionType(Enum):
    """Types of player actions that can disrupt enemy plans."""
    
    DESTRUCTION = auto()          # Enemy unit destroyed (KIA)
    MOVEMENT_BLOCK = auto()       # Movement path blocked/occupied
    COVER_DISRUPT = auto()        # Cover position compromised
    FLANK_EXPOSED = auto()        # Flanking maneuver detected
    KEY_TARGET_HIT = auto()       # High-value target hit/stunned/suppressed
    PSI_INTERRUPTION = auto()     # Psi control disrupted
    STATUS_IMPAIRMENT = auto()   # Unit status impaired (stunned/burning/bleeding)


class PlanState(Enum):
    """Current state of an enemy plan."""
    
    INITIATING = "initiating"      # Planning phase, waiting for opportunity
    ACTIVE = "active"              # Currently being executed
    DISRUPTED = "disrupted"        # Interrupted by player action
    COMPLETED = "completed"        # Successfully executed
    ABORTED = "aborted"            # Abandoned due to failure/changes
    CANCELLED = "cancelled"        # No longer relevant (enemy destroyed, objective lost)


# =============================================================================
# Data: Plan Template Definitions per Faction
# =============================================================================

@dataclass
class DisruptionCondition:
    """Defines when a plan can be disrupted."""
    
    disruption_type: DisruptionType
    severity_threshold: float = 0.0   # 0.0-1.0, how severe must disruption be
    reset_turns: int = 1              # How many turns until plan can try again
    alternative_plan: str | None = None  # Alternative plan to switch to


@dataclass
class EnemyPlanTemplate:
    """Definition of a complete enemy strategic plan."""
    
    key: str
    label: str
    description: str
    
    # Execution priority (higher = more likely to attempt)
    priority: int = 10
    
    # Win condition for this plan
    success_indicators: list[str] = field(default_factory=list)
    
    # Disruption conditions per phase
    disruption_conditions: dict[str, DisruptionCondition] = field(
        default_factory=dict
    )
    
    # Faction/doctrine tags (for filtering by enemy type)
    faction_tags: list[str] = field(default_factory=list)


# =============================================================================
# Plan Registry: All available enemy plans organized by faction
# =============================================================================

CORP_37_PLANS: dict[str, EnemyPlanTemplate] = {
    "seize_objective": EnemyPlanTemplate(
        key="seize_objective",
        label="Seize Control",
        description="Advance coordinated units to capture mission objectives and deny player access.",
        priority=95,
        success_indicators=["objective_controlled"],
        faction_tags=["corp_37", "three_sevens"],
        disruption_conditions={
            "DESTRUCTION": DisruptionCondition(
                disruption_type=DisruptionType.DESTRUCTION,
                severity_threshold=1.0,
                reset_turns=2,
                alternative_plan="flank_objective"
            ),
            "FLANK_EXPOSED": DisruptionCondition(
                disruption_type=DisruptionType.FLANK_EXPOSED,
                severity_threshold=0.7,
                reset_turns=1,
                alternative_plan="cover_and_advance"
            ),
            "KEY_TARGET_HIT": DisruptionCondition(
                disruption_type=DisruptionType.KEY_TARGET_HIT,
                severity_threshold=0.8,
                reset_turns=3,
                alternative_plan="reorganize_assault"
            ),
        }
    ),
    "cover_and_advance": EnemyPlanTemplate(
        key="cover_and_advance",
        label="Cover Advance",
        description="Use cover positions to advance methodically toward objectives.",
        priority=80,
        success_indicators=["objective_near"],
        faction_tags=["corp_37"],
        disruption_conditions={
            "COVER_DISRUPT": DisruptionCondition(
                disruption_type=DisruptionType.COVER_DISRUPT,
                severity_threshold=0.9,
                reset_turns=2,
                alternative_plan="relocate_cover"
            ),
            "MOVEMENT_BLOCK": DisruptionCondition(
                disruption_type=DisruptionType.MOVEMENT_BLOCK,
                severity_threshold=0.8,
                reset_turns=1,
                alternative_plan="flank_objective"
            ),
        }
    ),
}

CORP_SAMURAI_PLANS: dict[str, EnemyPlanTemplate] = {
    "eliminate_specialist": EnemyPlanTemplate(
        key="eliminate_specialist",
        label="Hunter Kill",
        description="Focus fire on player specialists (Psi, sniper) to break their effectiveness.",
        priority=90,
        success_indicators=["specialist_down"],
        faction_tags=["corp_samurai", "corporate_security"],
        disruption_conditions={
            "KEY_TARGET_HIT": DisruptionCondition(
                disruption_type=DisruptionType.KEY_TARGET_HIT,
                severity_threshold=0.85,
                reset_turns=2,
                alternative_plan="pressure_main_force"
            ),
            "PSI_INTERRUPTION": DisruptionCondition(
                disruption_type=DisruptionType.PSI_INTERRUPTION,
                severity_threshold=1.0,
                reset_turns=3,
                alternative_plan="eliminate_specialist"
            ),
        }
    ),
    "pressure_main_force": EnemyPlanTemplate(
        key="pressure_main_force",
        label="Frontal Assault",
        description="Concentrate force against the largest threat cluster.",
        priority=75,
        success_indicators=["major_threat_down"],
        faction_tags=["corp_samurai"],
        disruption_conditions={
            "DESTRUCTION": DisruptionCondition(
                disruption_type=DisruptionType.DESTRUCTION,
                severity_threshold=1.0,
                reset_turns=1,
                alternative_plan=None
            ),
            "STATUS_IMPAIRMENT": DisruptionCondition(
                disruption_type=DisruptionType.STATUS_IMPAIRMENT,
                severity_threshold=0.6,
                reset_turns=2,
                alternative_plan="focus_weakest"
            ),
        }
    ),
}

STARVER_PLANS: dict[str, EnemyPlanTemplate] = {
    "overwhelming_swarm": EnemyPlanTemplate(
        key="overwhelming_swarm",
        label="Starver Tide",
        description="Rush in overwhelming numbers, ignore casualties, focus on killing any living target.",
        priority=100,
        success_indicators=["player_defeated"],
        faction_tags=["starver", "hungry_tide"],
        disruption_conditions={
            "DESTRUCTION": DisruptionCondition(
                disruption_type=DisruptionType.DESTRUCTION,
                severity_threshold=0.5,
                reset_turns=0,
                alternative_plan=None
            ),
            "KEY_TARGET_HIT": DisruptionCondition(
                disruption_type=DisruptionType.KEY_TARGET_HIT,
                severity_threshold=0.5,
                reset_turns=0,
                alternative_plan="overwhelming_swarm"
            ),
        }
    ),
}

MUTANT_PLANS: dict[str, EnemyPlanTemplate] = {
    "breach_close": EnemyPlanTemplate(
        key="breach_close",
        label="Mutant Charge",
        description="Ignore range, push through cover to force brutal close combat.",
        priority=92,
        success_indicators=["melee_engaged"],
        faction_tags=["mutant"],
        disruption_conditions={
            "COVER_DISRUPT": DisruptionCondition(
                disruption_type=DisruptionType.COVER_DISRUPT,
                severity_threshold=0.7,
                reset_turns=2,
                alternative_plan="breach_close"
            ),
            "MOVEMENT_BLOCK": DisruptionCondition(
                disruption_type=DisruptionType.MOVEMENT_BLOCK,
                severity_threshold=1.0,
                reset_turns=3,
                alternative_plan="flank_close"
            ),
        }
    ),
    "panic_and_bite": EnemyPlanTemplate(
        key="panic_and_bite",
        label="Feast Mode",
        description="Target wounded/panicked units for maximum damage output.",
        priority=70,
        success_indicators=["wounded_target"],
        faction_tags=["mutant"],
        disruption_conditions={
            "STATUS_IMPAIRMENT": DisruptionCondition(
                disruption_type=DisruptionType.STATUS_IMPAIRMENT,
                severity_threshold=0.8,
                reset_turns=1,
                alternative_plan=None
            ),
        }
    ),
}

RAIDER_PLANS: dict[str, EnemyPlanTemplate] = {
    "circle_and_isolate": EnemyPlanTemplate(
        key="circle_and_isolate",
        label="Isolation Trap",
        description="Flank to separate weak targets and eliminate them individually.",
        priority=88,
        success_indicators=["isolated_target"],
        faction_tags=["raider"],
        disruption_conditions={
            "FLANK_EXPOSED": DisruptionCondition(
                disruption_type=DisruptionType.FLANK_EXPOSED,
                severity_threshold=0.9,
                reset_turns=2,
                alternative_plan="pressure_cover"
            ),
            "MOVEMENT_BLOCK": DisruptionCondition(
                disruption_type=DisruptionType.MOVEMENT_BLOCK,
                severity_threshold=0.7,
                reset_turns=1,
                alternative_plan="direct_approach"
            ),
        }
    ),
    "pressure_cover": EnemyPlanTemplate(
        key="pressure_cover",
        label="Cover Fire",
        description="Use cover to maintain long-range suppression until targets are isolated.",
        priority=65,
        success_indicators=["suppressed"],
        faction_tags=["raider"],
        disruption_conditions={
            "COVER_DISRUPT": DisruptionCondition(
                disruption_type=DisruptionType.COVER_DISRUPT,
                severity_threshold=0.95,
                reset_turns=3,
                alternative_plan="circle_and_isolate"
            ),
        }
    ),
}

NOVATEK_PLANS: dict[str, EnemyPlanTemplate] = {
    "hunt_wounded": EnemyPlanTemplate(
        key="hunt_wounded",
        label="Hybrid Hunt",
        description="Target specifically wounded agents with unstable aggression patterns.",
        priority=96,
        success_indicators=["wounded_target"],
        faction_tags=["novatek_hybrid", "novatek_lab"],
        disruption_conditions={
            "STATUS_IMPAIRMENT": DisruptionCondition(
                disruption_type=DisruptionType.STATUS_IMPAIRMENT,
                severity_threshold=0.7,
                reset_turns=1,
                alternative_plan="hunt_wounded"
            ),
            "DESTRUCTION": DisruptionCondition(
                disruption_type=DisruptionType.DESTRUCTION,
                severity_threshold=1.0,
                reset_turns=2,
                alternative_plan="assess_new_targets"
            ),
        }
    ),
}

# =============================================================================
# Registry Access Functions
# =============================================================================

_PLAN_REGISTRY: dict[str, dict[str, EnemyPlanTemplate]] = {
    "corp_37": CORP_37_PLANS,
    "corp_samurai": CORP_SAMURAI_PLANS,
    "starver": STARVER_PLANS,
    "mutant": MUTANT_PLANS,
    "raider": RAIDER_PLANS,
    "novatek_hybrid": NOVATEK_PLANS,
}

GENERIC_PLAN: EnemyPlanTemplate = EnemyPlanTemplate(
    key="generic_assault",
    label="General Assault",
    description="Standard enemy behavior: advance, use cover, attack nearest target.",
    priority=50,
    disruption_conditions={
        "DESTRUCTION": DisruptionCondition(
            disruption_type=DisruptionType.DESTRUCTION,
            severity_threshold=1.0,
            reset_turns=1,
            alternative_plan=None
        ),
        "KEY_TARGET_HIT": DisruptionCondition(
            disruption_type=DisruptionType.KEY_TARGET_HIT,
            severity_threshold=0.7,
            reset_turns=2,
            alternative_plan="retreat_reposition"
        ),
    }
)


def normalize_enemy_theme(theme: object) -> str:
    """Normalize enemy theme to registry key."""
    if isinstance(theme, str):
        theme = theme.lower().strip()
    
    # Handle composite themes (robot power armor variants)
    theme_str = str(theme).lower()
    if "corp_37" in theme_str or "three_sevens" in theme_str:
        return "corp_37"
    if "corp_samurai" in theme_str or "corporate_security" in theme_str:
        return "corp_samurai"
    if "starver" in theme_str or "hungry_tide" in theme_str:
        return "starver"
    if "mutant" in theme_str:
        return "mutant"
    if "raider" in theme_str:
        return "raider"
    if "novatek" in theme_str or "hybrid" in theme_str:
        return "novatek_hybrid"
    
    return "generic"


def get_plans_for_enemy(enemy_theme: object) -> list[EnemyPlanTemplate]:
    """Get all available plans for an enemy's faction."""
    key = normalize_enemy_theme(enemy_theme)
    
    if key in _PLAN_REGISTRY:
        # Return all plans from this faction
        return list(_PLAN_REGISTRY[key].values())
    
    return [GENERIC_PLAN]


def get_best_plan_for_enemy(
    enemy_theme: object,
    player_units_count: int,
    has_objectives: bool = True,
    specialist_threat: bool = False,
) -> EnemyPlanTemplate:
    """
    Select the most appropriate plan based on context.
    
    Args:
        enemy_theme: Enemy's faction/theme
        player_units_count: Number of living player units
        has_objectives: Whether mission objectives exist
        specialist_threat: Whether high-value specialists are present
        
    Returns:
        The best-matching plan template with highest priority in context
    """
    plans = get_plans_for_enemy(enemy_theme)
    
    if not plans:
        return GENERIC_PLAN
    
    # Score each plan for current situation
    def score_plan(plan: EnemyPlanTemplate) -> int:
        base_score = plan.priority
        
        # Context modifiers
        if has_objectives and "objective" in plan.key.lower():
            base_score += 10
        elif specialist_threat and "specialist" in plan.key.lower():
            base_score += 15
        
        # Scale by force size (large forces favor overwhelming tactics)
        if player_units_count > 4:
            if "swarm" in plan.key.lower() or "tide" in plan.key.lower():
                base_score += 5
        elif player_units_count <= 2:
            if "isolate" in plan.key.lower() or "hunter" in plan.key.lower():
                base_score += 5
        
        return base_score
    
    # Return highest scoring plan
    best = max(plans, key=score_plan)
    return best


# =============================================================================
# Runtime Plan State (per enemy unit)
# =============================================================================

@dataclass
class EnemyPlanState:
    """Runtime state of an enemy's current plan."""
    
    template_key: str
    state: PlanState = PlanState.INITIATING
    
    # Disruption tracking
    disruption_count: dict[str, int] = field(default_factory=dict)  # Dict[DisruptionType, int]
    last_disruption_turn: int = 0
    
    # Execution progress
    progress_stages: list[int] = field(default_factory=list)
    current_stage_index: int = 0
    
    # Alternative plan fallback (if disrupted)
    alternate_template_key: str | None = None
    
    @property
    def is_active(self) -> bool:
        """Check if plan is currently being executed."""
        return self.state == PlanState.ACTIVE
    
    @property
    def can_attempt_execution(self) -> bool:
        """Check if plan can be attempted (not disrupted recently)."""
        if self.state == PlanState.DISRUPTED:
            return False
        
        # Check cooldowns
        for disruption_type, count in self.disruption_count.items():
            if count >= 2:  # Cooldown after 2 disruptions
                return False
        
        return True


# =============================================================================
# Plan Manager: Handles plan selection, execution, and disruption
# =============================================================================

class EnemyPlanManager:
    """Manages enemy intent plans with disruption handling."""
    
    def __init__(self):
        self.plans: dict[str, EnemyPlanState] = {}  # enemy_id -> plan_state
    
    def initialize_plan(self, enemy_id: str, enemy_theme: object) -> None:
        """Initialize a new plan for an enemy unit."""
        theme_key = normalize_enemy_theme(enemy_theme)
        
        if theme_key in _PLAN_REGISTRY:
            template = list(_PLAN_REGISTRY[theme_key].values())[0]
        else:
            template = GENERIC_PLAN
        
        self.plans[enemy_id] = EnemyPlanState(
            template_key=template.key,
            state=PlanState.INITIATING
        )
    
    def update_plan_state(self, enemy_theme: object) -> tuple[EnemyPlanTemplate | None, Protocol]:
        """
        Update plan based on current game state.
        
        Returns:
            Tuple of (current template, predicted intent) or (None, None) if no plan
        """
        # For simplified version, just return the best plan for the theme
        template = get_best_plan_for_enemy(
            enemy_theme=enemy_theme,
            player_units_count=0,
            has_objectives=True,
            specialist_threat=False,
        )
        
        # Return a mock intent for now
        from game.combat.tactical_identity import EnemyIntent
        return template, EnemyIntent(
            enemy=None, action="EXECUTE", 
            target=None, target_name=template.label, 
            rationale=template.description,
            color=(255, 100, 50)
        )
    
    def apply_disruption(
        self, 
        enemy_id: str, 
        disruption_type: DisruptionType,
        severity: float = 1.0,
        game_turn: int = 0
    ) -> None:
        """Apply a disruption to an enemy's plan."""
        if enemy_id not in self.plans:
            return
        
        state = self.plans[enemy_id]
        
        # Get the template for this enemy
        theme_key = normalize_enemy_theme(state.template_key)
        template = list(_PLAN_REGISTRY.get(theme_key, {}).values())[0] if theme_key in _PLAN_REGISTRY else GENERIC_PLAN
        
        # Check if this is actually severe enough to disrupt
        condition = template.disruption_conditions.get(disruption_type.key)
        if not condition or severity < condition.severity_threshold:
            return
        
        # Mark as disrupted
        state.state = PlanState.DISRUPTED
        state.last_disruption_turn = game_turn
        state.disruption_count[disruption_type] = state.disruption_count.get(disruption_type, 0) + 1
        
        # Get alternative plan if available
        alternate_key = condition.alternative_plan
        if alternate_key and alternate_key in _PLAN_REGISTRY:
            state.alternate_template_key = alternate_key
    
    def tick(self, game_turn: int) -> None:
        """Process turn end - reset cooldowns for plans that can retry."""
        for enemy_id, state in self.plans.items():
            if state.state == PlanState.DISRUPTED:
                # Reset disruptions after configured turns
                pass  # Full implementation would reset based on template config
    
    def destroy_enemy(self, enemy_id: str) -> None:
        """Mark enemy as destroyed - cancel their plan."""
        self.plans[enemy_id].state = PlanState.CANCELLED


# Global manager instance for combat system
_plan_manager = EnemyPlanManager()


def apply_enemy_disruption(
    enemy_id: str,
    disruption_type: DisruptionType,
    severity: float = 1.0,
) -> None:
    """
    Apply a player action that disrupts an enemy's plan.
    
    This gives the AI meaningful reasons to change behavior when
    players take strategic actions.
    """
    _plan_manager.apply_disruption(enemy_id, disruption_type, severity)


def get_current_plan(enemy_id: str) -> EnemyPlanState | None:
    """Get current plan state for enemy."""
    return _plan_manager.plans.get(enemy_id)


def predict_enemy_intent_with_plan(
    enemy_theme: object,
    player_units=None,
    objective=None,
) -> tuple[Protocol, str]:
    """
    Predict enemy intent using their current plan.
    
    Returns:
        Tuple of (intent details, plan label for UI feedback)
    """
    template = get_best_plan_for_enemy(
        enemy_theme=enemy_theme,
        player_units_count=len(player_units) if player_units else 0,
        has_objectives=objective is not None,
        specialist_threat=False
    )
    
    # Return intent based on plan type
    from game.combat.tactical_identity import EnemyIntent
    
    return EnemyIntent(
        enemy=None,
        action="EXECUTE",
        target=None,
        target_name=template.label,
        rationale=template.description,
        color=(255, 100, 50)
    ), template.label
