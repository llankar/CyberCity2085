"""Evaluate a licensed Charge source into a separate static geometry GLB study."""
import json
import sys
from pathlib import Path
import bpy

source=Path(sys.argv[sys.argv.index('--')+1]).resolve()
output=Path(sys.argv[sys.argv.index('--')+2]).resolve()
if source.drive.upper()!='E:' or output.drive.upper()!='E:': raise ValueError('Use E:')
output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
collection=bpy.data.collections['CH-security_bot']
graph=bpy.context.evaluated_depsgraph_get()
derived=[]
for obj in list(collection.all_objects):
    if obj.type!='MESH' or not obj.name.startswith('GEO-') or obj.hide_render:
        continue
    evaluated=obj.evaluated_get(graph)
    mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=graph)
    if not mesh.vertices:
        bpy.data.meshes.remove(mesh)
        continue
    mesh.transform(obj.matrix_world)
    copy=bpy.data.objects.new(obj.name+'_Evaluated',mesh)
    derived.append(copy)
scene=bpy.data.scenes.new('StaticGeometryDerivative')
bpy.context.window.scene=scene
for obj in derived: scene.collection.objects.link(obj)
bpy.context.view_layer.update()
for obj in derived: obj.select_set(True)
bpy.context.view_layer.objects.active=derived[0]
triangles=0
for obj in derived:
    obj.data.calc_loop_triangles(); triangles+=len(obj.data.loop_triangles)
assert derived and triangles>1000
bpy.ops.wm.save_as_mainfile(filepath=str(output/'security_geometry.blend'))
diagnostic=bpy.data.materials.new('NeutralGeometryDiagnostic_NotFinalPBR')
diagnostic.use_nodes=True
shader=diagnostic.node_tree.nodes['Principled BSDF']
shader.inputs['Base Color'].default_value=(.2,.23,.26,1)
shader.inputs['Roughness'].default_value=.65
for obj in derived:
    if not obj.material_slots:
        obj.data.materials.append(diagnostic)
    for slot in obj.material_slots:
        slot.material=diagnostic
bpy.ops.export_scene.gltf(filepath=str(output/'security_geometry.glb'),export_format='GLB',
                        use_selection=True,export_animations=False,export_apply=True,
                        export_materials='EXPORT')
report={'source':str(source),'meshes':len(derived),'triangles':triangles,
        'license':'https://creativecommons.org/licenses/by/4.0/',
        'credit':'Security Bot Rig (CC-BY) Blender Foundation | studio.blender.org',
        'modifications':'Evaluated static geometry; world transforms baked; original rig/source preserved',
        'limitations':['No exported rig/actions','Diagnostic placeholder materials; film PBR bake pending','Not optimized or artistically accepted']}
(output/'export_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CHARGE_STATIC_GEOMETRY_EXPORTED',json.dumps(report),flush=True)
