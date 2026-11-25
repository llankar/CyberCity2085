"""Inspect actual source-derived groom geometry and authored palette buffers."""
import json
import struct
import sys
from pathlib import Path
from glb_document import Glb

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2')/(sys.argv[1] if len(sys.argv)>1 else 'einar_groom02_layered_lod')
assert folder.resolve().drive.upper()=='E:'
report=json.loads((folder/'groom_report.json').read_text())
glb=Glb(folder/'authored_groom.glb'); data=glb.doc
assert len(data['meshes'])==4 and not data.get('skins') and not data.get('animations')
triangles=sum(data['accessors'][p['indices']]['count']//3 for m in data['meshes'] for p in m['primitives'])
assert triangles==sum(part['triangles'] for part in report['parts'])
stats={}
for mesh in data['meshes']:
    primitive=mesh['primitives'][0]
    color=primitive['attributes']['COLOR_0']; accessor=data['accessors'][color]
    assert accessor['componentType']==5126 and accessor['type']=='VEC3'
    values=[value[0] for value in struct.iter_unpack('<f',glb.values(color))]
    assert 0<=min(values)<max(values)<=1.00001 and len(set(values))>100
    stats[mesh['name']]={'min':min(values),'max':max(values),'mean':sum(values)/len(values)}
for part in report['parts']:
    assert 0<part['authored_diameter_range_m'][1]<.001
    assert 1.2<part['z_bounds'][0]<part['z_bounds'][1]<2.1
result={'meshes':4,'triangles':triangles,'bytes':(folder/'authored_groom.glb').stat().st_size,
        'palette':stats,'rig':'External rigid head binding; no jaw/expression rig','artistic_acceptance':'NOT VERIFIED'}
(folder/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('AUTHORED_GROOM_GEOMETRY_PALETTE_VERIFIED',json.dumps({'meshes':4,'triangles':triangles,'bytes':result['bytes']}))
