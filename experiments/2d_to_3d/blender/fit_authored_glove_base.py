"""Fit only the existing authored glove base into the real sleeve opening."""
import hashlib
import json
import sys
import math
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from cuff_skinning import influence

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
rigid='--rigid-base' in sys.argv
out=root/('rook_glove_rigid132' if rigid else 'rook_glove_base132');out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_run129/human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
glove=bpy.data.objects['AuthoredGlove_Game_body'];glove.data=glove.data.copy()
pose={n:rig.matrix_world@rig.pose.bones[n].matrix for n in ('RightHand','RightForeArm')}
rest={n:rig.matrix_world@rig.data.bones[n].matrix_local for n in pose}
deform={n:pose[n]@rest[n].inverted() for n in pose}
wrist=pose['RightHand'].translation;axis=(pose['RightForeArm'].translation-wrist).normalized()
old=[v.co.copy() for v in glove.data.vertices]
uvs=[tuple(v.uv) for v in glove.data.uv_layers.active.data]
changed=[];weights=[];protected=[]
for vertex in glove.data.vertices:
    desired=deform['RightHand']@vertex.co
    axial=(desired-wrist).dot(axis)
    amount=influence(axial+.03,.03)
    if not amount:
        weights.append(0.);protected.append(vertex.index);continue
    desired+=axis*.04*amount
    forearm=0. if rigid else influence((desired-wrist).dot(axis),.04)
    blend=deform['RightHand']*(1-forearm)+deform['RightForeArm']*forearm
    vertex.co=blend.inverted()@desired
    changed.append(vertex.index);weights.append(forearm)
assert protected and changed
assert all((glove.data.vertices[i].co-old[i]).length==0 for i in protected)
assert uvs==[tuple(v.uv) for v in glove.data.uv_layers.active.data]
for group in list(glove.vertex_groups):glove.vertex_groups.remove(group)
hand=glove.vertex_groups.new(name='RightHand');arm=glove.vertex_groups.new(name='RightForeArm')
for i,w in enumerate(weights):
    if w<1:hand.add([i],1-w,'REPLACE')
    if w>0:arm.add([i],w,'REPLACE')
scene.frame_set(0);bpy.context.view_layer.update()
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(root/'rook_run129/CREDITS.txt').read_text()+'\nGlove-base132: existing authored glove base fitted toward actual sleeve, retaining original UV and all protected palm/finger vertices. No primitive cuff, new faces or source-ring graft. Hand/forearm blend binds Ready fit; contact/art require review.\n'
credits=bpy.data.texts.new('GLOVE_BASE_FIT');credits.write(notice);credits.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'glove_report.json').write_text(json.dumps({'rigid_hand_base':rigid,'ready_hand_forearm_deformation_angle_deg':deform['RightHand'].to_quaternion().rotation_difference(deform['RightForeArm'].to_quaternion()).angle*180/math.pi,'changed_base_vertices':changed,'protected_palm_finger_vertices':len(protected),'protected_geometry_error_m':0.,'vertex_count':len(glove.data.vertices),'uv_unchanged':True,'maximum_base_rest_displacement_m':max((glove.data.vertices[i].co-old[i]).length for i in changed),'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'scope':'Authored glove base fit; no final contact or art acceptance'},indent=2))
print('AUTHORED_GLOVE_BASE_FITTED',len(changed),len(protected),flush=True)
