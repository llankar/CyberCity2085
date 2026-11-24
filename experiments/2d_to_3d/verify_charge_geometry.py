"""Check that the static GLB contains the evaluated mesh coverage reported by Blender."""
import json
import struct
import sys
from pathlib import Path

folder=Path(sys.argv[1]).resolve()
if folder.drive.upper()!='E:': raise ValueError('External geometry evidence required')
data=(folder/'security_geometry.glb').read_bytes()
magic,version,length=struct.unpack_from('<III',data)
assert magic==0x46546C67 and version==2 and length==len(data)
size,kind=struct.unpack_from('<II',data,12)
assert kind==0x4E4F534A
document=json.loads(data[20:20+size])
expected=json.loads((folder/'export_report.json').read_text())
triangles=sum(document['accessors'][p['indices']]['count']//3 for m in document['meshes'] for p in m['primitives'])
assert len(document['meshes'])==expected['meshes']
assert triangles==expected['triangles']
assert not document.get('skins') and not document.get('animations')
report={'meshes_verified':len(document['meshes']),'triangles_verified':triangles,
        'glb_bytes':len(data),'materials':'neutral diagnostic only',
        'rig_and_actions':'NOT EXPORTED','artistic_acceptance':'NOT VERIFIED'}
(folder/'geometry_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CHARGE_GEOMETRY_VERIFIED',json.dumps(report))
