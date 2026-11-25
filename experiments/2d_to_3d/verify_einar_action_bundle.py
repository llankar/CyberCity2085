"""Verify actual shared geometry, clip durations, morph resets and skin buffers."""
import hashlib
import json
import struct
import sys
from pathlib import Path
from glb_document import Glb

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
robot='--robot-bundle' in sys.argv
folder=root/('security_bundle01' if robot else 'einar_bundle02')
filename='robot_actions.glb' if robot else 'human_actions.glb'
expected_meshes=124 if robot else 76
expected_joints=124 if robot else 222
expected_images=496 if robot else 274
expected_triangles=269209 if robot else 235726
expected_clips={'Idle','Walk','Melee','Hit','Death'} if robot else {'Idle','Walk','Pistol_Shoot','Punch_Cross','Death01'}
report=json.loads((folder/'bundle_report.json').read_text())
glb=Glb(folder/filename); data=glb.doc
assert len(data['scenes'])==1 and len(data['skins'])==1
assert len(data['meshes'])==expected_meshes and len(data['skins'][0]['joints'])==expected_joints
assert {animation['name'] for animation in data['animations']}==expected_clips
assert all('bufferView' in image for image in data['images']) and len(data['images'])==expected_images
assert sum(data['accessors'][p['indices']]['count']//3 for m in data['meshes'] for p in m['primitives'])==expected_triangles
for source in report['sources']:
    assert hashlib.sha256((root/source['folder']/source.get('file','human_rig.glb')).read_bytes()).hexdigest()==source['sha256']
max_weight_error=0.0
for mesh in data['meshes']:
    count=report['union_targets'].get(mesh['name'],0)
    for primitive in mesh['primitives']:
        assert len(primitive.get('targets',[]))==count
        attributes=primitive['attributes']
        first=list(struct.iter_unpack('<4f',glb.values(attributes['WEIGHTS_0'])))
        second=list(struct.iter_unpack('<4f',glb.values(attributes['WEIGHTS_1']))) if 'WEIGHTS_1' in attributes else [(0,0,0,0)]*len(first)
        assert len(first)==len(second)
        for a,b in zip(first,second):
            assert all(0<=value<=1.000001 for value in a+b)
            max_weight_error=max(max_weight_error,abs(sum(a+b)-1))
assert max_weight_error<.00001
for animation in data['animations']:
    duration=max(data['accessors'][s['input']]['max'][0] for s in animation['samplers'])
    assert abs(duration-report['clips'][animation['name']])<.000001
    driven=set()
    for channel in animation['channels']:
        if channel['target']['path']!='weights': continue
        mesh=data['meshes'][data['nodes'][channel['target']['node']]['mesh']]
        sampler=animation['samplers'][channel['sampler']]
        assert data['accessors'][sampler['output']]['count']==data['accessors'][sampler['input']]['count']*report['union_targets'][mesh['name']]
        driven.add(mesh['name'])
    assert driven==report['union_targets'].keys(),'Every clip must drive all union corrections'
result={'meshes':expected_meshes,'joints':expected_joints,'skins':1,'triangles':expected_triangles,'images':expected_images,
        'clips':report['clips'],'max_weight_sum_error':max_weight_error,
        'bytes':(folder/filename).stat().st_size,'artistic_acceptance':'NOT VERIFIED'}
(folder/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('ROBOT_ACTION_BUNDLE_VERIFIED' if robot else 'EINAR_ACTION_BUNDLE_VERIFIED',json.dumps(result))
