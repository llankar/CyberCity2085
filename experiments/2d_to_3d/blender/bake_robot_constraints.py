"""Bake a mechanical fitting clip, preserving the constrained authoring source."""
import sys
from pathlib import Path
import bpy

folder = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
if folder.drive.upper() != 'E:':
    raise ValueError('External output required')
bpy.ops.wm.open_mainfile(filepath=str(folder / 'robot_blockout.blend'))
scene = bpy.context.scene
knee = bpy.data.objects['Knee_L']
for frame, angle in [(1, 0), (25, 0.6), (49, 0)]:
    knee.rotation_euler.x = angle
    knee.keyframe_insert(data_path='rotation_euler', frame=frame)
for obj in scene.objects:
    obj.select_set(obj.type in {'MESH', 'EMPTY'})
bpy.context.view_layer.objects.active = knee
bpy.ops.nla.bake(frame_start=1, frame_end=49, step=1, only_selected=True, visual_keying=True, clear_constraints=True, clear_parents=False, use_current_action=False, bake_types={'OBJECT'})
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'robot_baked_test.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder / 'robot_baked_test.glb'), export_format='GLB', use_selection=True, export_apply=True, export_animations=True, export_animation_mode='ACTIVE_ACTIONS')
print('ROBOT_CONSTRAINT_CLIP_BAKED frames=49')
