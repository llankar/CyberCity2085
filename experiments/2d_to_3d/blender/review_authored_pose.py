"""Render an explicit fitting stress pose; this is not a game animation."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector

folder = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
if folder.drive.upper() != 'E:':
    raise ValueError('External resources required')
bpy.ops.wm.open_mainfile(filepath=str(folder / 'authored_outfit.blend'))
rig = bpy.data.objects['rook_mpfb'].parent
for name, rotation in {
    'lowerarm_l': (1.1, 0, 0),
    'lowerarm_r': (0.9, 0, 0),
    'thigh_l': (-0.65, 0, 0),
    'calf_l': (0.8, 0, 0),
}.items():
    bone = rig.pose.bones.get(name)
    if bone is None:
        raise ValueError('Required pose bone missing: ' + name)
    bone.rotation_mode = 'XYZ'
    bone.rotation_euler = rotation
bpy.context.view_layer.update()
camera = bpy.context.scene.camera
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.05
for label, location in [('front', (0, -3.2, 1)), ('side', (3.2, 0, 1))]:
    camera.location = location
    camera.rotation_euler = (Vector((0, 0, 0.9)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = str(folder / ('stress_pose_' + label + '.png'))
    bpy.ops.render.render(write_still=True)
print('AUTHORED_STRESS_POSE_RENDERED')
