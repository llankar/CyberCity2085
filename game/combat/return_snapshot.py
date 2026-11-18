"""Serializable debrief data: replay presentation without replaying campaign rules."""
from types import SimpleNamespace
from game.character import Character
from game.mission_templates import MissionComplication
from game.unit import Unit


def build_return_snapshot(context,survivors,units,victory):
    rows=[]
    for unit in units:
        char=unit.character
        if char is None:continue
        rows.append(dict(character=char.to_dict(),health=unit.health,
            extraction_max_hp=getattr(unit,'extraction_max_hp',char.stats.max_hp),
            pre_level=getattr(char,'_pre_battle_level',char.stats.level),
            pre_stress=getattr(char,'_pre_battle_stress',char.stress),
            xp=getattr(char,'_mission_xp_gained',0),
            metrics={key:getattr(unit,'_'+key,None) for key in ['kills','damage_dealt','damage_taken','actions_used']}))
    return dict(victory=victory,units=rows,surviving_names=[c.name for c in survivors],
        complication=context.triggered_complication.to_dict() if context.triggered_complication else None)


def resume_return(state,mission,session_id):
    record=state.combat_sessions[session_id]
    if record.get('status')!='applied' or record.get('ui_status')!='pending':return None
    from .session_protocol import validate_result
    digest=validate_result(record['confirmed_result'],record,session_id)
    if digest!=record.get('result_digest'):raise ValueError('Stored result digest mismatch')
    data=record['return_snapshot'];current={c.name:c for c in state.characters};units=[]
    for row in data['units']:
        name=row['character']['name'];char=current.get(name) or Character.from_dict(row['character'])
        char._pre_battle_level=row['pre_level'];char._pre_battle_stress=row['pre_stress'];char._mission_xp_gained=row['xp']
        unit=Unit((0,0),stats=char.stats,character=char,health=row['health']);unit.extraction_max_hp=row['extraction_max_hp'];unit.external_metrics=True
        for key,value in row['metrics'].items():
            if value is not None:setattr(unit,'_'+key,value)
        units.append(unit)
    context=SimpleNamespace(game_state=state,mission=mission,window=None,_victory=data['victory'],
        triggered_complication=MissionComplication.from_dict(data['complication']) if data['complication'] else None)
    survivors=[current[name] for name in data['surviving_names'] if name in current]
    return context,survivors,units


def complete_return(state,session_id):
    record=state.combat_sessions[session_id]
    if record.get('status')!='applied':raise ValueError('Cannot finish an unresolved return')
    record['ui_status']='complete'
    try:
        from .checkpoints import write_campaign_checkpoint
        write_campaign_checkpoint(state,session_id,'after')
    except OSError:
        state.add_event('Combat resolved; checkpoint UI marker could not be refreshed. Recovery may show the debrief again, without another reward.')
