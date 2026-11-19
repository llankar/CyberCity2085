"""Compare approach planning with an independent shortest-path oracle."""

from collections import deque
import random
from types import SimpleNamespace

from game.combat.pack_maneuvers import approach_step, neighbors, route_step_to_any
from game.combat.objective_movement import objective_route_step


def distance(start, goals, legal):
    queue, seen = deque([(start, 0)]), {start}
    while queue:
        cell, length = queue.popleft()
        if cell in goals:
            return length
        for adjacent in neighbors(cell):
            if adjacent not in seen and legal(*adjacent):
                queue.append((adjacent, length + 1))
                seen.add(adjacent)
    return None


def test_approach_chooses_five_step_route_instead_of_seven_step_nearer_endpoint():
    rows = [".###...#", "#.#....#", ".#..#.##", ".S.##T#.",
            "........", ".....#.#", "........", "....#.#."]
    blocked = {(x*32, (7-y)*32) for y, row in enumerate(rows) for x, char in enumerate(row) if char in "#T"}
    legal = lambda x, y: 0 <= x < 256 and 0 <= y < 256 and (x, y) not in blocked
    actor, target = SimpleNamespace(position=(32, 128)), SimpleNamespace(position=(160, 128))
    goals = {cell for cell in neighbors(target.position) if legal(*cell)}
    oracle = distance(actor.position, goals, legal)
    assert oracle == 5
    for remaining in range(oracle, 0, -1):
        step = approach_step(actor, target, legal, width=256, height=256)
        assert step is not None and abs(step[0])+abs(step[1]) == 32
        actor.position = actor.position[0]+step[0], actor.position[1]+step[1]
        assert distance(actor.position, goals, legal) == remaining-1
    assert actor.position in goals


def test_seeded_obstacle_layouts_match_breadth_first_shortest_paths():
    rng = random.Random(2026)
    for _ in range(200):
        start, target = (32, 128), (160, 128)
        blocked = {(x*32, y*32) for x in range(8) for y in range(8) if rng.random() < .28} | {target}
        blocked.discard(start)
        legal = lambda x, y: 0 <= x < 256 and 0 <= y < 256 and (x, y) not in blocked
        goals = {cell for cell in neighbors(target) if legal(*cell)}
        expected = distance(start, goals, legal)
        step = route_step_to_any(start, goals, legal, width=256, height=256, max_visits=64)
        if expected is None:
            assert step is None
        else:
            assert step is not None
            next_cell = start[0]+step[0], start[1]+step[1]
            assert legal(*next_cell) and distance(next_cell, goals, legal) == expected-1


def test_containment_search_can_reach_a_line_beyond_the_first_five_blocked_approaches():
    # The five nearest legal line cells are sealed pockets; farther cells work.
    enemy = SimpleNamespace(position=(32, 160))
    objective = SimpleNamespace(kind="containment", breach_y=64, completed=False)
    legal = lambda x, y: (0 <= x < 320 and 0 <= y < 224
                          and not (y in {32, 96} and x < 256)
                          and not (y == 64 and x in {128, 192}))
    moves = 0
    for _ in range(20):
        step = objective_route_step(enemy, objective, legal, width=320, height=224)
        if step == (0, 0):
            break
        assert step is not None and abs(step[0])+abs(step[1]) == 32
        enemy.position = enemy.position[0]+step[0], enemy.position[1]+step[1]
        moves += 1
        assert legal(*enemy.position)
    assert enemy.position[1] <= objective.breach_y
    assert moves == 10


def test_search_budget_and_empty_or_already_reached_goals_remain_explicit():
    assert route_step_to_any((0, 0), (), lambda x, y: True) is None
    assert route_step_to_any((0, 0), {(0, 0)}, lambda x, y: True) is None
    assert route_step_to_any((0, 0), {(128, 128)}, lambda x, y: True, max_visits=1) is None


def test_qa_distinguishes_repeated_unchanged_rounds_from_a_turn_limit_alone():
    from game.combat.encounter_qa import simulate_encounter
    result = simulate_encounter(theme="generic", level=1, risk=1, count=1, seed=0,
                                policy="focus", objective_kind="extract", max_turns=15)
    # This policy never interacts; once enemies die it keeps guarding in place.
    assert result["outcome"] == "turn_limit"
    assert result["enemy_survivors"] == 0
    assert 1 <= result["longest_unchanged_rounds"] <= result["unchanged_rounds"] <= result["turns"]


def test_blocked_target_reorientation_uses_actual_wide_map_bounds():
    from game.combat import CombatEngine, CombatState
    from game.map_terrain import TerrainProfile
    from game.stats import PlayerStats, EnemyStats
    from game.unit import Unit
    terrain = TerrainProfile("wide", 2304, 768, 32,
                             frozenset((x, y) for x in range(0, 1792, 32) for y in range(0, 768, 32)), 255)
    old_target = Unit(position=(1920, 64), health=1, stats=PlayerStats(level=4))
    alternate = Unit(position=(1664, 64), health=40, stats=PlayerStats(level=4))
    enemy = Unit(position=(1536, 64), health=40, stats=EnemyStats(), unit_type="enemy", attack_range=1)
    engine = CombatEngine(CombatState(None, [old_target, alternate], [enemy]),
                          terrain_profile=terrain, can_enter=terrain.is_walkable)
    engine.start_player_turn()
    # Reserve the old promise explicitly; this tests invalidation, not scoring.
    engine.enemy_orders.reserve([enemy], [old_target], None, None, refresh=True, can_enter=terrain.is_walkable)
    engine.start_enemy_turn()
    engine.start_player_turn()
    assert engine.enemy_intents()[0].target is alternate
