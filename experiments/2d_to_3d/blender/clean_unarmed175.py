"""Remove tiny disconnected reconstruction dust, preserving body components."""
from pathlib import Path
import json
import bpy
import bmesh

folder = Path('E:/CyberCity2085-3d-lab/generated/phase2/hunyuan175/rook_unarmed')
bpy.ops.wm.open_mainfile(filepath=str(folder/'review_upright/optimized.blend'), use_scripts=False)
removed = 0
components = []
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
for obj in meshes:
    bm = bmesh.new(); bm.from_mesh(obj.data)
    unseen = set(bm.verts); discard = []
    while unseen:
        seed = unseen.pop(); group = {seed}; stack = [seed]
        while stack:
            current = stack.pop()
            for edge in current.link_edges:
                other = edge.other_vert(current)
                if other in unseen:
                    unseen.remove(other); group.add(other); stack.append(other)
        faces = {face for vertex in group for face in vertex.link_faces}
        components.append({'vertices': len(group), 'faces': len(faces)})
        if len(faces) < 40:
            discard.extend(group)
    removed += len(discard)
    bmesh.ops.delete(bm, geom=discard, context='VERTS')
    bm.to_mesh(obj.data); bm.free()
for obj in bpy.context.scene.objects:
    obj.select_set(obj in meshes or obj.name == 'ReviewNormalization')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'clean.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'clean.glb'), export_format='GLB', use_selection=True)
(folder/'cleanup.json').write_text(json.dumps({'components': components, 'removed_vertices': removed,
    'scope': 'Tiny disconnected dust only; no body sculpting or rig acceptance'}, indent=2))
print('UNARMED175_CLEANED', removed, flush=True)
