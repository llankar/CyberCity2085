"""CyberCity 2085 — Settings Screen.

Accessible from the title menu.  Allows toggling display, audio, and
accessibility options that are stored in a persistent SettingsState
object written to a small JSON file next to save slots.

No GameState dependency — settings apply globally.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

import arcade

from game.ui.palette import BACKGROUND
from game.ui.theme.typography import normalize_text_size, set_text_size

# ── Settings file path ────────────────────────────────────────────────────────

_SETTINGS_PATH = os.path.join("saves", "settings.json")
_TEXT_SIZE_OPTIONS = ["small", "medium", "large"]
_TEXT_SIZE_LABELS = ["Small", "Medium", "Large"]


@dataclass
class SettingsState:
    fullscreen: bool = False
    audio_enabled: bool = True
    music_volume: int = 70  # 0-100
    sfx_volume: int = 80  # 0-100
    high_contrast: bool = False
    show_grid: bool = True
    camera_shake: bool = True
    resolution_index: int = 1  # index into _RESOLUTIONS
    display_index: int = 0  # index into available screens
    text_size: str = "medium"
    godot_bin_path: str = ""
    extra_flags: dict = field(default_factory=dict)
    reduced_motion: bool = False  # Main-menu atmospheric animation


_RESOLUTIONS: list[tuple[int, int]] = [
    (1280, 720),
    (1920, 1000),
    (1920, 1080),
    (2560, 1440),
]


def load_settings() -> SettingsState:
    try:
        with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        s = SettingsState()
        s.fullscreen = bool(data.get("fullscreen", s.fullscreen))
        s.audio_enabled = bool(data.get("audio_enabled", s.audio_enabled))
        s.music_volume = int(data.get("music_volume", s.music_volume))
        s.sfx_volume = int(data.get("sfx_volume", s.sfx_volume))
        s.high_contrast = bool(data.get("high_contrast", s.high_contrast))
        s.show_grid = bool(data.get("show_grid", s.show_grid))
        s.camera_shake = bool(data.get("camera_shake", s.camera_shake))
        s.reduced_motion = bool(data.get("reduced_motion", s.reduced_motion))
        if isinstance(data.get("extra_flags"), dict):
            s.extra_flags = dict(data["extra_flags"])
        s.resolution_index = int(data.get("resolution_index", s.resolution_index))
        s.display_index = int(data.get("display_index", s.display_index))
        s.text_size = normalize_text_size(data.get("text_size", s.text_size))
        raw_godot_path = data.get("godot_bin_path", s.godot_bin_path)
        s.godot_bin_path = str(raw_godot_path or "").strip()
        set_text_size(s.text_size)
        return s
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        s = SettingsState()
        set_text_size(s.text_size)
        return s


def save_settings(s: SettingsState) -> None:
    os.makedirs("saves", exist_ok=True)
    s.text_size = normalize_text_size(s.text_size)
    s.godot_bin_path = s.godot_bin_path.strip()
    set_text_size(s.text_size)
    with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(s), f, indent=2)


def apply_settings(window, s: SettingsState) -> None:
    """Apply the saved preferences identically at startup and from Apply/Save."""
    set_text_size(s.text_size)
    from game.audio import SoundManager

    SoundManager.get().configure_from_settings(s)
    try:
        screens = _available_screens()
        screen = (
            screens[s.display_index] if 0 <= s.display_index < len(screens) else None
        )
        rw, rh = _RESOLUTIONS[s.resolution_index % len(_RESOLUTIONS)]
        if screen is not None:
            try:
                rw = min(rw, max(640, int(screen.width) - 80))
                rh = min(rh, max(480, int(screen.height) - 80))
            except Exception:
                pass
        if s.fullscreen:
            window.set_fullscreen(True, screen=screen)
        else:
            window.set_fullscreen(False)
            window.set_size(rw, rh)
            if screen is not None:
                try:
                    x = int(
                        getattr(screen, "x", 0) + max(0, (int(screen.width) - rw) // 2)
                    )
                    y = int(
                        getattr(screen, "y", 0) + max(0, (int(screen.height) - rh) // 2)
                    )
                    window.set_location(x, y)
                except Exception:
                    pass
    except Exception:
        pass  # Not all platforms support dynamic resize


def _persist_godot_bin_path(godot_bin_path: str) -> None:
    """Save only the Godot executable path without committing unsaved UI changes."""
    persisted = load_settings()
    persisted.godot_bin_path = str(godot_bin_path or "").strip()
    save_settings(persisted)


# ── Layout helpers ────────────────────────────────────────────────────────────


def _in(l: int, b: int, r: int, t: int, x: int, y: int) -> bool:
    return l <= x <= r and b <= y <= t


def _available_screens() -> list[object]:
    try:
        screens = list(arcade.get_screens())
    except Exception:
        screens = []
    return screens or [None]


def _screen_label(screen: object | None, index: int) -> str:
    if screen is None:
        return "Primary display"
    name = ""
    try:
        name = str(screen.get_monitor_name() or "").strip()
    except Exception:
        name = ""
    if not name:
        try:
            name = str(screen.get_device_name() or "").strip()
        except Exception:
            name = ""
    prefix = name if name else f"Display {index + 1}"
    try:
        size = f"{int(screen.width)}x{int(screen.height)}"
    except Exception:
        size = "Unknown size"
    return f"{prefix}  ({size})"


def _shorten_path(value: str, limit: int = 44) -> str:
    value = " ".join(str(value).split()).strip()
    if len(value) <= limit:
        return value
    keep = max(8, limit - 3)
    head = max(4, keep // 2)
    tail = max(4, keep - head)
    return f"{value[:head]}...{value[-tail:]}"


def _browse_for_godot_executable(current_path: str = "") -> str | None:
    """Open a native file picker and return the selected Godot executable path."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None

    try:
        start_dir = (
            Path(current_path).expanduser().parent if current_path else Path.cwd()
        )
    except Exception:
        start_dir = Path.cwd()

    root = tk.Tk()
    root.withdraw()
    try:
        filetypes = [("Executable files", "*.exe"), ("All files", "*.*")]
        selected = filedialog.askopenfilename(
            title="Select Godot executable",
            initialdir=str(start_dir),
            filetypes=filetypes,
        )
    finally:
        try:
            root.destroy()
        except Exception:
            pass
    return str(selected).strip() or None


