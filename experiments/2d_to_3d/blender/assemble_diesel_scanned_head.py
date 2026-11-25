"""Fit actual scanned anatomy to a coherent authored outfit; no cloth warping."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent))
from scanned_head_geometry import extract
from anatomical_groups import descendants

root=Path('E:/CyberCity2085-3d-lab')
base=root/'generated/phase2'
out=base/'diesel_scanned_head01'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(base/'renderpeople_nathan01/human.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST'
bpy.context.view_layer.update()
head=extract(rig,bpy.data.objects['Object_96'])
bpy.ops.wm.open_mainfile(filepath=str(base/'diesel_candidate01/human.blend'),use_scripts=False)
scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST'
bpy.context.view_layer.update()
review=json.loads((base/'diesel_candidate01/anatomy_review.json').read_text())
target_mid=sum((Vector(p) for p in review['eye_centres']),Vector())/2
source_width=max(p.x for p in head['positions'])-min(p.x for p in head['positions'])
target_width=review['head_weighted_bounds'][1][0]-review['head_weighted_bounds'][0][0]
scale=target_width/source_width
assert .8<scale<1.3,scale
fit=Matrix.Translation(target_mid)@Matrix.Scale(scale,4)@Matrix.Translation(-head['eye_midpoint'])
positions=[fit@p for p in head['positions']]
body=bpy.data.objects[review['body']]
groups={g.index:g.name for g in body.vertex_groups}
head_family=descendants({bone.name:bone.parent.name if bone.parent else None for bone in rig.data.bones},'mixamorig:Neck')
head_weight=[sum(g.weight for g in v.groups if groups[g.group] in head_family) for v in body.data.vertices]
neck_z=(rig.matrix_world@rig.data.bones['mixamorig:Neck'].head_local).z
remove={face.index for face in body.data.polygons if all((body.matrix_world@body.data.vertices[i].co).z>neck_z-.04 for i in face.vertices) and any(head_weight[i]>.2 for i in face.vertices)}
assert len(remove)>500
bm=bmesh.new()
bm.from_mesh(body.data)
bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[face for face in bm.faces if face.index in remove],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(body.data)
bm.free()
body.data.update()
removed_parts=[]
for obj in list(scene.objects):
    if obj.type=='MESH' and any(token in obj.name.lower() for token in ('beard','eyebrow','eye_brow','eyes.','hair.')):
        removed_parts.append(obj.name)
        bpy.data.objects.remove(obj,do_unlink=True)
mesh=bpy.data.meshes.new('CompleteScannedHead_SourceUV')
mesh.from_pydata(positions,[],head['faces'])
mesh.update()
uv=mesh.uv_layers.new(name='SourceUV')
for target,value in zip(uv.data,head['uv']):target.uv=value
mesh.normals_split_custom_set(head['normals'])
for face in mesh.polygons:face.use_smooth=True
material=bpy.data.materials.new('OriginalScannedPhototexture')
material.use_nodes=True
shader=material.node_tree.nodes['Principled BSDF']
shader.inputs['Roughness'].default_value=.996432
texture=material.node_tree.nodes.new('ShaderNodeTexImage')
texture.image=bpy.data.images.load(str(root/'sources/renderpeople_nathan/textures/rp_nathan_animated_003_mat_baseColor.jpeg'),check_existing=True)
material.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
mesh.materials.append(material)
obj=bpy.data.objects.new('ScannedNathanHead',mesh)
scene.collection.objects.link(obj)
obj.parent=rig
obj.matrix_world=Matrix.Identity(4)
neck=obj.vertex_groups.new(name='mixamorig:Neck')
head_group=obj.vertex_groups.new(name='mixamorig:Head')
head_z=(rig.matrix_world@rig.data.bones['mixamorig:Head'].head_local).z
for index,p in enumerate(positions):
    weight=max(0.,min(1.,(p.z-neck_z)/(head_z-neck_z)))
    if weight:head_group.add([index],weight,'REPLACE')
    if weight<1:neck.add([index],1-weight,'REPLACE')
modifier=obj.modifiers.new('ExistingMixamoHeadNeckRig','ARMATURE')
modifier.object=rig
notice=(root/'sources/diesel_character/CREDITS.txt').read_text()+'\n'+(base/'renderpeople_nathan01/CREDITS.txt').read_text()+'\nTraditional DCC head extraction and uniform eye-midpoint/head-width fit; original outfit and its rig retained, original painted head physically removed in derivative. No AI use, new animations, or final Rook art claim.\n'
bpy.data.texts.new('ASSEMBLY_CREDITS').write(notice)
rig.data.pose_position='POSE'
helpers={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
meshes=[o for o in scene.objects if o.type=='MESH' and o not in helpers]
assert len(meshes)==6
for o in scene.objects:o.select_set(o==rig or o in meshes)
bpy.context.view_layer.objects.active=rig
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'fit_report.json').write_text(json.dumps({'uniform_scale':scale,'fit_matrix':[list(row) for row in fit],'original_scanned_head_triangles':len(head['faces']),'deleted_original_body_faces':len(remove),'removed_original_parts':removed_parts,'meshes':len(meshes),'bones':len(rig.data.bones),'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'limitations':['Source outfit unchanged; no clothing recolor or warping','Head/neck only; no facial expression/blink rig','Neutral fit and art require inspection; no new action clips']},indent=2))
print('DIESEL_SCANNED_HEAD_ASSEMBLED',scale,len(remove),removed_parts,flush=True)
