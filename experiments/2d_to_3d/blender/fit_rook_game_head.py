"""Separate candidate fit: original MIT head anatomy, existing dressed body/rig."""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from head_skinning import neck_skull_weights

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'rook_head_fit126';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_material01/human.blend'),use_scripts=False)
scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
body=bpy.data.objects['char1']
original=len(body.data.polygons)
group_ids={g.index for g in body.vertex_groups if g.name in ('Head','head_end','headfront')}
weights={v.index:sum(g.weight for g in v.groups if g.group in group_ids) for v in body.data.vertices}
bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
remove=[]
for face in bm.faces:
    points=[body.matrix_world@v.co for v in face.verts]
    if all(p.z>1.515 and abs(p.x)<.14 for p in points) and (min(p.z for p in points)>1.60 or all(weights[v.index]>.7 for v in face.verts)):
        remove.append(face)
bmesh.ops.delete(bm,geom=remove,context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(body.data);bm.free()
assert original-len(body.data.polygons)>1000
with bpy.data.libraries.load(str(root/'rocketbox_head_review125/head.blend'),link=False) as (available,loaded):
    loaded.objects=['ActualGameHeadAndEyes']
head=loaded.objects[0];scene.collection.objects.link(head)
# Uniform scale and measured anatomical translation only, never shape projection.
pivot=Vector((0,0,1.54))
mapping=Matrix.Translation(Vector((-.0037,.045,-.015)))@Matrix.Translation(pivot)@Matrix.Scale(.95,4)@Matrix.Translation(-pivot)
head.data.transform(mapping)
head.name='MIT_HeadFitStudy'
head.parent=rig
head.matrix_world=Matrix.Identity(4)
neck=head.vertex_groups.new(name='neck');skull=head.vertex_groups.new(name='Head')
for vertex in head.data.vertices:
    neck_weight,skull_weight=neck_skull_weights(vertex.co.z)
    if neck_weight:neck.add([vertex.index],neck_weight,'REPLACE')
    if skull_weight:skull.add([vertex.index],skull_weight,'REPLACE')
modifier=head.modifiers.new('ExistingActorSkeleton','ARMATURE');modifier.object=rig
notice=(root/'rook_material01/CREDITS.txt').read_text()+'\n'+(root/'rocketbox_head_review125/CREDITS.txt').read_text()+'\nCandidate126: uniform95percent head fit, original UV retained, neck/head weights added. Hair likeness, seam, facial animation and final art not accepted.\n'
credits=bpy.data.texts.new('HEAD_FIT_CREDITS');credits.write(notice);credits.use_fake_user=True
rig.data.pose_position='POSE'
references={}
template=json.loads((root/'cyborg_actions01/native_reference.json').read_text())
helpers={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
meshes=[obj for obj in scene.objects if obj.type=='MESH' and obj not in helpers]
for track in rig.animation_data.nla_tracks:
    for other in rig.animation_data.nla_tracks:other.mute=other!=track
    strip=track.strips[0]
    samples=[]
    for sample in template[track.name]:
        value=strip.frame_start+sample['time_s']*24
        scene.frame_set(math.floor(value),subframe=value%1);bpy.context.view_layer.update()
        graph=bpy.context.evaluated_depsgraph_get();boxes={}
        for obj in meshes:
            evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
            points=[evaluated.matrix_world@v.co for v in data.vertices]
            boxes[obj.name.replace('.','_').replace(' ','_')]=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
            evaluated.to_mesh_clear()
        samples.append({'time_s':sample['time_s'],'mesh_bounds_blender':boxes})
    references[track.name]=samples
(out/'native_reference.json').write_text(json.dumps(references,indent=2))
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
for obj in scene.objects:obj.select_set(obj==rig or obj in meshes)
bpy.context.view_layer.objects.active=rig
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'fit_report.json').write_text(json.dumps({'removed_body_faces':original-len(body.data.polygons),'head_vertices':len(head.data.vertices),'uniform_scale':.95,'mapping':[list(row) for row in mapping],'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'limitations':['Candidate only; neck seam and six-clip deformation not accepted','Original short hair is not Rook quiff','No facial/eye animation in candidate']},indent=2))
print('ROOK_GAME_HEAD_FIT_READY',flush=True)
