"""Faction-specific tactical doctrines and deterministic enemy intent previews."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from game.enemy_themes import normalize_enemy_theme

# Import enemy plan system for enhanced AI prediction
try:
    from game.combat.enemy_plans import get_best_plan_for_enemy, EnemyPlanTemplate
except ImportError:
    EnemyPlanTemplate = None


@dataclass(frozen=True)
class TacticalProfile:
    key: str
    label: str
    doctrine: str
    wounded_weight: int
    specialist_weight: int
    low_defense_weight: int
    distance_weight: int
    cover_bias: float
    flank_bias: float
    objective_bias: float
    color: tuple[int, int, int]


@dataclass(frozen=True)
class EnemyIntent:
    enemy: object
    action: str
    target: object | None
    target_name: str
    rationale: str
    color: tuple[int, int, int]


_GENERIC = TacticalProfile(
    "generic", "HOSTILE", "Advance, use cover, and exploit exposed targets.",
    20, 15, 10, 2, 1.0, 1.0, 1.2, (255, 120, 80),
)

_PROFILES: dict[str, TacticalProfile] = {
    "generic": _GENERIC,
    "starver": TacticalProfile(
        "starver", "HUNGRY PACK", "Rush the nearest living target and overwhelm objectives.",
        10, 0, 0, 5, 0.0, 0.0, 1.4, (255, 82, 64),
    ),
    "mutant": TacticalProfile(
        "mutant", "MUTANT BRUTE", "Breach the line and force close combat.",
        15, 0, 5, 4, 0.0, 0.0, 1.2, (220, 100, 255),
    ),
    "raider": TacticalProfile(
        "raider", "RAIDER", "Circle cover, isolate weak agents, and take opportunistic flanks.",
        28, 8, 15, 2, 0.6, 1.4, 0.8, (255, 176, 72),
    ),
    "corp_samurai": TacticalProfile(
        "corp_samurai", "CORP STRIKE", "Use disciplined cover and eliminate battlefield specialists.",
        16, 28, 10, 1, 1.4, 1.3, 0.8, (80, 190, 255),
    ),
    "corp_37": TacticalProfile(
        "corp_37", "THREE SEVENS", "Advance under command cohesion and seize mission objectives.",
        18, 20, 8, 2, 1.0, 1.0, 1.5, (255, 70, 120),
    ),
    "novatek_hybrid": TacticalProfile(
        "novatek_hybrid", "NOVATEK HYBRID", "Hunt wounded agents with unstable close-range aggression.",
        38, 5, 12, 3, 0.0, 0.4, 1.1, (120, 255, 170),
    ),
}


def profile_for_theme(theme: object) -> TacticalProfile:
    """Resolve composite robot/power-armor themes to their parent doctrine."""

    key = normalize_enemy_theme(theme)
    if key.startswith("corp_37"):
        return _PROFILES["corp_37"]
    if key.startswith("corp_samurai"):
        return _PROFILES["corp_samurai"]
    return _PROFILES.get(key, _GENERIC)


def tactical_target_score(enemy: object, target: object) -> int:
    """Score a target using the enemy faction's visible doctrine."""
    
    profile = profile_for_theme(getattr(enemy, "enemy_theme", "generic"))
    score = 0
    stats = getattr(target, "stats", None)
    health = int(getattr(target, "health", 0))
    max_hp = max(1, int(getattr(stats, "max_hp", health or 1)))
    
    # Base scoring: wounded units are priority targets
    if health < max_hp * 0.40:
        score += profile.wounded_weight
    
    character = getattr(target, "character", None)
    role = str(getattr(character, "role", ""))
    
    # Specialist weighting for key roles (psi is high value threat)
    if role in {"psi", "sniper", "commander"}:
        score += profile.specialist_weight
    elif role in {"samurai", "assault", "heavy"}:
        score += profile.specialist_weight // 2
    
    # PENALTY TARGETING: Enemy avoids targets in dangerous states (telegraphed AI behavior)
    from game.agent_specializations import default_psi_state_for_unit, PsiState, Stance
    
    # Get current state of target for threat assessment
    psi_state = None
    stance = None
    
    if character is not None and hasattr(target, 'unit_context'):
        # Access unit context if available (used by combat system)
        unit_ctx = getattr(target, 'unit_context', {})
        if 'psi_state' in unit_ctx:
            psi_state = PsiState(unit_ctx['psi_state'])
        if 'stance' in unit_ctx:
            stance = Stance(unit_ctx['stance'])
    elif hasattr(target, 'get_psi_state') or callable(getattr(character, 'get_psi_state', None)):
        # Fallback: try direct method call
        psi_state = getattr(character, 'get_psi_state', lambda: PsiState.CONTROL)()
    
    # Apply state-based scoring adjustments for intelligent AI behavior
    if psi_state == PsiState.RISK:
        # Enemy targets RISK state units more aggressively (telegraphed threat detection)
        score += 15  # High priority - player is unstable/dangerous
        score += profile.wounded_weight  # Also treat as wounded due to instability
    
    elif psi_state == PsiState.CONTROL:
        # CONTROL state targets are less prioritized but still legitimate targets
        pass  # No penalty, normal scoring applies
    
    # Distance factor - enemies prefer closer targets per their doctrine
    distance = float(enemy.distance_to(target))
    score -= int(distance / 32) * profile.distance_weight
    
    return score


