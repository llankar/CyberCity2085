"""Python-owned atomic campaign checkpoints, separate from combat result files."""
from __future__ import annotations
import json
from pathlib import Path
from game.gamestate import GameState
from .session_protocol import atomic_json


def write_campaign_checkpoint(state,session_id,phase):
    if phase not in {'before','after'}:raise ValueError('Invalid checkpoint phase')
    record=state.combat_sessions[session_id]
    path=Path(record['checkpoints'][phase])
    path.parent.mkdir(parents=True,exist_ok=True)
    serialized=path.with_suffix('.serialize.tmp')
    try:
        state.save(str(serialized))
        data=json.loads(serialized.read_text(encoding='utf-8'))
        data['_combat_checkpoint']=dict(protocol_version=2,session_id=session_id,phase=phase)
        atomic_json(path,data)
    finally:
        serialized.unlink(missing_ok=True)


def checkpoint_info(path):
    path=Path(path)
    data=json.loads(path.read_text(encoding='utf-8'))
    marker=data.get('_combat_checkpoint',{})
    if marker.get('protocol_version')!=2 or marker.get('phase') not in {'before','after'}:
        raise ValueError('Not a versioned combat checkpoint')
    session_id=marker.get('session_id')
    if not isinstance(session_id,str) or len(session_id)!=32 or any(c not in '0123456789abcdef' for c in session_id):
        raise ValueError('Invalid checkpoint session identity')
    record=data.get('combat_sessions',{}).get(session_id)
    if not isinstance(record,dict) or record.get('session',{}).get('session_id')!=session_id:
        raise ValueError('Checkpoint session mismatch')
    if marker['phase']=='after' and record.get('status')!='applied':
        raise ValueError('Post-combat checkpoint is not applied')
    return marker,record


def latest_combat_checkpoint(directory=Path('runtime/godot_combat/sessions')):
    candidates=[]
    for name in ['campaign_before.json','campaign_after.json']:
        for path in Path(directory).glob('*/'+name):
            try:candidates.append((path.stat().st_mtime_ns,path))
            except OSError:pass
    for _,path in sorted(candidates,key=lambda x:x[0],reverse=True):
        try:checkpoint_info(path)
        except (OSError,ValueError,KeyError,TypeError):continue
        return path
    return None


def load_combat_checkpoint(path):
    marker,_=checkpoint_info(path)
    state=GameState.load(str(path))
    # Relocate only this explicit checkpoint's channels when its directory moves.
    session_id=marker['session_id'];record=state.combat_sessions[session_id]
    directory=Path(path).resolve().parent
    for key,name in [('result_path','result.json'),('prepared_path','prepared_result.json'),('ack_path','ack.json'),('status_path','status.json'),('audio_path','audio_release.json')]:
        if key == 'audio_path' and key not in record['session']:
            continue
        record['session'][key]=str(directory/name)
    record['checkpoints']={phase:str(directory/('campaign_'+phase+'.json')) for phase in ['before','after']}
    return state,session_id
