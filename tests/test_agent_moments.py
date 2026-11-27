from unittest.mock import patch
import random
from types import SimpleNamespace

from game.character import Character
from game.combat import CombatEngine, CombatState
from game.combat.agent_moments import record_last_stand
from game.unit import Unit
from game.stats import EnemyStats
from game.management.equipment import Weapon


def fixture():
    character = Character("Rook", traits=["brave"])
    character.loadout.primary_weapon = Weapon("blade", "Blade", "primary_weapon", range_cells=1, attack_stat="str")
    actor = Unit(position=(0,0),health=1,stats=character.stats,character=character)
    enemy = Unit(position=(32,0),health=1,stats=EnemyStats(),unit_type="enemy")
    actor.health = actor.stats.hp = 1
    enemy.health = enemy.stats.hp = 1
    return character, actor, enemy, CombatState(None,[actor],[enemy])


def test_real_low_health_kill_records_dialogue_and_persistent_memory():
    character, actor, enemy, state = fixture()
    engine = CombatEngine(state)
    engine.start_player_turn()
    with patch("game.combat.attack_resolution.random.random", return_value=0):
        result = engine.perform_action("melee",actor=actor,target=enemy)
    assert result.success and result.defeated_target
    assert any("Who's next?" in line for line in state.logs)
    assert len(character.history)==1
    restored = Character.from_dict(character.to_dict())
    assert restored.history==character.history
    assert "1 HP" in restored.history[0]


def test_real_attack_metrics_feed_one_factual_under_fire_memory():
    from game.combat.agent_moments import remember_under_fire
    from game.combat.attack_resolution import resolve_attack

    character, actor, enemy, state = fixture()
    enemy.stats.str = 13
    actor.stats.max_hp = 20
    actor.health = actor.stats.hp = actor.stats.max_hp
    with patch("game.combat.attack_resolution.random.random", side_effect=[0.0, 1.0]):
        resolution = resolve_attack(enemy, actor, "melee", spend_ap=False)
    assert resolution.damage == actor._damage_taken == enemy._damage_dealt
    assert not hasattr(enemy, "_kills")
    assert remember_under_fire(character, state.mission, actor._damage_taken, actor.stats.max_hp) is not None
    assert remember_under_fire(character, state.mission, actor._damage_taken, actor.stats.max_hp) is not None
    assert character.history.count(
        f"Tactical engagement: stayed in the fight after taking {actor._damage_taken} damage."
    ) == 1


def test_last_stand_dialogue_reflects_ambition_and_active_scars():
    from game.combat.godot_bridge import _agent_payload

    character, actor, enemy, state = fixture()
    character.ambition = "Find my sister"
    enemy.health = 0
    record_last_stand(state, actor, enemy, defeated=True)
    assert any("something to finish" in line for line in state.logs)
    assert _agent_payload(character)["last_stand_dialogue"] == "I've still got something to finish."

    character.temporary_scars.append({"key": "combat_trauma", "days_remaining": 2})
    next_battle = CombatState(None, [actor], [enemy])
    record_last_stand(next_battle, actor, enemy, defeated=True)
    assert any("I remember how this ends" in line for line in next_battle.logs)
    assert len(character.history) == 2


def test_repeated_kills_do_not_spam_but_a_new_battle_can_be_remembered():
    character, actor, enemy, state = fixture()
    enemy.health=0
    before=random.getstate()
    record_last_stand(state,actor,enemy,defeated=True)
    record_last_stand(state,actor,enemy,defeated=True)
    assert len(character.history)==1 and random.getstate()==before
    record_last_stand(CombatState(None,[actor],[]),actor,enemy,defeated=True)
    assert len(character.history)==2


def test_misses_full_health_and_dead_or_non_allied_actors_do_not_create_memories():
    character, actor, enemy, state = fixture()
    record_last_stand(state,actor,enemy,defeated=False)
    enemy.health=0
    actor.health=character.stats.max_hp
    record_last_stand(state,actor,enemy,defeated=True)
    actor.health=0
    record_last_stand(state,actor,enemy,defeated=True)
    actor.health=1
    record_last_stand(CombatState(None,[],[]),actor,enemy,defeated=True)
    assert not character.history and not state.logs


def test_fear_and_cautious_personality_change_the_reaction():
    character, actor, enemy, state = fixture()
    character.fears=["death"]
    enemy.health=0
    record_last_stand(state,actor,enemy,defeated=True)
    assert any("I'm scared" in line for line in state.logs)
    character.fears=[]
    character.traits=[]
    character.personality_primary_trait="cautious"
    other=CombatState(None,[actor],[])
    record_last_stand(other,actor,enemy,defeated=True)
    assert any("need cover" in line for line in other.logs)


