"""Geometry and semantic contracts for the holographic World Map."""

from dataclasses import replace
from types import SimpleNamespace
import pytest
from game.ui.layouts.world_map_beacons import (
    Beacon,
    Rect,
    arrange_beacons,
    artwork_obstacles,
    briefing_link,
)
from game.ui.components.world_map_beacons import category_for


@pytest.mark.parametrize(
    "mission,narrative,expected",
    [
        (SimpleNamespace(title="[STORY] Relay"), False, "story"),
        (SimpleNamespace(title="Relay", risk_level=5), False, "operation"),
        (SimpleNamespace(title="Relay", tags=["urgent"]), False, "urgent"),
        (
            SimpleNamespace(
                title="Relay", emotional_impact_hint={"normalized_tags": ["emergency"]}
            ),
            True,
            "urgent",
        ),
        (
            SimpleNamespace(
                title="Relay",
                tags=None,
                emotional_impact_hint={"normalized_tags": None},
            ),
            True,
            "narrative",
        ),
    ],
)
def test_category_comes_from_mission_metadata(mission, narrative, expected):
    assert category_for(mission, narrative) == expected


def test_link_routes_around_labels_without_crossing_them():
    obstacle = Rect(40, 20, 70, 80)
    path = briefing_link((10, 50), (100, 50), [obstacle], Rect(0, 0, 110, 100))
    assert path[0] == (10, 50) and path[-1] == (100, 50)
    assert len(path) >= 4
    for (x, y), (u, v) in zip(path, path[1:]):
        assert x == u or y == v
        if y == v:
            assert not (
                obstacle.bottom < y < obstacle.top
                and max(x, u) > obstacle.left
                and min(x, u) < obstacle.right
            )
        else:
            assert not (
                obstacle.left < x < obstacle.right
                and max(y, v) > obstacle.bottom
                and min(y, v) < obstacle.top
            )


def test_duplicate_city_pins_are_separated_and_deterministic():
    image = Rect(0, 0, 1200, 675)
    specs = [
        Beacon(
            str(i), "combat", i, "operation", "Mission", "Warsaw", (0.5, 0.55), i == 0
        )
        for i in range(8)
    ]
    placements = arrange_beacons(specs, image)
    assert placements == arrange_beacons(specs, image)
    occupied = artwork_obstacles(image)
    for p in placements:
        for r in [p.marker, p.label]:
            assert r.inside(image)
            assert not any(r.intersects(o) for o in occupied)
            occupied.append(r)
