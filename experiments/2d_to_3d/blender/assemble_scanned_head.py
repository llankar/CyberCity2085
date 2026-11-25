"""Traditional DCC assembly of licensed scanned anatomy and authored game armor.

No generated human geometry, texture recolor, source overwrite or runtime edit.
"""
import json,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from anatomical_groups import descendants

root=Path('E:/CyberCity2085-3d-lab');base=root/'generated/phase2';out=base/'scanned_armor_head01';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(base/'renderpeople_nathan01/human.blend'),use_scripts=False)
source_rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');source_rig.data.pose_position='REST'
bpy.context.view_layer.update();body=bpy.data.objects['Object_96'];body.data.calc_loop_triangles()
world=[body.matrix_world@v.co for v in body.data.vertices]
groups={g.index:g.name for g in body.vertex_groups}
anatomy=descendants({b.name:b.parent.name if b.parent else None for b in source_rig.data.bones},'rp_nathan_animated_003_walking_neck_06')
head_groups={i for i,name in groups.items() if name in anatomy}
weights=[sum(g.weight for g in v.groups if g.group in head_groups) for v in body.data.vertices]
faces=[p for p in body.data.polygons if all(world[i].z>1.54 and weights[i]>.5 for i in p.vertices)]
indices=sorted({i for p in faces for i in p.vertices});mapping={old:new for new,old in enumerate(indices)}
positions=[world[i].copy() for i in indices];polygons=[[mapping[i] for i in p.vertices] for p in faces]
uv=[tuple(body.data.uv_layers.active.data[i].uv) for p in faces for i in p.loop_indices]
normal_matrix=body.matrix_world.to_3x3().inverted().transposed()
normals=[(normal_matrix@body.data.corner_normals[i].vector).normalized() for p in faces for i in p.loop_indices]
eye_names=['rp_nathan_animated_003_walking_eye_l_011','rp_nathan_animated_003_walking_eye_r_013']
source_eyes=[source_rig.matrix_world@source_rig.data.bones[n].head_local for n in eye_names]
source_eye_mid=sum(source_eyes,Vector())/2
source_width=max(p.x for p in positions)-min(p.x for p in positions)
assert len(indices)>3000 and len(faces)>6000

bpy.ops.wm.open_mainfile(filepath=str(base/'unvanquished_motion01/human_actions.blend'),use_scripts=False)
scene=bpy.data.scenes['AuthoredGameActions'];bpy.context.window.scene=scene
rig=bpy.data.objects['AuthoredGameRig'];rig.data.pose_position='REST';bpy.context.view_layer.update()
old_head=bpy.data.objects['Game_head'];old_points=[old_head.matrix_world@v.co for v in old_head.data.vertices]
scale=(max(p.x for p in old_points)-min(p.x for p in old_points))/source_width
target_eyes=[rig.matrix_world@rig.data.bones[n].head_local for n in ['eye.L','eye.R']]
target_eye_mid=sum(target_eyes,Vector())/2
# The two REST anatomies face Blender-Y. Authored poses can turn the root180deg;
# fitting in bind space avoids confusing posed forward with anatomical rest.
transform=Matrix.Translation(target_eye_mid)@Matrix.Scale(scale,4)@Matrix.Translation(-source_eye_mid)
for name in ['Game_head','Game_eye.L','Game_eye.R','Game_teeth_lower','Game_teeth_upper']:
 bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
mesh=bpy.data.meshes.new('AuthoredScannedHead');mesh.from_pydata([transform@p for p in positions],[],polygons);mesh.update()
layer=mesh.uv_layers.new(name='OriginalPhotographicUV')
for loop,value in zip(layer.data,uv):loop.uv=value
for polygon in mesh.polygons:polygon.use_smooth=True
mesh.normals_split_custom_set([tuple(n) for n in normals])
normal_storage_error=max(abs(a-b) for actual,expected in zip(mesh.corner_normals,normals) for a,b in zip(actual.vector,expected))
assert normal_storage_error<2e-4,('Custom normal storage error',normal_storage_error)
material=bpy.data.materials.new('RenderpeopleHead_OriginalPhototexture');material.use_nodes=True
shader=material.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.996432
texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(root/'sources/renderpeople_nathan/textures/rp_nathan_animated_003_mat_baseColor.jpeg'),check_existing=True)
material.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
material['source_license']='CC BY4.0';material['source_author']='Renderpeople';material['modification']='Original selected head/neck UV, image and normals; uniform bind-space alignment, neck/head skin rebinding only'
mesh.materials.append(material)
head=bpy.data.objects.new('Game_ScannedHead',mesh);scene.collection.objects.link(head);head.parent=rig;head.matrix_world=Matrix.Identity(4)
neck_group=head.vertex_groups.new(name='neck');head_group=head.vertex_groups.new(name='head')
for i,p in enumerate(positions):
 weight=max(0.,min(1.,(p.z-1.56)/.08))
 if weight>0:head_group.add([i],weight,'REPLACE')
 if weight<1:neck_group.add([i],1-weight,'REPLACE')
modifier=head.modifiers.new('AuthoredGameHeadNeckSkin','ARMATURE');modifier.object=rig
rig.data.pose_position='POSE'
notice=(base/'unvanquished_human01/CREDITS.txt').read_text()+'\n'+(base/'renderpeople_nathan01/CREDITS.txt').read_text()+'\nAssembly contribution: CC BY-SA4.0 https://creativecommons.org/licenses/by-sa/4.0/ ; underlying armor remains CC BY-SA3.0, scanned head CC BY4.0. Original notices retained. Traditional DCC head extraction, proportional bind-space fit and neck/head rebinding. No AI use. Facial animation/neck fit/Rook identity unaccepted.\n'
bpy.data.texts.new('SCANNED_ARMOR_COMBINED_CREDITS').write(notice)
for track in rig.animation_data.nla_tracks:track.mute=False
for obj in scene.objects:obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(out/'human_actions.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_keep_anim_armature=True,export_extras=True,export_copyright=notice)
references={}
meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==17
for track in rig.animation_data.nla_tracks:
 for other in rig.animation_data.nla_tracks:other.mute=other!=track
 samples=[]
 end=track.strips[0].frame_end
 for index in range(9):
  frame=end*index/8;scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
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
(out/'assembly_report.json').write_text(json.dumps({'source_head_vertices':len(indices),'source_head_faces':len(faces),'uniform_scale':scale,'head_bind_transform_blender':[list(row) for row in transform],'normal_storage_max_component_error':normal_storage_error,'mesh_count':17,'bones':122,'face_expression_preserved':False,'source_image_or_uv_modified':False,'scope':'First assembled visual study, not accepted Rook','contribution_license':'CC-BY-SA-4.0','original_licenses':['CC-BY-SA-3.0','CC-BY-4.0']},indent=2))
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
print('SCANNED_AUTHORED_ARMOR_ASSEMBLED',len(indices),len(faces),scale,len(meshes),flush=True)
