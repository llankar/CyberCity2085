"""Check actual partial-human export, explicitly preserving unconverted coverage."""
import json
import struct
import sys
from pathlib import Path

mechanics = '--mechanics' in sys.argv
folder = Path('E:/CyberCity2085-3d-lab/generated/phase2') / ('einar_pbr01' if mechanics else 'einar_dielectrics01')
coverage = json.loads((folder / 'coverage.json').read_text())
baked = coverage.get('baked', coverage.get('dielectric_baked', [])) + coverage.get('mechanical_baked', [])
names = baked + [entry['object'] for entry in coverage['unresolved']]
assert len(names) == len(set(names)) == coverage['total_meshes'] == 76
payload = (folder / ('human_pbr.glb' if mechanics else 'human_partial.glb')).read_bytes()
magic, version, length = struct.unpack_from('<III', payload)
assert (magic, version, length) == (0x46546C67, 2, len(payload))
size, kind = struct.unpack_from('<II', payload, 12)
assert kind == 0x4E4F534A
data = json.loads(payload[20:20 + size])
assert len(data['scenes']) == 1 and len(data['meshes']) == 76
assert not data.get('skins') and not data.get('animations')
triangles = sum(data['accessors'][p['indices']]['count'] // 3
                for mesh in data['meshes'] for p in mesh['primitives'])
assert triangles == 235726
assert all('bufferView' in image for image in data['images'])
materials = [m for m in data['materials'] if m.get('name', '').endswith(('_DielectricStudy', '_GamePBR'))]
assert len(materials) == len(baked) > 0
for material in materials:
    assert 'baseColorTexture' in material['pbrMetallicRoughness']
    assert 'metallicRoughnessTexture' in material['pbrMetallicRoughness']
    assert 'normalTexture' in material
result = {'meshes': 76, 'triangles': triangles, 'bytes': len(payload),
          'converted_meshes': len(materials), 'unresolved_meshes': len(coverage['unresolved']),
          'embedded_images': len(data['images']), 'rig_actions': 'NOT EXPORTED',
          'artistic_acceptance': 'NOT VERIFIED', 'complete_material_coverage': not coverage['unresolved']}
(folder / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('HUMAN_DIELECTRICS_VERIFIED', json.dumps(result))
