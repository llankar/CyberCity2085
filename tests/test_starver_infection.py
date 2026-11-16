"""Rare irreversible campaign consequences, not a curable combat status."""

from unittest.mock import patch

from game.character import Character, is_deployable
from game.combat import CombatEngine, CombatState
from game.combat.attack_resolution import build_attack_context, resolve_attack
from game.gamestate import GameState
from game.persistence import SaveSystem
from game.starver_infection import INCUBATION_DAYS, TRANSMISSION_CHANCE, advance_infection, transmit_bite, infection_label
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def units():
    character = Character("Rook")
    character.stats.max_hp = character.stats.hp = 100
    defender = Unit(position=(32, 0), health=100, stats=character.stats, character=character)
    attacker = Unit(position=(0, 0), health=30, stats=EnemyStats(str=8, max_hp=30),
                    unit_type="enemy", enemy_theme="starver")
    return attacker, defender, character


def test_starver_stride_increases_movement_without_increasing_attack_ap():
    attacker, _, _ = units()
    attacker.reset_actions()
    assert attacker.action_points == 2 and attacker.bonus_move_points == 1
    for _ in range(3):
        attacker.move(32, 0)
    assert attacker.position == (96, 0)
    assert attacker.action_points == 0 and attacker.bonus_move_points == 0
    attacker.apply_status("suppressed")
    attacker.reset_actions()
    assert attacker.action_points == 0 and attacker.bonus_move_points == 0


def test_boosted_bite_preview_and_resolution_agree():
    attacker, defender, _ = units()
    bite = build_attack_context(attacker, defender, "melee")
    attacker.enemy_theme = "generic"
    normal = build_attack_context(attacker, defender, "melee")
    attacker.enemy_theme = "starver"
    assert bite.normal_damage == normal.normal_damage + max(2, (normal.normal_damage+3)//4)
    rolls = iter([0.0, 1.0, 1.0])  # Hit, no crit, no infection.
    result = resolve_attack(attacker, defender, "melee", rng=lambda: next(rolls))
    assert result.damage == bite.normal_damage
    assert not result.infection_transmitted


def test_exact_rare_threshold_and_repeated_bites_do_not_reset_the_clock():
    attacker, defender, character = units()
    assert not transmit_bite(attacker, defender, lambda: TRANSMISSION_CHANCE)
    assert transmit_bite(attacker, defender, lambda: TRANSMISSION_CHANCE - 0.0001)
    assert character.starver_infection_days == INCUBATION_DAYS
    advance_infection(character)
    assert not transmit_bite(attacker, defender, lambda: 0.0)
    assert character.starver_infection_days == INCUBATION_DAYS - 1
    assert len(character.history) == 1


def test_miss_non_starver_ranged_asset_and_fatal_bites_do_not_transmit():
    attacker, defender, character = units()
    resolve_attack(attacker, defender, "melee", rng=lambda: 1.0)
    assert character.starver_infection_days is None
    attacker.reset_actions()
    rolls = iter([0.0, 1.0])
    resolve_attack(attacker, defender, "fire", rng=lambda: next(rolls))
    assert character.starver_infection_days is None
    attacker.enemy_theme = "mutant"
    assert not transmit_bite(attacker, defender, lambda: 0.0)
    attacker.enemy_theme = "starver"
    defender.spec_ops_asset = object()
    assert not transmit_bite(attacker, defender, lambda: 0.0)
    defender.spec_ops_asset = None
    defender.health = 0
    assert not transmit_bite(attacker, defender, lambda: 0.0)


def test_real_bite_survives_saving_healing_and_converts_on_the_third_day(tmp_path):
    attacker, defender, character = units()
    rolls = iter([0.0, 1.0, 0.0])
    result = resolve_attack(attacker, defender, "melee", rng=lambda: next(rolls))
    assert result.infection_transmitted
    state = GameState(characters=[character], selected_agent_names=[character.name])
    # Ordinary medical recovery and HP healing cannot erase the independent clock.
    character.stats.hp = character.stats.max_hp
    character.recovery_turns = 1
    save_path = tmp_path / "infected_campaign.json"
    assert SaveSystem.save_game(state, save_path).ok
    state, loaded = SaveSystem.load_game(save_path)
    assert loaded.ok and state is not None
    with patch("game.gamestate.roll_random_event"):
        state.advance_days(2)
        survivor = state.characters[0]
        assert survivor.starver_infection_days == 1
        assert not survivor.starver_transformed
        assert "INCURABLE" in infection_label(survivor)
        state.advance_days(1)
    assert survivor.role == "starver" and survivor.starver_transformed
    assert not is_deployable(survivor)
    assert survivor.name not in state.selected_agent_names
    assert any("has become a Starver" in line for line in survivor.history)
    restored = Character.from_dict(survivor.to_dict())
    restored.stats.hp = restored.stats.max_hp
    restored.recovery_turns = 0
    assert not is_deployable(restored)
    assert advance_infection(restored) is None


def test_old_agent_saves_remain_uninfected_and_dying_does_not_resurrect_an_agent():
    old = Character.from_dict({"name": "Old save"})
    assert old.starver_infection_days is None and not old.starver_transformed
    old.starver_infection_days = 1
    old.stats.hp = 0
    assert advance_infection(old) is None
    assert not old.starver_transformed


def test_engine_announces_transmission_on_the_real_enemy_phase():
    attacker, defender, character = units()
    engine = CombatEngine(CombatState(None, [defender], [attacker]))
    engine.start_player_turn()
    with patch("game.combat.attack_resolution.random.random", return_value=0.0):
        engine.start_enemy_turn()
    assert character.starver_infection_days == INCUBATION_DAYS
    assert any("INCURABLE" in line for line in engine.state.logs)
