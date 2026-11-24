"""Bake supported robot surfaces with explicit coverage and isolated UVs."""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from charge_pbr import bake_object,channels

folder=Path(sys.argv[sys.argv.index('--')+1]).resolve()
if folder.drive.upper()!='E:': raise ValueError('Use E:')
folder.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/security_geometry01/security_geometry.blend',use_scripts=False)
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
scene=bpy.data.scenes.new('IsolatedRobotBake'); bpy.context.window.scene=scene
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=1
scene.render.bake.use_clear=True; scene.render.bake.margin=4
report={'total_meshes':len(objects),'baked':[],'unresolved':[],
        'credit':'Security Bot Rig (CC-BY) Blender Foundation | studio.blender.org',
        'license':'https://creativecommons.org/licenses/by/4.0/','rig_actions':'NOT EXPORTED'}
diagnostic=bpy.data.materials.new('UnresolvedMaterial_Diagnostic'); diagnostic.use_nodes=True
diagnostic.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.3,.1,.3,1)
for index,obj in enumerate(objects):
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj; obj.select_set(True)
    try:
        for slot in obj.material_slots: channels(slot.material)
    except ValueError as error:
        report['unresolved'].append({'object':obj.name,'reason':str(error)})
        for slot in obj.material_slots: slot.material=diagnostic
    else:
        bake_object(obj,folder,f'part_{index:03d}')
        report['baked'].append(obj.name)
    obj.select_set(False); scene.collection.objects.unlink(obj)
    (folder/'coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('ROBOT_PBR_COVERAGE',index+1,'/',len(objects),'baked',len(report['baked']),'unresolved',len(report['unresolved']),flush=True)
for obj in objects: scene.collection.objects.link(obj); obj.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'robot_pbr.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'robot_pbr.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False)
print('ROBOT_PBR_EXPORT_FINISHED',flush=True)
