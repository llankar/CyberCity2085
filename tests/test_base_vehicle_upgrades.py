from game.gamestate import GameState
from game.character import Character
from game.combat.godot_bridge import build_godot_combat_payload
from game.combat.godot_resolution import resolve_godot_result
from game.combat_system import create_player_units
from game.management.equipment import default_equipment_catalog, equipment_purchase_price
from game.mission_system import launch_selected_mission
from game.mission_templates import MissionTemplate
from game.ui.screens.mission_briefing_view import build_mission_briefing_facts
from test_unified_mission_resolution import scenario
from unittest.mock import patch


def test_base_and_vehicle_upgrades_purchase_atomically_and_persist(tmp_path):
    state = GameState()
    state.funds.current_funds = 100_000
    assert state.purchase_base_upgrade("trauma_center")[0]
    assert state.purchase_base_upgrade("field_medevac", vehicle=True)[0]
    balance = state.available_funds
    assert not state.purchase_base_upgrade("field_medevac", vehicle=True)[0]
    assert state.available_funds == balance
    path = tmp_path / "upgrades.json"
    state.save(path)
    restored = GameState.load(path)
    assert restored.base_upgrade_ids == ["trauma_center"]
    assert restored.vehicle_upgrade_ids == ["field_medevac"]


def test_rapid_fabricator_discount_is_used_by_real_purchase():
    item = default_equipment_catalog()["primary_weapon"][0]
    state = GameState(base_upgrade_ids=["rapid_fabricator"])
    expected = max(1, int(round(equipment_purchase_price(item) * .9 / 10) * 10))
    state.funds.current_funds = expected
    assert state.equipment_price(item) == expected
    assert state.purchase_equipment(item)[0]
    assert state.available_funds == 0


def test_vector_engines_shorten_launched_mission_and_boost_both_combat_clients():
    agent = Character("Rook", role="samurai")
    mission = MissionTemplate(
        id="vector", title="Vector", objective_text="Deploy",
        target_faction="Starvers", district="Chrome", district_pressure={},
        starting_enemy_count=3, duration_days=3,
    )
    state = GameState(
        characters=[agent], selected_agent_names=[agent.name],
        mission_templates=[mission], vehicle_upgrade_ids=["vector_engines", "armored_cradle"],
    )
    state.mission_board_generated_day = state.calendar.current_day
    state.mission_board_version = 2
    launched = launch_selected_mission(state)
    assert launched.duration_days == 2
    bonuses = state.deployment_combat_bonuses()
    unit = create_player_units([agent], deployment_bonuses=bonuses)[0]
    baseline = create_player_units([agent])[0]
    assert unit.stats.defense == baseline.stats.defense + 2
    assert unit.initiative_bonus == baseline.initiative_bonus + 1
    payload = build_godot_combat_payload(state, launched)
    assert payload["squad"][0]["defense"] == baseline.stats.defense + 2
    assert payload["squad"][0]["initiative"] > 0
    assert payload["combat_ui"]["deployment_upgrades"] == ["vector_engines", "armored_cradle"]


def test_signal_array_reveals_real_hostile_estimate_in_briefing():
    mission = MissionTemplate(
        id="signal", title="Signal", objective_text="Inspect signals",
        target_faction="Starvers", district="Chrome", district_pressure={},
        starting_enemy_count=6,
    )
    limited = build_mission_briefing_facts(GameState(), mission)
    informed = build_mission_briefing_facts(
        GameState(base_upgrade_ids=["signal_array"]), mission
    )
    assert limited["mission_intel_level"] == 0 and "Limited" in limited["hostile_estimate"]
    assert informed["mission_intel_level"] == 1
    assert informed["hostile_estimate"] == "6 hostiles // Starvers doctrine"


def test_trauma_center_removes_one_additional_recovery_day(tmp_path):
    state, mission, session, result = scenario(tmp_path)
    state.base_upgrade_ids.append("trauma_center")
    result["agents"][0]["hp"] = 0
    with patch("game.battle_outcomes.random.choice", return_value="critically injured"):
        resolve_godot_result(state, mission, result, session["session_id"])
    assert state.characters[0].recovery_turns == 1
