from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from game.gamestate import GameState

DEFAULT_SAVE_PATH = Path("savegame.json")


@dataclass(frozen=True)
class SaveSystemResult:
    ok: bool
    message: str


class SaveSystem:
    """Small save-slot service for JSON campaign persistence."""

    @staticmethod
    def save_game(game_state: GameState, path: Path | str = DEFAULT_SAVE_PATH) -> SaveSystemResult:
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        game_state.save(str(save_path))
        return SaveSystemResult(True, f"Campaign saved to {save_path}.")

    @staticmethod
    def load_game(path: Path | str = DEFAULT_SAVE_PATH) -> tuple[GameState | None, SaveSystemResult]:
        save_path = Path(path)
        if not save_path.exists():
            return None, SaveSystemResult(False, f"No save file at {save_path}.")
        game_state = GameState.load(str(save_path))
        return game_state, SaveSystemResult(True, f"Campaign loaded from {save_path}.")
