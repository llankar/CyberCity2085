"""Executable counterplay contracts, independent of rendering and global battles."""

import json

from game.combat import ai_decision, enemy_plans
from game.combat.enemy_plans import DisruptionType, EnemyPlanManager, PlanState


def test_specialist_hunt_uses_its_own_threshold_and_recovers_into_real_alternate():
    manager = EnemyPlanManager()
    manager.initialize_plan("hunter", "corp_samurai_robot")
    plan = manager.plans["hunter"]
    manager.apply_disruption("hunter", DisruptionType.KEY_TARGET_HIT, 0.84, 4)
    assert plan.state == PlanState.INITIATING
    manager.apply_disruption("hunter", DisruptionType.KEY_TARGET_HIT, 0.85, 4)
    assert plan.state == PlanState.DISRUPTED
    assert not plan.can_attempt_execution
    assert plan.alternate_template_key == "pressure_main_force"
    manager.tick(5)
    assert plan.state == PlanState.DISRUPTED
    manager.tick(6)
    assert plan.state == PlanState.ACTIVE
    assert plan.template_key == "pressure_main_force"
    assert plan.can_attempt_execution
    assert plan.disruption_count == {}


def test_repeated_interruptions_extend_delay_and_unregistered_alternates_are_not_activated():
    manager = EnemyPlanManager()
    manager.initialize_plan("soldier", "corp_37")
    manager.apply_disruption("soldier", DisruptionType.KEY_TARGET_HIT, 1, 2)
    manager.apply_disruption("soldier", DisruptionType.KEY_TARGET_HIT, 1, 4)
    plan = manager.plans["soldier"]
    assert plan.disruption_count[DisruptionType.KEY_TARGET_HIT] == 2
    assert plan.alternate_template_key is None  # No invented reorganize_assault template.
    manager.tick(5)
    assert not plan.can_attempt_execution
    manager.tick(7)
    assert plan.template_key == "seize_objective"
    assert plan.can_attempt_execution


def test_destroyed_plan_cannot_reactivate_or_be_disrupted():
    manager = EnemyPlanManager()
    manager.initialize_plan("hunter", "corp_samurai")
    manager.apply_disruption("hunter", DisruptionType.KEY_TARGET_HIT, 1, 3)
    manager.destroy_enemy("hunter")
    manager.apply_disruption("hunter", DisruptionType.PSI_INTERRUPTION, 1, 8)
    manager.tick(100)
    assert manager.plans["hunter"].state == PlanState.CANCELLED
    assert not manager.plans["hunter"].can_attempt_execution
    manager.destroy_enemy("unknown")
    manager.apply_disruption("unknown", DisruptionType.DESTRUCTION)


def test_ai_public_adapter_forwards_turn_and_exposes_serializable_counterplay(monkeypatch):
    manager = EnemyPlanManager()
    monkeypatch.setattr(enemy_plans, "_plan_manager", manager)
    manager.initialize_plan("hunter", "corp_samurai")
    ai_decision.apply_enemy_disruption(
        "hunter", DisruptionType.KEY_TARGET_HIT, 1, game_turn=11
    )
    info = ai_decision.get_enemy_plan_info("hunter")
    assert info["state"] == "disrupted"
    assert info["last_disruption_turn"] == 11
    assert info["disruption_count"] == {"KEY_TARGET_HIT": 1}
    assert json.loads(json.dumps(info))["alternate_plan"] == "pressure_main_force"
