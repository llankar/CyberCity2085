"""Verify source geometry/UV retention independently of artistic acceptance."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).parent))
from scanned_head_geometry import extract

root = Path('E:/CyberCity2085-3d-lab/generated/phase2')
out = root / 'diesel_scanned_head01'
bpy.ops.wm.open_mainfile(filepath=str(root / 'renderpeople_nathan01/human.blend'), use_scripts=False)
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
rig.data.pose_position = 'REST'
bpy.context.view_layer.update()
source = extract(rig, bpy.data.objects['Object_96'])
bpy.ops.wm.open_mainfile(filepath=str(root / 'diesel_candidate01/human.blend'), use_scripts=False)
outfit = {}
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and any(token in obj.name.lower() for token in ('boots', 'jacket', 'pants', 'shirt')):
        outfit[obj.name] = ([tuple(v.co) for v in obj.data.vertices],
                            [list(f.vertices) for f in obj.data.polygons],
                            [tuple(v.uv) for v in obj.data.uv_layers.active.data])
assert len(outfit) == 4
report = json.loads((out / 'fit_report.json').read_text())
fit = Matrix(report['fit_matrix'])
bpy.ops.wm.open_mainfile(filepath=str(out / 'human.blend'), use_scripts=False)
head = bpy.data.objects['ScannedNathanHead']
assert len(head.data.vertices) == len(source['positions'])
assert [list(f.vertices) for f in head.data.polygons] == source['faces']
position_error = max((v.co - fit @ p).length for v, p in zip(head.data.vertices, source['positions']))
uv_error = max((v.uv.x-u[0])**2+(v.uv.y-u[1])**2 for v, u in zip(head.data.uv_layers.active.data, source['uv']))
assert position_error < 1e-6, position_error
assert uv_error < 1e-12, uv_error
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
assert len(rig.data.bones) == 65
helpers = {bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
assert len([o for o in bpy.context.scene.objects if o.type == 'MESH' and o not in helpers]) == 6
assert head.modifiers[0].object == rig
assert len(head.vertex_groups) == 2
for name, (vertices, faces, uvs) in outfit.items():
    mesh = bpy.data.objects[name].data
    assert [tuple(v.co) for v in mesh.vertices] == vertices, name
    assert [list(f.vertices) for f in mesh.polygons] == faces, name
    assert [tuple(v.uv) for v in mesh.uv_layers.active.data] == uvs, name
texture = next(n.image for n in head.data.materials[0].node_tree.nodes if n.type == 'TEX_IMAGE')
source_image = Path('E:/CyberCity2085-3d-lab/sources/renderpeople_nathan/textures/rp_nathan_animated_003_mat_baseColor.jpeg')
assert bytes(texture.packed_file.data) == source_image.read_bytes()
result = {'status': 'PASS', 'scope': 'Saved Blender head geometry, UV, phototexture and rig retention only; artistic acceptance NOT VERIFIED',
          'maximum_position_error_m': position_error, 'maximum_uv_squared_error': uv_error,
          'triangles': len(source['faces']), 'bones': len(rig.data.bones), 'unchanged_outfit_meshes': sorted(outfit),
          'glb_sha256': hashlib.sha256((out/'human.glb').read_bytes()).hexdigest()}
assert result['glb_sha256'] == report['glb_sha256']
(out/'source_retention.json').write_text(json.dumps(result, indent=2), encoding='utf8')
print('DIESEL_HEAD_SOURCE_RETENTION_PASS', flush=True)
