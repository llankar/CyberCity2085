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
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from game.agents.sheet_calculations import compute_derived_stats
from game.battle_maps import select_battle_map_entry
from game.deployment import selected_deployable_agents, selected_deployable_assets
from game.gamestate import GameState
from game.mission_templates import MissionTemplate
from game.ui.portraits import portrait_path_for_character, portrait_path_for_power_armor, portrait_path_for_robot

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
    session_id: str = ""
    result_path: Path | None = None
    process_pid: int | None = None
    process: Any = field(default=None, repr=False, compare=False)
    runtime: Any = field(default=None, repr=False, compare=False)

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
    from game.map_geometry import load_map_geometry
    return {
        "key": map_entry.key,
        "label": map_entry.label,
        "path": map_entry.path,
        "environment": map_entry.environment,
        "geometry": load_map_geometry(map_entry.path),
    }


def _agent_payload(character) -> dict[str, Any]:
    from .agent_moments import last_stand_dialogue

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
        "last_stand_dialogue": last_stand_dialogue(character),
        "aim":         derived["aim"],
        "defense":     derived["defense"],
        "initiative":  derived["initiative"],
        "melee_power": derived["melee_power"],
        "size_scale":  3.5 if is_robot else (1.15 if str(character.role).lower() in {"power_armor", "heavy_armor"} else 1.0),
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
        "size_scale": 3.5 if is_robot else 1.15,
        "portrait_path": portrait_path_for_robot(asset.id, asset_type) if is_robot else portrait_path_for_power_armor(asset.id, asset_type),
        "pilot_agent_name": getattr(asset, "pilot_agent_name", ""),
    }


def copy_audio_assets() -> None:
    """Mirror production WAV/MP3 files into the Godot project audio directory.

    Godot loads audio as ``res://audio/*.wav``.  This copies both sfx and music
    sub-folders.  Missing source directories are silently skipped.
    """
    src_root = Path("assets/audio")
    if not src_root.is_dir():
        return
    GODOT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    current = {path.name for pattern in ("*.wav", "*.mp3") for path in src_root.rglob(pattern)}
    for old in GODOT_AUDIO_DIR.iterdir():
        if old.is_file() and old.suffix.lower() in {".wav", ".mp3"} and old.name not in current:
            old.unlink()
    for pattern in ("*.wav", "*.mp3"):
        for source in src_root.rglob(pattern):
            dest = GODOT_AUDIO_DIR / source.name
            if not dest.exists() or dest.stat().st_mtime < source.stat().st_mtime:
                shutil.copy2(source, dest)


