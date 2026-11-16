"""AI decision-making layer that uses enemy plans for tactical behavior."""

from __future__ import annotations

from typing import Iterable

from game.combat.enemy_plans import (
    get_best_plan_for_enemy, DisruptionType,
    apply_enemy_disruption as _apply_disruption, get_current_plan
)
from game.combat.tactical_identity import (
    predict_enemy_intent, EnemyIntent, build_enemy_intents
)


def make_ai_decision(
    enemy,
    player_units: Iterable[object],
    objective=None,
    current_turn=0,
) -> tuple[str, str]:
    """
    Make a tactical decision for an AI unit using the plan system.
    
    Returns:
        Tuple of (action_name, rationale)
    """
    theme = getattr(enemy, "enemy_theme", "generic")
    
    # Get context from game state
    living_units = [u for u in player_units if int(getattr(u, "health", 0)) > 0]
    has_objectives = objective is not None and str(getattr(objective, "kind", "")).lower() in {"defend", "containment"}
    
    # Check for specialist threats (Psi, sniper, commander)
    specialist_threat = any(
        hasattr(unit, 'character') and 
        getattr(unit, 'character', None) is not None and
        str(getattr(unit.character, 'role', '')).lower() in {'psi', 'sniper', 'commander'}
        for unit in living_units
    )
    
    # Get best plan for this enemy based on context
    template = get_best_plan_for_enemy(
        enemy_theme=theme if hasattr(enemy, "enemy_theme") else "generic",
        player_units_count=len(living_units),
        has_objectives=has_objectives,
        specialist_threat=specialist_threat
    )
    
    # Predict intent from plan
    intent = predict_enemy_intent(
        enemy=enemy,
        player_units=living_units,
        objective=objective
    )
    
    return (intent.action, f"{template.label}: {intent.rationale}")


def apply_enemy_disruption(
    enemy_id: str,
    disruption_type: DisruptionType,
    severity: float = 1.0,
    *,
    game_turn: int = 0,
) -> None:
    """
    Apply a player action that disrupts an enemy's plan.
    
    This gives the AI meaningful reasons to change behavior when
    players take strategic actions.
    """
    _apply_disruption(enemy_id, disruption_type, severity, game_turn)


def get_enemy_plan_info(enemy_id: str) -> dict:
    """Get diagnostic info about an enemy's current plan."""
    plan = get_current_plan(enemy_id)
    
    if not plan:
        return {"error": "No plan initialized"}
    
    # Get template info
    theme_key = getattr(plan, 'template_key', 'unknown')
    plans_for_theme = []
    try:
        from game.combat.enemy_plans import get_plans_for_enemy
        for enemy_theme in ['corp_37', 'corp_samurai', 'starver', 'mutant', 'raider']:
            plans = get_plans_for_enemy(enemy_theme)
            if any(p.key == theme_key for p in plans):
                plans_for_theme = plans
                break
    except Exception:
        pass
    
    return {
        "enemy_id": enemy_id,
        "template_key": plan.template_key,
        "state": str(plan.state.value),
        "is_active": plan.is_active,
        "can_attempt_execution": plan.can_attempt_execution,
        "disruption_count": {kind.name: count for kind, count in plan.disruption_count.items()},
        "last_disruption_turn": plan.last_disruption_turn,
        "alternate_plan": plan.alternate_template_key,
        "available_plans": [p.key for p in plans_for_theme] if plans_for_theme else ["generic_assault"],
    }


# Build enemy intents using the new plan system
def build_enhanced_enemy_intents(
    enemies: Iterable[object],
    player_units: Iterable[object],
    objective=None,
) -> list[EnemyIntent]:
    """Build all enemy intents with enhanced plan-based prediction."""
    return build_enemy_intents(enemies, player_units, objective=objective)
