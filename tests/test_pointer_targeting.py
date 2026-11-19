from types import SimpleNamespace

from game.combat.targeting import target_index_at_point


def target(position, *, health=10, visible=True):
    return SimpleNamespace(position=position, health=health, visible=visible)


def test_pointer_selection_uses_camera_pan_and_rendered_shake_offset():
    candidates=[target((320,192)),target((640,320))]
    assert target_index_at_point(candidates,256,160,camera_offset=(64,32))==0
    assert target_index_at_point(candidates,256,160,camera_offset=(320,0)) is None


def test_nearest_visible_living_candidate_is_selected_with_stable_ties():
    candidates=[target((96,96),health=0),target((96,96),visible=False),target((112,96)),target((80,96))]
    assert target_index_at_point(candidates,96,96)==2
    assert target_index_at_point(candidates,400,400) is None
