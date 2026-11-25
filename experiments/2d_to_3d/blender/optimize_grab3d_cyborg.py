"""Create a separate realtime LOD while retaining the licensed source intact."""
import hashlib
import json
import struct
from pathlib import Path
import bpy

root = Path('E:/CyberCity2085-3d-lab/generated/phase2')
source = root/'grab3d_cyborg01'
out = root/'grab3d_cyborg_lod01'
out.mkdir(exist_ok=True)
source_hash = hashlib.sha256((source/'human.glb').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'), use_scripts=False)
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
helpers = {bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH' and o not in helpers)
rig.data.pose_position = 'REST'
bpy.context.view_layer.objects.active = mesh
for obj in bpy.context.scene.objects:
    obj.select_set(obj == mesh)
before = len(mesh.data.polygons)
modifier = mesh.modifiers.new('ExperimentalRealtimeLOD', 'DECIMATE')
modifier.ratio = .2
modifier.use_collapse_triangulate = True
bpy.ops.object.modifier_move_up(modifier=modifier.name)
bpy.ops.object.modifier_apply(modifier=modifier.name)
mesh.data.calc_loop_triangles()
triangles = len(mesh.data.loop_triangles)
assert 55_000 < triangles < 65_000, triangles
assert all(abs(sum(g.weight for g in v.groups)-1) < .001 for v in mesh.data.vertices)
discarded = max(sum(sorted((g.weight for g in v.groups), reverse=True)[4:]) for v in mesh.data.vertices)
bpy.ops.object.vertex_group_limit_total(limit=4)
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
assert all(len(v.groups) <= 4 for v in mesh.data.vertices)
rig.data.pose_position = 'POSE'
print('SOURCE_ANIMATION_TIMING', bpy.context.scene.render.fps,
      [(track.name, [(strip.frame_start,strip.frame_end,strip.action_frame_start,strip.action_frame_end) for strip in track.strips]) for track in rig.animation_data.nla_tracks], flush=True)
for track in rig.animation_data.nla_tracks:
    for strip in track.strips:
        strip.frame_start_ui = 0
for obj in bpy.context.scene.objects:
    obj.select_set(obj == rig or obj == mesh)
bpy.context.view_layer.objects.active = rig
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'), export_format='GLB',
    use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS',
    export_force_sampling=True, export_optimize_animation_size=False,
    export_extras=True, export_copyright=(source/'CREDITS.txt').read_text())
data = (out/'human.glb').read_bytes()
length = struct.unpack_from('<I', data, 12)[0]
document = json.loads(data[20:20+length])
clips = [clip.get('name') for clip in document.get('animations', [])]
assert set(clips) == {'walk', 'run'}, clips
assert hashlib.sha256((source/'human.glb').read_bytes()).hexdigest() == source_hash
(out/'CREDITS.txt').write_text((source/'CREDITS.txt').read_text(), encoding='utf8')
(out/'optimization_report.json').write_text(json.dumps({
    'source_glb_sha256': source_hash, 'glb_sha256': hashlib.sha256(data).hexdigest(),
    'original_faces': before, 'triangles': triangles, 'bones': len(rig.data.bones),
    'vertices': len(mesh.data.vertices), 'normalized_skin_weights': True, 'clips': clips,
    'maximum_weight_discarded_for_four_influence_limit': discarded,
    'limitations': ['Decimation deformation and silhouette require native visual inspection',
                    'No authored Rook identity or additional action clips']}, indent=2), encoding='utf8')
print('GRAB3D_REALTIME_LOD_EXPORTED', triangles, clips, flush=True)
