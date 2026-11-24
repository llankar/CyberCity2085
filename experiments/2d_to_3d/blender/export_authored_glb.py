"""Export a fitted authored outfit without destroying its Blender source."""
import sys
import json
from pathlib import Path
import bpy

folder = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
if folder.drive.upper() != 'E:':
    raise ValueError('External output required')
bpy.ops.wm.open_mainfile(filepath=str(folder / 'authored_outfit.blend'))
rig = bpy.data.objects['rook_mpfb'].parent
pose_clip = '--pose-clip' in sys.argv
realtime = '--realtime' in sys.argv
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
    if realtime:
        obj.data.calc_loop_triangles()
        triangles = len(obj.data.loop_triangles)
        budget = 12000
        if 'armor' in source.name.lower():
            budget = 30000
        elif 'short' in source.name.lower():
            budget = 6000
        elif 'high-poly' in source.name.lower():
            budget = 2000
        if triangles > budget:
            simplify = obj.modifiers.new('RealtimeDerivative', 'DECIMATE')
            simplify.ratio = budget / triangles
            simplify.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier=simplify.name)
        obj.data.calc_loop_triangles()
        print('REALTIME_MESH', source.name, triangles, '->', len(obj.data.loop_triangles))
    copies.append(obj)
bpy.ops.object.select_all(action='DESELECT')
for obj in copies + [rig]:
    obj.select_set(True)
bpy.context.view_layer.objects.active = rig
filename = 'authored_pose_test.glb' if pose_clip else 'authored_outfit.glb'
if realtime:
    filename = filename.replace('.glb', '_realtime.glb')
bpy.ops.export_scene.gltf(filepath=str(folder / filename), export_format='GLB', use_selection=True, export_apply=False, export_animations=True)
if (folder / 'material_factors.json').is_file():
    sys.path.insert(0, str(Path(__file__).parent))
    from glb_material_factors import apply_material_factors
    print('GLTF_MATERIAL_FACTORS', apply_material_factors(folder / filename,
          json.loads((folder / 'material_factors.json').read_text(encoding='utf-8'))))
print('AUTHORED_GLB_EXPORTED meshes=%s' % len(copies))