def test_real_aid_records_both_agents_and_uses_existing_bond_until_debrief():
    helper = Character("Echo",role="medic")
    patient = Character("Rook",relationships={"Echo":5})
    medic = Unit(position=(0,0),stats=helper.stats,character=helper)
    wounded = Unit(position=(32,0),stats=patient.stats,character=patient)
    wounded.health = wounded.stats.hp = 1
    enemy = Unit(position=(256,0),stats=EnemyStats(),unit_type="enemy")
    state = CombatState(None,[medic,wounded],[enemy])
    engine=CombatEngine(state)
    engine.start_player_turn()
    result=engine.perform_action("first_aid",actor=medic,target=wounded)
    assert result.success and result.consumed_ap==1 and wounded.health==3
    assert len(helper.history)==len(patient.history)==1
    assert any("wouldn't leave me" in line for line in state.logs)
    assert patient.relationships=={"Echo":5}
    engine.perform_action("first_aid",actor=medic,target=wounded)
    assert len(helper.history)==len(patient.history)==1


def test_rescue_debrief_applies_a_reciprocal_bond_once():
    from game.narrative.relationship_consequences import apply_tactical_relationship_consequences

    helper = Character("Echo", relationships={"Rook": 2})
    patient = Character("Rook", relationships={"Echo": -1})
    moments = [{
        "kind": "rescue",
        "agent_name": "Echo",
        "patient_name": "Rook",
        "text": "Echo stopped the bleeding for Rook.",
    }]

    changes = apply_tactical_relationship_consequences([helper, patient], moments)

    assert helper.relationships["Rook"] == 3
    assert patient.relationships["Echo"] == 0
    assert changes == [{
        "kind": "rescue_bond",
        "source": "Echo",
        "target": "Rook",
        "delta": 1,
        "text": "Relationship: Echo and Rook gained +1 bond after the rescue.",
    }]
    assert apply_tactical_relationship_consequences([helper, patient], moments) == []
    assert helper.relationships["Rook"] == 3
    assert patient.relationships["Echo"] == 0


def test_campaign_resolution_persists_rescue_bond_and_debrief_change(tmp_path):
    from game.combat.mission_resolution import resolve_campaign_battle
    from game.gamestate import GameState
    from game.mission_templates import MissionTemplate
    from game.persistence import SaveSystem

    helper = Character("Echo", role="medic")
    patient = Character("Rook")
    helper_unit = Unit(position=(0, 0), stats=helper.stats, character=helper)
    patient_unit = Unit(position=(32, 0), stats=patient.stats, character=patient)
    state = GameState(characters=[helper, patient])
    mission = MissionTemplate(
        "rescue_bond_test",
        "Clinic Hold",
        "Hold the clinic.",
        "Raiders",
        "Clinic",
        {},
        0,
    )
    combat_state = CombatState(mission, [helper_unit, patient_unit], [])
    combat_state.tactical_flags["agent_moments"] = [{
        "kind": "rescue",
        "agent_name": "Echo",
        "patient_name": "Rook",
        "text": "Echo stopped the bleeding for Rook.",
    }]
    context = SimpleNamespace(
        game_state=state,
        enemy_units=[],
        initial_enemy_count=0,
        player_units=[helper_unit, patient_unit],
        defeated_player_units=[],
        combat_state=combat_state,
        mission=mission,
        triggered_complication=None,
        resolve_mission_outcome=lambda victory: None,
        resolve_defeated_player_unit=lambda unit: None,
    )

    resolve_campaign_battle(context, True)

    assert helper.relationships["Rook"] == 1
    assert patient.relationships["Echo"] == 1
    changes = state.latest_mission_debrief["relationship_changes"]
    assert changes[0]["kind"] == "rescue_bond"
    assert any("gained +1 bond" in event for event in state.event_log)

    path = tmp_path / "relationship-consequence.json"
    assert SaveSystem.save_game(state, path).ok
    loaded, status = SaveSystem.load_game(path)
    assert status.ok
    assert loaded.characters[0].relationships["Rook"] == 1
    assert loaded.characters[1].relationships["Echo"] == 1
    assert loaded.latest_mission_debrief["relationship_changes"] == changes


def test_aid_cannot_revive_dead_or_treat_enemy():
    helper=Character("Echo",role="medic")
    medic=Unit(position=(0,0),stats=helper.stats,character=helper)
    enemy=Unit(position=(32,0),stats=EnemyStats(),unit_type="enemy")
    engine=CombatEngine(CombatState(None,[medic],[enemy]))
    engine.start_player_turn()
    assert not engine.perform_action("first_aid",actor=medic,target=enemy).success
    casualty_char=Character("Lost")
    casualty=Unit(position=(32,0),stats=casualty_char.stats,character=casualty_char)
    casualty.health=0
    engine.state.allied_units.append(casualty)
    assert not engine.perform_action("first_aid",actor=medic,target=casualty).success
    medic.health=0
    assert not engine.perform_action("first_aid",actor=medic).success


