"""Sound manager — loads synthesised WAV files and plays them via Arcade's audio API.

Usage:
    from game.audio import SoundManager
    sm = SoundManager.get()
    sm.configure(enabled=True, sfx_volume=0.8, music_volume=0.4, camera_shake=True)
    sm.play("sfx_fire")
    sm.play_music("music_battle", loop=True)
    sm.stop_music()

All methods are no-ops when audio is disabled or the WAV file is absent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

_SFX_DIR   = Path("assets/audio/sfx")
_MUSIC_DIR = Path("assets/audio/music")

_SFX_NAMES = [
    "sfx_fire", "sfx_melee", "sfx_psi", "sfx_hit", "sfx_miss",
    "sfx_death", "sfx_overwatch", "sfx_move", "sfx_turn_player",
    "sfx_turn_enemy", "sfx_victory", "sfx_defeat", "sfx_ui_click",
    "sfx_deploy", "sfx_reinforce", "sfx_stun", "sfx_bleed",
    "sfx_intel_reveal", "sfx_act_advance",
]

_MUSIC_NAMES = ["music_battle", "music_briefing", "music_debrief"]


class SoundManager:
    """Global singleton audio manager. Safe to call before Arcade window exists."""

    _instance: "SoundManager | None" = None

    @classmethod
    def get(cls) -> "SoundManager":
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def __init__(self) -> None:
        self._sfx:    dict[str, Any] = {}
        self._music:  dict[str, Any] = {}
        self._music_player: Any = None
        self._current_music: str | None = None
        self._enabled: bool = True
        self._sfx_vol: float = 0.80
        self._music_vol: float = 0.42
        self.camera_shake: bool = True
        self._loaded = False

    # ── Public API ────────────────────────────────────────────────────────────

    def ensure_loaded(self) -> None:
        """Load all sounds. Must be called after an Arcade window exists."""
        if self._loaded:
            return
        self._loaded = True
        self._load()

    def configure(
        self,
        *,
        enabled: bool | None = None,
        sfx_volume: float | None = None,
        music_volume: float | None = None,
        camera_shake: bool | None = None,
    ) -> None:
        if enabled is not None:
            self._enabled = enabled
        if sfx_volume is not None:
            self._sfx_vol = max(0.0, min(1.0, sfx_volume))
        if music_volume is not None:
            self._music_vol = max(0.0, min(1.0, music_volume))
        if camera_shake is not None:
            self.camera_shake = camera_shake
        # Update live music volume if playing
        if self._music_player is not None:
            try:
                self._music_player.volume = self._music_vol if self._enabled else 0.0
            except Exception:
                pass

    def configure_from_settings(self, settings: Any) -> None:
        """Accept a SettingsState object (audio_enabled, sfx_volume, music_volume, camera_shake)."""
        self.configure(
            enabled=getattr(settings, "audio_enabled", True),
            sfx_volume=getattr(settings, "sfx_volume", 80) / 100.0,
            music_volume=getattr(settings, "music_volume", 70) / 100.0,
            camera_shake=getattr(settings, "camera_shake", True),
        )

    def play(self, name: str, volume_scale: float = 1.0) -> None:
        """Play a named SFX (sfx_fire, sfx_hit, …). Silent on any error."""
        if not self._enabled:
            return
        self.ensure_loaded()
        sound = self._sfx.get(name)
        if sound is None:
            return
        try:
            import arcade
            arcade.play_sound(sound, volume=self._sfx_vol * volume_scale)
        except Exception:
            pass

    def play_music(self, name: str, loop: bool = True) -> None:
        """Start looping background music. Stops current track first."""
        if name == self._current_music:
            return
        self.stop_music()
        if not self._enabled:
            return
        self.ensure_loaded()
        sound = self._music.get(name)
        if sound is None:
            return
        try:
            import arcade
            self._music_player = arcade.play_sound(
                sound, volume=self._music_vol, loop=loop
            )
            self._current_music = name
        except Exception:
            pass

    def stop_music(self) -> None:
        if self._music_player is None:
            return
        try:
            import arcade
            arcade.stop_sound(self._music_player)
        except Exception:
            pass
        self._music_player = None
        self._current_music = None

    # ── Internals ─────────────────────────────────────────────────────────────

    def _load(self) -> None:
        try:
            import arcade
        except ImportError:
            return
        for name in _SFX_NAMES:
            path = _SFX_DIR / f"{name}.wav"
            if path.exists():
                try:
                    self._sfx[name] = arcade.load_sound(str(path))
                except Exception:
                    pass
        for name in _MUSIC_NAMES:
            path = _MUSIC_DIR / f"{name}.wav"
            if path.exists():
                try:
                    self._music[name] = arcade.load_sound(str(path), streaming=True)
                except Exception:
                    pass
