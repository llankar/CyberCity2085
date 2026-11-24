from game.character import Character
from game.combat.equipment_recovery import (
    resolve_equipment_custody,
    snapshot_deployed_equipment,
)
from game.gamestate import GameState
from game.management.equipment import default_equipment_catalog
from unittest.mock import patch

from game.combat.godot_resolution import resolve_godot_result
from test_unified_mission_resolution import scenario


def equipped_agent(name, primary_id):
    character = Character(name, role="samurai")
    item = next(
        item for item in default_equipment_catalog()["primary_weapon"]
        if item.id == primary_id
    )
    character.loadout.equip("primary_weapon", item)
    return character


def test_survivor_recovers_dead_teammate_equipment_without_changing_stock():
    survivor = equipped_agent("Rook", "pulse_rifle")
    casualty = equipped_agent("Null", "monoblade")
    state = GameState(
        characters=[survivor, casualty],
        owned_equipment={"pulse_rifle": 1, "monoblade": 1},
    )
    snapshot = snapshot_deployed_equipment(state.characters, ["Rook", "Null"])
    state.characters.remove(casualty)

    report = resolve_equipment_custody(state, snapshot, victory=False)

    assert state.owned_equipment == {"pulse_rifle": 1, "monoblade": 1}
    assert report == {
        "status": "recovered", "total_wipe": False, "deployed_agents": 2,
        "casualties": 1, "recovered": {"monoblade": 1}, "lost": {},
    }


def test_failed_total_wipe_loses_only_deployed_gear_and_preserves_research():
    rook = equipped_agent("Rook", "pulse_rifle")
    null = equipped_agent("Null", "monoblade")
    state = GameState(
        characters=[rook, null],
        owned_equipment={"pulse_rifle": 3, "monoblade": 2, "katana": 4},
        completed_research=["weapon_corporate_rail_lattice"],
    )
    snapshot = snapshot_deployed_equipment(state.characters, ["Rook", "Null"])
    state.characters.clear()

    report = resolve_equipment_custody(state, snapshot, victory=False)

    assert state.owned_equipment == {
        "pulse_rifle": 2, "monoblade": 1, "katana": 4,
    }
    assert state.completed_research == ["weapon_corporate_rail_lattice"]
    assert report["status"] == "lost"
    assert report["lost"] == {"monoblade": 1, "pulse_rifle": 1}


def test_victory_recovers_equipment_even_when_no_deployed_agent_returns():
    agent = equipped_agent("Rook", "pulse_rifle")
    state = GameState(characters=[agent], owned_equipment={"pulse_rifle": 1})
    snapshot = snapshot_deployed_equipment(state.characters, ["Rook"])
    state.characters.clear()

    report = resolve_equipment_custody(state, snapshot, victory=True)

    assert state.owned_equipment == {"pulse_rifle": 1}
    assert report["status"] == "recovered"
    assert report["recovered"] == {"pulse_rifle": 1}


def test_undeployed_reserve_agent_does_not_prevent_total_wipe_loss():
    deployed = equipped_agent("Rook", "pulse_rifle")
    reserve = equipped_agent("Longshot", "monoblade")
    state = GameState(
        characters=[deployed, reserve],
        owned_equipment={"pulse_rifle": 1, "monoblade": 1},
    )
    snapshot = snapshot_deployed_equipment(state.characters, ["Rook"])
    state.characters.remove(deployed)

    report = resolve_equipment_custody(state, snapshot, victory=False)

    assert report["total_wipe"] and report["lost"] == {"pulse_rifle": 1}
    assert state.owned_equipment == {"monoblade": 1}


def test_godot_total_wipe_applies_equipment_loss_once_across_replay(tmp_path):
    state, mission, session, result = scenario(tmp_path)
    pulse = next(
        item for item in default_equipment_catalog()["primary_weapon"]
        if item.id == "pulse_rifle"
    )
    state.characters[0].loadout.equip("primary_weapon", pulse)
    state.owned_equipment = {"pulse_rifle": 2}
    # Refresh the immutable departure snapshot after this fixture's late loadout setup.
    state.combat_sessions[session["session_id"]]["equipment_snapshot"] = (
        snapshot_deployed_equipment(state.characters, ["Vera"])
    )
    result.update(outcome="defeat")
    result["agents"][0]["hp"] = 0

    with patch("game.battle_outcomes.random.choice", return_value="killed"):
        resolve_godot_result(state, mission, result, session["session_id"])

    assert state.owned_equipment == {"pulse_rifle": 1}
    assert state.latest_mission_debrief["equipment_recovery"]["lost"] == {
        "pulse_rifle": 1
    }
    assert resolve_godot_result(state, mission, result, session["session_id"]) is None
    assert state.owned_equipment == {"pulse_rifle": 1}
