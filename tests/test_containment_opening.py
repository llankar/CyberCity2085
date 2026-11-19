"""Containment opening spacing follows paths and respects corridor capacity."""

from game.combat.encounter_placement import fit_encounter, approach_distances, connected_regions
from game.map_terrain import TerrainProfile, build_terrain_profile
from game.battle_maps import build_battle_map_catalog


def test_open_map_gives_hostiles_more_than_a_starver_activation_to_breach():
    floor = frozenset((x,y) for x in range(0,512,32) for y in range(0,512,32))
    terrain = TerrainProfile("open",512,512,32,floor,255)
    placed = fit_encounter(terrain, [(64,64)], [(256,224)], [(448,320)],
                           objective_kind="containment", breach_y=192)
    assert placed.enemies[0][1] >= 320
    assert placed.breach_y == 192


def test_all_maps_use_best_available_opening_distance_without_dropping_enemies():
    for entry in build_battle_map_catalog():
        for size in ((1280,720),(960,640),(1920,1000)):
            terrain = build_terrain_profile(entry.path,*size)
            placed = fit_encounter(terrain,[(96+i*64,64) for i in range(6)],
                                   [(1152,352+i*32) for i in range(8)],[(448,320)],
                                   objective_kind="containment",breach_y=192)
            region = connected_regions(terrain)[0]
            distance = approach_distances(region,{c for c in region if c[1]<=placed.breach_y})
            candidates = region-placed.deployment_cells-set(placed.allies)-set(placed.objectives)
            ranked = sorted((distance[c] for c in candidates if c[1]>placed.breach_y), reverse=True)
            expected = min(4,ranked[7])
            assert len(set(placed.enemies)) == 8
            assert all(distance[c]>=expected and c[1]>placed.breach_y for c in placed.enemies), entry.filename
            assert all(terrain.is_walkable(*c) for c in (*placed.allies,*placed.enemies))


def test_shallow_corridor_adjusts_frontier_and_preserves_headcount():
    floor = frozenset((x,y) for x in range(0,512,32) for y in range(0,320,32))
    terrain = TerrainProfile("shallow",512,320,32,floor,255)
    placed = fit_encounter(terrain,[(64,64)],[(256,224)]*8,[(448,160)],
                           objective_kind="containment",breach_y=192)
    assert len(set(placed.enemies)) == 8
    assert placed.breach_y == 128
    assert all(y>=256 for x,y in placed.enemies)
    assert max(y for x,y in placed.deployment_cells) == 96


def test_freeway_has_four_step_approaches_at_small_viewports():
    for size in ((1280,720),(960,640)):
        terrain=build_terrain_profile("assets/maps/city_exterior_elevated_freeway.png",*size)
        placed=fit_encounter(terrain,[(96+i*64,64) for i in range(6)],[(1152,352+i*32) for i in range(8)],
                             [(448,320)],objective_kind="containment",breach_y=192)
        region=connected_regions(terrain)[0]
        distance=approach_distances(region,{c for c in region if c[1]<=placed.breach_y})
        assert min(distance[c] for c in placed.enemies)>=4
        assert all(y<=placed.breach_y for x,y in placed.allies)


def test_real_starver_cannot_cross_on_first_activation_when_four_steps_fit():
    from game.combat import CombatEngine, CombatState
    from game.mission_objectives import BattleObjective
    from game.stats import PlayerStats, EnemyStats
    from game.unit import Unit
    floor = frozenset((x,y) for x in range(0,512,32) for y in range(0,512,32))
    terrain = TerrainProfile("open",512,512,32,floor,255)
    placed = fit_encounter(terrain,[(64,64)],[(256,224)],[(448,320)],
                           objective_kind="containment",breach_y=192)
    ally = Unit(position=placed.allies[0],health=1000,stats=PlayerStats())
    enemy = Unit(position=placed.enemies[0],health=50,stats=EnemyStats(),
                 unit_type="enemy",enemy_theme="starver",attack_range=1)
    objective = BattleObjective("containment",placed.objectives[0],"BREACH LINE",breach_y=placed.breach_y)
    engine = CombatEngine(CombatState(None,[ally],[enemy],objective=objective),
                          can_enter=terrain.is_walkable,terrain_profile=terrain)
    engine.start_player_turn()
    assert not engine.start_enemy_turn().ended
    assert enemy.position[1]>placed.breach_y and not objective.failed
