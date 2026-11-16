"""A fixed-tile mutant windup; no homing attack or separate hazard system."""

from dataclasses import replace
from math import dist

from .battlefield import trace_sight_line
from .tactical_identity import profile_for_theme


def can_project(enemy, position, cover_nodes):
    return (position is not None and 32 < dist(enemy.position, position) <= 128
            and trace_sight_line(enemy.position, position, cover_nodes).clear)


def reserve_projection(enemy, intent, objective, cover_nodes):
    if (profile_for_theme(enemy.enemy_theme).key != "mutant"
            or enemy.enemy_subtype not in {"heavy", "elite", "commander"}
            or enemy.control_cooldown > 0 or intent.action == "HOLD"):
        return intent
    aim = intent.target.position if intent.target is not None else getattr(objective, "position", None)
    if not can_project(enemy, aim, cover_nodes):
        return intent
    return replace(intent, action="TOXIN", target=None, target_name="marked tile",
                   destination=tuple(aim),
                   rationale="2 AP: sludge on the marked tile. Leave it or break sight before release.")
