"""Create a tactical-scale derivative without editing licensed source geometry."""
import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--source', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--height', type=float, default=2.4)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
source, output = Path(args.source).resolve(), Path(args.output).resolve()
if output.drive.upper() != 'E:' or not 0.5 <= args.height <= 10:
    raise ValueError('Use E: and a plausible tactical height')
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()
meshes = [o for o in scene.objects if o.type == 'MESH']
rigs = [o for o in scene.objects if o.type == 'ARMATURE']
for rig in rigs:
    rig.data.pose_position = 'REST'
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
for obj in meshes:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    points.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
    evaluated.to_mesh_clear()
for rig in rigs:
    rig.data.pose_position = 'POSE'
low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
original_height = high.z - low.z
assert original_height > 0
roots = [o for o in scene.objects if o.parent is None]
root = bpy.data.objects.new('TacticalScaleRoot', None)
scene.collection.objects.link(root)
for obj in roots:
    obj.parent = root
factor = args.height / original_height
root.scale = (factor,) * 3
root.location = (-factor * (low.x + high.x) / 2,
                 -factor * (low.y + high.y) / 2, -factor * low.z)
bpy.context.view_layer.update()
actions = {action.name: list(action.frame_range) for action in bpy.data.actions}
report = {'source': str(source), 'source_height': original_height,
          'target_height': args.height, 'scale': factor, 'mesh_count': len(meshes),
          'actions': actions, 'geometry_modified': False,
          'note': 'Evaluated rest-pose vertex height; animation envelope may differ.'}
(output / 'normalization.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'george_tactical.blend'))
bpy.ops.export_scene.gltf(filepath=str(output / 'george_tactical.glb'),
                        export_format='GLB', export_animations=True,
                        export_animation_mode='NLA_TRACKS')
print('TACTICAL_ROBOT_NORMALIZED ' + json.dumps(report))
