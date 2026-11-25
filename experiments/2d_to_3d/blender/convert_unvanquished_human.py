"""Neutral authored armor qualification; preserve originals, no production changes."""
import json,math,hashlib
from pathlib import Path
import bpy
from mathutils import Matrix
root=Path('E:/CyberCity2085-3d-lab');source=root/'sources/unvanquished_human';out=root/'generated/phase2/unvanquished_human01';out.mkdir(exist_ok=True)
metadata=json.loads((source/'acquisition.json').read_text());assert metadata['license']=='CC-BY-SA-3.0'
bpy.ops.wm.open_mainfile(filepath=str(source/'human_male.blend'),use_scripts=False)
rig=bpy.data.objects['Armature'];rig.data.pose_position='REST'
if rig.animation_data:
 rig.animation_data.action=None
 for track in rig.animation_data.nla_tracks:track.mute=True
allowed={'body','head','eye.L','eye.R','teeth_lower','teeth_upper'}
parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith('armor_') or o.name in allowed)]
assert len(parts)==21
for obj in list(bpy.data.objects):
 if obj.type=='MESH' and obj not in parts:
  mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
  if mesh.users==0:bpy.data.meshes.remove(mesh)
for obj in parts+[rig]:obj.hide_viewport=False;obj.hide_render=False;obj.hide_set(False)
bpy.context.view_layer.update()
points=[o.matrix_world@v.co for o in parts for v in o.data.vertices]
floor=min(p.z for p in points);height=max(p.z for p in points)-floor;scale=1.85/height
rig.matrix_world=Matrix.Translation((0,0,-floor*scale))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Scale(scale,4)@rig.matrix_world
bpy.context.view_layer.update()
materials={}
for group,stem,roughness in [('armor','armor',.48),('body','base',.72),('head','head',.58)]:
 material=bpy.data.materials.new('Authored_'+group+'_LegacyNormalStudy');material.use_nodes=True
 nodes=material.node_tree.nodes;links=material.node_tree.links;shader=nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=roughness;shader.inputs['Metallic'].default_value=0.
 extension='.jpg' if stem=='head' else '.png'
 color=nodes.new('ShaderNodeTexImage');color.image=bpy.data.images.load(str(source/(stem+extension)),check_existing=True);links.new(color.outputs['Color'],shader.inputs['Base Color'])
 normal=nodes.new('ShaderNodeTexImage');normal.image=bpy.data.images.load(str(source/(stem+'_n'+extension)),check_existing=True);normal.image.colorspace_settings.name='Non-Color'
 normalmap=nodes.new('ShaderNodeNormalMap');links.new(normal.outputs['Color'],normalmap.inputs['Color']);links.new(normalmap.outputs['Normal'],shader.inputs['Normal'])
 material['source_license']='CC BY-SA3.0';material['conversion']='Original diffuse/normal retained; legacy specular maps not falsely treated as metallic/roughness'
 materials[group]=material
for obj in parts:
 obj.data.materials.clear();obj.data.materials.append(materials['armor' if obj.name.startswith('armor_') else ('body' if obj.name=='body' else 'head')])
 for face in obj.data.polygons:face.material_index=0
 bpy.context.view_layer.update()
weights=[sum(g.weight>1e-7 for g in v.groups) for o in parts for v in o.data.vertices]
notice=(source/'CREDITS.txt').read_text()+'\nDerivative: neutral rest-pose scale/orientation normalization, authored armor separated, original diffuse/normal wired into principled materials. Legacy specular conversion/art not accepted. Derivative under CC BY-SA3.0.\n'
bpy.data.texts.new('ASSET_CREDITS_CC_BY_SA3').write(notice)
scene=bpy.context.scene;scene.render.fps=60
for obj in scene.objects:obj.select_set(obj in parts or obj==rig)
bpy.context.view_layer.objects.active=rig
reference={}
for obj in parts:
 evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
 reference[obj.name]=[list(evaluated.matrix_world@mesh.vertices[i].co) for i in range(0,len(mesh.vertices),max(1,len(mesh.vertices)//20))]
 evaluated.to_mesh_clear()
(out/'static_surface_reference.json').write_text(json.dumps(reference))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human_armor.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_armor.glb'),export_format='GLB',use_selection=True,export_animations=False,export_all_influences=True,export_extras=True,export_copyright=notice)
report={'source_commit':metadata['commit'],'source_acquisition_bytes':metadata['bytes'],'source_height_units':height,'scale_to_1_85m':scale,'axis_rotation_z_radians':math.pi/2,'meshes':[o.name for o in parts],'bones':len(rig.data.bones),'maximum_source_vertex_groups':max(weights),'source_actions_retained_in_blend':len(bpy.data.actions),'exported_animations':0,'original_diffuse_normal_maps':6,'legacy_specular_maps_applied':False,'license':'CC BY-SA3.0','scope':'New authored armor/body neutral qualification, no Nathan mixing or accepted Rook identity'}
(out/'conversion_report.json').write_text(json.dumps(report,indent=2));(out/'CREDITS.txt').write_text(notice,encoding='utf8')
print('UNV_NEUTRAL_ARMOR_EXPORTED',len(parts),len(rig.data.bones),max(weights),height,scale,flush=True)
