import pytest

from game.character import Character
from game.combat import CombatEngine, CombatState
from game.management.equipment import equip_starter_loadout
from game.stats import EnemyStats
from game.unit import Unit


def fixture(**kwargs):
    character=Character("Rook")
    equip_starter_loadout(character.loadout,"samurai")
    ally=Unit(position=(32,32),stats=character.stats,character=character)
    enemy=Unit(position=(64,32),stats=EnemyStats(),unit_type="enemy")
    state=CombatState(None,[ally],[enemy])
    engine=CombatEngine(state,**kwargs)
    return engine,ally,enemy


@pytest.mark.parametrize("delta",((0,0),(64,0),(32,32),(1,0)))
def test_grid_rejects_zero_diagonal_fractional_and_multi_cell_moves_without_cost(delta):
    engine,ally,_=fixture()
    before=ally.action_points
    result=engine.perform_action("move",actor=ally,move_delta=delta)
    assert not result.success and ally.position==(32,32) and ally.action_points==before


def test_shared_occupancy_applies_without_optional_callback():
    engine,ally,_=fixture()
    assert not engine.perform_action("move",actor=ally,move_delta=(32,0)).success
    assert engine.perform_action("move",actor=ally,move_delta=(0,32)).success
    assert ally.position==(32,64) and ally.action_points==1


def test_nonmember_actor_and_dead_or_allied_attack_targets_are_rejected_without_cost():
    engine,ally,enemy=fixture()
    outsider=Unit(position=(32,32),stats=ally.stats,character=ally.character)
    assert not engine.perform_action("move",actor=outsider,move_delta=(0,32)).success
    assert outsider.action_points==2
    enemy.health=0
    assert not engine.perform_action("melee",actor=ally,target=enemy).success
    assert not engine.perform_action("melee",actor=ally,target=ally).success
    assert ally.action_points==2


def test_terrain_is_authoritative_even_without_optional_callback():
    from game.map_terrain import TerrainProfile
    terrain=TerrainProfile("floor",128,128,32,frozenset({(32,32),(64,32)}),255)
    engine,ally,_=fixture(terrain_profile=terrain)
    assert not engine.perform_action("move",actor=ally,move_delta=(0,32)).success
    assert ally.position==(32,32) and ally.action_points==2
    from game.cover_system import CoverNode
    engine,ally,_=fixture(cover_nodes=[CoverNode(1,2,"high",False)])
    assert not engine.perform_action("move",actor=ally,move_delta=(0,32)).success
    assert ally.position==(32,32) and ally.action_points==2
