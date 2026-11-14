"""Validate actual shipped map art through the production terrain pipeline.

No desktop window, mouse/keyboard input, or user save is involved.
"""

import pytest

from game.battle_maps import build_battle_map_catalog
from game.combat.battlefield import (
    build_battlefield_plan,
    connect_inferred_terrain,
    reachable_objective_positions,
)
from game.map_terrain import build_terrain_profile


def representative_maps():
    selected = {}
    for entry in build_battle_map_catalog():
        selected.setdefault((entry.environment, entry.scene), entry)
    return list(selected.values())


@pytest.mark.parametrize("entry", representative_maps(), ids=lambda entry: entry.key)
def test_real_map_preserves_mission_approach_and_every_sequential_anchor(entry):
    spawn = (96, 64)
    anchors = (spawn, (160, 64), (640, 448), (448, 320), (320, 224))
    terrain = build_terrain_profile(entry.path, 1280, 720, forced_walkable=anchors[:3])
    terrain, lanes = connect_inferred_terrain(terrain, anchors)
    resolved = reachable_objective_positions(anchors[3:], spawn, terrain)
    # Inferred maps must preserve the authored mission distance, not collapse
    # the witness or exfil point onto the isolated deployment island.
    if terrain.threshold != 255:
        assert resolved == anchors[3:]
    assert all(terrain.is_walkable(*point) for point in resolved)
    assert all(terrain.is_walkable(*point) for point in lanes)
    plan = build_battlefield_plan(
        map_index=3, width=1280, height=720, terrain_profile=terrain,
        reserved_positions=anchors[:3] + resolved, objective_kind="extract",
    )
    assert all(not hazard.contains(anchor) for hazard in plan.hazards for anchor in anchors[:3] + resolved)
    assert all(not terrain.is_walkable(node.world_x, node.world_y) for node in plan.cover_nodes)
    assert all(not node.passable for node in plan.cover_nodes)
