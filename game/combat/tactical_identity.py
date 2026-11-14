"""Faction-specific tactical doctrines and deterministic enemy intent previews."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from game.enemy_themes import normalize_enemy_theme


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
    if health < max_hp * 0.40:
        score += profile.wounded_weight
    character = getattr(target, "character", None)
    role = str(getattr(character, "role", ""))
    if role in {"psi", "sniper", "commander"}:
        score += profile.specialist_weight
    elif role in {"samurai", "assault", "heavy"}:
        score += profile.specialist_weight // 2
    if stats is not None and int(getattr(stats, "defense", 3)) < 3:
        score += profile.low_defense_weight
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
    """Predict the next AI priority without mutating combat state."""

    profile = profile_for_theme(getattr(enemy, "enemy_theme", "generic"))
    living = [unit for unit in player_units if int(getattr(unit, "health", 0)) > 0]
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
