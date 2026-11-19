"""Optional, provenance-tracked SFX preview routing for CyberCity 2085.

Only WAVs physically present in assets/audio/overhaul are eligible. The legacy
sounds remain the fallback. Additional CC0/CC-BY files are distinct assets and
keep separate attribution; their quality is still subject to listening review.
"""
from __future__ import annotations

from pathlib import Path

OVERHAUL_DIR = Path("assets/audio/overhaul")

PREFERRED_SFX: dict[str, tuple[str, ...]] = {
    "sfx_fire": ("weapons/fire_assault_01.wav",),
    "sfx_fire_assault": ("weapons/fire_assault_01.wav",),
    "sfx_fire_pistol": ("weapons/fire_pistol_01.wav",),
    "sfx_fire_laser": ("weapons/fire_laser_cc0_01.wav", "weapons/fire_laser_cc0_02.wav"),
    "sfx_hit": ("combat/impact_metal_01.wav", "combat/impact_metal_cc0_01.wav"),
    "sfx_hit_metal": (
        "combat/impact_metal_01.wav", "combat/impact_metal_cc0_01.wav",
        "combat/impact_metal_cc0_02.wav",
    ),
    "sfx_hit_glass": ("combat/impact_glass_cc0_01.wav",),
    "sfx_hit_organic": ("combat/impact_organic_cc0_01.wav",),
    "sfx_melee": ("combat/melee_cc0_01.wav",),
    "sfx_explosion_small": ("combat/explosion_small_cc0_01.wav",),
    "sfx_move": ("movement/step_concrete_01.wav", "movement/step_concrete_cc0_01.wav"),
    "sfx_move_concrete": (
        "movement/step_concrete_01.wav", "movement/step_concrete_cc0_01.wav",
        "movement/step_concrete_cc0_02.wav", "movement/step_concrete_cc0_03.wav",
    ),
    "sfx_move_metal": ("movement/step_metal_cc0_01.wav",),
    "sfx_move_robot": ("movement/move_robot_cc0_01.wav",),
    "sfx_shield": ("technology/shield_cc0_01.wav",),
    "sfx_terminal": ("technology/terminal_cc0_01.wav",),
    "sfx_door_open": ("technology/door_open_cc0_01.wav",),
    "sfx_ui_click": (
        "ui/ui_click_01.wav", "ui/ui_click_cc0_01.wav", "ui/ui_click_cc0_02.wav",
    ),
    "sfx_ui_confirm": ("ui/ui_confirm_cc0_01.wav",),
    "sfx_ui_refuse": ("ui/ui_refuse_cc0_01.wav",),
    "sfx_city_short": ("ambience/ambience_city_short_candidate_02.wav",),
}

AMBIENCE_CITY_CANDIDATES = (
    "ambience/ambience_city_cc0_01.wav",
    "ambience/ambience_city_loop_candidate_01.wav",
)
AMBIENCE_CITY_RAIN = "ambience/ambience_city_rain_cc0_01.wav"
AMBIENCE_LAB = "ambience/ambience_laboratory_ccby_01.wav"
CITY_SHORT_CUE = "ambience/ambience_city_short_candidate_02.wav"


def preview_sfx_paths(event: str, *, root: Path = OVERHAUL_DIR) -> tuple[Path, ...]:
    """Find existing WAV variants, preserving defined priority without duplicates."""
    paths = []
    for relative in PREFERRED_SFX.get(event, ()):
        target = root / relative
        if target.is_file() and target not in paths:
            paths.append(target)
    return tuple(paths)


def preview_sfx_path(event: str, *, root: Path = OVERHAUL_DIR) -> Path | None:
    """Legacy-compatible first available preview WAV."""
    return next(iter(preview_sfx_paths(event, root=root)), None)


def preview_city_ambience_path(*, root: Path = OVERHAUL_DIR) -> Path | None:
    """Dedicated ambience layer, never an alternative soundtrack."""
    for relative in AMBIENCE_CITY_CANDIDATES:
        candidate = root / relative
        if candidate.is_file():
            return candidate
    return None


def preview_city_short_cue_path(*, root: Path = OVERHAUL_DIR) -> Path | None:
    target = root / CITY_SHORT_CUE
    return target if target.is_file() else None
