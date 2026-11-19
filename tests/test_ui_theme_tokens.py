from game.ui.command_center import build_command_center_layout
from game.ui.command_deck import build_command_deck_layout
from game.ui.room_interaction import expanded_room_rect, layout_action_buttons, RoomAction
from game.ui.theme import spacing, typography


def test_typography_hierarchy_ordered() -> None:
    assert typography.screen_title > typography.panel_title > typography.body_secondary > typography.meta


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


def test_management_commands_use_wide_cards_and_wrap_without_overflow() -> None:
    actions = [RoomAction(str(index), "city", f"Command {index}") for index in range(11)]

    buttons = layout_action_buttons(1280, 720, actions)

    assert all(button.rect.width > button.rect.height for button in buttons)
    assert len({button.rect.bottom for button in buttons}) == 2
    assert min(button.rect.left for button in buttons) >= spacing.xl
    assert max(button.rect.right for button in buttons) <= 1280 - spacing.xl
