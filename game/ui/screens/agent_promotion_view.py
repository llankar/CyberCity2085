"""Agent Promotion Screen — shown between battle and debrief when agents level up.

Displays each promoted agent's portrait, old→new level, and stat gains.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import arcade

if TYPE_CHECKING:
    from game.gamestate import GameState
    from game.character import Character


@dataclass
class PromotionRecord:
    """Snapshot of one agent's level-up event."""

    character: "Character"
    old_level: int
    new_level: int
    portrait_path: str | None = None


class AgentPromotionView(arcade.View):
    """Sequenced promotion screen — shows one agent per page, CONTINUE advances."""

    def __init__(
        self,
        game_state: "GameState",
        promotions: list[PromotionRecord],
        next_view: arcade.View,
    ) -> None:
        super().__init__()
        self.game_state = game_state
        self.promotions = promotions
        self.next_view = next_view
        self._index = 0
        self._elapsed = 0.0
        self._portrait_cache: dict[str, arcade.Texture | None] = {}
        self._continue_rect: tuple[int, int, int, int] | None = None

    def on_show_view(self) -> None:
        arcade.set_background_color((4, 10, 18))
        self._load_portraits()
        from game.audio import SoundManager

        SoundManager.get().play("sfx_victory", 0.6)

    def _load_portraits(self) -> None:
        for rec in self.promotions:
            if rec.portrait_path and rec.portrait_path not in self._portrait_cache:
                try:
                    self._portrait_cache[rec.portrait_path] = arcade.load_texture(
                        rec.portrait_path
                    )
                except Exception:
                    self._portrait_cache[rec.portrait_path] = None

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
        self._visual_deck.promotion(self)

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
                    self._advance()
                return
        if key in (
            arcade.key.RETURN,
            arcade.key.ENTER,
            arcade.key.SPACE,
            arcade.key.ESCAPE,
        ):
            self._advance()

    def on_mouse_press(self, x, y, button, modifiers):
        for hit in getattr(self, "_hits", []):
            if hit.contains(x, y):
                if not self._visual_deck.activate(hit) and hit.action == "continue":
                    self._advance()
                return

    def _advance(self) -> None:
        self._index += 1
        self._elapsed = 0.0
        if self._index >= len(self.promotions):
            from game.audio import SoundManager

            SoundManager.get().play("sfx_deploy", 0.5)
            self.window.show_view(self.next_view)
        else:
            from game.audio import SoundManager

            SoundManager.get().play("sfx_victory", 0.5)
