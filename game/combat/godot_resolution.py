"""Validate then resolve externally simulated combat on a campaign shadow copy."""
from __future__ import annotations
from copy import deepcopy
from types import SimpleNamespace
from game.battle_outcomes import resolve_defeated_agent_outcome
from game.mission_system import resolve_mission_outcome
from game.unit import Unit
from .agent_moments import record_losses, remember_last_stand
from .mission_resolution import resolve_campaign_battle
from .session_protocol import agent_result_identities, validate_result
from .checkpoints import write_campaign_checkpoint


def resolve_godot_result(game_state,mission,result,session_id):
    record=game_state.combat_sessions.get(session_id)
    if record is None or record['mission_id']!=mission.id:raise ValueError('Unknown mission session')
    digest=validate_result(result,record,session_id)
    if record['status']=='applied':
        if record.get('result_digest')!=digest:raise ValueError('Conflicting replay of an applied result')
        return None
    if record['status']!='pending':raise ValueError('Session is not pending')
    shadow=deepcopy(game_state)
    characters={c.name:c for c in shadow.characters}
    assets={a.id:a for a in shadow.spec_ops_assets}
    units=[]
    moments=[]
    identities = agent_result_identities(record['expected_agents'])
    for row in result['agents']:
        name = identities[row['name']]
        name = getattr(shadow, '_loaded_agent_renames', {}).get(name, name)
        if name not in characters:
            raise ValueError('Deployed agent no longer exists')
        character = characters[name]
        if 'last_stand_hp' in row:
            moments.append(remember_last_stand(character, mission, row['last_stand_hp']))
        unit=Unit((0,0),stats=character.stats,character=character,health=row['hp'])
        unit.external_metrics=True
        if 'stress' in row:unit.reported_stress=row['stress']
        for metric in ['kills','damage_dealt','damage_taken','actions_used']:
            if metric in row:setattr(unit,'_'+metric,row[metric])
        units.append(unit)
    for row in result['support']:
        if row['id'] not in assets:raise ValueError('Deployed support no longer exists')
        asset=assets[row['id']]
        units.append(Unit((0,0),stats=asset.combat_stats(),spec_ops_asset=asset,health=row['hp']))
    renames = getattr(shadow, '_loaded_agent_renames', {})
    objective_contributions = {
        renames.get(identities[row['name']], identities[row['name']]): row['objective_contribution']
        for row in result['agents'] if row.get('objective_contribution', 0) > 0
    }
    context=SimpleNamespace(game_state=shadow,mission=deepcopy(mission),player_units=units,
        defeated_player_units=[],enemy_units=[],initial_enemy_count=result['initial_enemy_count'],
        triggered_complication=None,window=None,
        equipment_snapshot=deepcopy(record.get('equipment_snapshot')),
        combat_state=SimpleNamespace(mission=mission, logs=[], tactical_flags={
            'agent_moments': moments,
            'objective_contributions': objective_contributions,
        }))
    record_losses(context.combat_state, units)
    def resolve_defeated_player_unit(unit):
        outcome = resolve_defeated_agent_outcome(
            unit.character,
            remove_character=shadow.record_agent_death,
            record_event=shadow.add_event,
            prevent_death=(
                getattr(context, '_field_medevac_available', False)
                and not getattr(context, '_field_medevac_used', False)
            ),
        )
        if outcome == "field medevac":
            context._field_medevac_used = True
        return outcome
    context.resolve_defeated_player_unit = resolve_defeated_player_unit
    def resolve_outcome(victory):
        context.triggered_complication=resolve_mission_outcome(shadow,context.mission,victory,None)
    context.resolve_mission_outcome=resolve_outcome
    survivors,units=resolve_campaign_battle(
        context, result['outcome']=='victory', defeated_override=result['enemies_killed'],
        objective_progress=result.get('objective_progress'),
    )
    shadow.latest_mission_debrief.setdefault('deployment_vehicle', {})['heavy_strike_used'] = bool(
        result.get('heavy_strike_used', False)
    )
    shadow.latest_mission_debrief['external_combat']={k:deepcopy(result[k]) for k in
        ['outcome','turn_reached','enemies_killed','objective_completed','objective_progress'] if k in result}
    shadow.latest_mission_debrief['mission_outcome']=result['outcome']
    from .return_snapshot import build_return_snapshot
    shadow.combat_sessions[session_id].update(status='applied',result_digest=digest,confirmed_result=deepcopy(result),
        ui_status='pending',return_snapshot=build_return_snapshot(context,survivors,units,result['outcome']=='victory'))
    write_campaign_checkpoint(shadow,session_id,'after')
    # No campaign mutation occurs until the whole resolver succeeds.
    game_state.__dict__.update(shadow.__dict__)
    context.game_state=game_state
    return context,survivors,units
