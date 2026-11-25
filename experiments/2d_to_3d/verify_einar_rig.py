"""Check the real game skeleton and diagnostic clip, without action overclaim."""
import json
import struct
import sys
from pathlib import Path

walk='--walk' in sys.argv
idle='--idle' in sys.argv or walk
bundle='--bundle' in sys.argv
equipped='--equipped' in sys.argv
surface_corrections='--surface-corrections' in sys.argv
ual=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--ual=')),None)
if equipped: ual='Pistol_Shoot'
if ual and not all(c.isalnum() or c=='_' for c in ual): raise ValueError('Invalid animation name')
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/('einar_pistol_fit01' if equipped else f'einar_ual_{ual}01' if ual else 'einar_motion01' if bundle else 'einar_walk01' if walk else 'einar_idle01' if idle else 'einar_rig01')
if surface_corrections:
    assert ual and not bundle
    folder=folder.with_name(folder.name+'_surfaces')
reference_folder=root/f'einar_ual_{ual}01' if equipped else root/'einar_idle01' if bundle else folder
if surface_corrections and equipped: reference_folder=reference_folder.with_name(reference_folder.name+'_surfaces')
report=json.loads((reference_folder/'rig_report.json').read_text())
payload=(folder/('human_pistol.glb' if equipped else 'human_motion.glb' if bundle else 'human_rig.glb')).read_bytes()
magic,version,length=struct.unpack_from('<III',payload)
assert (magic,version,length)==(0x46546C67,2,len(payload))
size,kind=struct.unpack_from('<II',payload,12)
assert kind==0x4E4F534A
data=json.loads(payload[20:20+size])
binary_start=28+size
def weight_vectors(index):
    accessor=data['accessors'][index]; view=data['bufferViews'][accessor['bufferView']]
    assert accessor['componentType']==5126 and accessor['type']=='VEC4'
    start=binary_start+view.get('byteOffset',0)+accessor.get('byteOffset',0)
    stride=view.get('byteStride',16)
    return [struct.unpack_from('<4f',payload,start+i*stride) for i in range(accessor['count'])]
expected_meshes=85 if equipped else 76
assert len(data['scenes'])==1 and len(data['meshes'])==expected_meshes
assert len(data['skins'])==1 and len(data['skins'][0]['joints'])==report['joints']==222
clips=[ual] if ual else ['Idle','Walk'] if bundle else ['Walk' if walk else 'Idle' if idle else 'FittingStressTest']
assert sorted(a['name'] for a in data['animations'])==sorted(clips)
durations={}
for animation in data['animations']:
    duration=max(data['accessors'][sampler['input']]['max'][0] for sampler in animation['samplers'])
    durations[animation['name']]=duration
    reference=json.loads((root/('einar_walk01' if animation['name']=='Walk' else 'einar_idle01')/'rig_report.json').read_text()) if bundle else report
    if 'duration_s' in reference: assert abs(duration-reference['duration_s'])<.0001
assert all('JOINTS_0' in p['attributes'] and 'WEIGHTS_0' in p['attributes'] for m in data['meshes'] for p in m['primitives'])
max_weight_error=0.0; max_influences=0
for mesh in data['meshes']:
    for primitive in mesh['primitives']:
        attributes=primitive['attributes']
        first=weight_vectors(attributes['WEIGHTS_0'])
        second=weight_vectors(attributes['WEIGHTS_1']) if 'WEIGHTS_1' in attributes else [(0,0,0,0)]*len(first)
        assert len(first)==len(second)
        for a,b in zip(first,second):
            values=a+b
            assert all(0<=weight<=1.000001 for weight in values)
            max_weight_error=max(max_weight_error,abs(sum(values)-1))
            max_influences=max(max_influences,sum(weight>0 for weight in values))
assert max_weight_error<.00001 and max_influences<=8
assert report['neutral_max_vertex_error']<.0001
if ual:
    assert report['licensed_motion_retarget']['license']=='CC0 1.0'
    assert report['licensed_motion_retarget']['max_control_rotation_error_radians']<.01
else: assert report['source_head_rotation_radians']>(.005 if idle or bundle else .05)
assert all('bufferView' in image for image in data['images'])
result={'meshes':expected_meshes,'joints':222,'skins':1,'clips':clips,
        'neutral_max_vertex_error':report['neutral_max_vertex_error'],'bytes':len(payload),
        'max_influences':max_influences,'max_weight_sum_error':max_weight_error,
        'clip_durations_s':durations,'gameplay_animation_set':'INCOMPLETE','artistic_deformation':'NOT VERIFIED'}
(folder/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('EINAR_GAME_RIG_VERIFIED',json.dumps(result))
