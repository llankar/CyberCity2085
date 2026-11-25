"""Recover real adjacent forearm faces and bind the original glove continuously."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix,Vector,Quaternion
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).parent.parent))
from anatomical_groups import descendants
from cuff_skinning import influence

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'rook_cuff132';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_run129/human.blend'),use_scripts=False)
target_scene=bpy.context.scene;rig=next(o for o in target_scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
target_scene.frame_set(0);bpy.context.view_layer.update()
glove=bpy.data.objects['AuthoredGlove_Game_body']
old_points=[glove.matrix_world@v.co for v in glove.data.vertices]
old_tree=KDTree(len(old_points))
for i,p in enumerate(old_points):old_tree.insert(p,i)
old_tree.balance()
pose={n:rig.matrix_world@rig.pose.bones[n].matrix for n in ('RightHand','RightForeArm')}
rest={n:rig.matrix_world@rig.data.bones[n].matrix_local for n in pose}
deform={n:pose[n]@rest[n].inverted() for n in pose}
axis=(pose['RightForeArm'].translation-pose['RightHand'].translation).normalized()
with bpy.data.libraries.load(str(root/'scanned_armor_contact01/pistol_fit01/human_pistol.blend'),link=False) as (available,loaded):loaded.scenes=['AuthoredGameActions']
source_scene=loaded.scenes[0];bpy.context.window.scene=source_scene
source_rig=next(o for o in source_scene.objects if o.type=='ARMATURE')
for track in source_rig.animation_data.nla_tracks:track.mute=track.name!='Shoot'
source_scene.frame_set(8);bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get()
evaluated_rig=source_rig.evaluated_get(graph)
source_wrist=evaluated_rig.matrix_world@evaluated_rig.pose.bones['hand.R'].matrix
source_elbow=evaluated_rig.matrix_world@evaluated_rig.pose.bones[source_rig.data.bones['hand.R'].parent.name].matrix.translation
fit=json.loads((root/'scanned_armor_contact01/pistol_fit01/fit_report.json').read_text())
rotation=Matrix(fit['world_placement_blender']).to_quaternion().inverted()
mapping=Matrix.Translation(pose['RightHand'].translation)@rotation.to_matrix().to_4x4()@Matrix.Scale(.95,4)@Matrix.Translation(-source_wrist.translation)
mapped_axis=(mapping.to_3x3()@(source_elbow-source_wrist.translation)).normalized()
alignment=mapped_axis.rotation_difference(axis)
family=descendants({b.name:b.parent.name if b.parent else None for b in source_rig.data.bones},'hand.R')
found=[]
for obj in source_scene.objects:
    if obj.type!='MESH' or obj.name.startswith('EquippedPistol_'):continue
    groups={g.index for g in obj.vertex_groups if g.name in family}
    if not groups:continue
    weights=[sum(g.weight for g in v.groups if g.group in groups) for v in obj.data.vertices]
    selected={f.index for f in obj.data.polygons if all(weights[i]>.5 for i in f.vertices)}
    if not selected:continue
    assert len(selected)==190,(obj.name,len(selected))
    original_vertices={i for f in selected for i in obj.data.polygons[f].vertices}
    edges={}
    for face in obj.data.polygons:
        for edge in face.edge_keys:edges.setdefault(tuple(sorted(edge)),set()).add(face.index)
    expanded=set(selected)
    for ring in range(2):
        neighbours=set()
        for index in expanded:
            for edge in obj.data.polygons[index].edge_keys:neighbours|=edges[tuple(sorted(edge))]
        expanded|=neighbours
    evaluated=obj.evaluated_get(graph)
    data=bpy.data.meshes.new_from_object(evaluated,depsgraph=graph)
    assert len(data.vertices)==len(obj.data.vertices)
    bm=bmesh.new();bm.from_mesh(data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
    ids=bm.verts.layers.int.new('source_index')
    for v in bm.verts:v[ids]=v.index
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index not in expanded],context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bm.verts.index_update();source_ids=[v[ids] for v in bm.verts]
    bm.to_mesh(data);bm.free();data.transform(evaluated.matrix_world)
    found.append((data,source_ids,original_vertices,len(expanded)))
assert len(found)==1
data,source_ids,original_vertices,face_count=found[0]
bpy.context.window.scene=target_scene
vertex_weights=[];retention=[]
desired_points=[mapping@v.co for v in data.vertices]
data.transform(deform['RightHand'].inverted()@mapping)
for vertex,source_index,desired in zip(data.vertices,source_ids,desired_points):
    if source_index not in original_vertices:
        offset=desired-pose['RightHand'].translation
        amount=influence(offset.dot(mapped_axis),.03)
        desired=pose['RightHand'].translation+Quaternion().slerp(alignment,amount)@offset
    axial=(desired-pose['RightHand'].translation).dot(axis)
    forearm=0. if source_index in original_vertices else influence(axial)
    blend=deform['RightHand']*(1-forearm)+deform['RightForeArm']*forearm
    vertex.co=blend.inverted()@desired
    vertex_weights.append(forearm)
    if source_index in original_vertices:retention.append(old_tree.find(vertex.co)[2])
assert len(retention)==206 and max(retention)<1e-5,('Original glove moved',len(retention),max(retention))
glove.data=data
for group in list(glove.vertex_groups):glove.vertex_groups.remove(group)
hand=glove.vertex_groups.new(name='RightHand');arm=glove.vertex_groups.new(name='RightForeArm')
for i,w in enumerate(vertex_weights):
    if w<1:hand.add([i],1-w,'REPLACE')
    if w>0:arm.add([i],w,'REPLACE')
bpy.data.scenes.remove(source_scene);bpy.ops.outliner.orphans_purge(do_recursive=True)
target_scene.frame_set(0);bpy.context.view_layer.update()
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in target_scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(root/'rook_run129/CREDITS.txt').read_text()+'\nCuff132: two adjacent authored Unvanquished forearm face rings recovered with original UV/material, bound to RightHand/RightForeArm through inverse blended skin matrix. Original206hand vertices retained in bind geometry; contact and art acceptance require review.\n'
credits=bpy.data.texts.new('AUTHORED_CUFF_CREDITS');credits.write(notice);credits.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'cuff_report.json').write_text(json.dumps({'source_hand_faces':190,'expanded_faces':face_count,'vertices':len(data.vertices),'original_glove_retention_error_m':max(retention),'maximum_forearm_weight':max(vertex_weights),'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'scope':'Authored topology recovery and preserved palm; not surface contact or art acceptance'},indent=2))
print('AUTHORED_CUFF_RECOVERED',face_count,len(data.vertices),max(retention),flush=True)
