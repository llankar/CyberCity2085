"""Verify the actual static human GLB against its evaluation report, not artwork."""
import json
import struct
from pathlib import Path

folder = Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_geometry01')
report = json.loads((folder / 'geometry_report.json').read_text())
payload = (folder / 'einar_geometry.glb').read_bytes()
magic, version, length = struct.unpack_from('<III', payload)
assert (magic, version, length) == (0x46546C67, 2, len(payload))
size, kind = struct.unpack_from('<II', payload, 12)
assert kind == 0x4E4F534A
data = json.loads(payload[20:20 + size])
assert len(data['scenes']) == 1
assert len(data['meshes']) == report['meshes']
assert not data.get('skins') and not data.get('animations')
triangles = sum(data['accessors'][p['indices']]['count'] // 3
                for mesh in data['meshes'] for p in mesh['primitives'])
assert triangles == report['triangles_study'] < report['triangles_evaluated']
assert all('.proxy' not in mesh.get('name', '') for mesh in data['meshes'])
assert all('uri' not in buffer for buffer in data['buffers'])
result = {'meshes': len(data['meshes']), 'triangles': triangles,
          'bytes': len(payload), 'rig_actions': 'NOT EXPORTED',
          'materials': 'DIAGNOSTIC ONLY', 'artistic_acceptance': 'NOT VERIFIED'}
(folder / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('HUMAN_STATIC_GEOMETRY_VERIFIED', json.dumps(result))
