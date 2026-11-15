"""Shared soundtrack selection for Arcade and the Godot handoff."""

from pathlib import Path

MUSIC_DIR = Path("assets/audio/music")
MUSIC_TRACKS = {
    "music_title": "Intro 1.mp3",
    "music_management": "Intro 2.mp3",
    "music_briefing": "Intro 2.mp3",
    "music_battle": "Neon Street Warfare.mp3",
    "music_hacking": "Subnet Breach.mp3",
    "music_chase": "Neon Highway Chase.mp3",
    "music_finale": "Cybernetic Final Battle.mp3",
    "music_finale_climax": "Cybernetic Final Battle 2.mp3",
    "music_ending": "Intro 1.mp3",
    "music_debrief": "music_debrief.wav",
}


def battle_music_key(mission=None) -> str:
    if mission is None:
        return "music_battle"
    mission_id = str(getattr(mission, "id", "")).lower()
    tags = [str(tag).lower() for tag in getattr(mission, "tags", ())]
    if mission_id == "sm_act5_seven_minutes":
        return "music_finale_climax"
    if mission_id.startswith("sm_act5_") or "finale" in tags:
        return "music_finale"
    objective = str(getattr(mission, "objective_type", "")).lower()
    if objective in {"data_theft", "data_with_detour", "sabotage", "sabotage_window"}:
        return "music_hacking"
    text = " ".join([str(getattr(mission, "title", "")), str(getattr(mission, "objective_text", "")), *tags]).lower()
    if any(word in text for word in ("chase", "pursuit", "convoy", "highway")):
        return "music_chase"
    return "music_battle"


def music_path(key: str) -> Path | None:
    preferred = MUSIC_DIR / MUSIC_TRACKS.get(key, f"{key}.wav")
    if preferred.is_file():
        return preferred
    fallback = "music_briefing" if key in {"music_title", "music_management", "music_ending", "music_briefing"} else "music_battle"
    path = MUSIC_DIR / f"{fallback}.wav"
    return path if path.is_file() else None
