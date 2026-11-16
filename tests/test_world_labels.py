"""Crowded marker captions keep their consequences readable."""

from game.ui.components.combat.world_labels import place_caption
import pytest


def test_dense_captions_have_disjoint_boxes_and_stable_placement():
    anchors = [(100, 100, 180), (100, 100, 160), (110, 108, 220), (280, 100, 120)]
    occupied = []
    result = [place_caption(*anchor, occupied) for anchor in anchors]
    for i, a in enumerate(result):
        for b in result[i+1:]:
            assert a[2]+6 <= b[0] or b[2]+6 <= a[0] or a[3]+6 <= b[1] or b[3]+6 <= a[1]
    again = []
    assert result == [place_caption(*anchor, again) for anchor in anchors]


def test_distant_caption_keeps_requested_location():
    occupied = [(0, 0, 100, 20)]
    assert place_caption(300, 10, 100, occupied) == (250, 10, 350, 30)


def test_caption_escapes_reserved_objective_panel_and_nearby_hazard():
    occupied = [(78, 386, 428, 462), (360, 470, 500, 490)]
    a = place_caption(384, 394, 190, occupied)
    for b in occupied[:-1]:
        assert a[2]+6 <= b[0] or b[2]+6 <= a[0] or a[3]+6 <= b[1] or b[3]+6 <= a[1]


@pytest.mark.parametrize("size", [(960,640), (1280,720), (1920,1000)])
@pytest.mark.parametrize("pan", [(0,0), (64,-146), (-80,60)])
def test_edge_captions_stay_in_camera_view_and_clear_reserved_resources(size, pan):
    w,h = size
    dx,dy = pan
    bounds = (dx+8,dy+218,dx+w-8,dy+h-42)
    occupied = [(dx+14,dy+h-92,dx+534,dy+h-46)]
    for x,y in ((dx-100,dy+h+50), (dx+w+100,dy+h), (dx,dy), (dx+w,dy), (dx+280,dy+h-80)):
        box = place_caption(x,y,180,occupied,bounds=bounds)
        assert box is not None
        assert bounds[0] <= box[0] < box[2] <= bounds[2]
        assert bounds[1] <= box[1] < box[3] <= bounds[3]
        for other in occupied[:-1]:
            assert box[2]+6 <= other[0] or other[2]+6 <= box[0] or box[3]+6 <= other[1] or other[3]+6 <= box[1]


def test_impossible_layout_is_explicit_and_does_not_add_a_clipped_plate():
    occupied = [(0,0,200,100)]
    assert place_caption(100,50,100,occupied,bounds=(0,0,200,100)) is None
    assert len(occupied) == 1
    assert place_caption(0,0,300,[],bounds=(0,0,200,100)) is None
