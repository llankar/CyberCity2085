"""Live cinematic main menu. Presentation is separate from campaign actions."""

from __future__ import annotations
from pathlib import Path
import arcade
from game.ui.layouts.title_menu import title_layout

_MENU_ITEMS = [
    ("NEW GAME", "new_game"),
    ("CONTINUE", "continue"),
    ("SETTINGS", "settings"),
    ("QUIT", "quit"),
]
_TITLE_BACKGROUND_ASSET = Path("assets/ui/title_background.png")
_TITLE_VISUAL_ASSET = Path("assets/ui/title/city_visual_2.png")


class TitleView(arcade.View):
    menu_items = _MENU_ITEMS

    def __init__(self):
        super().__init__()
        self._shown = False
        self._elapsed = 0.0
        self._hover_index = 0
        self._background_texture = None
        self._buttons = []
        self._renderer = None
        self._continue_available = False
        self._continue_path = None
        self._reduced_motion = False
        self._focus_amounts = [1.0, 0.0, 0.0, 0.0]
        self._message = ""

    def on_show_view(self):
        arcade.set_background_color((2, 8, 15))
        self._background_texture = self._load_background_texture()
        from game.audio import SoundManager
        from game.ui.screens.settings_screen import load_settings

        settings = load_settings()
        self._reduced_motion = getattr(settings, "reduced_motion", False)
        self._refresh_continue()
        self._shown = True
        self._buttons = self._build_buttons(self.window.width, self.window.height)
        music = SoundManager.get()
        music.configure_from_settings(settings)
        music.play_music("music_title")

    def _refresh_continue(self):
        from game.persistence import SaveSystem
        from game.persistence.save_system import SAVE_SLOT_COUNT

        paths = [SaveSystem.slot_path(i) for i in range(1, SAVE_SLOT_COUNT + 1)]
        from game.combat.checkpoints import latest_combat_checkpoint
        recovery=latest_combat_checkpoint()
        if recovery is not None:paths.append(recovery)
        existing = []
        for path in paths:
            try:
                if path.is_file():
                    existing.append((path.stat().st_mtime_ns, path))
            except OSError:
                continue
        self._continue_path = (
            max(existing, key=lambda pair: pair[0])[1] if existing else None
        )
        self._continue_available = self._continue_path is not None
        if not self._shown:
            self._hover_index = 1 if self._continue_available else 0
        elif self._hover_index == 1 and not self._continue_available:
            self._hover_index = 0

    def _load_background_texture(self):
        from game.ui.panels import _load_texture_once

        for path in (_TITLE_VISUAL_ASSET, _TITLE_BACKGROUND_ASSET):
            texture = _load_texture_once(str(path))
            if texture is not None:
                return texture
        return None

    def _build_buttons(self, w, h):
        layout = title_layout(w, h)
        return [
            (r.left, r.bottom, r.right, r.top, label, key)
            for r, (label, key) in zip(layout.buttons, _MENU_ITEMS)
        ]

    def on_draw(self):
        self.clear()
        self._buttons = self._build_buttons(self.window.width, self.window.height)
        if self._renderer is None:
            from game.ui.components.title_menu import TitleMenuRenderer

            self._renderer = TitleMenuRenderer()
        self._renderer.draw(self, self.window.width, self.window.height)

    def on_update(self, delta_time):
        if not self._reduced_motion:
            self._elapsed += max(0, min(delta_time, 0.1))
        for i, amount in enumerate(self._focus_amounts):
            target = 1.0 if i == self._hover_index else 0.0
            self._focus_amounts[i] = (
                target
                if self._reduced_motion
                else amount + (target - amount) * min(1, delta_time * 12)
            )

    def _index_at(self, x, y):
        for i, (l, b, r, t, *_) in enumerate(self._buttons):
            if l <= x <= r and b <= y <= t:
                return i
        return None

    def on_mouse_motion(self, x, y, _dx, _dy):
        index = self._index_at(x, y)
        if index is not None and (index != 1 or self._continue_available):
            self._hover_index = index

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if title_layout(self.window.width, self.window.height).motion.contains(x, y):
            self._toggle_motion()
            return
        index = self._index_at(x, y)
        if index is not None:
            self._activate(_MENU_ITEMS[index][1])

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.SPACE):
            self._activate(_MENU_ITEMS[self._hover_index][1])
        elif key == arcade.key.ESCAPE:
            self._activate("quit")
        elif key == getattr(arcade.key, "M", 77):
            self._toggle_motion()
        elif key in (arcade.key.UP, arcade.key.W, arcade.key.DOWN, arcade.key.S):
            step = -1 if key in (arcade.key.UP, arcade.key.W) else 1
            index = (self._hover_index + step) % len(_MENU_ITEMS)
            while index == 1 and not self._continue_available:
                index = (index + step) % len(_MENU_ITEMS)
            self._hover_index = index

    def _toggle_motion(self):
        from game.ui.screens.settings_screen import load_settings, save_settings

        settings = load_settings()
        self._reduced_motion = not self._reduced_motion
        settings.reduced_motion = self._reduced_motion
        save_settings(settings)

    def _activate(self, key):
        if key == "quit":
            arcade.exit()
            return
        if key == "new_game":
            from game.ui.screens.new_game_screen import NewGameSetupView

            self.window.show_view(NewGameSetupView())
            return
        if key == "continue":
            if not self._continue_available:
                self._message = "NO SAVED CAMPAIGN — START A NEW GAME"
                return
            from game.persistence import SaveSystem

            try:
                if self._continue_path.name in {"campaign_before.json","campaign_after.json"}:
                    from game.combat.checkpoints import load_combat_checkpoint
                    loaded,_session_id=load_combat_checkpoint(self._continue_path)
                else:
                    loaded, _result = SaveSystem.load_game(self._continue_path)
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                loaded = None
            if loaded is not None:
                self._go_management(loaded)
            else:
                self._message = "SAVE UNAVAILABLE — NO CAMPAIGN WAS LOADED"
                self._continue_available = False
                self._hover_index = 0
            return
        if key == "settings":
            from game.ui.screens.settings_screen import SettingsView

            self.window.show_view(SettingsView(return_view=self))

    def _go_management(self, game_state):
        from game.ui.screens.combat_recovery import show_combat_recovery
        try:
            if show_combat_recovery(self.window,game_state):return
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            self._message = "COMBAT RECOVERY INVALID — NO REWARD WAS REAPPLIED"
            return
        from game.ui.screens.management_screen import ManagementView

        view = ManagementView(game_state)
        view.setup()
        self.window.show_view(view)
