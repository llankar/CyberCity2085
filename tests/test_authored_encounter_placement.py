"""All playable manual maps feed strict Arcade terrain and connected encounters."""

from types import SimpleNamespace

from game.battle_maps import build_battle_map_catalog
from game.combat.battlefield import build_battlefield_plan, connect_inferred_terrain
from game.combat.encounter_placement import connected_regions, fit_encounter
from game.map_terrain import build_terrain_profile
from game.mission_objectives import create_battle_objective


def test_manual_landmarks_override_art_and_forced_spawn_holes():
    path = "assets/maps/city_district_holo_square.png"
    profile = build_terrain_profile(path, 1280, 720, forced_walkable=((640, 352),))
    assert profile.source == "manual_wall_traces_v1"
    assert not profile.is_walkable(640, 352)  # Stored holo-platform cell (20,14).
    assert profile.is_walkable(640, 480)  # Reviewed open floor at (20,9).
    unchanged, lanes = connect_inferred_terrain(profile, ((640, 352), (640, 480)))
    assert unchanged is profile and not lanes


def test_every_playable_map_fits_connected_unique_teams_and_objectives_without_carving():
    entries = build_battle_map_catalog()
    assert len(entries) == 122
    for entry in entries:
        for width, height in ((1280, 720), (960, 640)):
            profile = build_terrain_profile(entry.path, width, height)
            assert profile.source == "manual_wall_traces_v1", entry.filename
            original = profile.walkable_cells
            for kind in ("extract", "defend", "containment", "recon_scan", "civilian_rescue", "data_theft", "sabotage", "assassination"):
                objective = create_battle_objective(SimpleNamespace(objective_type=kind))
                placed = fit_encounter(profile, [(96+i*64, 64) for i in range(6)],
                                        [(1152, 352+i*32) for i in range(8)],
                                        objective.marker_positions, objective_kind=kind, breach_y=objective.breach_y)
                all_cells = (*placed.allies, *placed.enemies, *placed.objectives)
                assert len(set(all_cells)) == len(all_cells), (entry.filename, kind)
                assert all(profile.is_walkable(*cell) for cell in all_cells), (entry.filename, kind)
                assert set(all_cells) <= connected_regions(profile)[0]
                assert set(placed.allies) <= placed.deployment_cells
                assert not set(placed.enemies) & placed.deployment_cells
                assert profile.walkable_cells is original
                if kind == "containment":
                    assert all(y > placed.breach_y for x, y in placed.enemies)
                if kind == "defend":
                    assert all(max(abs(x-ox), abs(y-oy)) > 32 for x, y in placed.enemies for ox, oy in placed.objectives)


def test_closed_bottom_interior_uses_reachable_deployment_cells():
    profile = build_terrain_profile("assets/maps/cybercity_inner_02_safehouse.png", 1280, 720)
    placed = fit_encounter(profile, [(96, 64), (160, 64)], [(1152, 352)], [(448, 320)])
    assert min(y for x, y in placed.deployment_cells) > 112
    assert all(profile.is_walkable(*cell) for cell in placed.allies)


def test_non_opaque_blockers_do_not_become_high_cover():
    # Water blocks movement but must not produce a fabricated solid LOS wall.
    profile = SimpleNamespace(cell_size=32, sight_blocked_cells=frozenset(),
                              is_walkable=lambda x, y: (x, y) != (64, 64))
    plan = build_battlefield_plan(map_index=0, width=160, height=160,
                                 reserved_positions=(), terrain_profile=profile)
    assert not plan.cover_nodes
