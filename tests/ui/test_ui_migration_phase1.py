from game.ui.command_deck import build_command_deck_layout
from game.ui.screens.command_deck.layout import build_command_deck_layout as migrated_build_layout


def test_command_deck_wrapper_matches_migrated_module() -> None:
    assert build_command_deck_layout(1280, 720) == migrated_build_layout(1280, 720)
