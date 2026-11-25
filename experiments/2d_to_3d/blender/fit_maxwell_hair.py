"""Fit actual authored, licensed hair geometry to the first scanned-head candidate."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from acquire_maxwell_hair import qualify_grant
from glb_document import Glb

root=Path('E:/CyberCity2085-3d-lab');base=root/'generated/phase2';source=root/'sources/makehuman_maxwell_hair';out=base/'scanned_armor_hair01';out.mkdir(exist_ok=True)
grant=qualify_grant(json.loads((source/'publisher_pack_metadata.json').read_text()),(source/'elvs_maxwell_hair.mhclo').read_text(),(source/'maxwell_hair_mh.obj').read_text(),(source/'publisher_ccby_faq.html').read_text(encoding='utf8'))
for entry in json.loads((source/'acquisition.json').read_text())['files']:
 assert hashlib.sha256((source/entry['local_name']).read_bytes()).hexdigest()==entry['sha256'],'Acquired hair changed'
bpy.ops.wm.open_mainfile(filepath=str(base/'scanned_armor_head01/human_actions.blend'),use_scripts=False)
scene=bpy.data.scenes['AuthoredGameActions'];bpy.context.window.scene=scene
rig=bpy.data.objects['AuthoredGameRig'];rig.data.pose_position='REST';bpy.context.view_layer.update()
head=bpy.data.objects['Game_ScannedHead'];head_points=[head.matrix_world@v.co for v in head.data.vertices]
before=set(scene.objects)
bpy.ops.wm.obj_import(filepath=str(source/'maxwell_hair_mh.obj'),forward_axis='NEGATIVE_Z',up_axis='Y')
imported=[o for o in scene.objects if o not in before and o.type=='MESH'];assert len(imported)==1
hair=imported[0];original=[hair.matrix_world@v.co for v in hair.data.vertices]
assert len(original)==765 and len(hair.data.polygons)==1468
low=Vector([min(p[i] for p in original) for i in range(3)]);high=Vector([max(p[i] for p in original) for i in range(3)])
assert 7<low.z<8 and 9<high.z<10,'Unexpected OBJ source axes'
head_low=Vector([min(p[i] for p in head_points) for i in range(3)]);head_high=Vector([max(p[i] for p in head_points) for i in range(3)])
scale=(head_high.x-head_low.x+.016)/(high.x-low.x)
translation=Vector(((head_high.x+head_low.x)/2-scale*(high.x+low.x)/2,head_high.y+.005-scale*high.y,head_high.z+.085-scale*high.z))
scalp_offset=Vector((0,-.01,-.045)) # calibrated from actual neutral profile; first bounds-only fit floated
translation+=scalp_offset
fit=Matrix.Translation(translation)@Matrix.Scale(scale,4)
source_to_bind=fit@hair.matrix_world
hair.data.transform(source_to_bind);hair.name='Game_MaxwellHair';hair.parent=rig;hair.matrix_world=Matrix.Identity(4)
for polygon in hair.data.polygons:polygon.use_smooth=True # OBJ has no authored normals/smoothing groups
group=hair.vertex_groups.new(name='head');group.add(list(range(len(hair.data.vertices))),1,'REPLACE')
modifier=hair.modifiers.new('AuthoredHeadBinding','ARMATURE');modifier.object=rig
material=bpy.data.materials.new('Elvaerwyn_MaxwellHair_OriginalTexture');material.use_nodes=True;material.use_backface_culling=False
nodes=material.node_tree.nodes;links=material.node_tree.links;shader=nodes.get('Principled BSDF')
shader.inputs['Roughness'].default_value=.7;shader.inputs['Metallic'].default_value=0
texture=nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(source/'maxhairtex6.png'),check_existing=True)
links.new(texture.outputs['Color'],shader.inputs['Base Color'])
cut=nodes.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=.35
links.new(texture.outputs['Alpha'],cut.inputs[0]);links.new(cut.outputs[0],shader.inputs['Alpha'])
material['source_author']='Elvaerwyn';material['source_grant_label']='CC_by / CC-BY';material['license_definition']='MakeHuman CC-BY FAQ refers to CC BY4.0'
hair.data.materials.clear();hair.data.materials.append(material)
rig.data.pose_position='POSE'
notice=(base/'scanned_armor_head01/CREDITS.txt').read_text()+'\n'+(source/'CREDITS.txt').read_text()+'\nModification: Maxwell hair uniformly fitted to scanned head and rigidly head-skinned; original image/UV/triangles retained. Physically lit alpha-cut material replacing legacy shadeless/emissive settings. First fit, not accepted Rook hairstyle/contact. Assembly contribution CC BY-SA4.0.\n'
bpy.data.texts.new('AUTHORED_HAIR_CREDITS').write(notice)
for track in rig.animation_data.nla_tracks:track.mute=False
for obj in scene.objects:obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(out/'human_actions.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_keep_anim_armature=True,export_extras=True,export_copyright=notice)
portable=Glb(out/'human_actions.glb')
hair_material=next(m for m in portable.doc['materials'] if m.get('name')==material.name)
before_alpha=hair_material.get('alphaMode','OPAQUE')
assert before_alpha=='MASK' and abs(hair_material['alphaCutoff']-.35)<1e-6 and hair_material.get('doubleSided'), 'Native Blender mask export differs from shader'
meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==18
references={}
for track in rig.animation_data.nla_tracks:
 for other in rig.animation_data.nla_tracks:other.mute=other!=track
 samples=[]
 for index in range(9):
  frame=track.strips[0].frame_end*index/8;scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
  graph=bpy.context.evaluated_depsgraph_get();geometry={}
  for obj in meshes:
   evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
   geometry[obj.name]=[list(evaluated.matrix_world@data.vertices[i].co) for i in range(0,len(data.vertices),max(1,len(data.vertices)//12))]
   evaluated.to_mesh_clear()
  samples.append({'time_s':frame/120,'meshes':geometry})
 references[track.name]=samples
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Idle'
scene.frame_set(0);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human_actions.blend'))
(out/'source_surface_reference.json').write_text(json.dumps(references))
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'hair_fit_report.json').write_text(json.dumps({'vertices':765,'triangles':1468,'uniform_scale':scale,'manual_scalp_offset_blender_m':list(scalp_offset),'smooth_normals':True,'source_to_bind_blender':[list(row) for row in source_to_bind],'world_fit_blender':[list(row) for row in fit],'original_texture_sha256':hashlib.sha256((source/'maxhairtex6.png').read_bytes()).hexdigest(),'native_blender_alpha_mode':before_alpha,'alpha_cutoff':.35,'double_sided':True,'portable_metadata_overridden':False,'source_shader_emission_adopted':False,'grant':grant,'limitations':['Bounds/profile fit, not scalp collision/contact solver','No claim of source full PBR maps or accepted Rook hair']},indent=2))
print('AUTHORED_MAXWELL_HAIR_FITTED',scale,len(meshes),before_alpha,flush=True)
