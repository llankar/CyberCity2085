"""Integrate actual posed hand geometry and a licensed pistol, never primitives."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from anatomical_groups import descendants

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'cyborg_pistol01'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'cyborg_ready01/human.blend'),use_scripts=False)
target_scene=bpy.context.scene
target_rig=next(o for o in target_scene.objects if o.type=='ARMATURE')
target_mesh=next(o for o in target_scene.objects if o.type=='MESH' and o.vertex_groups)
with bpy.data.libraries.load(str(root/'scanned_armor_contact01/pistol_fit01/human_pistol.blend'),link=False) as (available,loaded):
    loaded.scenes=['AuthoredGameActions']
source_scene=loaded.scenes[0]
bpy.context.window.scene=source_scene
source_rig=next(o for o in source_scene.objects if o.type=='ARMATURE')
for track in source_rig.animation_data.nla_tracks:track.mute=track.name!='Shoot'
source_scene.frame_set(8)
bpy.context.view_layer.update()
source_graph=bpy.context.evaluated_depsgraph_get()
evaluated_rig=source_rig.evaluated_get(source_graph)
source_wrist=evaluated_rig.matrix_world@evaluated_rig.pose.bones['hand.R'].matrix
source_fit=json.loads((root/'scanned_armor_contact01/pistol_fit01/fit_report.json').read_text())
# The actual pistol's local forward is -Y/up+Z; remove the borrowed source aim
# orientation rather than retaining its opposite-facing world direction.
aim_rotation=Matrix(source_fit['world_placement_blender']).to_quaternion().inverted()
family=descendants({bone.name:bone.parent.name if bone.parent else None for bone in source_rig.data.bones},'hand.R')
parts=[]
graph=bpy.context.evaluated_depsgraph_get()
for obj in source_scene.objects:
    if obj.type!='MESH':continue
    weapon=obj.name.startswith('EquippedPistol_')
    selected=None
    if not weapon:
        groups={group.index for group in obj.vertex_groups if group.name in family}
        if not groups:continue
        weight=[sum(group.weight for group in vertex.groups if group.group in groups) for vertex in obj.data.vertices]
        selected={face.index for face in obj.data.polygons if all(weight[i]>.5 for i in face.vertices)}
        if not selected:continue
    evaluated=obj.evaluated_get(graph)
    data=bpy.data.meshes.new_from_object(evaluated,depsgraph=graph)
    if selected is not None:
        assert len(data.vertices)==len(obj.data.vertices)
        bm=bmesh.new();bm.from_mesh(data);bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm,geom=[face for face in bm.faces if face.index not in selected],context='FACES')
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
        bm.to_mesh(data);bm.free()
    data.transform(evaluated.matrix_world)
    parts.append((obj.name,data,weapon))
assert sum(weapon for name,data,weapon in parts)==9
assert any(not weapon for name,data,weapon in parts)
bpy.context.window.scene=target_scene
track=next(track for track in target_rig.animation_data.nla_tracks if track.name=='CombatReadyStudy')
action=track.strips[0].action
for other in target_rig.animation_data.nla_tracks:other.mute=True
target_rig.animation_data.action=action
for frame in range(49):
    target_scene.frame_set(frame)
    bpy.context.view_layer.update()
    hand=target_rig.pose.bones['RightHand']
    world=target_rig.matrix_world@hand.matrix
    hand.matrix=target_rig.matrix_world.inverted()@Matrix.LocRotScale(world.translation,aim_rotation@source_wrist.to_quaternion(),world.to_scale())
    bpy.context.view_layer.update()
    for channel in ('location','rotation_quaternion','scale'):hand.keyframe_insert(channel,frame=frame,group=hand.name)
target_rig.animation_data.action=None
track.mute=False
target_scene.frame_set(0)
bpy.context.view_layer.update()
pose=target_rig.matrix_world@target_rig.pose.bones['RightHand'].matrix
rest=target_rig.matrix_world@target_rig.data.bones['RightHand'].matrix_local
mapping=Matrix.Translation(pose.translation)@aim_rotation.to_matrix().to_4x4()@Matrix.Scale(.95,4)@Matrix.Translation(-source_wrist.translation)
to_bind=rest@pose.inverted()@mapping
equipped=[]
for name,data,weapon in parts:
    data.transform(to_bind)
    assert max((v.co-rest.translation).length for v in data.vertices)<.5, name
    obj=bpy.data.objects.new(('Pistol_' if weapon else 'AuthoredGlove_')+name,data)
    target_scene.collection.objects.link(obj)
    obj.parent=target_rig
    obj.matrix_world=Matrix.Identity(4)
    group=obj.vertex_groups.new(name='RightHand')
    group.add(list(range(len(data.vertices))),1,'REPLACE')
    modifier=obj.modifiers.new('ActualAuthoredHandAndWeapon','ARMATURE');modifier.object=target_rig
    equipped.append(obj)
index=target_mesh.vertex_groups['RightHand'].index
weights=[sum(g.weight for g in v.groups if g.group==index) for v in target_mesh.data.vertices]
remove={face.index for face in target_mesh.data.polygons if any(weights[i]>.75 for i in face.vertices)}
assert remove
bm=bmesh.new();bm.from_mesh(target_mesh.data);bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[face for face in bm.faces if face.index in remove],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(target_mesh.data);bm.free()
notice=(root/'cyborg_ready01/CREDITS.txt').read_text()+'\nSelected actual right-hand geometry: '+(root/'unvanquished_human01/CREDITS.txt').read_text()+'\nPistol: FireWarden, CC0 https://opengameart.org/content/lowpoly-pistol\nCombined experimental hand/weapon adaptation under CC BY-SA3.0; no Nathan head or Maxwell hair geometry included. Authored closed hand baked to one wrist; no animated trigger finger claim.\n'
credits=bpy.data.texts.new('HAND_AND_WEAPON_CREDITS')
credits.write(notice)
credits.use_fake_user=True
# Remove borrowed scene and orphan body/head data before packing this derivative.
bpy.data.scenes.remove(source_scene)
bpy.ops.outliner.orphans_purge(do_recursive=True)
helpers={bone.custom_shape for bone in target_rig.pose.bones if bone.custom_shape}
visible=[obj for obj in target_scene.objects if obj.type=='MESH' and obj not in helpers]
references=[]
for frame in range(0,49,6):
    target_scene.frame_set(frame)
    bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    boxes={}
    for obj in visible:
        evaluated=obj.evaluated_get(graph)
        data=evaluated.to_mesh()
        points=[evaluated.matrix_world@v.co for v in data.vertices]
        boxes[obj.name.replace('.','_').replace(' ','_')]=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
        evaluated.to_mesh_clear()
    references.append({'time_s':frame/24,'mesh_bounds_blender':boxes})
target_scene.frame_set(0)
(out/'native_reference.json').write_text(json.dumps(references,indent=2),encoding='utf8')
for obj in target_scene.objects:obj.select_set(obj==target_rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=target_rig
bpy.ops.file.pack_all()
assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
assert not any('nathan' in image.name.lower() for image in bpy.data.images)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'assembly_report.json').write_text(json.dumps({'parts':[{'name':obj.name,'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons)} for obj in equipped],'removed_original_hand_faces':len(remove),'uniform_hand_and_gun_scale':.95,'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'limitations':['Closed authored right-hand shape is rigid on target wrist','Wrist seam, gun aim and contact require native visual review','No animated trigger finger, combat fire recoil, or final Rook art approval']},indent=2),encoding='utf8')
print('CYBORG_AUTHORED_HAND_WEAPON_EXPORTED',len(equipped),len(remove),flush=True)
