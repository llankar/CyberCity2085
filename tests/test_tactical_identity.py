from types import SimpleNamespace

from game.combat.tactical_identity import (
    build_enemy_intents,
    predict_enemy_intent,
    profile_for_theme,
    tactical_target_score,
)
from game.deployment import build_tactical_briefing
from game.mission_templates import MissionTemplate
from game.recruitment import recruit_agent
from game.management.equipment import equip_starter_loadout
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def _enemy(theme: str, position=(0, 0), attack_range=3) -> Unit:
    return Unit(
        position=position,
        stats=EnemyStats(hp=8, max_hp=8, agi=5, str=5, defense=2),
        health=8,
        attack_range=attack_range,
        unit_type="enemy",
        enemy_theme=theme,
    )


def _agent(name: str, role: str, position=(128, 0), hp=10, defense=3) -> Unit:
    character = SimpleNamespace(name=name, role=role)
    return Unit(
        position=position,
        stats=PlayerStats(hp=hp, max_hp=10, defense=defense),
        health=hp,
        character=character,
    )


def test_intent_does_not_advertise_fire_outside_weapon_range_or_an_empty_target():
    hunter = _enemy("corp_samurai", attack_range=2)
    target = _agent("Mara", "sniper", (320, 0))
    assert predict_enemy_intent(hunter, [target]).action == "COVER"
    assert predict_enemy_intent(hunter, []).action == "HOLD"


def test_completed_objective_is_not_advertised_as_a_breach_target():
    enemy = _enemy("corp_37", attack_range=1)
    objective = SimpleNamespace(kind="defend", completed=True)
    target = _agent("Iris", "psi", (320, 0))
    assert predict_enemy_intent(enemy, [target], objective=objective).action != "BREACH"


def test_every_enemy_can_preview_a_one_shot_squad_iterable():
    target = _agent("Mara", "sniper")
    intents = build_enemy_intents(
        [_enemy("starver"), _enemy("raider")], (unit for unit in [target])
    )
    assert len(intents) == 2
    assert all(intent.target is target for intent in intents)


def test_theme_families_resolve_to_distinct_readable_doctrines() -> None:
    assert profile_for_theme("corp_37_power_armor").label == "THREE SEVENS"
    assert profile_for_theme("corp_samurai_robot").cover_bias > 1
    assert profile_for_theme("starver").cover_bias == 0
    assert profile_for_theme("novatek_hybrid").wounded_weight > profile_for_theme("generic").wounded_weight


def test_preflight_briefing_connects_enemy_doctrine_and_agent_kits() -> None:
    mission = MissionTemplate(
        id="doctrine_test",
        title="Doctrine Test",
        objective_text="Hold the line.",
        target_faction="Three Sevens Corp",
        district="Warsaw",
        district_pressure={},
        starting_enemy_count=2,
        risk_level=2,
        fund_reward=40,
        duration_days=1,
        enemy_theme="corp_37",
    )
    agent = recruit_agent([], "sniper", "Ghost")
    equip_starter_loadout(agent.loadout, agent.role)

    briefing = build_tactical_briefing(mission, [agent])

    assert briefing.enemy_label == "THREE SEVENS"
    assert briefing.squad_count == 1
    assert briefing.armed_count == 1
    assert briefing.ready
    assert "Ghost: Sniper Rifle" in briefing.loadout_summary
    assert briefing.capability_summary == "RANGED"
    assert briefing.tactical_gap == "Understrength squad"
    assert briefing.recovery_load == "LOW"


def test_preflight_exposes_balanced_roles_and_management_recovery_cost() -> None:
    mission = MissionTemplate(
        id="high_risk",
        title="Last Light",
        objective_text="Hold the breach.",
        target_faction="Hungry Tide",
        district="Warrens",
        district_pressure={},
        starting_enemy_count=6,
        risk_level=5,
        enemy_theme="starver",
    )
    samurai = recruit_agent([], "samurai", "Rook")
    sniper = recruit_agent([], "sniper", "Longshot")
    psi = recruit_agent([], "psi", "Oracle")
    samurai.stress = 72
    sniper.stress = 68
    psi.stress = 75

    briefing = build_tactical_briefing(mission, [samurai, sniper, psi])

    assert briefing.capability_summary == "FRONTLINE / RANGED / CONTROL"
    assert briefing.tactical_gap == "Balanced response"
    assert briefing.recovery_load == "CRITICAL"


def test_novatek_hybrid_prefers_a_wounded_agent() -> None:
    enemy = _enemy("novatek_hybrid")
    healthy = _agent("Aegis", "samurai", (64, 0), hp=10)
    wounded = _agent("Nyx", "samurai", (128, 0), hp=2)

    assert tactical_target_score(enemy, wounded) > tactical_target_score(enemy, healthy)
    assert predict_enemy_intent(enemy, [healthy, wounded]).target is wounded


def test_corporate_unit_telegraphs_a_flank_against_cover() -> None:
    enemy = _enemy("corp_samurai", attack_range=5)
    target = _agent("Mara", "sniper", (96, 0))
    target.in_cover_bonus = 2

    intent = predict_enemy_intent(enemy, [target])

    assert intent.action == "FLANK"
    assert intent.target_name == "Mara"
    assert "cover" in intent.rationale


def test_three_sevens_telegraphs_objective_pressure_out_of_range() -> None:
    enemy = _enemy("corp_37", attack_range=1)
    target = _agent("Iris", "psi", (320, 0))
    objective = SimpleNamespace(kind="defend", position=(64, 64), completed=False)

    intent = predict_enemy_intent(enemy, [target], objective=objective)

    assert intent.action == "BREACH"
    assert intent.target is None


def test_intent_builder_hides_dead_and_unseen_enemies() -> None:
    target = _agent("Rook", "samurai")
    visible = _enemy("raider")
    hidden = _enemy("starver")
    hidden.visible = False
    dead = _enemy("mutant")
    dead.health = 0

    intents = build_enemy_intents([visible, hidden, dead], [target])

    assert len(intents) == 1
    assert intents[0].enemy is visible
