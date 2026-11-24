"""Static human conversion study: preserve evaluated source, optimize copies only."""
import json
from pathlib import Path
import bpy

folder = Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_geometry01')
folder.mkdir(parents=True, exist_ok=True)
source = 'E:/CyberCity2085-3d-lab/sources/charge_studio/einar_release_v1.blend'
bpy.ops.wm.open_mainfile(filepath=source, use_scripts=False)
for obj in bpy.data.objects:
    if obj.animation_data:
        for driver in obj.animation_data.drivers:
            if 'RIG-Displacement' in driver.data_path:
                driver.mute = True
    for modifier in obj.modifiers:
        if modifier.type == 'NODES' and 'Displacement' in modifier.name:
            modifier.show_render = False
            modifier.show_viewport = False
collection = bpy.data.collections['CH-einar']
graph = bpy.context.evaluated_depsgraph_get()
copies = []
before = 0
for obj in collection.all_objects:
    if obj.type != 'MESH' or obj.hide_render or not obj.visible_get() or not obj.name.startswith('GEO-'):
        continue
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(graph), preserve_all_data_layers=True, depsgraph=graph)
    if not mesh.polygons:
        bpy.data.meshes.remove(mesh)
        continue
    mesh.transform(obj.matrix_world)
    mesh.calc_loop_triangles()
    before += len(mesh.loop_triangles)
    copies.append(bpy.data.objects.new(obj.name + '_GameStudy', mesh))
    print('HUMAN_EVALUATED', obj.name, len(mesh.loop_triangles), flush=True)
scene = bpy.data.scenes.new('HumanStaticConversionStudy')
bpy.context.window.scene = scene
for obj in copies:
    scene.collection.objects.link(obj)
bpy.context.view_layer.update()
# Save untouched evaluated geometry/materials for subsequent texture baking.
bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'einar_evaluated.blend'))
diagnostic = bpy.data.materials.new('GeometryOnly_NotFinalHumanMaterials')
diagnostic.use_nodes = True
diagnostic.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.24, .27, .3, 1)
diagnostic.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .65
after = 0
for obj in copies:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    count = len(obj.data.loop_triangles)
    if count > 500:
        modifier = obj.modifiers.new('StaticStudyDecimate', 'DECIMATE')
        modifier.ratio = min(1.0, 90000 / max(before, 1))
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.calc_loop_triangles()
    after += len(obj.data.loop_triangles)
    obj.data.materials.clear()
    obj.data.materials.append(diagnostic)
for obj in copies:
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(folder / 'einar_geometry.glb'), export_format='GLB',
                         use_selection=True, use_active_scene=True, export_animations=False)
report = {'source': source, 'meshes': len(copies), 'triangles_evaluated': before,
          'triangles_study': after, 'credit': 'Einar Rig (CC-BY) Blender Foundation | studio.blender.org',
          'license': 'https://creativecommons.org/licenses/by/4.0/',
          'limitations': ['Static diagnostic geometry only; not artistic acceptance',
                          'No film hair curves converted', 'No game rig or actions',
                          'Material baking and neutral textured comparison pending',
                          'Decimation has not been checked for deforming topology']}
(folder / 'geometry_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
assert copies and after > 1000 and after <= before
print('CHARGE_HUMAN_GEOMETRY_OK', json.dumps(report), flush=True)
