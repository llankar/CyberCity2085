"""Pure tactical combat state and transition helpers."""

from .events import CombatEvent, CombatEventResult, CombatEventTrigger
from .movement import can_enter_cell, path_to_cell, reachable_cells
from .state import CombatState


def __getattr__(name: str):
    if name in {"BattleCheckResult", "CombatActionResult", "CombatEngine"}:
        from .engine import BattleCheckResult, CombatActionResult, CombatEngine

        return {
            "BattleCheckResult": BattleCheckResult,
            "CombatActionResult": CombatActionResult,
            "CombatEngine": CombatEngine,
        }[name]
    if name in {
        "GodotCombatLaunchResult",
        "build_godot_combat_payload",
        "build_godot_combat_command",
        "launch_godot_combat_ui",
        "write_godot_combat_handoff",
    }:
        from .godot_bridge import (
            GodotCombatLaunchResult,
            build_godot_combat_command,
            build_godot_combat_payload,
            launch_godot_combat_ui,
            write_godot_combat_handoff,
        )

        return {
            "GodotCombatLaunchResult": GodotCombatLaunchResult,
            "build_godot_combat_payload": build_godot_combat_payload,
            "build_godot_combat_command": build_godot_combat_command,
            "launch_godot_combat_ui": launch_godot_combat_ui,
            "write_godot_combat_handoff": write_godot_combat_handoff,
        }[name]
    raise AttributeError(name)


__all__ = [
    "BattleCheckResult",
    "CombatActionResult",
    "CombatEngine",
    "CombatEvent",
    "CombatEventResult",
    "CombatEventTrigger",
    "CombatState",
    "GodotCombatLaunchResult",
    "build_godot_combat_payload",
    "build_godot_combat_command",
    "launch_godot_combat_ui",
    "write_godot_combat_handoff",
    "can_enter_cell",
    "path_to_cell",
    "reachable_cells",
]