def read_godot_combat_result(
    result_path: Path | str = RESULT_JSON_PATH,
    *, advance_bookmark: bool=True, raise_io_errors: bool=False,
) -> dict[str, Any] | None:
    """Read a Godot result and retain its external music playback bookmark.

    Returns ``None`` if the file does not exist or is malformed.
    """
    path = Path(result_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        bookmark = data.get("music_playback")
        if isinstance(bookmark, dict) and isinstance(bookmark.get("path"), str):
            try:
                from game.audio import SoundManager
                position = float(bookmark["position"])
                if advance_bookmark and "captured_at" in bookmark:
                    import math
                    import time
                    captured = float(bookmark["captured_at"])
                    if math.isfinite(captured):
                        position += max(0.0, time.time() - captured)
                SoundManager.get().remember_music_position(bookmark["path"], position)
            except (KeyError, TypeError, ValueError):
                pass
        return data
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    except OSError:
        if raise_io_errors:
            raise
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
    from game.audio.music_catalog import battle_music_key, music_path
    from game.ui.screens.settings_screen import load_settings
    audio_settings = load_settings()
    track = music_path(battle_music_key(mission))
    map_payload = _map_payload(mission)
    environment = str(map_payload.get("environment", "")).lower()
    if any(marker in environment for marker in ("laboratory", "research", "lab", "science")):
        ambience_profile = "laboratory"
    elif any(marker in environment for marker in ("rain", "storm", "wet_city")):
        ambience_profile = "city_rain"
    elif any(marker in environment for marker in ("city", "urban", "street", "downtown", "neon")):
        ambience_profile = "city"
    else:
        ambience_profile = ""
    from game.audio import SoundManager
    return {
        "schema_version": GODOT_SCHEMA_VERSION,
        "source": "CyberCity2085",
        "ui_engine": "godot",
        "audio": {
            "battle_music_path": str(track.resolve()) if track else "",
            "start_position": SoundManager.get().music_position_for(track) if track else 0.0,
            "enabled": audio_settings.audio_enabled,
            "music_volume": audio_settings.music_volume / 100.0,
            "sfx_volume": audio_settings.sfx_volume / 100.0,
            "ambience_profile": ambience_profile,
        },
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
        "map": map_payload,
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


def bundled_godot_executable() -> str | None:
    if getattr(sys, "frozen", False):
        bundled = Path(sys.executable).resolve().parent / "bin" / "godot"
        candidates = sorted(path for path in bundled.glob("*.exe") if path.is_file())
        if candidates:
            return str(candidates[0])
    return None


def find_godot_executable() -> str | None:
    """Return the configured Godot executable, if available on this machine."""
    bundled = bundled_godot_executable()
    if bundled:
        return bundled
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
    window_rect: tuple[int, int, int, int] | None = None,
) -> list[str]:
    """Build the Godot command that opens the combat-mission UI project."""
    exe = executable if executable is not None else find_godot_executable()
    if not exe:
        return []
    project_path = Path(project_dir).resolve()
    handoff_file = Path(handoff_path).resolve()
    window_options = []
    if window_rect is not None:
        x, y, width, height = window_rect
        if width <= 0 or height <= 0:
            raise ValueError("Invalid combat viewport size")
        window_options = ["--borderless", "--position", f"{x},{y}", "--resolution", f"{width}x{height}"]
    return [
        exe,
        *window_options,
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
    window_rect: tuple[int, int, int, int] | None = None,
    resume_session_id: str | None = None,
    runtime=None,
    viewport: tuple[int,int] | None = None,
    position: tuple[int,int] | None = None,
) -> GodotCombatLaunchResult:
    """Prepare the Godot handoff and optionally start Godot in a separate process.

    Args:
        wait: When True, block until Godot exits and read the result JSON.
              Arcade's event loop will be frozen for the duration — this is
              intentional since the player is inside the Godot combat window.
    """
    if resume_session_id and wait:
        raise ValueError("Tactical recovery requires the nonblocking campaign route")
    if wait and start_process:
        return launch_godot_combat_ui_blocking(
            game_state, mission, handoff_path=handoff_path, executable=executable
        )
    # Remove stale results so a new battle cannot apply the previous reward twice.
    RESULT_JSON_PATH.unlink(missing_ok=True)
    # Remove stale IPC files so we don't accidentally read previous mission data
    ipc_result_path = Path("runtime/godot_combat/ipc_result.json")
    if ipc_result_path.exists():
        ipc_result_path.unlink(missing_ok=True)

    try:
        copy_audio_assets()
        if resume_session_id:
            from .tactical_recovery import prepare_resume_payload
            from .session_protocol import atomic_json
            payload = prepare_resume_payload(game_state, mission, resume_session_id)
            path = Path(handoff_path)
            atomic_json(path, payload)
        else:
            path = write_godot_combat_handoff(game_state, mission, handoff_path=handoff_path)
        from .session_protocol import create_session
        path, session = create_session(game_state, mission, path)
    except (OSError,ValueError,TypeError) as exc:
        return GodotCombatLaunchResult(Path(handoff_path),[],False,f"Godot session preparation failed: {exc}")
    if runtime is not None:
        try:
            dimensions=viewport or ((window_rect[2],window_rect[3]) if window_rect else (1280,720))
            location=position or ((window_rect[0],window_rect[1]) if window_rect else None)
            runtime.submit(path, session['session_id'], dimensions, location)
        except (OSError,ValueError) as exc:
            from .tactical_recovery import resume_launch_failed
            resume_launch_failed(game_state,session['session_id'])
            return GodotCombatLaunchResult(path,[],False,str(exc),session_id=session['session_id'],
                result_path=Path(session['result_path']),runtime=runtime)
        from .tactical_recovery import cancel_superseded_processes
        cancel_superseded_processes(game_state,session['session_id'])
        return GodotCombatLaunchResult(path,list(runtime.process.args),True,'Mission sent to the application Godot runtime.',
            session_id=session['session_id'],result_path=Path(session['result_path']),
            process_pid=runtime.process.pid,process=runtime.process,runtime=runtime)
    command = build_godot_combat_command(path, executable=executable, window_rect=window_rect)
    if not command:
        from .tactical_recovery import resume_launch_failed
        resume_launch_failed(game_state, session["session_id"])
        return GodotCombatLaunchResult(
            path,
            [],
            False,
            "Godot handoff created; install Godot or set CYBERCITY_GODOT_BIN to launch the combat UI.",
            session_id=session["session_id"], result_path=Path(session["result_path"]),
        )
    if not start_process:
        from .tactical_recovery import resume_launch_failed
        resume_launch_failed(game_state, session["session_id"])
        return GodotCombatLaunchResult(
            path, command, False, "Godot combat UI command prepared.", session_id=session["session_id"], result_path=Path(session["result_path"])
        )
    try:
        proc = subprocess.Popen(command)
    except OSError as exc:
        from .tactical_recovery import resume_launch_failed
        resume_launch_failed(game_state, session["session_id"])
        return GodotCombatLaunchResult(
            path, command, False, f"Godot launch failed: {exc}", session_id=session["session_id"], result_path=Path(session["result_path"])
        )
    from .tactical_recovery import cancel_superseded_processes
    cancel_superseded_processes(game_state, session['session_id'])
    # The campaign retains music until Godot confirms readiness.
    return GodotCombatLaunchResult(
        path, command, True, "Godot combat UI launched.", session_id=session["session_id"], result_path=Path(session["result_path"]), process_pid=proc.pid, process=proc
    )


def launch_godot_combat_ui_blocking(
    game_state: GameState,
    mission: MissionTemplate,
    *,
    handoff_path: Path | str = DEFAULT_HANDOFF_PATH,
    executable: str | None = None,
    timeout: float | None = None,
) -> GodotCombatLaunchResult:
    """Compatibility API: wait for a result or child exit, without an OS pipe.

    The campaign UI uses the nonblocking handoff view. This API has no arbitrary
    battle time limit by default; callers may supply an explicit timeout.
    """
    import time
    from .godot_ipc import start_ipc_server, read_ipc_result, cleanup_ipc_files

    path = Path(handoff_path)
    directory = path.parent
    command = []
    proc = None
    try:
        _, signal_path = start_ipc_server(directory)
        copy_audio_assets()
        path = write_godot_combat_handoff(
            game_state, mission, handoff_path=path, ipc_pipe_path=signal_path
        )
        command = build_godot_combat_command(path, executable=executable)
        if not command:
            return GodotCombatLaunchResult(path, [], False, "Godot unavailable; use Arcade fallback.")
        proc = subprocess.Popen(command)
        from game.audio import SoundManager
        SoundManager.get().pause_music(external=True)
        deadline = time.monotonic() + max(0, timeout) if timeout is not None else None
        while True:
            result = read_ipc_result(directory)
            if result is not None:
                return GodotCombatLaunchResult(path, command, True, "Godot combat UI completed.", combat_result=result)
            code = proc.poll()
            if code is not None:
                # One final read in case the child published just before exiting.
                result = read_ipc_result(directory)
                if result is not None:
                    return GodotCombatLaunchResult(path, command, True, "Godot combat UI completed.", combat_result=result)
                return GodotCombatLaunchResult(path, command, False, f"Godot exited ({code}) without a combat result; use Arcade fallback.")
            if deadline is not None and time.monotonic() >= deadline:
                return GodotCombatLaunchResult(path, command, False, "Godot combat timed out; use Arcade fallback.")
            time.sleep(0.05)
    except (OSError, ValueError) as exc:
        return GodotCombatLaunchResult(path, command, False, f"Godot launch error: {exc}")
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        try:
            cleanup_ipc_files(directory)
        except OSError:
            pass
