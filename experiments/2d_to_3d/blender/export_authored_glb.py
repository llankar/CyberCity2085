"""Export a fitted authored outfit without destroying its Blender source."""
import sys
from pathlib import Path
import bpy

folder = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
if folder.drive.upper() != 'E:':
    raise ValueError('External output required')
bpy.ops.wm.open_mainfile(filepath=str(folder / 'authored_outfit.blend'))
rig = bpy.data.objects['rook_mpfb'].parent
pose_clip = '--pose-clip' in sys.argv
if pose_clip:
    bpy.context.scene.render.fps = 24
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 25
    rotations = {'lowerarm_l': 1.1, 'lowerarm_r': 0.9, 'thigh_l': -0.65, 'calf_l': 0.8}
    for name, angle in rotations.items():
        bone = rig.pose.bones[name]
        bone.rotation_mode = 'XYZ'
        for frame, value in [(1, 0), (25, angle)]:
            bone.rotation_euler = (value, 0, 0)
            bone.keyframe_insert(data_path='rotation_euler', frame=frame)
    rig.animation_data.action.name = 'FittingStressTest'
    bpy.context.scene.frame_set(1)
copies = []
for source in list(bpy.context.scene.objects):
    if source.type != 'MESH' or source.name == 'PreviewFloor' or source.hide_render:
        continue
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.collection.objects.link(obj)
    obj.name = source.name + '_Export'
    for slot in obj.material_slots:
        if not slot.material or not slot.material.use_nodes:
            continue
        slot.material = slot.material.copy()
        shader = next((n for n in slot.material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if shader and 'short' not in source.name.lower() and 'hair' not in source.name.lower():
            for link in list(shader.inputs['Alpha'].links):
                slot.material.node_tree.links.remove(link)
            shader.inputs['Alpha'].default_value = 1.0
            shader.inputs['Coat Weight'].default_value = 0.0
    if obj.data.shape_keys:
        mixed = obj.shape_key_add(name='ExportShape', from_mix=True)
        positions = [v.co.copy() for v in mixed.data]
        obj.shape_key_clear()
        for vertex, position in zip(obj.data.vertices, positions):
            vertex.co = position
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for modifier in list(obj.modifiers):
        if modifier.type != 'ARMATURE':
            if modifier.type == 'SUBSURF':
                modifier.levels = 1
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    copies.append(obj)
bpy.ops.object.select_all(action='DESELECT')
for obj in copies + [rig]:
    obj.select_set(True)
bpy.context.view_layer.objects.active = rig
filename = 'authored_pose_test.glb' if pose_clip else 'authored_outfit.glb'
bpy.ops.export_scene.gltf(filepath=str(folder / filename), export_format='GLB', use_selection=True, export_apply=False, export_animations=True)
print('AUTHORED_GLB_EXPORTED meshes=%s' % len(copies))
