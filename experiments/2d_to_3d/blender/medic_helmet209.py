"""Reuse an already acquired authored helmet as a detachable medic accessory."""
from pathlib import Path
import bpy,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/medic209';OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
source=LAB/'generated/phase2/rocketbox_military03/accessories01/accessories.blend'
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
 loaded.objects=['AuthoredProp_5028']
helmet=loaded.objects[0];assert helmet is not None
bpy.context.collection.objects.link(helmet);bpy.context.view_layer.update()
points=[helmet.matrix_world@v.co for v in helmet.data.vertices]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
center=(lo+hi)/2;scale=.29/(hi.x-lo.x)
helmet.data=helmet.data.copy();helmet.data.transform(Matrix.Scale(scale,4)@Matrix.Translation(-center)@helmet.matrix_world)
helmet.parent=None;helmet.matrix_world=Matrix.Identity(4)
for modifier in list(helmet.modifiers):
 if modifier.type=='ARMATURE':helmet.modifiers.remove(modifier)
helmet.name='AuthoredMedicHelmet209';helmet.select_set(True);bpy.context.view_layer.objects.active=helmet
assert len(helmet.data.vertices)>100,'Unexpected placeholder instead of authored helmet'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'helmet.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'helmet.glb'),export_format='GLB',use_selection=True)
(OUT/'accessory.json').write_text(json.dumps({'source':str(source),'authored_object':'AuthoredProp_5028','width_m':.29,'dimensions_m':list((hi-lo)*scale),'vertices':len(helmet.data.vertices),'scope':'detachable source helmet; body/rig/animations unchanged'},indent=2))
print('MEDIC209_HELMET_READY',list((hi-lo)*scale),flush=True)
