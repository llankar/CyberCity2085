"""Versioned, session-isolated local mailboxes. Python owns campaign state."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from uuid import uuid4

PROTOCOL_VERSION = 2


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    temporary.replace(path)


def create_session(game_state, mission, handoff_path):
    from copy import deepcopy
    previous_sessions=deepcopy(game_state.combat_sessions)
    payload=json.loads(Path(handoff_path).read_text(encoding='utf-8'))
    session_id=uuid4().hex
    directory=Path(handoff_path).parent/'sessions'/session_id
    session=dict(protocol_version=PROTOCOL_VERSION,session_id=session_id,mission_id=mission.id,
                 result_path=str((directory/'result.json').resolve()),
                 prepared_path=str((directory/'prepared_result.json').resolve()),
                 ack_path=str((directory/'ack.json').resolve()),status_path=str((directory/'status.json').resolve()))
    session['audio_path']=str((directory/'audio_release.json').resolve())
    session['snapshot_path']=str((directory/'tactical_snapshot.json').resolve())
    session['control_path']=str((directory/'control.json').resolve())
    fingerprint_payload={k:v for k,v in payload.items() if k not in {'session','audio','resume_snapshot'}}
    session['handoff_fingerprint']=hashlib.sha256(json.dumps(fingerprint_payload,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    resume=payload.get('resume_snapshot')
    if resume is not None:
        resume['source_session_id']=resume['session_id']
        resume['session_id']=session_id
        if resume.get('handoff_fingerprint')!=session['handoff_fingerprint']:
            raise ValueError('Tactical snapshot belongs to a changed deployment or map')
    payload['session']=session
    path=directory/'handoff.json'
    atomic_json(path,payload)
    if resume is not None:
        atomic_json(session['snapshot_path'], resume)
    superseded=[key for key,value in game_state.combat_sessions.items() if value.get('status')=='pending']
    for previous in game_state.combat_sessions.values():
        if previous.get('status')=='pending':previous['status']='superseded'
    game_state.combat_sessions[session_id]=dict(mission_id=mission.id,status='pending',
        session=session,superseded_sessions=superseded,expected_agents=payload['squad'],expected_support=payload['support_assets'],
        mission=mission.to_dict(),checkpoints={phase:str((directory/('campaign_'+phase+'.json')).resolve()) for phase in ['before','after']})
    if resume is not None:
        game_state.combat_sessions[session_id]['resumed_from_session']=resume['source_session_id']
    try:
        from .checkpoints import write_campaign_checkpoint
        write_campaign_checkpoint(game_state,session_id,'before')
    except (OSError,ValueError,TypeError):
        game_state.combat_sessions=previous_sessions
        raise
    return path,session


def result_digest(result):
    return hashlib.sha256(json.dumps({k:v for k,v in result.items() if k!='music_playback'},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def integer(value,field,minimum=0,maximum=1000000):
    if type(value) is not int or not minimum<=value<=maximum:
        raise ValueError(f'{field}: invalid integer')
    return value


def validate_result(result, record, session_id):
    try:json.dumps(result,allow_nan=False)
    except (ValueError,TypeError) as exc:raise ValueError('Combat result is not finite JSON') from exc
    if not isinstance(result,dict) or result.get('protocol_version')!=PROTOCOL_VERSION:
        raise ValueError('Unsupported combat result protocol')
    if result.get('session_id')!=session_id or result.get('mission_id')!=record['mission_id']:
        raise ValueError('Combat result belongs to another session or mission')
    if result.get('phase')!='confirmed' or not isinstance(result.get('outcome'),str) or result.get('outcome') not in {'victory','defeat','retreat'}:
        raise ValueError('Combat result has not been confirmed or has an invalid outcome')
    integer(result.get('turn_reached'),'turn_reached',1)
    initial=integer(result.get('initial_enemy_count'),'initial_enemy_count',0,10000)
    spawned=integer(result.get('enemies_spawned_total',initial),'enemies_spawned_total',initial,10000)
    integer(result.get('enemies_killed'),'enemies_killed',0,spawned)
    for group,expected,identity in [('agents',record['expected_agents'],'name'),('support',record['expected_support'],'id')]:
        rows=result.get(group)
        if not isinstance(rows,list):raise ValueError(f'Missing {group} state')
        reference={entry[identity]:entry for entry in expected}
        if len(reference)!=len(expected):raise ValueError('Ambiguous deployment identities')
        if len(rows)!=len(reference):raise ValueError(f'Incomplete {group} state')
        seen=set()
        for row in rows:
            if not isinstance(row,dict):raise ValueError(f'Invalid {group} row')
            key=row.get(identity)
            if not isinstance(key,str) or key not in reference or key in seen:raise ValueError(f'Unknown/duplicate {group} identity')
            seen.add(key)
            expected_hp=reference[key]['max_hp']
            if type(row.get('max_hp')) is not int or row.get('max_hp')!=expected_hp:raise ValueError('Unit maximum HP changed')
            integer(row.get('hp'),'hp',0,expected_hp)
            if 'stress' in row:integer(row['stress'],'stress',0,100)
            for name in ['kills','damage_dealt','damage_taken','actions_used']:
                if name in row:integer(row[name],name)
    # Do not accept economy commands from the combat engine.
    if any(k in result for k in ['funds_earned','xp_per_agent','rewards']):
        raise ValueError('Rewards must be calculated by the campaign resolver')
    return result_digest(result)


def read_session_status(path, session_id, mission_id):
    """A stale or partially written mailbox cannot declare another mission ready."""
    try:
        status = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    if not isinstance(status, dict):
        return None
    if (status.get('protocol_version') != PROTOCOL_VERSION
            or status.get('session_id') != session_id
            or status.get('mission_id') != mission_id
            or type(status.get('ready')) is not bool
            or status.get('event') not in {'combat_started', 'result_prepared', 'result_confirmed', 'error'}):
        return None
    return status


def acknowledge_applied_session(record, session_id):
    """A restarted Python host can release an already-confirmed results window."""
    if record.get('status') != 'applied':
        raise ValueError('Cannot acknowledge an unresolved session')
    digest = validate_result(record['confirmed_result'], record, session_id)
    if digest != record.get('result_digest'):
        raise ValueError('Stored result digest mismatch')
    atomic_json(record['session']['ack_path'], dict(protocol_version=PROTOCOL_VERSION,
        session_id=session_id,status='accepted',result_digest=digest))