# ── View ──────────────────────────────────────────────────────────────────────


class SettingsView(arcade.View):
    """Full-screen settings panel accessible from the title menu."""

    def __init__(self, return_view=None) -> None:
        super().__init__()
        self._return_view = return_view
        self._settings = load_settings()
        self._elapsed = 0.0
        self._message = ""
        self._msg_timer = 0.0
        # Hit rects for toggle buttons
        self._hits: list[tuple[int, int, int, int, str]] = []

    # ── Arcade lifecycle ──────────────────────────────────────────────────────

    def on_show_view(self) -> None:
        arcade.set_background_color(BACKGROUND)

    def on_update(self, dt: float) -> None:
        self._elapsed += dt
        if hasattr(self, "_visual_deck"):
            self._visual_deck.update(dt)
        if self._msg_timer > 0:
            self._msg_timer = max(0.0, self._msg_timer - dt)

    def on_draw(self) -> None:
        self.clear()
        if not hasattr(self, "_visual_deck"):
            from game.ui.components.utilities.settings import SettingsDeck

            self._visual_deck = SettingsDeck()
        self._visual_deck.draw(self)
        self._visual_hits = list(self._hits)
        self._hits = [
            (h.left, h.bottom, h.right, h.top, h.action) for h in self._visual_hits
        ]

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.ESCAPE:
            self._back()
        elif hasattr(self, "_visual_deck"):
            self._hits = self._visual_hits
            result = self._visual_deck.keyboard(key)
            if result and result is not True:
                if not self._visual_deck.activate(result):
                    self._handle(result.action)
            self._hits = [
                (h.left, h.bottom, h.right, h.top, h.action) for h in self._visual_hits
            ]

    def on_mouse_press(self, x: float, y: float, _button: int, _modifiers: int) -> None:
        xi, yi = int(x), int(y)
        for l, b, r, t, action in self._hits:
            if _in(l, b, r, t, xi, yi):
                self._handle(action)
                return

    def on_mouse_motion(self, x, y, dx, dy):
        if hasattr(self, "_visual_deck"):
            self._hits = self._visual_hits
            self._visual_deck.motion(x, y)
            self._hits = [
                (h.left, h.bottom, h.right, h.top, h.action) for h in self._visual_hits
            ]

    # ── Background ────────────────────────────────────────────────────────────

    # ── Main panel ────────────────────────────────────────────────────────────

    # ── Action handling ───────────────────────────────────────────────────────

    def _handle(self, action: str) -> None:
        s = self._settings
        if action == "back":
            self._back()
        elif action == "save_apply":
            self._apply_and_save()
        elif action == "toggle_fullscreen":
            s.fullscreen = not s.fullscreen
        elif action == "toggle_grid":
            s.show_grid = not s.show_grid
        elif action == "toggle_contrast":
            s.high_contrast = not s.high_contrast
        elif action == "toggle_audio":
            s.audio_enabled = not s.audio_enabled
        elif action == "toggle_motion":
            s.reduced_motion = not s.reduced_motion
        elif action == "toggle_shake":
            s.camera_shake = not s.camera_shake
        elif action == "text_prev":
            current = normalize_text_size(s.text_size)
            s.text_size = _TEXT_SIZE_OPTIONS[
                (_TEXT_SIZE_OPTIONS.index(current) - 1) % len(_TEXT_SIZE_OPTIONS)
            ]
        elif action == "text_next":
            current = normalize_text_size(s.text_size)
            s.text_size = _TEXT_SIZE_OPTIONS[
                (_TEXT_SIZE_OPTIONS.index(current) + 1) % len(_TEXT_SIZE_OPTIONS)
            ]
        elif action == "res_prev":
            s.resolution_index = (s.resolution_index - 1) % len(_RESOLUTIONS)
        elif action == "res_next":
            s.resolution_index = (s.resolution_index + 1) % len(_RESOLUTIONS)
        elif action == "screen_prev":
            s.display_index = (s.display_index - 1) % len(_available_screens())
        elif action == "screen_next":
            s.display_index = (s.display_index + 1) % len(_available_screens())
        elif action == "godot_bin_browse":
            selected = _browse_for_godot_executable(self._settings.godot_bin_path)
            if selected:
                s.godot_bin_path = selected
                _persist_godot_bin_path(s.godot_bin_path)
                self._message = "Godot executable selected."
                self._msg_timer = 2.0
        elif action == "godot_bin_clear":
            s.godot_bin_path = ""
            _persist_godot_bin_path(s.godot_bin_path)
            self._message = "Godot executable path cleared."
            self._msg_timer = 2.0

    def _apply_and_save(self) -> None:
        s = self._settings
        save_settings(s)
        apply_settings(self.window, s)
        self._message = "Settings saved."
        self._msg_timer = 2.5

    def _back(self) -> None:
        if self._return_view is not None:
            self.window.show_view(self._return_view)
            return
        from game.ui.screens.title_screen import TitleView

        self.window.show_view(TitleView())
