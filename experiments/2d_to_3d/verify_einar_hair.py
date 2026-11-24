"""Check actual strand derivative placement/coverage; never artistic acceptance."""
import json
import struct
from pathlib import Path

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_hair01')
report=json.loads((folder/'hair_report.json').read_text())
payload=(folder/'human_hair.glb').read_bytes()
magic,version,length=struct.unpack_from('<III',payload)
assert (magic,version,length)==(0x46546C67,2,len(payload))
size,kind=struct.unpack_from('<II',payload,12)
assert kind==0x4E4F534A
data=json.loads(payload[20:20+size])
assert len(data['scenes'])==1 and len(data['meshes'])==80
triangles=sum(data['accessors'][p['indices']]['count']//3 for mesh in data['meshes'] for p in mesh['primitives'])
assert triangles==235726+report['hair_triangles']
for part in report['parts']:
    assert 1.2<part['z_bounds'][0]<part['z_bounds'][1]<2.1
    assert part['triangles']>0
assert len(report['parts'])==4 and all('bufferView' in image for image in data['images'])
result={'meshes':80,'triangles':triangles,'hair_triangles':report['hair_triangles'],
        'bytes':len(payload),'placement_bounds':'PASS','artistic_acceptance':'NOT VERIFIED',
        'rig_actions':'NOT EXPORTED'}
(folder/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('EINAR_HAIR_GEOMETRY_VERIFIED',json.dumps(result))
