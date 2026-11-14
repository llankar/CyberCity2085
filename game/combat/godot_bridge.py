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
import re
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from game.agents.sheet_calculations import compute_derived_stats
from game.battle_maps import select_battle_map_entry
from game.deployment import selected_deployable_agents, selected_deployable_assets
from game.gamestate import GameState
from game.mission_templates import MissionTemplate
from game.ui.portraits import portrait_path_for_character

GODOT_COMBAT_PROJECT_DIR = Path("godot/combat_missions_ui")
DEFAULT_HANDOFF_PATH = Path("runtime/godot_combat/mission_handoff.json")
RESULT_JSON_PATH = Path("runtime/godot_combat/mission_result.json")
GODOT_AUDIO_DIR = Path("godot/combat_missions_ui/audio")
GODOT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class GodotCombatLaunchResult:
    """Outcome of preparing or starting the Godot combat UI."""

    handoff_path: Path
    command: list[str]
    launched: bool
    message: str
    combat_result: dict[str, Any] | None = None
    process_pid: int | None = None

    @property
    def ready_for_godot(self) -> bool:
        """Return whether the handoff payload and command are available."""
        return bool(self.command)

    @property
    def outcome(self) -> str:
        """Shortcut for the mission outcome string ('victory', 'defeat', 'retreat')."""
        if self.combat_result is None:
            return "unknown"
        return str(self.combat_result.get("outcome", "unknown"))


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
    sheet_attrs = {
        "level": int(stats.level),
        "str": int(stats.str),
        "agi": int(stats.agi),
        "con": int(stats.con),
        "cha": int(stats.cha),
        "psi": int(stats.psi),
        "defense": int(stats.defense),
    }
    stress_state = (
        "steady" if character.stress < 35
        else "rattled" if character.stress < 65
        else "frayed" if character.stress < 85
        else "breaking"
    )
    loadout_bonuses = character.loadout.total_stat_bonuses()
    derived = compute_derived_stats(sheet_attrs, character.skills, loadout_bonuses, stress_state)
    is_robot = str(getattr(character, "role", "")).lower() == "robot"
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
        "aim":         derived["aim"],
        "defense":     derived["defense"],
        "initiative":  derived["initiative"],
        "melee_power": derived["melee_power"],
        "size_scale":  3.5 if is_robot else 1.0,
    }


def _asset_payload(asset) -> dict[str, Any]:
    stats = asset.combat_stats()
    asset_type = str(asset.asset_type)
    is_robot = asset_type in {"combat_robot", "support_robot"} or asset_type.endswith("_robot")
    return {
        "id": asset.id,
        "name": asset.name,
        "asset_type": asset_type,
        "role": "robot" if is_robot else "power_armor",
        "hp": stats.hp,
        "max_hp": stats.max_hp,
        "defense": stats.defense,
        "initiative": 14 + stats.agi,
        "action_points": int(getattr(asset, "action_points", 2)),
        "actions": list(asset.combat_actions),
        "size_scale": 3.5 if is_robot else 2.0,
        "pilot_agent_name": getattr(asset, "pilot_agent_name", ""),
    }


def copy_audio_assets() -> None:
    """Copy WAV files from assets/audio/ into the Godot project's audio/ directory.

    Godot loads audio as ``res://audio/*.wav``.  This copies both sfx and music
    sub-folders.  Missing source directories are silently skipped.
    """
    src_root = Path("assets/audio")
    if not src_root.is_dir():
        return
    GODOT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for wav in src_root.rglob("*.wav"):
        dest = GODOT_AUDIO_DIR / wav.name
        if not dest.exists() or dest.stat().st_mtime < wav.stat().st_mtime:
            shutil.copy2(wav, dest)


