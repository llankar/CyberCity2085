"""Shared Arcade view base classes."""

import arcade

from game.gamestate import GameState


class GameView(arcade.View):
    """Arcade view base that receives the shared persistent state explicitly."""

    def __init__(self, game_state: GameState | None = None):
        super().__init__()
        self.game_state = game_state or GameState()
