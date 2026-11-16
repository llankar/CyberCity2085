"""Raider and Starver decisions run through actual phase transitions."""

from types import SimpleNamespace
from unittest.mock import patch

from game.character import Character
from game.combat import CombatEngine, CombatState
from game.combat.attack_resolution import resolve_attack
from game.combat.pack_maneuvers import route_step
from game.combat_system import create_enemy_units
from game.mission_templates import MissionTemplate
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def agent(name, position, hp=100):
    return Unit(position=position, health=hp, stats=PlayerStats(max_hp=100), attack_range=8,
                character=SimpleNamespace(name=name, role="samurai"))


def hostile(theme, position, attack_range=3):
    return Unit(position=position, health=30, stats=EnemyStats(max_hp=30),
                unit_type="enemy", enemy_theme=theme, attack_range=attack_range)


def test_raider_prefers_an_isolated_agent_and_regrouping_is_visible_counterplay():
    a, b, c = agent("Rook", (64, 0), 1), agent("Echo", (64, 32)), agent("Nyx", (224, 0))
    enemy = hostile("raider", (0, 0))
    engine = CombatEngine(CombatState(None, [a, b, c], [enemy]))
    engine.start_player_turn()
    intent = engine.enemy_intents()[0]
    assert intent.action == "ISOLATE"
    assert intent.target is c  # Wounded Rook already has a nearby teammate.
    b.position = (224, 32)
    regrouped = engine.enemy_intents()[0]
    assert regrouped.target is a
    assert "squad_regrouped" in regrouped.rationale
    engine.enemy_intents()
    assert sum("squad_regrouped" in line for line in engine.state.logs) == 1


def test_raider_fires_once_and_pays_the_other_ap_for_its_exit():
    target = agent("Rook", (160, 96))
    enemy = hostile("raider", (96, 96))
    engine = CombatEngine(CombatState(None, [target], [enemy]))
    engine.start_player_turn()
    with patch("game.combat_system.resolve_attack", wraps=resolve_attack) as attacks:
        engine.start_enemy_turn()
    assert attacks.call_count == 1
    assert enemy.position == (64, 96)
    assert enemy.action_points == 0


def test_a_second_regroup_can_interrupt_a_new_isolation_target_in_the_same_phase():
    a, b, c, d = (agent("Rook", (64, 0), 1), agent("Echo", (64, 32)),
                  agent("Nyx", (224, 0)), agent("Mara", (384, 0)))
    enemy = hostile("raider", (0, 0))
    engine = CombatEngine(CombatState(None, [a, b, c, d], [enemy]))
    engine.start_player_turn()
    assert engine.enemy_intents()[0].target is c
    b.position = (224, 32)
    assert engine.enemy_intents()[0].target is a
    c.position = (96, 0)
    assert engine.enemy_intents()[0].target is not a
    engine.enemy_intents()
    assert sum("squad_regrouped" in line for line in engine.state.logs) == 2


def test_boxed_in_raider_cannot_take_a_free_escape_step():
    target = agent("Rook", (160, 96))
    enemy = hostile("raider", (96, 96))
    engine = CombatEngine(CombatState(None, [target], [enemy]), can_enter=lambda x, y: False)
    engine.start_player_turn()
    with patch("game.combat_system.resolve_attack", wraps=resolve_attack) as attacks:
        engine.start_enemy_turn()
    assert attacks.call_count == 2
    assert enemy.position == (96, 96)
    assert enemy.action_points == 0


def test_raider_exit_triggers_real_overwatch_processing():
    target = agent("Rook", (160, 96))
    enemy = hostile("raider", (96, 96))
    engine = CombatEngine(CombatState(None, [target], [enemy]))
    engine.start_player_turn()
    target.on_overwatch = True
    def attack(actor, defender, *args, **kwargs):
        if actor is target:
            enemy.health = 0
            return SimpleNamespace(damage=30, hit=True)
        actor.action_points -= 1
        return SimpleNamespace(damage=0, hit=False)
    with patch("game.combat_system.resolve_attack", side_effect=attack):
        result = engine.start_enemy_turn()
    assert result.outcome == "victory"
    assert enemy not in engine.state.enemy_units
    assert not target.on_overwatch


def test_pack_reserves_distinct_approaches_and_uses_melee_even_if_range_is_misconfigured():
    target = agent("Rook", (160, 96))
    enemies = [hostile("starver", (96, 96), 8), hostile("starver", (64, 64), 8)]
    engine = CombatEngine(CombatState(None, [target], enemies))
    engine.start_player_turn()
    intents = engine.enemy_intents()
    assert all(intent.action == "SWARM" for intent in intents)
    assert len({intent.destination for intent in intents}) == 2
    with patch("game.combat_system.resolve_attack", wraps=resolve_attack) as attacks:
        engine.start_enemy_turn()
    assert attacks.call_count == 2  # One bonus stride lets the first Starver arrive before spending attack AP.
    assert all(call.args[2] == "melee" for call in attacks.call_args_list)
    assert enemies[0].position == (128, 96)
    assert enemies[1].position == (160, 64)
    assert all(enemy.action_points == 0 for enemy in enemies)


def test_starver_takes_a_legal_detour_instead_of_stalling_against_a_wall():
    walls = {(32, 0), (32, 32), (32, 64)}
    target = agent("Rook", (128, 32))
    enemy = hostile("starver", (0, 32), 1)
    engine = CombatEngine(CombatState(None, [target], [enemy]), can_enter=lambda x, y: (x, y) not in walls)
    engine.start_player_turn()
    engine.start_enemy_turn()
    assert enemy.position == (32, 96)  # Third movement step comes from the Starver stride.
    assert enemy.action_points == 0
    assert target.health == 100


def test_screening_a_reserved_approach_breaks_the_lane_without_free_movement():
    target, screen = agent("Rook", (160, 96)), agent("Echo", (224, 224))
    enemy = hostile("starver", (64, 96), 1)
    engine = CombatEngine(CombatState(None, [target, screen], [enemy]),
                          can_enter=lambda x, y: (x, y) not in {target.position, screen.position})
    engine.start_player_turn()
    destination = engine.enemy_intents()[0].destination
    assert destination is not None
    screen.position = destination
    interrupted = engine.enemy_intents()[0]
    assert "approach_blocked" in interrupted.rationale
    assert interrupted.destination is None
    assert enemy.position == (64, 96)


def test_moving_the_prey_cancels_the_old_surround_but_not_the_chase():
    target = agent("Rook", (160, 96))
    enemy = hostile("starver", (64, 96), 1)
    engine = CombatEngine(CombatState(None, [target], [enemy]))
    engine.start_player_turn()
    target.position = (192, 96)
    intent = engine.enemy_intents()[0]
    assert intent.action == "RUSH" and intent.destination is None
    assert "prey_moved" in intent.rationale
    engine.start_enemy_turn()
    assert enemy.position != (64, 96)
    assert enemy.action_points == 0


def test_generated_starvers_do_not_inherit_ranged_subtype_loadouts():
    mission = MissionTemplate(id="pack", title="Pack", objective_text="Survive", target_faction="Hungry Tide",
                              district="Badlands", district_pressure={}, starting_enemy_count=4, enemy_theme="starver")
    leader = Character("Veteran")
    leader.stats.level = 7
    enemies, _ = create_enemy_units(mission, [leader])
    assert any(enemy.enemy_subtype == "commander" for enemy in enemies)
    assert {enemy.attack_range for enemy in enemies} == {1}


def test_route_search_is_bounded_when_the_destination_is_sealed():
    assert route_step((0, 0), (96, 96), lambda x, y: False, max_visits=2) is None
