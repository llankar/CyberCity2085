"""Validate exported robot geometry and explicitly account for partial PBR coverage."""
import json
import struct
import sys
from pathlib import Path

folder=Path(sys.argv[1]).resolve()
if folder.drive.upper()!='E:': raise ValueError('Use E:')
coverage=json.loads((folder/'coverage.json').read_text())
assert len(coverage['baked'])+len(coverage['unresolved'])==coverage['total_meshes']
names=coverage['baked']+[entry['object'] for entry in coverage['unresolved']]
assert len(set(names))==len(names)
payload=(folder/'robot_pbr.glb').read_bytes()
magic,version,length=struct.unpack_from('<III',payload)
assert magic==0x46546C67 and version==2 and length==len(payload)
size,kind=struct.unpack_from('<II',payload,12)
assert kind==0x4E4F534A
data=json.loads(payload[20:20+size])
assert len(data['scenes'])==1 and len(data['meshes'])==coverage['total_meshes']
triangles=sum(data['accessors'][p['indices']]['count']//3 for m in data['meshes'] for p in m['primitives'])
assert triangles==269209
assert all('bufferView' in image for image in data['images'])
baked_materials=[m for m in data['materials'] if m.get('name','').endswith('_GamePBR')]
assert len(baked_materials)==len(coverage['baked'])
for material in baked_materials:
    pbr=material['pbrMetallicRoughness']
    assert 'baseColorTexture' in pbr and 'metallicRoughnessTexture' in pbr
    assert 'normalTexture' in material
report={'meshes':len(data['meshes']),'triangles':triangles,'glb_bytes':len(payload),
        'pbr_meshes':len(coverage['baked']),'unresolved_meshes':len(coverage['unresolved']),
        'embedded_images':len(data['images']),'complete_material_coverage':not coverage['unresolved'],
        'artistic_fidelity':'NOT VERIFIED','rig_actions':'NOT EXPORTED'}
(folder/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ROBOT_PBR_COVERAGE_VERIFIED',json.dumps(report))
