"""Validate runtime snapshots; never import combat-engine data into campaign saves."""
from copy import deepcopy
import json
import math
import re
from pathlib import Path

FIELDS = ('initial_enemy_count', 'turn_side', 'turn_number', 'enemy_turn_timer',
          'active_player_index', '_queued_player_index', 'selected_target_index',
          'selected_action', 'pending_end_turn_confirmation', 'show_combat_log', 'objective_progress',
          'objective_completed', 'overwatch_indices', 'defend_indices', 'combat_log')
GRID = (40, 28)


def whole(value, low, high):
    return (type(value) in (int, float) and math.isfinite(value)
            and low <= value <= high and int(value) == value)


def cell(value):
    return (isinstance(value, list) and len(value) == 2
            and all(whole(v, 0, bound-1) for v, bound in zip(value, GRID)))


def validate_tactical_snapshot(snapshot, record):
    try:
        json.dumps(snapshot, allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise ValueError('Snapshot is not finite JSON') from exc
    if not isinstance(snapshot, dict) or snapshot.get('protocol_version') != 2 or snapshot.get('snapshot_version') != 1:
        raise ValueError('Unsupported tactical snapshot')
    for key in ('session_id', 'mission_id', 'handoff_fingerprint'):
        if not snapshot.get(key) or snapshot[key] != record['session'].get(key):
            raise ValueError('Snapshot identity mismatch: '+key)
    state = snapshot.get('state')
    if not isinstance(state, dict) or any(key not in state for key in FIELDS):
        raise ValueError('Incomplete tactical state')
    if state['turn_side'] not in ('player', 'enemy') or not whole(state['turn_number'], 1, 100000):
        raise ValueError('Invalid tactical turn')
    if not whole(state['initial_enemy_count'], 0, 10000) or not whole(state['objective_progress'], 0, 100000):
        raise ValueError('Invalid tactical counters')
    if any(type(state[key]) is not bool for key in ('pending_end_turn_confirmation', 'objective_completed', 'show_combat_log')):
        raise ValueError('Invalid tactical flags')
    if not isinstance(state['selected_action'], str) or not isinstance(state['combat_log'], list) or len(state['combat_log']) > 10000 or any(not isinstance(line, str) for line in state['combat_log']):
        raise ValueError('Invalid tactical presentation')
    timer = state['enemy_turn_timer']
    if type(timer) not in (int, float) or not 0 <= timer <= 60:
        raise ValueError('Invalid enemy timer')
    for group in ('player_units', 'enemy_units', 'vehicle_units'):
        units = state.get(group)
        if not isinstance(units, list) or len(units) > 1000:
            raise ValueError('Invalid tactical unit group')
        for row in units:
            if (not isinstance(row, dict) or not cell(row.get('position'))
                    or not whole(row.get('max_hp'), 1, 1000000)
                    or not whole(row.get('hp'), 0, row['max_hp'])
                    or not whole(row.get('ap'), 0, 100000)
                    or not isinstance(row.get('status_effects', []), list)):
                raise ValueError('Invalid tactical unit')
            for key in ('stress', 'defense', 'initiative', 'aim', 'melee_power', 'damage_dealt', 'damage_taken', 'kills', 'actions_used'):
                if key in row and not whole(row[key], 0, 1000000):
                    raise ValueError('Invalid tactical unit statistic')
            if 'size_scale' in row and (type(row['size_scale']) not in (int, float) or not .1 <= row['size_scale'] <= 50):
                raise ValueError('Invalid tactical unit scale')
            for key in ('name', 'role', 'kind'):
                if key in row and not isinstance(row[key], str):
                    raise ValueError('Invalid tactical unit label')
            for key in ('status_effects', 'available_actions'):
                if key in row and (not isinstance(row[key], list) or any(not isinstance(value, str) for value in row[key])):
                    raise ValueError('Invalid tactical unit effects or actions')
    if state['initial_enemy_count'] > len(state['enemy_units']):
        raise ValueError('Invalid tactical encounter count')
    expected = record['expected_agents'] + record['expected_support']
    players = state['player_units']
    if len(players) != len(expected):
        raise ValueError('Deployment mismatch')
    for index, (row, original) in enumerate(zip(players, expected)):
        if (row.get('name') != original.get('name') or row.get('asset_id') != original.get('id')
                or row['max_hp'] != original['max_hp']):
            raise ValueError('Deployment identity mismatch')
        if index < len(record['expected_agents']) and row.get('role') != str(original['role']).lower():
            raise ValueError('Deployment role mismatch')
    for key, low, high in [('active_player_index', 0, max(0, len(players)-1)),
                           ('_queued_player_index', -1, len(players)-1),
                           ('selected_target_index', -1, max(0, len(state['enemy_units'])-1))]:
        if not whole(state[key], low, high):
            raise ValueError('Invalid tactical selection')
    for key in ('overwatch_indices', 'defend_indices'):
        if not isinstance(state[key], list) or any(not whole(i, 0, len(players)-1) for i in state[key]):
            raise ValueError('Invalid tactical posture')
    if not isinstance(state.get('objective'), dict) or not cell(state['objective'].get('cell')):
        raise ValueError('Invalid tactical objective')
    facings = snapshot.get('token_facings', {})
    if not isinstance(facings, dict):
        raise ValueError('Invalid token facing table')
    for key, facing in facings.items():
        if not isinstance(key, str) or not re.fullmatch('[pev][0-9]+', key):
            raise ValueError('Invalid token identity')
        group = {'p':'player_units','e':'enemy_units','v':'vehicle_units'}[key[0]]
        if not whole(int(key[1:]), 0, len(state[group])-1) or not whole(facing, 0, 7):
            raise ValueError('Invalid token facing')
    camera = snapshot.get('camera')
    if not isinstance(camera, dict) or not isinstance(camera.get('position'), list) or len(camera['position']) != 2:
        raise ValueError('Invalid tactical camera')
    if 'viewport' in camera and (not isinstance(camera['viewport'], list) or len(camera['viewport'])!=2 or any(not whole(v,1,16384) for v in camera['viewport'])):
        raise ValueError('Invalid reference viewport')
    if any(type(camera.get(key)) is not bool for key in ('visual_mode','top_down')):
        raise ValueError('Invalid tactical projection')
    if any(type(v) not in (int, float) for v in camera['position']+[camera.get('zoom')]) or not .1 <= camera['zoom'] <= 3:
        raise ValueError('Invalid tactical camera')
    return snapshot


def prepare_resume_payload(game_state, mission, session_id):
    record = game_state.combat_sessions.get(session_id)
    if not record or record['status'] != 'pending' or record['mission_id'] != mission.id:
        raise ValueError('Only a pending matching mission can resume')
    channels = record['session']
    if any(Path(channels[key]).exists() for key in ('result_path', 'prepared_path')):
        raise ValueError('A result is available: confirm recovery instead of replaying combat')
    path = Path(channels.get('snapshot_path', ''))
    if not path.is_file() or path.stat().st_size > 8*1024*1024:
        raise ValueError('Tactical snapshot missing or too large')
    snapshot = validate_tactical_snapshot(json.loads(path.read_text(encoding='utf-8')), record)
    payload = json.loads(path.with_name('handoff.json').read_text(encoding='utf-8'))
    # Keep the deployed roster/map from this session, not a newly generated encounter.
    payload['resume_snapshot'] = deepcopy(snapshot)
    return payload


def resume_launch_failed(game_state, new_session_id):
    """A failed replacement must not invalidate the still-recoverable source."""
    record = game_state.combat_sessions[new_session_id]
    sources = record.get('superseded_sessions', [])
    if not sources:
        return
    record['status'] = 'abandoned'
    for source in sources:
        old = game_state.combat_sessions.get(source)
        if old and old['status'] == 'superseded':
            old['status'] = 'pending'
    from .checkpoints import write_campaign_checkpoint
    try:
        write_campaign_checkpoint(game_state, new_session_id, 'before')
    except OSError:
        game_state.add_event('Recovery launch failed; the original checkpoint is still available.')


def cancel_session_process(game_state, session_id):
    from .session_protocol import atomic_json
    channel = game_state.combat_sessions[session_id]['session'].get('control_path')
    if not channel:
        return  # Old protocol: never terminate an arbitrary PID from a save file.
    try:
        atomic_json(channel, dict(protocol_version=2,session_id=session_id,event='superseded'))
    except OSError:
        game_state.add_event('Inactive Godot session isolated; the old window may need closing manually.')


def cancel_superseded_processes(game_state, new_session_id):
    record = game_state.combat_sessions[new_session_id]
    for session_id in record.get('superseded_sessions', []):
        cancel_session_process(game_state, session_id)
