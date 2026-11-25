"""Validate exported robot geometry and explicitly account for partial PBR coverage."""
import json
import struct
import sys
from pathlib import Path

folder=Path(sys.argv[1]).resolve()
rigged='--rigged' in sys.argv
if folder.drive.upper()!='E:': raise ValueError('Use E:')
coverage=json.loads((folder/'coverage.json').read_text())
assert len(coverage['baked'])+len(coverage['unresolved'])==coverage['total_meshes']
names=coverage['baked']+[entry['object'] for entry in coverage['unresolved']]
assert len(set(names))==len(names)
payload=(folder/('robot_idle.glb' if rigged else 'robot_pbr.glb')).read_bytes()
magic,version,length=struct.unpack_from('<III',payload)
assert magic==0x46546C67 and version==2 and length==len(payload)
size,kind=struct.unpack_from('<II',payload,12)
assert kind==0x4E4F534A
data=json.loads(payload[20:20+size])
assert len(data['scenes'])==1 and len(data['meshes'])==coverage['total_meshes']
triangles=sum(data['accessors'][p['indices']]['count']//3 for m in data['meshes'] for p in m['primitives'])
assert triangles==269209
assert all('bufferView' in image for image in data['images'])
if rigged:
    assert len(data['skins'])==1 and len(data['skins'][0]['joints'])==124
    assert len(data['animations'])==1 and data['animations'][0]['name']=='Idle'
    animation=data['animations'][0]
    assert abs(max(data['accessors'][s['input']]['max'][0] for s in animation['samplers'])-2)<.0001
    assert all('JOINTS_0' in p['attributes'] and 'WEIGHTS_0' in p['attributes'] for m in data['meshes'] for p in m['primitives'])
    for mesh in data['meshes']:
        for primitive in mesh['primitives']:
            accessor=data['accessors'][primitive['attributes']['WEIGHTS_0']]
            view=data['bufferViews'][accessor['bufferView']]
            assert accessor['componentType']==5126 and accessor['type']=='VEC4'
            offset=28+size+view.get('byteOffset',0)+accessor.get('byteOffset',0)
            for index in range(accessor['count']):
                weights=struct.unpack_from('<4f',payload,offset+index*view.get('byteStride',16))
                assert abs(sum(weights)-1)<.00001 and all(0<=w<=1 for w in weights)
baked_materials=[m for m in data['materials'] if m.get('name','').endswith('_GamePBR')]
assert len(baked_materials)==len(coverage['baked'])
for material in baked_materials:
    pbr=material['pbrMetallicRoughness']
    assert 'baseColorTexture' in pbr and 'metallicRoughnessTexture' in pbr
    assert 'normalTexture' in material
report={'meshes':len(data['meshes']),'triangles':triangles,'glb_bytes':len(payload),
        'pbr_meshes':len(coverage['baked']),'unresolved_meshes':len(coverage['unresolved']),
        'embedded_images':len(data['images']),'complete_material_coverage':not coverage['unresolved'],
        'artistic_fidelity':'NOT VERIFIED','rig_actions':'Idle head scan study only' if rigged else 'NOT EXPORTED'}
(folder/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ROBOT_PBR_COVERAGE_VERIFIED',json.dumps(report))
