"""Measure actual hand and pistol landmarks, without changing the saved actor."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

root = Path('E:/CyberCity2085-3d-lab/generated/phase2/scanned_armor_shoot01')
bpy.ops.wm.open_mainfile(filepath=str(root/'pistol_fit01/human_pistol.blend'), use_scripts=False)
scene = bpy.data.scenes['AuthoredGameActions']
bpy.context.window.scene = scene
scene.frame_set(8)
bpy.context.view_layer.update()
rig = bpy.data.objects['AuthoredGameRig']
graph = bpy.context.evaluated_depsgraph_get()
bones = {bone.name: {'head': list(rig.matrix_world @ bone.head),
                     'tail': list(rig.matrix_world @ bone.tail)}
         for bone in rig.pose.bones if any(word in bone.name for word in
                                          ('finger_', 'hand.', 'forearm.', 'upper_arm.'))}
parts = {}
for obj in scene.objects:
    if not obj.name.startswith('EquippedPistol_'):
        continue
    evaluated = obj.evaluated_get(graph)
    mesh = evaluated.to_mesh()
    points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    parts[obj.name] = {'min': list(low), 'max': list(high), 'center': list((low+high)/2)}
    evaluated.to_mesh_clear()
output = {'frame': 8, 'bones': bones, 'pistol_parts': parts}
(root/'grip_landmarks.json').write_text(json.dumps(output, indent=2))
print('SCANNED_GRIP_LANDMARKS', json.dumps({name: value for name,value in parts.items() if 'trigger' in name}), flush=True)
