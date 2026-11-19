"""Preview routing for the seven user-supplied CyberCity 2085 audio assets.

All WAVs are optional: a checkout without downloaded media keeps its legacy
sound effects. These user-supplied samples are *not* listening-approved.
Do not move or change the music catalog.
"""
from __future__ import annotations

from pathlib import Path

OVERHAUL_DIR = Path("assets/audio/overhaul")

# These are explicitly exploratory defaults; there is no metadata yet to
# distinguish all weapon and surface types at existing call sites.
PREFERRED_SFX: dict[str, tuple[str, ...]] = {
    "sfx_fire": ("weapons/fire_assault_01.wav",),
    "sfx_fire_assault": ("weapons/fire_assault_01.wav",),
    "sfx_fire_pistol": ("weapons/fire_pistol_01.wav",),
    "sfx_hit": ("combat/impact_metal_01.wav",),
    "sfx_hit_metal": ("combat/impact_metal_01.wav",),
    "sfx_move": ("movement/step_concrete_01.wav",),
    "sfx_move_concrete": ("movement/step_concrete_01.wav",),
    "sfx_ui_click": ("ui/ui_click_01.wav",),
    "sfx_city_short": ("ambience/ambience_city_short_candidate_02.wav",),
}

AMBIENCE_CITY = "ambience/ambience_city_loop_candidate_01.wav"
CITY_SHORT_CUE = "ambience/ambience_city_short_candidate_02.wav"


def preview_sfx_path(event: str, *, root: Path = OVERHAUL_DIR) -> Path | None:
    """Return installed preview WAV for a known event; otherwise None."""
    for relative in PREFERRED_SFX.get(event, ()):
        target = root / relative
        if target.is_file():
            return target
    return None


def preview_city_ambience_path(*, root: Path = OVERHAUL_DIR) -> Path | None:
    """Optional city ambience WAV; never a substitute for background music."""
    target = root / AMBIENCE_CITY
    return target if target.is_file() else None


def preview_city_short_cue_path(*, root: Path = OVERHAUL_DIR) -> Path | None:
    """Unreviewed short city cue (may be a UI sound; use only as a preview)."""
    target = root / CITY_SHORT_CUE
    return target if target.is_file() else None
