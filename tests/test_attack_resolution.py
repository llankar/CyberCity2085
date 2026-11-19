"""Authoritative tactical attack calculation regressions."""

from types import SimpleNamespace
from unittest.mock import patch

from game.combat import CombatEngine, CombatState
from game.combat.attack_resolution import build_attack_context, resolve_attack
from game.combat_system import run_enemy_ai
from game.character import Character
from game.cover_system import CoverNode
from game.stats import EnemyStats, PlayerStats
from game.unit import STATUS_BLEEDING, Unit


def _attacker(position=(0, 0), *, agi=8, attack_range=6, ap=2) -> Unit:
    return Unit(
        position=position,
        stats=PlayerStats(agi=agi, str=5, psi=4, defense=1, con=1),
        health=11,
        attack_range=attack_range,
        action_points=ap,
    )


def _defender(position=(64, 0), *, defense=2, hp=20) -> Unit:
    stats = EnemyStats(level=2, defense=defense)
    stats.hp = hp
    return Unit(position=position, stats=stats, health=hp, unit_type="enemy")


def test_context_is_identical_for_preview_inputs_and_execution() -> None:
    attacker = _attacker()
    defender = _defender()
    defender.in_cover_bonus = 2
    cover = [CoverNode(1, 0, "high")]

    context = build_attack_context(attacker, defender, "fire", cover_nodes=cover)
    rolls = iter((0.0, 0.99))
    resolution = resolve_attack(
        attacker, defender, "fire", cover_nodes=cover, rng=lambda: next(rolls)
    )

    assert resolution.context == context
    assert resolution.hit
    assert resolution.damage == context.normal_damage
    assert resolution.consumed_ap == 1


def test_flanking_negates_cover_in_authoritative_context() -> None:
    defender = _defender(position=(64, 0))
    defender.in_cover_bonus = 2
    cover = [CoverNode(1, 0, "high")]

    protected = build_attack_context(_attacker(position=(0, 0)), defender, "fire", cover_nodes=cover)
    flanked = build_attack_context(_attacker(position=(96, 0)), defender, "fire", cover_nodes=cover)

    assert protected.cover_bonus == 2
    assert not protected.flanking
    assert flanked.cover_bonus == 0
    assert flanked.flanking
    assert flanked.hit_chance > protected.hit_chance


def test_miss_spends_exactly_one_ap_for_player_and_enemy() -> None:
    attacker = _attacker(ap=2)
    defender = _defender(hp=100)
    with patch("game.combat.attack_resolution.random.random", return_value=0.999):
        result = resolve_attack(attacker, defender, "fire")
    assert result.reason == "miss"
    assert attacker.action_points == 1

    enemy = _defender(position=(64, 0), hp=20)
    enemy.attack_range = 4
    enemy.action_points = 1
    ally = _attacker(position=(0, 0), ap=2)
    ally.stats.hp = ally.health = 100
    with patch("game.combat.attack_resolution.random.random", return_value=0.999):
        actions = run_enemy_ai([ally], [enemy])
    assert enemy.action_points == 0
    assert actions[-1].decision_reason == "attack_missed"


def test_missile_has_distinct_damage_and_consumes_capacity() -> None:
    attacker = _attacker()
    attacker.spec_ops_asset = SimpleNamespace(missile_capacity=2)
    defender = _defender(hp=30)

    result = resolve_attack(attacker, defender, "missiles", rng=lambda: 0.0)

    assert result.success and result.hit
    assert result.context.normal_damage > attacker.stats.agi
    assert result.consumed_resource == 1
    assert attacker.spec_ops_asset.missile_capacity == 1


def test_first_aid_can_stabilize_adjacent_ally_and_clear_bleeding() -> None:
    medic = _attacker(position=(0, 0), ap=2)
    medic.character = Character("Patch", traits=["first aid"])
    patient = _attacker(position=(32, 0), ap=0)
    patient.health = patient.stats.hp = 4
    patient.apply_status(STATUS_BLEEDING)
    state = CombatState(None, [medic, patient], [_defender()], turn="player")

    result = CombatEngine(state).perform_action("first_aid", actor=medic, target=patient)

    assert result.success
    assert patient.health == 6
    assert not patient.has_status(STATUS_BLEEDING)
    assert medic.action_points == 1
    assert "clears BLEEDING" in result.message
