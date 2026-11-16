"""Window-free packaged-runtime checks. Never reads or changes a player save."""

from pathlib import Path
from tempfile import TemporaryDirectory

from game.battle_maps import build_battle_map_catalog
from game.character import Character
from game.combat.encounter_qa import simulate_encounter
from game.gamestate import GameState
from game.map_geometry import load_map_geometry
from game.persistence import SaveSystem


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
    if not Path("godot/combat_missions_ui/project.godot").is_file():
        raise RuntimeError("Missing optional Godot project")
    character = Character("Smoke Agent", starver_infection_days=2)
    state = GameState(characters=[character], selected_agent_names=[character.name])
    with TemporaryDirectory(prefix="cybercity-smoke-") as temporary:
        path = Path(temporary) / "campaign.json"
        saved = SaveSystem.save_game(state, path)
        if not saved.ok:
            raise RuntimeError(saved.message)
        restored, loaded = SaveSystem.load_game(path)
        if not loaded.ok or restored is None or restored.characters[0].starver_infection_days != 2:
            raise RuntimeError("Packaged campaign save/load roundtrip failed")
    entry = next(entry for entry in entries if entry.filename == "city_industrial_dockside_terminal.png")
    battle = simulate_encounter(theme="corp_37_robot", level=2, risk=2, count=2, seed=0,
                                policy="objective_counterplay", map_path=entry.path, max_turns=60)
    if battle["outcome"] not in {"victory", "defeat"} or not battle["geometry_checked"]:
        raise RuntimeError("Packaged reference battle did not reach a legal terminal outcome")
    return {"status": "ok", "manual_maps": len(entries), "mp3_tracks": len(music),
            "story_objectives_preserved": len(STORY_MISSIONS),
            "save_roundtrip": True, "battle": battle, "game_window_opened": False}
