"""Godot combat-mission UI handoff helpers.

Arcade remains the campaign shell while Godot owns the mission-combat UI.
This module builds a compact JSON payload that the Godot project can read
without importing Python game code.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from game.battle_maps import select_battle_map_entry
from game.deployment import selected_deployable_agents, selected_deployable_assets
from game.gamestate import GameState
from game.mission_templates import MissionTemplate
from game.ui.portraits import portrait_path_for_character

GODOT_COMBAT_PROJECT_DIR = Path("godot/combat_missions_ui")
DEFAULT_HANDOFF_PATH = Path("runtime/godot_combat/mission_handoff.json")
GODOT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class GodotCombatLaunchResult:
    """Outcome of preparing or starting the Godot combat UI."""

    handoff_path: Path
    command: list[str]
    launched: bool
    message: str

    @property
    def ready_for_godot(self) -> bool:
        """Return whether the handoff payload and command are available."""
        return bool(self.command)


def _mission_payload(mission: MissionTemplate) -> dict[str, Any]:
    return {
        "id": mission.id,
        "title": mission.title,
        "objective_text": mission.objective_text,
        "objective_type": getattr(mission, "objective_type", "eliminate"),
        "target_faction": mission.target_faction,
        "district": str(mission.district),
        "risk_level": mission.risk_level,
        "duration_days": mission.duration_days,
        "fund_reward": mission.fund_reward,
        "enemy_theme": getattr(mission, "enemy_theme", ""),
    }


def _map_payload(mission: MissionTemplate) -> dict[str, Any]:
    map_entry = select_battle_map_entry(mission)
    if map_entry is None:
        return {}
    return {
        "key": map_entry.key,
        "label": map_entry.label,
        "path": map_entry.path,
        "environment": map_entry.environment,
    }


def _agent_payload(character) -> dict[str, Any]:
    stats = character.stats
    portrait_path = portrait_path_for_character(character)
    return {
        "name": character.name,
        "role": character.role,
        "level": stats.level,
        "hp": stats.hp,
        "max_hp": stats.max_hp,
        "stress": character.stress,
        "portrait_path": portrait_path,
        "emotional_hook": getattr(character, "background", "")
        or getattr(character, "personality_primary_trait", ""),
        "available_actions": character.loadout.combat_actions(),
    }


def _asset_payload(asset) -> dict[str, Any]:
    return {
        "id": asset.id,
        "name": asset.name,
        "asset_type": asset.asset_type,
        "hp": asset.combat_stats().hp,
        "actions": list(asset.combat_actions),
        "pilot_agent_name": getattr(asset, "pilot_agent_name", ""),
    }


def build_godot_combat_payload(
    game_state: GameState,
    mission: MissionTemplate,
) -> dict[str, Any]:
    """Build a render-engine-neutral JSON payload for the Godot combat UI."""
    selected_agents = selected_deployable_agents(
        game_state.characters, game_state.selected_agent_names
    )
    selected_assets = selected_deployable_assets(
        game_state.spec_ops_assets,
        game_state.selected_asset_ids,
        selected_agents,
    )
    return {
        "schema_version": GODOT_SCHEMA_VERSION,
        "source": "CyberCity2085",
        "ui_engine": "godot",
        "campaign": {
            "corp_name": game_state.corp_name,
            "city_name": game_state.city_name,
            "base_name": game_state.base_name,
            "calendar_day": game_state.calendar.current_day,
        },
        "mission": _mission_payload(mission),
        "map": _map_payload(mission),
        "squad": [_agent_payload(character) for character in selected_agents],
        "support_assets": [_asset_payload(asset) for asset in selected_assets],
        "combat_ui": {
            "grid_size": 32,
            "movement_mode": "tactical_grid",
            "primary_actions": [
                "move",
                "melee",
                "fire",
                "psi",
                "defend",
                "overwatch",
            ],
            "fallback": "arcade_battle_view",
        },
        "narrative_priorities": [
            "emergent_storytelling",
            "agent_attachment",
            "small_memorable_systems",
        ],
    }


def write_godot_combat_handoff(
    game_state: GameState,
    mission: MissionTemplate,
    *,
    handoff_path: Path | str = DEFAULT_HANDOFF_PATH,
) -> Path:
    """Write the current mission handoff JSON and return its path."""
    path = Path(handoff_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_godot_combat_payload(game_state, mission)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def find_godot_executable() -> str | None:
    """Return the configured Godot executable, if available on this machine."""
    try:
        from game.ui.screens.settings_screen import load_settings

        configured = str(getattr(load_settings(), "godot_bin_path", "")).strip()
        if configured:
            return os.path.expandvars(os.path.expanduser(configured))
    except Exception:
        pass
    for env_key in ("CYBERCITY_GODOT_BIN", "GODOT4_BIN", "GODOT_BIN"):
        value = os.environ.get(env_key)
        if value:
            return os.path.expandvars(os.path.expanduser(value))
    return shutil.which("godot4") or shutil.which("godot")


def build_godot_combat_command(
    handoff_path: Path | str,
    *,
    executable: str | None = None,
    project_dir: Path | str = GODOT_COMBAT_PROJECT_DIR,
) -> list[str]:
    """Build the Godot command that opens the combat-mission UI project."""
    exe = executable if executable is not None else find_godot_executable()
    if not exe:
        return []
    project_path = Path(project_dir).resolve()
    handoff_file = Path(handoff_path).resolve()
    return [
        exe,
        "--path",
        str(project_path),
        "--",
        "--handoff",
        str(handoff_file),
    ]


def launch_godot_combat_ui(
    game_state: GameState,
    mission: MissionTemplate,
    *,
    handoff_path: Path | str = DEFAULT_HANDOFF_PATH,
    start_process: bool = True,
    executable: str | None = None,
) -> GodotCombatLaunchResult:
    """Prepare the Godot handoff and optionally start Godot in a separate process."""
    path = write_godot_combat_handoff(game_state, mission, handoff_path=handoff_path)
    command = build_godot_combat_command(path, executable=executable)
    if not command:
        return GodotCombatLaunchResult(
            path,
            [],
            False,
            "Godot handoff created; install Godot or set CYBERCITY_GODOT_BIN to launch the combat UI.",
        )
    if not start_process:
        return GodotCombatLaunchResult(
            path, command, False, "Godot combat UI command prepared."
        )
    try:
        subprocess.Popen(command)
    except OSError as exc:
        return GodotCombatLaunchResult(
            path, command, False, f"Godot launch failed: {exc}"
        )
    return GodotCombatLaunchResult(path, command, True, "Godot combat UI launched.")
