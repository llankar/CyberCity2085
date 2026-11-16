"""Precision doctrine bound to existing robot and Novatek specialist rosters."""

from dataclasses import replace

from game.enemy_themes import normalize_enemy_theme
from .battlefield import trace_sight_line

PRECISION_THEMES = {"corp_samurai_robot", "corp_37_robot", "novatek_hybrid"}


def lock_valid(enemy, target, position, cover_nodes):
    return (target is not None and target.health > 0 and target.position == position
            and 32 < enemy.distance_to(target) <= enemy.attack_range * 32
            and trace_sight_line(enemy.position, target.position, cover_nodes).clear)


def reserve_precision(enemy, intent, cover_nodes):
    if (normalize_enemy_theme(enemy.enemy_theme) not in PRECISION_THEMES
            or enemy.enemy_subtype not in {"elite", "commander"}
            or enemy.control_cooldown > 0 or intent.action == "HOLD"
            or intent.target is None):
        return intent
    aim = tuple(intent.target.position)
    if not lock_valid(enemy, intent.target, aim, cover_nodes):
        return intent
    return replace(intent, action="LOCK", destination=aim,
                   rationale="2 AP precision shot (+2 attack, 30% crit). Move the target or break sight to spoil aim (1 AP lost).")
