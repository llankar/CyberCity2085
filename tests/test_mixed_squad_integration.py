"""Actual selected role kits and support units share placement/action rules."""

from unittest.mock import patch

from game.character import Character
from game.combat import CombatEngine, CombatState
from game.combat_system import create_player_units
from game.management.equipment import equip_starter_loadout
from game.management.spec_ops_assets import default_spec_ops_assets
from game.unit import Unit
from game.stats import EnemyStats


def selected_team():
    characters=[Character(name,role=role) for name,role in
                (("Rook","samurai"),("Longshot","sniper"),("Oracle","psi"),("Echo","medic"))]
    for character in characters:
        equip_starter_loadout(character.loadout,character.role)
    assets=default_spec_ops_assets()[:2]
    return create_player_units(characters,[c.name for c in characters],assets,[a.id for a in assets])


def test_selected_mixed_team_fits_every_authored_map_without_overlap_or_wall_carving():
    from game.battle_maps import build_battle_map_catalog
    from game.map_terrain import build_terrain_profile
    from game.combat.encounter_placement import fit_encounter
    team=selected_team()
    assert len(team)==6 and sum(u.spec_ops_asset is not None for u in team)==2
    for entry in build_battle_map_catalog():
        terrain=build_terrain_profile(entry.path,1280,720)
        original=terrain.walkable_cells
        placed=fit_encounter(terrain,[u.position for u in team],[(1152,352+i*32) for i in range(6)])
        assert len(set((*placed.allies,*placed.enemies)))==12
        assert all(terrain.is_walkable(*cell) for cell in (*placed.allies,*placed.enemies))
        assert terrain.walkable_cells is original


def test_mixed_roles_and_asset_resolve_real_actions_with_distinct_costs():
    team=selected_team()
    samurai,sniper,psi,medic,robot,drone=team
    for unit,position in zip(team,((32,0),(0,32),(32,32),(0,0),(64,32),(96,32))):
        unit.position=position
    enemy=Unit(position=(64,0),stats=EnemyStats(),unit_type="enemy")
    enemy.health=enemy.stats.hp=1000
    engine=CombatEngine(CombatState(None,team,[enemy]))
    engine.start_player_turn()
    with patch("game.combat.attack_resolution.random.random",return_value=0):
        for actor,action in ((samurai,"melee"),(sniper,"fire"),(psi,"psi"),(robot,"missiles")):
            before=actor.action_points
            capacity=robot.spec_ops_asset.missile_capacity
            result=engine.perform_action(action,actor=actor,target=enemy)
            assert result.success and result.damage>0
            assert actor.action_points==before-result.consumed_ap
            if action=="missiles":
                assert result.consumed_resource==1
                assert robot.spec_ops_asset.missile_capacity==capacity-1
    samurai.health=1
    assert engine.perform_action("first_aid",actor=medic,target=samurai).success
    assert samurai.health==3
    assert engine.perform_action("overwatch",actor=drone).success
    assert drone.on_overwatch


def test_piloted_armor_retains_exact_pilot_identity_without_duplicate_foot_unit():
    pilot=Character("Mara",role="sniper")
    teammate=Character("Echo",role="medic")
    suit=default_spec_ops_assets()[2]
    suit.pilot_agent_name=pilot.name
    units=create_player_units([pilot,teammate],[pilot.name,teammate.name],[suit],[suit.id])
    assert len(units)==2
    armor=next(unit for unit in units if unit.spec_ops_asset is suit)
    assert armor.character is pilot
    assert sum(unit.character is pilot for unit in units)==1
    assert armor.stats is not pilot.stats


def test_unselected_suit_cannot_reserve_the_selected_suits_pilot():
    from game.deployment import sanitize_selected_asset_ids
    pilot=Character("Mara")
    suits=default_spec_ops_assets()[2:]
    for suit in suits:
        suit.pilot_agent_name=pilot.name
    selected=[suits[1].id]
    assert sanitize_selected_asset_ids(suits,selected,[pilot])==selected
    units=create_player_units([pilot],[pilot.name],suits,selected)
    assert len(units)==1 and units[0].character is pilot
    assert units[0].spec_ops_asset is suits[1]


def test_one_named_pilot_cannot_duplicate_into_two_selected_suits():
    from game.deployment import selected_deployment_manifest
    pilot,other=Character("Mara"),Character("Echo")
    suits=default_spec_ops_assets()[2:]
    for suit in suits:
        suit.pilot_agent_name=pilot.name
    manifest=selected_deployment_manifest([pilot,other],[pilot.name,other.name],suits,[s.id for s in suits])
    assert manifest.assets==[suits[0]]
    assert manifest.agents==[other]


def test_absent_or_recovering_assigned_pilot_cannot_launch_in_armor():
    pilot=Character("Mara",recovery_turns=2)
    other=Character("Echo")
    suit=default_spec_ops_assets()[2]
    suit.pilot_agent_name=pilot.name
    units=create_player_units([pilot,other],[pilot.name,other.name],[suit],[suit.id])
    assert len(units)==1 and units[0].character is other
    assert units[0].spec_ops_asset is None
