"""Corporate coordination has executable costs and positional counterplay."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from game.combat import CombatEngine, CombatState
from game.combat.command_network import command_accuracy, linked_commander
from game.cover_system import CoverNode
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def encounter():
    def agent(name, x):
        return Unit(position=(x, 0), health=100, stats=PlayerStats(max_hp=100),
                    character=SimpleNamespace(name=name, role="samurai"), attack_range=8)
    def enemy(role, position):
        return Unit(position=position, health=30, stats=EnemyStats(max_hp=30),
                    unit_type="enemy", enemy_theme="corp_samurai", enemy_subtype=role, attack_range=8)
    a, b = agent("Rook", 64), agent("Echo", 160)
    commander = enemy("commander", (0, 0))
    heavy = enemy("heavy", (0, 64))
    grunt = enemy("grunt", (96, 0))
    # Followers intentionally precede the leader in the data.
    engine = CombatEngine(CombatState(None, [a, b], [heavy, grunt, commander]))
    return engine, a, b, commander, heavy, grunt


def spend_shot(actor, target, *args, hit=True, **kwargs):
    if kwargs.get("spend_ap", True):
        actor.action_points -= 1
    return SimpleNamespace(damage=1 if hit else 0, hit=hit)


def test_linked_roles_share_leader_target_regardless_of_list_order():
    engine, a, b, commander, heavy, grunt = encounter()
    engine.start_player_turn()
    by_enemy = {id(intent.enemy): intent for intent in engine.enemy_intents()}
    assert by_enemy[id(commander)].target is a
    assert by_enemy[id(grunt)].target is a
    assert by_enemy[id(grunt)].action == "FOCUS"
    assert by_enemy[id(heavy)].action == "SUPPRESS"
    assert by_enemy[id(heavy)].coordinator is commander
    b.health = 1
    assert {id(intent.target) for intent in engine.enemy_intents()} == {id(a)}


@pytest.mark.parametrize("hit", [True, False])
def test_suppression_commits_both_ap_even_when_it_misses(hit):
    engine, a, b, commander, heavy, grunt = encounter()
    engine.start_player_turn()
    with patch("game.combat_system.resolve_attack", side_effect=lambda actor, target, *args, **kw: spend_shot(actor, target, hit=hit, **kw)) as fire:
        engine.start_enemy_turn()
    heavy_shots = [call for call in fire.call_args_list if call.args[0] is heavy]
    assert len(heavy_shots) == 1
    assert heavy.action_points == 0
    assert a.has_status("suppressed") is hit
    assert any("2 AP" in line for line in engine.state.logs)
    engine.start_player_turn()
    assert a.action_points == (0 if hit else 2)
    assert not a.has_status("suppressed")  # Status is consumed at the phase boundary.


@pytest.mark.parametrize("break_link", ["dead", "suppressed", "distance", "sight"])
def test_command_counterplay_releases_the_heavy_order(break_link):
    engine, a, b, commander, heavy, grunt = encounter()
    if break_link == "sight":
        heavy.position = (128, 0)
        a.position, b.position = (192, 0), (256, 0)
    engine.start_player_turn()
    assert engine.enemy_orders.orders[id(heavy)].intent.action == "SUPPRESS"
    if break_link == "dead":
        commander.health = 0
    elif break_link == "suppressed":
        commander.apply_status("suppressed")
    elif break_link == "distance":
        commander.position = (512, 512)
    else:
        engine.cover_nodes = [CoverNode(2, 0, "high", False)]
    intent = next(intent for intent in engine.enemy_intents() if intent.enemy is heavy)
    assert intent.coordinator is None
    assert intent.action != "SUPPRESS"
    assert "command_lost" in intent.rationale
    engine.enemy_intents()
    # One notification for each affected follower, not one per frame.
    assert sum("command_lost" in line for line in engine.state.logs) <= 2


def test_mixed_factions_do_not_receive_each_others_orders():
    engine, a, b, commander, heavy, grunt = encounter()
    heavy.enemy_theme = "corp_37"
    engine.start_player_turn()
    assert engine.enemy_orders.orders[id(heavy)].intent.coordinator is None


def test_accuracy_does_not_stack_or_corrupt_capped_stats_and_restores_on_error():
    engine, a, b, commander, heavy, grunt = encounter()
    others = engine.state.enemy_units + [commander]
    heavy.stats.agi = 5
    with command_accuracy(heavy, others):
        assert heavy.stats.agi == 6
    assert heavy.stats.agi == 5
    heavy.stats.agi = 99
    with pytest.raises(RuntimeError):
        with command_accuracy(heavy, others):
            assert heavy.stats.agi == 99
            raise RuntimeError("resolver failed")
    assert heavy.stats.agi == 99
    commander.apply_status("stunned")
    assert linked_commander(heavy, others) is None


def test_commander_killed_by_overwatch_cannot_coordinate_later_activations():
    engine, a, b, commander, heavy, grunt = encounter()
    a.position, b.position = (192, 0), (256, 0)
    commander.attack_range = 1
    engine.state.enemy_units = [commander, heavy]
    engine.start_player_turn()
    assert engine.enemy_orders.orders[id(heavy)].intent.action == "SUPPRESS"
    a.on_overwatch = True
    def resolve(actor, target, *args, **kwargs):
        if actor is a and target is commander:
            commander.health = 0
            return SimpleNamespace(damage=30, hit=True)
        return spend_shot(actor, target, hit=False, **kwargs)
    with patch("game.combat_system.resolve_attack", side_effect=resolve):
        engine.start_enemy_turn()
    assert commander.health == 0
    assert not a.has_status("suppressed")
    assert engine.enemy_orders.orders[id(heavy)].intent.coordinator is None
    assert any("command_lost" in line for line in engine.state.logs)
