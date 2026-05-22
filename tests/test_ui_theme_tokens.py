from game.ui.command_center import build_command_center_layout
from game.ui.command_deck import build_command_deck_layout
from game.ui.room_interaction import expanded_room_rect, layout_action_buttons, RoomAction
from game.ui.theme import spacing, typography


def test_typography_hierarchy_ordered() -> None:
    assert typography.title > typography.section > typography.meta


def test_layouts_keep_tokenized_spacing() -> None:
    center_panels = build_command_center_layout(1280, 720, "corp")
    deck_panels = build_command_deck_layout(1280, 720)
    assert center_panels[0].left == spacing.md + 2
    assert deck_panels[0].left == spacing.md


def test_expanded_room_and_actions_use_spacing_tokens() -> None:
    expanded = expanded_room_rect(1280, 720)
    assert expanded.left >= spacing.lg
    buttons = layout_action_buttons(1280, 720, [RoomAction("a", "city"), RoomAction("b", "city")])
    assert buttons[1].rect.left - buttons[0].rect.right >= spacing.md