def test_real_campaign_save_retains_current_battle_moments_and_debrief(tmp_path):
    from game.narrative.debrief import build_mission_debrief_report, DebriefReport
    from game.gamestate import GameState
    from game.persistence import SaveSystem
    character, actor, enemy, state=fixture()
    enemy.health=0
    record_last_stand(state,actor,enemy,defeated=True)
    report=build_mission_debrief_report([character],None,False,
                                        tactical_moments=state.tactical_flags["agent_moments"])
    assert report.lines[0].consequence_type=="last_stand"
    assert report.heroic_action==report.tactical_moments[0]["text"]
    campaign=GameState(characters=[character])
    campaign.latest_mission_debrief=report.to_dict()
    path=tmp_path/"remembered_campaign.json"
    assert SaveSystem.save_game(campaign,path).ok
    loaded,status=SaveSystem.load_game(path)
    assert status.ok
    assert loaded.characters[0].history==character.history
    restored=DebriefReport.from_dict(loaded.latest_mission_debrief)
    assert restored.tactical_moments==report.tactical_moments
    assert restored.lines[0].text==report.lines[0].text
    assert DebriefReport.from_dict({}).tactical_moments==[]
    # Another battle does not inherit the previous battle's moments/history.
    empty=build_mission_debrief_report([character],None,True,tactical_moments=[])
    assert not empty.tactical_moments
    assert all(line.consequence_type!="last_stand" for line in empty.lines)


def test_rescue_debrief_names_both_agents_and_copies_event_data():
    from game.combat.agent_moments import record_rescue
    from game.narrative.debrief import build_mission_debrief_report
    helper,actor,enemy,state=fixture()
    patient=Character("Echo")
    target=Unit(position=(32,0),stats=patient.stats,character=patient)
    target.health=3
    record_rescue(state,actor,target,before_hp=1,cleared_bleeding=False)
    moments=state.tactical_flags["agent_moments"]
    report=build_mission_debrief_report([helper,patient],None,True,tactical_moments=moments)
    assert report.lines[0].consequence_type=="rescue"
    assert "Rook" in report.lines[0].text and "Echo" in report.lines[0].text
    moments[0]["text"]="changed"
    assert report.tactical_moments[0]["text"]!="changed"


def test_real_enemy_kill_is_remembered_after_ai_removes_the_fallen_agent():
    character, actor, enemy, state=fixture()
    friend=Character("Echo",relationships={"Rook":5})
    survivor=Unit(position=(64,0),stats=friend.stats,character=friend)
    survivor.health=survivor.stats.hp=1000
    state.allied_units.append(survivor)
    enemy.stats.str=50
    enemy.health=enemy.stats.hp=50
    engine=CombatEngine(state)
    engine.start_player_turn()
    with patch("game.combat.attack_resolution.random.random",return_value=0):
        engine.start_enemy_turn()
    assert actor.health<=0
    assert any("Rook was downed" in line for line in character.history)
    assert any("stay with me" in line for line in state.logs)
    assert any("saw Rook go down under fire" in line for line in friend.history)
    count=len(character.history)
    engine.end_battle_check()
    assert len(character.history)==count
    assert len([m for m in state.tactical_flags["agent_moments"] if m["kind"]=="downed"])==1


def test_status_death_is_remembered_and_loss_has_debrief_loss_tone():
    from game.narrative.debrief import build_mission_debrief_report
    character,actor,enemy,state=fixture()
    actor.apply_status("bleeding")
    engine=CombatEngine(state)
    engine.start_player_turn()
    assert actor.health<=0
    report=build_mission_debrief_report([],None,False,tactical_moments=state.tactical_flags["agent_moments"])
    assert report.lines[0].emotional_tone=="loss"
    assert report.lines[0].agent_name==character.name
    assert report.heroic_action!=report.lines[0].text


def test_already_fallen_units_and_living_departures_do_not_generate_new_losses():
    character,actor,enemy,state=fixture()
    actor.health=0
    engine=CombatEngine(state)
    engine.end_battle_check()
    assert not character.history
    character,actor,enemy,state=fixture()
    engine=CombatEngine(state)
    state.allied_units.clear()
    engine.end_battle_check()
    assert not character.history


def test_real_panic_activation_is_remembered_once_without_changing_its_duration():
    from game.narrative.debrief import build_mission_debrief_report
    character,actor,enemy,state=fixture()
    character.trauma=["Old ambush"]
    actor.apply_status("panicked")
    engine=CombatEngine(state)
    engine.start_player_turn()
    assert actor.action_points==0 and not actor.has_status("panicked")
    assert any("Not again" in line for line in state.logs)
    assert len(character.history)==1
    engine.start_player_turn()
    assert actor.action_points==2 and len(character.history)==1
    actor.apply_status("panicked")
    engine.start_player_turn()
    assert len(character.history)==1
    report=build_mission_debrief_report([character],None,False,tactical_moments=state.tactical_flags["agent_moments"])
    assert report.lines[0].emotional_tone=="tense"
    assert report.lines[0].consequence_type=="panic"
    from game.combat.agent_moments import record_panic
    character.trauma=[]
    character.ambition="Find my sister"
    actor.apply_status("panicked")
    other=CombatState(None,[actor],[enemy])
    record_panic(other,actor)
    assert any("something to finish" in line for line in other.logs)
