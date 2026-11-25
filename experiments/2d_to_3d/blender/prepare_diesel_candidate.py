"""Import one complete authored first-human alternative, preserving its source."""
import hashlib
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab')
source=root/'sources/diesel_character'
out=root/'generated/phase2/diesel_candidate01'
out.mkdir(exist_ok=True)
original=source/'Diesel.glb'
before=hashlib.sha256(original.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(original),merge_vertices=False)
scene=bpy.context.scene
rigs=[obj for obj in scene.objects if obj.type=='ARMATURE']
assert len(rigs)==1
rig=rigs[0]
assert len(rig.data.bones)==65
helpers={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
meshes=[obj for obj in scene.objects if obj.type=='MESH' and obj not in helpers]
assert len(meshes)==11
graph=bpy.context.evaluated_depsgraph_get()
points=[]
for obj in meshes:
    evaluated=obj.evaluated_get(graph)
    mesh=evaluated.to_mesh()
    points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
    evaluated.to_mesh_clear()
low=[min(point[i] for point in points) for i in range(3)]
high=[max(point[i] for point in points) for i in range(3)]
height=high[2]-low[2]
assert 1.4<height<2.3,('Unexpected source units',low,high)
for obj in helpers:obj.hide_render=True;obj.hide_set(True)
notice=(source/'CREDITS.txt').read_text()+'\nExperimental source-preserving first-human alternative. No animations added, no final Rook identity or art acceptance.\n'
bpy.data.texts.new('SOURCE_CREDITS').write(notice)
bpy.ops.file.pack_all()
assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
for obj in scene.objects:obj.select_set(obj==rig or obj in meshes)
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True,export_copyright=notice)
assert hashlib.sha256(original.read_bytes()).hexdigest()==before
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'import_report.json').write_text(json.dumps({'original_sha256':before,'source_unchanged':True,'derived_glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'meshes':len(meshes),'bones':len(rig.data.bones),'world_bounds_blender':[low,high],'height_m':height,'images':[{'name':image.name,'dimensions':list(image.size),'packed':bool(image.packed_file)} for image in bpy.data.images],'limitations':['Source T-pose only; no authored animation claims','No final Rook silhouette, face or outfit adaptation yet']},indent=2))
print('DIESEL_EDITABLE_CANDIDATE_READY',height,len(meshes),len(rig.data.bones),flush=True)