def _target_name(target: object | None) -> str:
    if target is None:
        return "objective"
    character = getattr(target, "character", None)
    if character is not None:
        return str(getattr(character, "name", "agent"))
    asset = getattr(target, "spec_ops_asset", None)
    if asset is not None:
        return str(getattr(asset, "name", "asset"))
    return "agent"


def predict_enemy_intent(
    enemy: object,
    player_units: Iterable[object],
    *,
    objective: object | None = None,
) -> EnemyIntent:
    """Predict the next AI priority using plan-based decision making."""

    profile = profile_for_theme(getattr(enemy, "enemy_theme", "generic"))
    living = [unit for unit in player_units if int(getattr(unit, "health", 0)) > 0]
    
    # Use enemy plan system for strategic intent prediction
    if EnemyPlanTemplate is not None:
        # Get context from game state
        has_objectives = objective is not None and str(getattr(objective, "kind", "")).lower() in {"defend", "containment"}
        specialist_threat = any(
            hasattr(unit, 'character') and 
            getattr(unit, 'character', None) is not None and
            str(getattr(unit.character, 'role', '')).lower() in {'psi', 'sniper', 'commander'}
            for unit in living
        )
        
        # Get best plan for this enemy based on context
        template = get_best_plan_for_enemy(
            enemy_theme=enemy.enemy_theme if hasattr(enemy, "enemy_theme") else "generic",
            player_units_count=len(living),
            has_objectives=has_objectives,
            specialist_threat=specialist_threat
        )
        
        # Derive intent from plan type
        plan_key = template.key.lower()
        target = max(living, key=lambda u: tactical_target_score(enemy, u), default=None) if living else None
        
        if "objective" in plan_key:
            action, rationale = "SEIZE", f"{template.label}: {template.description}"
        elif "specialist" in plan_key or "hunter" in plan_key:
            target = max(living, key=lambda u: tactical_target_score(enemy, u), default=None)
            if target is None:
                action, rationale = "HOLD", f"Wait for specialist opportunity"
            else:
                dist = float(enemy.distance_to(target))
                if dist <= 32:
                    action, rationale = "STRIKE", f"Hunter Kill on {_target_name(target)}"
                else:
                    action, rationale = "FIRE", f"Eliminate {_target_name(target)} (specialist)"
        elif "swarm" in plan_key or "tide" in plan_key or "starver" in plan_key:
            target = max(living, key=lambda u: tactical_target_score(enemy, u), default=None) if living else None
            if target is not None:
                dist = float(enemy.distance_to(target))
                action, rationale = "RUSH", f"Tide assault on {_target_name(target)}"
            else:
                action, rationale = "HOLD", "Overwhelming numbers ready"
        elif "breach" in plan_key or "charge" in plan_key:
            target = max(living, key=lambda u: tactical_target_score(enemy, u), default=None) if living else None
            if target is not None:
                dist = float(enemy.distance_to(target))
                action, rationale = "BREACH", f"Mutant charge on {_target_name(target)}"
            else:
                action, rationale = "AVANCE", "Close assault position"
        elif "isolate" in plan_key or "circle" in plan_key:
            target = max(living, key=lambda u: tactical_target_score(enemy, u), default=None) if living else None
            if target is not None:
                dist = float(enemy.distance_to(target))
                action, rationale = "FLANK", f"Isolate {_target_name(target)}"
            else:
                action, rationale = "HUNT", "Seek isolated target"
        elif "cover" in plan_key and "advance" in plan_key:
            action, rationale = "COVER_ADVANCE", f"Methodical advance ({template.label})"
        elif "pressure" in plan_key or "assault" in plan_key:
            target = max(living, key=lambda u: tactical_target_score(enemy, u), default=None) if living else None
            if target is not None:
                dist = float(enemy.distance_to(target))
                action, rationale = "PRESSURE", f"Frontal attack on {_target_name(target)}"
            else:
                action, rationale = "ADVANCE", "Prepare assault"
        elif "hunt" in plan_key and "wounded" in plan_key:
            target = max(living, key=lambda u: tactical_target_score(enemy, u), default=None) if living else None
            if target is not None:
                dist = float(enemy.distance_to(target))
                action, rationale = "HUNT_WOUNDED", f"Hybrid hunt on {_target_name(target)}"
            else:
                action, rationale = "SEARCH", "Look for wounded targets"
        elif "hunt" in plan_key:
            target = max(living, key=lambda u: tactical_target_score(enemy, u), default=None) if living else None
            if target is not None:
                dist = float(enemy.distance_to(target))
                action, rationale = "HUNT", f"Hunt on {_target_name(target)}"
            else:
                action, rationale = "SEARCH", "Seek targets"
        else:
            target = max(living, key=lambda u: tactical_target_score(enemy, u), default=None) if living else None
            if target is not None:
                dist = float(enemy.distance_to(target))
                if dist <= 32:
                    action, rationale = "EXECUTE_PLAN", f"Execute {template.label}"
                elif dist <= template.attack_range if hasattr(template, 'attack_range') else 96:
                    action, rationale = "EXECUTE_PLAN", f"Attack range - {template.label}"
                else:
                    action, rationale = "EXECUTE_PLAN", f"Advance - {template.label}"
            else:
                action, rationale = "HOLD", f"{template.label}: Waiting for opportunity"
        
        return EnemyIntent(enemy, action, target, _target_name(target), rationale, profile.color)
    
    # Fallback to original doctrine-based prediction if plans not available
    target = max(living, key=lambda unit: tactical_target_score(enemy, unit), default=None)
    if target is None:
        return EnemyIntent(enemy, "HOLD", None, "none", "No viable target", profile.color)

    distance = float(enemy.distance_to(target))
    attack_range = max(1, int(getattr(enemy, "attack_range", 1))) * 32
    objective_kind = str(getattr(objective, "kind", "")) if objective else ""
    if distance <= 32:
        action, rationale = "STRIKE", f"Close assault on {_target_name(target)}"
    elif distance <= attack_range:
        if int(getattr(target, "in_cover_bonus", 0)) > 0 and profile.flank_bias >= 1.0:
            action, rationale = "FLANK", f"Break {_target_name(target)}'s cover"
        else:
            action, rationale = "FIRE", f"Ranged attack on {_target_name(target)}"
    elif objective_kind in {"defend", "containment"} and profile.objective_bias >= 1.1:
        action, rationale = "BREACH", f"Pressure {objective_kind} objective"
        target = None
    elif profile.cover_bias >= 1.0 and int(getattr(enemy, "in_cover_bonus", 0)) <= 0:
        action, rationale = "COVER", "Seek a protected firing position"
    else:
        action, rationale = "HUNT", f"Advance on {_target_name(target)}"
    return EnemyIntent(enemy, action, target, _target_name(target), rationale, profile.color)


def build_enemy_intents(
    enemy_units: Iterable[object],
    player_units: Iterable[object],
    *,
    objective: object | None = None,
) -> list[EnemyIntent]:
    return [
        predict_enemy_intent(enemy, player_units, objective=objective)
        for enemy in enemy_units
        if int(getattr(enemy, "health", 0)) > 0 and bool(getattr(enemy, "visible", True))
    ]
