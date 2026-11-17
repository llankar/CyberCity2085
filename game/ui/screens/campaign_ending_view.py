"""Final campaign epilogue presentation."""

from __future__ import annotations

import arcade

from game.ui.theme.colors import colors


def build_ending_summary(game_state) -> dict:
    """Return a render-independent ending payload for tests and other clients."""

    ending = game_state.campaign.ending
    if ending is None:
        return {}
    return {
        "outcome_id": ending.outcome_id,
        "title": ending.title,
        "summary": ending.summary,
        "world_lines": list(ending.world_lines),
        "agent_epilogues": list(ending.agent_epilogues),
        "resolved_day": ending.resolved_day,
        "continue_action": "TitleView",
    }


class CampaignEndingView(arcade.View):
    """A restrained finale focused on consequences and remembered agents."""

    def __init__(self, game_state) -> None:
        super().__init__()
        self.game_state = game_state
        self.summary = build_ending_summary(game_state)
        self._elapsed = 0.0

    def on_show_view(self) -> None:
        arcade.set_background_color(colors.surface_elevated)
        from game.audio import SoundManager
        from game.ui.screens.settings_screen import load_settings

        music = SoundManager.get()
        music.configure_from_settings(load_settings())
        music.play_music("music_ending")

    def on_update(self, delta_time: float) -> None:
        self._elapsed += delta_time
        if hasattr(self, "_visual_deck"):
            self._visual_deck.update(delta_time)

    def on_draw(self):
        self.clear()
        if not hasattr(self, "_visual_deck"):
            from game.ui.components.utilities.reports import ReportDeck

            self._visual_deck = ReportDeck()
        self._elapsed = getattr(self, "_elapsed", 0.0)
        self._visual_deck.ending(self)

    def on_mouse_motion(self, x, y, dx, dy):
        if hasattr(self, "_visual_deck"):
            self._visual_deck.motion(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if hasattr(self, "_visual_deck"):
            for name, (_, _, rect) in self._visual_deck.capacities.items():
                if rect.contains(x, y):
                    self._visual_deck.turn_page(name, -1 if scroll_y > 0 else 1)
                    break

    def on_key_press(self, key, modifiers) -> None:
        if hasattr(self, "_visual_deck") and key in (
            arcade.key.TAB,
            arcade.key.UP,
            arcade.key.DOWN,
            arcade.key.SPACE,
        ):
            result = self._visual_deck.keyboard(key)
            if result:
                if (
                    result is not True
                    and not self._visual_deck.activate(result)
                    and result.action == "continue"
                ):
                    self._return_to_title()
                return
        if key in (
            arcade.key.RETURN,
            arcade.key.ENTER,
            arcade.key.SPACE,
            arcade.key.ESCAPE,
        ):
            self._return_to_title()

    def on_mouse_press(self, x, y, button, modifiers):
        for hit in self._hits:
            if hit.contains(x, y):
                if not self._visual_deck.activate(hit):
                    self._return_to_title()
                return

    def _return_to_title(self) -> None:
        from game.ui.screens.title_screen import TitleView

        self.window.show_view(TitleView())
