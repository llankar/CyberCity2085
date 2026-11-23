"""Window-free packaged-runtime checks. Never reads or changes a player save."""

from pathlib import Path
import json
import subprocess
import sys
from tempfile import TemporaryDirectory

from game.battle_maps import build_battle_map_catalog
from game.character import Character
from game.combat.encounter_qa import simulate_encounter
from game.gamestate import GameState
from game.map_geometry import load_map_geometry
from game.persistence import SaveSystem


def check_bundled_tactical_startup(executable: str, project: Path) -> None:
    """Boot the bundled main scene and check its readiness marker."""
    with TemporaryDirectory(prefix="cybercity-godot-smoke-") as temporary:
        root = Path(temporary)
        handoff = root / "handoff.json"
        handoff.write_text(
            json.dumps({"asset_base_dir": str(project.resolve().parents[1]), "audio": {"enabled": False}}),
            encoding="utf-8",
        )
        log = root / "godot.log"
        process = subprocess.run(
            [executable, "--headless", "--audio-driver", "Dummy", "--path",
             str(project.resolve()), "--quit-after", "30", "--log-file",
             str(log), "--", "--handoff", str(handoff)],
            timeout=30,
        )
        output = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
        if process.returncode or "SCRIPT ERROR" in output or "TACTICAL COMBAT UI READY" not in output:
            raise RuntimeError(f"Bundled Godot tactical startup failed: {output[-1500:]}")


def run_smoke():
    from game.campaign.story_missions import STORY_MISSIONS
    from game.mission_generation import story_mission_to_template
    from game.mission_templates import MissionTemplate
    story_state = GameState()
    for story in STORY_MISSIONS:
        mission = story_mission_to_template(story, story_state)
        if MissionTemplate.from_dict(mission.to_dict()).objective_type != story.objective_type:
            raise RuntimeError(f"Story objective lost during cloning: {story.id}")
    entries = build_battle_map_catalog()
    if not entries:
        raise RuntimeError("No bundled playable maps")
    for entry in entries:
        geometry = load_map_geometry(entry.path)
        if not geometry or geometry.get("method") != "manual_wall_traces_v1" or not geometry.get("reviewed"):
            raise RuntimeError(f"Missing/stale bundled manual survey: {entry.filename}")
    music = sorted(path.name for path in Path("assets/audio/music").glob("*.mp3") if path.stat().st_size)
    expected = {"Intro 1.mp3", "Intro 2.mp3", "Neon Street Warfare.mp3", "Subnet Breach.mp3",
                "Neon Highway Chase.mp3", "Cybernetic Final Battle.mp3", "Cybernetic Final Battle 2.mp3"}
    if not expected <= set(music):
        raise RuntimeError("Incomplete bundled MP3 soundtrack")
    godot_project = Path("godot/combat_missions_ui")
    if not (godot_project / "project.godot").is_file():
        raise RuntimeError("Missing optional Godot project")
    from game.combat.godot_bridge import bundled_godot_executable
    bundled_godot = bundled_godot_executable()
    if sys.platform == "win32" and getattr(sys, "frozen", False) and not bundled_godot:
        raise RuntimeError("Missing bundled Windows Godot executable")
    if bundled_godot:
        check_bundled_tactical_startup(bundled_godot, godot_project)
    cyberware_atlas = Path("assets/ui/cyberware/cyberware_atlas_v2.png")
    if not cyberware_atlas.is_file() or cyberware_atlas.stat().st_size == 0:
        raise RuntimeError("Missing bundled cyberware atlas")
    character = Character(
        "Smoke Agent",
        starver_infection_days=2,
        installed_cyberware=["smart_eye", "tactical_coprocessor"],
    )
    state = GameState(characters=[character], selected_agent_names=[character.name])
    with TemporaryDirectory(prefix="cybercity-smoke-") as temporary:
        path = Path(temporary) / "campaign.json"
        saved = SaveSystem.save_game(state, path)
        if not saved.ok:
            raise RuntimeError(saved.message)
        restored, loaded = SaveSystem.load_game(path)
        if (
            not loaded.ok
            or restored is None
            or restored.characters[0].starver_infection_days != 2
            or restored.characters[0].installed_cyberware != ["smart_eye", "tactical_coprocessor"]
            or restored.characters[0].humanity != 3
        ):
            raise RuntimeError("Packaged campaign save/load roundtrip failed")
    entry = next(entry for entry in entries if entry.filename == "city_industrial_dockside_terminal.png")
    battle = simulate_encounter(theme="corp_37_robot", level=2, risk=2, count=2, seed=0,
                                policy="objective_counterplay", map_path=entry.path, max_turns=60)
    if battle["outcome"] not in {"victory", "defeat"} or not battle["geometry_checked"]:
        raise RuntimeError("Packaged reference battle did not reach a legal terminal outcome")
    return {"status": "ok", "manual_maps": len(entries), "mp3_tracks": len(music),
            "story_objectives_preserved": len(STORY_MISSIONS),
            "save_roundtrip": True, "cyberware_roundtrip": True,
            "cyberware_atlas": cyberware_atlas.name,
            "battle": battle, "game_window_opened": False,
            "bundled_godot": Path(bundled_godot).name if bundled_godot else None,
            "bundled_tactical_headless_startup": bool(bundled_godot)}