def read_godot_combat_result(
    result_path: Path | str = RESULT_JSON_PATH,
) -> dict[str, Any] | None:
    """Read and return the mission result JSON written by Godot's MissionResults node.

    Returns ``None`` if the file does not exist or is malformed.
    """
    path = Path(result_path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def build_godot_combat_payload(
    game_state: GameState,
    mission: MissionTemplate,
    *,
    ipc_pipe_path: str = "",  # Optional IPC pipe path for two-way signaling
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
        # Absolute path to the CyberCity2085 project root so Godot can locate
        # assets/units/, assets/maps/, etc. regardless of its working directory.
        "asset_base_dir": str(Path.cwd().resolve()),
        # IPC pipe path for two-way signaling with Python (Unix FIFO)
        "ipc_pipe_path": ipc_pipe_path,
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


def validate_godot_combat_payload(payload: dict[str, Any]) -> list[str]:
    """Return contract violations for the versioned Arcade-to-Godot handoff."""
    errors: list[str] = []
    if payload.get("schema_version") != GODOT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {GODOT_SCHEMA_VERSION}")
    required_objects = {
        "campaign": ("corp_name", "city_name", "base_name", "calendar_day"),
        "mission": ("id", "title", "objective_text", "objective_type", "district"),
        "map": ("key", "label", "path", "environment"),
        "combat_ui": ("grid_size", "movement_mode", "primary_actions", "fallback"),
    }
    for section, keys in required_objects.items():
        value = payload.get(section)
        if not isinstance(value, dict):
            errors.append(f"{section} must be an object")
            continue
        for key in keys:
            if key not in value:
                errors.append(f"{section}.{key} is required")
    for section in ("squad", "support_assets", "narrative_priorities"):
        if not isinstance(payload.get(section), list):
            errors.append(f"{section} must be a list")
    for index, agent in enumerate(payload.get("squad", [])):
        if not isinstance(agent, dict):
            errors.append(f"squad[{index}] must be an object")
            continue
        for key in ("name", "role", "hp", "max_hp", "available_actions"):
            if key not in agent:
                errors.append(f"squad[{index}].{key} is required")
    for index, asset in enumerate(payload.get("support_assets", [])):
        if not isinstance(asset, dict):
            errors.append(f"support_assets[{index}] must be an object")
            continue
        for key in ("id", "name", "asset_type", "hp", "max_hp", "actions"):
            if key not in asset:
                errors.append(f"support_assets[{index}].{key} is required")
    combat_ui = payload.get("combat_ui", {})
    primary_actions = combat_ui.get("primary_actions", []) if isinstance(combat_ui, dict) else []
    if not isinstance(primary_actions, list):
        errors.append("combat_ui.primary_actions must be a list")
    else:
        for action in ("move", "fire", "defend", "overwatch"):
            if action not in primary_actions:
                errors.append(f"combat_ui.primary_actions must include {action}")
    return errors


def write_godot_combat_handoff(
    game_state: GameState,
    mission: MissionTemplate,
    *,
    handoff_path: Path | str = DEFAULT_HANDOFF_PATH,
    ipc_pipe_path: str = "",
) -> Path:
    """Write the current mission handoff JSON and return its path."""
    path = Path(handoff_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_godot_combat_payload(game_state, mission, ipc_pipe_path=ipc_pipe_path)
    errors = validate_godot_combat_payload(payload)
    if errors:
        raise ValueError("Invalid Godot combat handoff: " + "; ".join(errors))
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _godot_installation_roots() -> list[Path]:
    """Bounded portable-install locations; never recursively scan user disks."""
    roots = [Path("tools/godot"), Path("bin/godot")]
    if os.name == "nt":
        roots.extend(Path(f"{drive}:/Godot") for drive in string.ascii_uppercase)
        for key in ("PROGRAMFILES", "LOCALAPPDATA"):
            if os.environ.get(key):
                roots.append(Path(os.environ[key]) / "Godot")
    return roots


def _find_portable_godot() -> str | None:
    candidates: list[Path] = []
    for root in _godot_installation_roots():
        if not root.is_dir():
            continue
        for pattern in ("Godot*.exe", "godot.exe", "*/Godot*.exe"):
            candidates.extend(path for path in root.glob(pattern) if path.is_file())
    if not candidates:
        return None

    def priority(path: Path):
        version = re.search(r"(?:v)?(\d+)\.(\d+)(?:\.(\d+))?", path.name)
        numbers = tuple(int(part or 0) for part in version.groups()) if version else (0, 0, 0)
        return numbers, "console" not in path.stem.lower(), str(path)

    return str(max(candidates, key=priority).resolve())


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
    return shutil.which("godot4") or shutil.which("godot") or _find_portable_godot()


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
    wait: bool = False,
    executable: str | None = None,
) -> GodotCombatLaunchResult:
    """Prepare the Godot handoff and optionally start Godot in a separate process.

    Args:
        wait: When True, block until Godot exits and read the result JSON.
              Arcade's event loop will be frozen for the duration — this is
              intentional since the player is inside the Godot combat window.
    """
    # Remove stale IPC files so we don't accidentally read previous mission data
    ipc_result_path = Path("runtime/godot_combat/ipc_result.json")
    if ipc_result_path.exists():
        ipc_result_path.unlink(missing_ok=True)

    copy_audio_assets()

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
        if wait:
            subprocess.run(command, check=False)
            # Read from IPC pipe or standard result file
            ipc_result = read_godot_combat_result(ipc_result_path)
            if not ipc_result:
                # Fallback to old method for backwards compatibility
                return GodotCombatLaunchResult(
                    path, command, True, "Godot combat UI completed (no IPC result).", None
                )
            return GodotCombatLaunchResult(
                path, command, True, "Godot combat UI completed.", ipc_result
            )
        proc = subprocess.Popen(command)
    except OSError as exc:
        return GodotCombatLaunchResult(
            path, command, False, f"Godot launch failed: {exc}"
        )
    return GodotCombatLaunchResult(
        path, command, True, "Godot combat UI launched.", process_pid=proc.pid
    )


def launch_godot_combat_ui_blocking(
    game_state: GameState,
    mission: MissionTemplate,
    *,
    handoff_path: Path | str = DEFAULT_HANDOFF_PATH,
    executable: str | None = None,
) -> GodotCombatLaunchResult:
    """Prepare the Godot handoff and block until combat completes.

    This method sets up IPC pipes for two-way communication between Python
    and Godot during the combat session. When Godot finishes, it writes a result
    JSON file that this method will read before returning control to Python.

    Args:
        game_state: Current campaign state with characters and assets.
        mission: Mission template defining the combat scenario.
        executable: Path to Godot executable (optional).

    Returns:
        GodotCombatLaunchResult with combat_result populated if Godot completed.
    """
    from .godot_ipc import start_ipc_server, read_ipc_result_blocking, cleanup_ipc_files
    from pathlib import Path as GamePath

    game_state_dir = GamePath.cwd()
    handoff_path = GamePath(handoff_path)
    parent_dir = handoff_path.parent
    parent_dir.mkdir(parents=True, exist_ok=True)

    # Start IPC server for two-way communication
    ipc_socket, pipe_path_str = start_ipc_server(parent_dir)
    
    copy_audio_assets()
    
    # Write handoff JSON with IPC pipe path so Godot can signal completion to Python
    path = write_godot_combat_handoff(
        game_state, mission, handoff_path=handoff_path, ipc_pipe_path=pipe_path_str
    )
    command = build_godot_combat_command(path, executable=executable, project_dir=GODOT_COMBAT_PROJECT_DIR)
    
    if not command:
        cleanup_ipc_files(parent_dir)
        return GodotCombatLaunchResult(
            path, [], False, "Godot handoff created; install Godot to launch combat."
        )

    try:
        # Launch Godot in background
        proc = subprocess.Popen(command)
        
        # Wait for Godot to complete and write result file
        import time
        timeout = 300.0  # 5 minutes max wait
        start_time = time.time()
        combat_result = None
        
        while (time.time() - start_time) < timeout:
            # Check if result file exists via IPC
            result = read_ipc_result_blocking(parent_dir, timeout=timeout - (time.time() - start_time))
            if result is not None:
                combat_result = result
                break
            time.sleep(0.2)

        # Clean up IPC files
        cleanup_ipc_files(parent_dir)
        
        if combat_result is None:
            return GodotCombatLaunchResult(
                path, command, False, f"Godot combat timed out after {int(timeout)}s."
            )

        return GodotCombatLaunchResult(
            path, command, True, "Godot combat UI completed.", combat_result=combat_result
        )

    except Exception as exc:
        cleanup_ipc_files(parent_dir)
        return GodotCombatLaunchResult(
            path, command, False, f"Godot launch error: {exc}"
        )
