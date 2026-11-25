"""Preserve a complete licensed source in editable Blender and native GLB."""
import hashlib
import json
import shutil
import struct
from pathlib import Path
import bpy

root = Path('E:/CyberCity2085-3d-lab')
source = root/'sources/grab3d_cyborg'
out = root/'generated/phase2/grab3d_cyborg01'
out.mkdir(exist_ok=True)
original = source/'cyborg-rigged.glb'
data = original.read_bytes()
size, kind = struct.unpack_from('<II', data, 12)
assert kind == 0x4e4f534a
document = json.loads(data[20:20+size])
assert all('uri' not in image for image in document.get('images', []))
assert all('uri' not in buffer for buffer in document.get('buffers', []))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(original), merge_vertices=False)
scene = bpy.context.scene
rigs = [obj for obj in scene.objects if obj.type == 'ARMATURE']
assert len(rigs) == 1
rig = rigs[0]
helpers = {bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
meshes = [obj for obj in scene.objects if obj.type == 'MESH' and obj not in helpers]
assert meshes and all(obj.vertex_groups for obj in meshes)
for obj in helpers:
    obj.hide_render = True
    obj.hide_set(True)
points = [obj.matrix_world@v.co for obj in meshes for v in obj.data.vertices]
low = [min(p[i] for p in points) for i in range(3)]
high = [max(p[i] for p in points) for i in range(3)]
assert 1.4 < high[2]-low[2] < 2.3, (low, high)
notice = (source/'LICENSE.txt').read_text()+'\nPublisher: https://grab3d.com/models/characters/cyborg/\nExperimental source-preserving comparison; not accepted Rook.\n'
bpy.data.texts.new('SOURCE_CREDITS').write(notice)
bpy.ops.file.pack_all()
assert all(image.packed_file for image in bpy.data.images if image.source == 'FILE')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
# Native comparison deliberately uses exact source bytes, not an unverified animation re-export.
shutil.copyfile(original, out/'human.glb')
(out/'CREDITS.txt').write_text(notice, encoding='utf8')
report = {'source_sha256': hashlib.sha256(data).hexdigest(),
          'source_unchanged': original.read_bytes() == data,
          'native_glb_is_exact_source': (out/'human.glb').read_bytes() == data,
          'meshes': len(meshes), 'bones': len(rig.data.bones),
          'triangles': sum(len(obj.data.loop_triangles) for obj in meshes),
          'world_bounds_blender': [low, high],
          'animations': [clip.get('name') for clip in document.get('animations', [])],
          'images': [{'name': image.name, 'dimensions': list(image.size), 'packed': bool(image.packed_file)} for image in bpy.data.images],
          'limitations': ['Source rig and actions require deformation inspection', 'No artistic or Rook likeness acceptance', 'Saved Blend animation re-export not verified']}
(out/'import_report.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print('GRAB3D_EDITABLE_CANDIDATE_READY', json.dumps(report), flush=True)
