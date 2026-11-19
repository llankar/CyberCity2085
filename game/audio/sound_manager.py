"""Sound manager — plays WAV effects and the contextual MP3 soundtrack.

Usage:
    from game.audio import SoundManager
    sm = SoundManager.get()
    sm.configure(enabled=True, sfx_volume=0.8, music_volume=0.4, camera_shake=True)
    sm.play("sfx_fire")
    sm.play_music("music_battle", loop=True)
    sm.stop_music()

All methods are no-ops when audio is disabled or the selected file is absent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from .music_catalog import MUSIC_TRACKS, music_path
from .overhaul_assets import preview_sfx_paths, preview_city_ambience_path

_MUSIC_DIR = Path("assets/audio/music")

_SFX_NAMES = [
    "sfx_fire", "sfx_melee", "sfx_psi", "sfx_hit", "sfx_miss",
    "sfx_death", "sfx_overwatch", "sfx_move", "sfx_turn_player",
    "sfx_turn_enemy", "sfx_victory", "sfx_defeat", "sfx_ui_click",
    "sfx_deploy", "sfx_reinforce", "sfx_stun", "sfx_bleed",
    "sfx_intel_reveal", "sfx_act_advance", "sfx_fire_pistol", "sfx_city_short",
    "sfx_fire_laser", "sfx_hit_metal", "sfx_hit_glass", "sfx_hit_organic",
    "sfx_move_concrete", "sfx_move_metal", "sfx_move_robot",
    "sfx_shield", "sfx_terminal", "sfx_door_open", "sfx_explosion_small",
    "sfx_ui_confirm", "sfx_ui_refuse",
]

_MUSIC_NAMES = list(MUSIC_TRACKS)


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
        self._sfx_variants: dict[str, list[Any]] = {}
        self._sfx_next_variant: dict[str, int] = {}
        self._music:  dict[str, Any] = {}
        self._music_paths: dict[str, Path] = {}
        self._music_player: Any = None
        self._ambience_player: Any = None
        self._ambience_source: Any = None
        self._current_music: str | None = None
        self._current_path: str | None = None
        self._music_positions: dict[str, float] = {}
        self._external_music = False
        self._view_transition_depth = 0
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
        if not self._enabled:
            self.stop_ambience()
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
        variants = self._sfx_variants.get(name)
        if variants:
            idx = self._sfx_next_variant.get(name, 0) % len(variants)
            self._sfx_next_variant[name] = idx + 1
            sound = variants[idx]
        else:
            sound = self._sfx.get(name)
        if sound is None:
            return
        try:
            import arcade
            arcade.play_sound(sound, volume=self._sfx_vol * volume_scale)
        except Exception:
            pass

    def play_city_ambience(self, volume_scale: float = 0.10) -> None:
        """Low-volume urban environmental bed; no music track is changed."""
        if not self._enabled or self._ambience_player is not None:
            return
        path = preview_city_ambience_path()
        if path is None:
            return
        try:
            import arcade
            source = arcade.load_sound(str(path), streaming=False)
            player = arcade.play_sound(
                source, volume=max(0.0, min(1.0, self._sfx_vol * volume_scale)),
                loop=True,
            )
            if player is not None:
                self._ambience_source = source
                self._ambience_player = player
        except Exception:
            pass

    def stop_ambience(self) -> None:
        """Stop a dedicated ambience player without touching the soundtrack."""
        player = self._ambience_player
        self._ambience_player = None
        self._ambience_source = None
        if player is not None:
            try:
                import arcade
                arcade.stop_sound(player)
            except Exception:
                pass

    @staticmethod
    def _track_id(path: str | Path) -> str:
        import os
        return os.path.normcase(str(Path(path).resolve()))

    def music_position_for(self, path: str | Path) -> float:
        track = self._track_id(path)
        if track == self._current_path and self._music_player is not None:
            try:
                return max(0.0, float(self._music_player.time))
            except (AttributeError, TypeError, ValueError):
                pass
        return self._music_positions.get(track, 0.0)

    def remember_music_position(self, path: str | Path, position: float) -> None:
        import math
        if not math.isfinite(position) or position < 0:
            return
        track = self._track_id(path)
        self._music_positions[track] = position
        if track == self._current_path and self._music_player is not None:
            try:
                duration = getattr(getattr(self._music_player, "source", None), "duration", None)
                self._music_player.seek(position % duration if duration and duration > 0 else position)
            except Exception:
                pass

    def begin_view_transition(self) -> None:
        self._view_transition_depth += 1
        self.pause_music()

    def end_view_transition(self) -> None:
        self._view_transition_depth = max(0, self._view_transition_depth - 1)
        if self._view_transition_depth == 0:
            self.resume_music()

    def pause_music(self, *, external: bool = False) -> None:
        if external:
            self._external_music = True
        if self._music_player is None:
            return
        if self._current_path:
            self._music_positions[self._current_path] = self.music_position_for(self._current_path)
        try:
            self._music_player.pause()
        except Exception:
            pass

    def release_external_music(self) -> None:
        """Reclaim transport after the external engine stops or launch fails."""
        self._external_music = False
        self.resume_music()

    def resume_music(self) -> None:
        if not self._enabled or self._external_music or self._view_transition_depth or self._music_player is None:
            return
        try:
            if not self._music_player.playing:
                self._music_player.play()
        except Exception:
            pass

    def play_music(self, name: str, loop: bool = True) -> None:
        """Reuse the same physical track across UI aliases and resume its transport."""
        if not self._enabled:
            return
        self._external_music = False
        self.ensure_loaded()
        requested = self._music_paths.get(name)
        same_file = requested is not None and self._track_id(requested) == self._current_path
        if self._music_player is not None and (name == self._current_music or same_file):
            self._current_music = name
            self.resume_music()
            if name == "music_management":
                self.play_city_ambience()
            else:
                self.stop_ambience()
            return
        self.stop_music()
        selected_path = None
        if requested is not None:
            import arcade
            self._music.clear()
            for path in [requested]:
                if not path.is_file():
                    continue
                try:
                    self._music[name] = arcade.load_sound(str(path), streaming=False)
                    selected_path = path
                    break
                except Exception:
                    continue
        sound = self._music.get(name)
        if sound is None:
            return
        try:
            import arcade
            player = arcade.play_sound(sound, volume=self._music_vol, loop=loop)
            if player is None:
                return
            self._music_player = player
            self._current_music = name
            if name == "music_management":
                self.play_city_ambience()
                self.play("sfx_city_short", volume_scale=0.18)
            self._current_path = self._track_id(selected_path) if selected_path else None
            position = self._music_positions.get(self._current_path, 0.0)
            if position > 0:
                duration = getattr(getattr(player, "source", None), "duration", None)
                player.seek(position % duration if duration and duration > 0 else position)
            if self._view_transition_depth:
                player.pause()
        except Exception:
            pass

    def stop_music(self) -> None:
        """Release playback while retaining the track bookmark for later UI visits."""
        self.stop_ambience()
        if self._music_player is not None:
            self.pause_music()
            try:
                import arcade
                arcade.stop_sound(self._music_player)
            except Exception:
                pass
        self._music_player = None
        self._current_music = None
        self._current_path = None

    # ── Internals ─────────────────────────────────────────────────────────────

    def _load(self) -> None:
        try:
            import arcade
        except ImportError:
            return
        for name in _SFX_NAMES:
            # Decode only actual locally installed WAVs; never attempt manifest placeholders.
            paths = list(preview_sfx_paths(name))
            loaded = []
            for path in paths:
                try:
                    loaded.append(arcade.load_sound(str(path)))
                except Exception:
                    continue
            if loaded:
                self._sfx[name] = loaded[0]
                self._sfx_variants[name] = loaded
        for name in _MUSIC_NAMES:
            path = music_path(name)
            if path is not None:
                self._music_paths[name] = path
