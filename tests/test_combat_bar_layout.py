import pytest

from game.combat_actions import CombatAction
from game.ui.combat_action_bar import combat_action_bar_rect, layout_combat_action_buttons, combat_action_at_point


@pytest.mark.parametrize("width",(960,1280,1920))
@pytest.mark.parametrize("count",(4,8,12))
def test_action_buttons_fit_without_overlap_and_keep_header_rows_free(width,count):
    actions=[CombatAction(str(i),"Action","combat_move") for i in range(count)]
    bar=combat_action_bar_rect(width)
    buttons=layout_combat_action_buttons(width,actions)
    for action,rect in buttons:
        assert bar.left<=rect.left<rect.right<=bar.right
        assert bar.bottom<=rect.bottom<rect.top<=bar.top-40
        assert combat_action_at_point(buttons,rect.center_x,rect.center_y) is action
    assert all(a.right<b.left for (_,a),(_,b) in zip(buttons,buttons[1:]))
