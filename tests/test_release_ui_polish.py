from game.ui.new_game_options import DIFFICULTY_LABELS
from game.ui.screens.facility import room_directory_entries


def test_hub_directory_exposes_every_room_with_shortcut():
    entries = room_directory_entries(1920, 1000, "hub")

    assert [room.key for room, _ in entries] == [
        "command", "city", "squad", "assets", "research", "intel"
    ]
    assert [label.split()[0] for _, label in entries] == [
        "F1", "F2", "F3", "F4", "F5", "F6"
    ]


def test_difficulty_descriptions_are_wrapped_inside_cards():
    assert all("\n" in description for _, description, _ in DIFFICULTY_LABELS)
    assert max(len(line) for _, description, _ in DIFFICULTY_LABELS for line in description.splitlines()) <= 21
