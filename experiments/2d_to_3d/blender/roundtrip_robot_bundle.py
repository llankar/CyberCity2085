"""Verify editability by re-exporting the saved robot Blend, not rebuilding it."""
import hashlib
import json
import shutil
import sys
from bisect import bisect_right
import numpy as np
from pathlib import Path
import bpy
sys.path.insert(0, str(Path(__file__).parent.parent))
from glb_document import Glb
from quaternion_sampling import slerp

root = Path('E:/CyberCity2085-3d-lab/generated/phase2')
source = root / 'security_bundle01'
out = root / 'security_roundtrip01'
out.mkdir(exist_ok=True)
blend = source / 'robot_actions.blend'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
before = digest(blend)
bpy.ops.wm.open_mainfile(filepath=str(blend), use_scripts=False)
scene = bpy.context.scene
assert scene.render.fps == 30
scene.render.fps = 120
rigs = [obj for obj in scene.objects if obj.type == 'ARMATURE']
assert len(rigs) == 1
rig = rigs[0]
helpers = {bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
meshes = [obj for obj in scene.objects if obj.type == 'MESH' and obj not in helpers]
assert len(meshes) == 124
original = Glb(source / 'robot_actions.glb').doc
source_names = {original['meshes'][node['mesh']]['name']: node['name']
                for node in original['nodes'] if 'mesh' in node}
assert len(source_names) == 124
for name in source_names.values():
    collision = bpy.data.objects.get(name)
    if collision:
        collision.name = '__ImportOnly_' + name
for obj in meshes:
    # Blender's importer uses mesh datablock names for these skinned objects.
    # Restore the exact reviewed node identity from the source GLB, never guess
    # a suffix-normalization rule that could conflate different cable parts.
    assert obj.data.name in source_names, obj.data.name
    obj.name = source_names[obj.data.name]
owners = [rig, *[obj.data.shape_keys for obj in meshes if obj.data.shape_keys]]
tracks = {}
resampled_actions = set()
resampled_paths = 0
for owner in owners:
    animation = owner.animation_data
    if not animation:
        continue
    animation.action = None
    tracks[owner.name] = [track.name for track in animation.nla_tracks]
    assert set(tracks[owner.name]) == {'Idle', 'Walk', 'Melee', 'Hit', 'Death'}
    for track in animation.nla_tracks:
        track.mute = False
        assert len(track.strips) == 1
        strip = track.strips[0]
        # glTF importer places time zero at Blender frame1. Preserve source
        # key timing but remove that import-only offset on every animated owner.
        assert abs(strip.frame_start - 1) < 1e-5
        original_end = strip.frame_end
        original_scale = strip.scale
        strip.frame_start_ui = 0
        assert abs(strip.frame_end - (original_end - 1)) < 1e-5
        assert abs(strip.scale - original_scale) < 1e-5
        # Source Idle knots are24Hz, the other clips30Hz. Sampling at their
        # common multiple preserves piecewise-linear corrective motion.
        strip.scale *= 4
        action = strip.action
        if action in resampled_actions:
            continue
        resampled_actions.add(action)
        for layer in action.layers:
            for action_strip in layer.strips:
                for bag in action_strip.channelbags:
                    paths = {}
                    for curve in bag.fcurves:
                        if curve.data_path.endswith('rotation_quaternion'):
                            paths.setdefault(curve.data_path, {})[curve.array_index] = curve
                    for path, curves in paths.items():
                        assert set(curves) == {0,1,2,3}
                        knots = sorted({float(key.co.x) for curve in curves.values() for key in curve.keyframe_points})
                        rotations = [np.array([curves[i].evaluate(time) for i in range(4)]) for time in knots]
                        rotations = [q / np.linalg.norm(q) for q in rotations]
                        modes = {key.interpolation for curve in curves.values() for key in list(curve.keyframe_points)[:-1]}
                        if modes == {'CONSTANT'}:
                            assert all(abs(float(q @ rotations[0])) > 1-1e-7 for q in rotations), (action.name,path,'Varying STEP rotation')
                            continue
                        assert modes <= {'LINEAR'}, (action.name, path, modes)
                        times = sorted(set(knots) | {knots[0] + i / 4 for i in range(int(round((knots[-1]-knots[0])*4))+1)})
                        samples = []
                        for time in times:
                            index = max(0, min(len(knots)-1, bisect_right(knots,time)-1))
                            q = rotations[-1] if index == len(knots)-1 else slerp(rotations[index], rotations[index+1], (time-knots[index])/(knots[index+1]-knots[index]))
                            samples.append(q)
                        for component, curve in curves.items():
                            curve.keyframe_points.clear()
                            curve.keyframe_points.add(len(times))
                            for key, time, q in zip(curve.keyframe_points, times, samples):
                                key.co = (time, float(q[component]))
                                key.interpolation = 'LINEAR'
                            curve.update()
                        resampled_paths += 1
for obj in scene.objects:
    obj.select_set(obj == rig or obj in meshes)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.gltf(
    filepath=str(out / 'robot_actions.glb'), export_format='GLB',
    use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS',
    export_force_sampling=True, export_optimize_animation_size=False,
    export_optimize_animation_keep_anim_armature=True,
    export_optimize_animation_keep_anim_object=True, export_extras=True,
    export_copyright=bpy.data.texts['ASSET_CREDITS'].as_string())
assert digest(blend) == before
for name in ['bundle_report.json', 'CREDITS.txt']:
    shutil.copyfile(source / name, out / name)
(out / 'roundtrip_report.json').write_text(json.dumps({
    'source_blend_sha256': before, 'source_blend_unchanged': True,
    'source_glb_sha256': digest(source / 'robot_actions.glb'),
    'roundtrip_glb_sha256': digest(out / 'robot_actions.glb'),
    'tracks_by_owner': tracks, 'meshes': len(meshes),
    'slerp_resampled_quaternion_paths': resampled_paths,
    'scope': 'Re-export only; native deformation comparison required'}, indent=2))
print('ROBOT_SAVED_BLEND_REEXPORTED', len(tracks), flush=True)
