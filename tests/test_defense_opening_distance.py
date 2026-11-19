"""Defenders get an approach phase through placement, never hidden immunity."""

from collections import deque
from types import SimpleNamespace

from game.battle_maps import build_battle_map_catalog
from game.combat import CombatEngine, CombatState
from game.combat.encounter_placement import connected_regions, fit_encounter
from game.map_terrain import TerrainProfile, build_terrain_profile
from game.mission_objectives import BattleObjective, create_battle_objective
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def distances(region, objectives):
    goals = {cell for cell in region if any(max(abs(cell[0]-x), abs(cell[1]-y)) <= 32 for x, y in objectives)}
    field, queue = {cell: 0 for cell in goals}, deque(goals)
    while queue:
        x, y = queue.popleft()
        for cell in ((x+32, y), (x-32, y), (x, y+32), (x, y-32)):
            if cell in region and cell not in field:
                field[cell] = field[x, y] + 1
                queue.append(cell)
    return field


def test_spawn_is_outside_three_moves_of_the_entire_breach_square():
    floor = frozenset((x, y) for x in range(0, 384, 32) for y in range(0, 320, 32))
    terrain = TerrainProfile("open", 384, 320, 32, floor, 255)
    placed = fit_encounter(terrain, [(32, 64)], [(256, 128)], [(192, 128)], objective_kind="defend")
    field = distances(floor, placed.objectives)
    assert field[placed.enemies[0]] >= 4
    assert placed.objectives == ((192, 128),)


def test_real_starver_activation_cannot_breach_immediately_from_fitted_spawn():
    floor = frozenset((x, y) for x in range(0, 384, 32) for y in range(0, 320, 32))
    terrain = TerrainProfile("open", 384, 320, 32, floor, 255)
    placed = fit_encounter(terrain, [(32, 64)], [(256, 128)], [(192, 128)], objective_kind="defend")
    ally = Unit(position=placed.allies[0], health=1000, stats=PlayerStats(level=5))
    enemy = Unit(position=placed.enemies[0], health=50, stats=EnemyStats(),
                 unit_type="enemy", enemy_theme="starver", attack_range=1)
    state = CombatState(None, [ally], [enemy], objective=BattleObjective("defend", placed.objectives[0], "RELAY"))
    engine = CombatEngine(state, can_enter=terrain.is_walkable, terrain_profile=terrain)
    engine.start_player_turn()
    result = engine.start_enemy_turn()
    assert not result.ended and not state.objective.failed
    assert enemy.action_points == enemy.bonus_move_points == 0


def test_wall_protected_nearby_spawn_is_kept_when_its_actual_route_is_long_enough():
    floor = frozenset((x, y) for x in range(0, 384, 32) for y in range(0, 320, 32)
                      if not (x == 224 and 64 <= y <= 192))
    terrain = TerrainProfile("wall", 384, 320, 32, floor, 255)
    placed = fit_encounter(terrain, [(32, 64)], [(256, 128)], [(192, 128)], objective_kind="defend")
    assert placed.enemies == ((256, 128),)
    assert distances(floor, placed.objectives)[placed.enemies[0]] >= 4


def test_all_authored_defense_maps_fit_opening_distance_at_three_window_sizes():
    for entry in build_battle_map_catalog():
        for size in ((1280, 720), (960, 640), (1920, 1000)):
            terrain = build_terrain_profile(entry.path, *size)
            objective = create_battle_objective(SimpleNamespace(objective_type="defend"))
            placed = fit_encounter(terrain, [(96+i*64, 64) for i in range(6)],
                                    [(1152, 352+i*32) for i in range(8)], objective.marker_positions,
                                    objective_kind="defend")
            field = distances(connected_regions(terrain)[0], placed.objectives)
            assert all(field[cell] >= 4 for cell in placed.enemies), (entry.filename, size)
            assert len(set(placed.enemies)) == 8 and len(set(placed.allies)) == 6
