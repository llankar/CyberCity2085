"""Separate real eye-surface material; preserve authored scan geometry/texture/rig."""
import json,hashlib
from pathlib import Path
import bpy
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');folder=root/'nathan_eyes01';folder.mkdir(exist_ok=True)
source=root/'renderpeople_nathan01/human.blend';source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
body=bpy.data.objects['Object_96'];rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST';bpy.context.view_layer.update()
parents=list(range(len(body.data.vertices)))
def find(i):
 while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
 return i
for edge in body.data.edges:
 a,b=map(find,edge.vertices);parents[a]=b
parts={}
for v in body.data.vertices:parts.setdefault(find(v.index),[]).append(v.index)
eye_ids=set();selected=[]
for ids in parts.values():
 points=[body.matrix_world @ body.data.vertices[i].co for i in ids]
 if len(ids) in (106,121) and min(p.z for p in points)>1.7 and max(p.z for p in points)<1.76:
  eye_ids.update(ids);selected.append({'first_vertex':ids[0],'vertices':len(ids)})
assert sorted(p['vertices'] for p in selected)==[106,106,121,121]
material=body.data.materials[0].copy();material.name='AuthoredEyePhototexture_CornealSurface'
shader=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
shader.inputs['Roughness'].default_value=.18
shader.inputs['IOR'].default_value=1.376
shader.inputs['Coat Weight'].default_value=.65
shader.inputs['Coat Roughness'].default_value=.035
material['modification']='Eye-only corneal material response; original photographed iris/sclera and geometry retained'
index=len(body.data.materials);body.data.materials.append(material);faces=0
for face in body.data.polygons:
 selected_vertices=[i in eye_ids for i in face.vertices]
 assert all(selected_vertices) or not any(selected_vertices),'Eye/body boundary classification crossed a face'
 if all(selected_vertices):face.material_index=index;faces+=1
assert faces>400
rig.data.pose_position='POSE';bpy.context.scene.frame_set(0)
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in bpy.context.scene.objects:obj.select_set(obj not in helpers)
bpy.context.view_layer.objects.active=rig
notice=(root/'renderpeople_nathan01/CREDITS.txt').read_text()+'\nModification: separate eye-only corneal response; authored iris texture, geometry,89joint skin and Walk retained. Not accepted Rook art.'
bpy.data.texts.new('EYE_MATERIAL_CREDITS').write(notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_extras=True,export_animations=True,export_animation_mode='SCENE',export_anim_scene_split_object=False,export_anim_single_armature=False,export_anim_slide_to_zero=True,export_copyright=notice)
(folder/'material_report.json').write_text(json.dumps({'source_blend_sha256':source_hash,'eye_islands':selected,'eye_faces':faces,'eye_vertices':len(eye_ids),'material':material.name,'roughness':.18,'ior':1.376,'coat_weight':.65,'coat_roughness':.035,'scope':'Material-only derivative; no new anatomy, texture recolor or accepted identity'},indent=2))
(folder/'CREDITS.txt').write_text(notice,encoding='utf8')
(folder/'surface_reference.json').write_bytes((root/'renderpeople_nathan01/surface_reference.json').read_bytes())
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
print('NATHAN_AUTHORED_EYE_MATERIAL',faces,len(eye_ids),flush=True)
