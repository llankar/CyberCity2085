"""Separate QA target-choice failures from actual unreachable pack markers."""

from types import SimpleNamespace

from game.combat import CombatEngine, CombatState
from game.combat.encounter_qa import first_reachable_approach
from game.combat.movement import can_enter_cell
from game.map_terrain import TerrainProfile
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def test_qa_tries_a_farther_reachable_target_instead_of_guarding_at_a_sealed_one():
    actor = SimpleNamespace(position=(32, 32))
    near, far = SimpleNamespace(position=(96, 32)), SimpleNamespace(position=(128, 160))
    floor = {(32, 32), (32, 64), (64, 64), (64, 96), (96, 96), (128, 96), (128, 128)}
    selected, step = first_reachable_approach(actor, [near, far], lambda x, y: (x, y) in floor,
                                             width=224, height=224)
    assert selected is far and step == (0, 32)


def encounter(with_approach):
    # (96,128) is free but sealed. (128,96) is the reachable assault square.
    floor = {(32, 32), (32, 64), (64, 64), (96, 64), (128, 64), (96, 128), (128, 128)}
    if with_approach:
        floor.add((128, 96))
    terrain = TerrainProfile("fixture", 256, 224, 32, frozenset(floor), 255)
    ally = Unit(position=(128, 128), health=100, stats=PlayerStats(level=5))
    enemy = Unit(position=(32, 32), health=50, stats=EnemyStats(level=3),
                 unit_type="enemy", enemy_theme="starver", attack_range=1)
    state = CombatState(None, [ally], [enemy])
    engine = CombatEngine(state, terrain_profile=terrain,
                          can_enter=lambda x, y: can_enter_cell(x, y, terrain_profile=terrain,
                                                               allied_units=[ally], enemy_units=[enemy]))
    engine.start_player_turn()
    return engine, enemy, floor


def test_starver_reserves_reachable_assault_square_and_executes_the_shown_approach():
    engine, enemy, floor = encounter(True)
    shown = engine.enemy_intents()[0]
    assert shown.action == "SWARM" and shown.destination == (128, 96)
    assert shown.destination != (96, 128)
    engine.start_enemy_turn()
    assert enemy.position == (96, 64) and enemy.position in floor
    assert enemy.action_points == enemy.bonus_move_points == 0
    assert not any("movement_blocked" in message for message in engine.state.logs)


def test_starver_does_not_promise_an_unreachable_free_square():
    engine, enemy, _ = encounter(False)
    shown = engine.enemy_intents()[0]
    assert shown.action != "SWARM" and shown.destination is None
    engine.start_enemy_turn()
    assert enemy.position == (32, 32)
    assert any("movement_blocked" in message for message in engine.state.logs)
