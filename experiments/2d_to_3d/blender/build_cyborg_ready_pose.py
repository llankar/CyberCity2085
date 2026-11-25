"""First non-stretch ready-pose study on the real CC0 cyberpunk mesh."""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).parent.parent))
from two_bone_ik import elbow_target

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'grab3d_cyborg_lod01'
out=root/'cyborg_ready01'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=True
rig.animation_data.action=None
rig.data.pose_position='POSE'
for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()

def point(name):
    return rig.matrix_world@rig.pose.bones[name].matrix.translation

def rotate_joint(name,target,endpoint):
    pivot=point(name)
    rotation=(point(endpoint)-pivot).rotation_difference(target-pivot)
    bone=rig.pose.bones[name]
    world=rig.matrix_world@bone.matrix
    bone.matrix=rig.matrix_world.inverted()@Matrix.Translation(pivot)@rotation.to_matrix().to_4x4()@Matrix.Translation(-pivot)@world
    bpy.context.view_layer.update()

original_lengths={}
for side in ('Left','Right'):
    upper,lower,hand=[side+part for part in ('Arm','ForeArm','Hand')]
    original_lengths[side]=[(point(lower)-point(upper)).length,(point(hand)-point(lower)).length]
action=bpy.data.actions.new('CombatReadyStudy')
rig.animation_data.action=action
scene.render.fps=24
scene.frame_start=0
scene.frame_end=48
samples=[]
for frame in range(49):
    scene.frame_set(frame)
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    errors={}
    for side,target_value in [('Right',(-.105,-.35,1.31)),('Left',(.075,-.32,1.24))]:
        upper,lower,hand=[side+part for part in ('Arm','ForeArm','Hand')]
        target=Vector(target_value)+Vector((0,0,.003*math.sin(frame*math.tau/48)))
        shoulder=point(upper)
        lengths=original_lengths[side]
        elbow=Vector(elbow_target(shoulder,target,[0,0,-1],*lengths))
        rotate_joint(upper,elbow,lower)
        rotate_joint(lower,target,hand)
        # No invented finger contact: this source has only rigid hand bones.
        errors[side]={'wrist_error_m':(point(hand)-target).length,
                      'length_error_m':max(abs((point(lower)-point(upper)).length-lengths[0]),abs((point(hand)-point(lower)).length-lengths[1]))}
    for bone in rig.pose.bones:
        bone.rotation_mode='QUATERNION'
        bone.keyframe_insert('location',frame=frame,group=bone.name)
        bone.keyframe_insert('rotation_quaternion',frame=frame,group=bone.name)
        bone.keyframe_insert('scale',frame=frame,group=bone.name)
    samples.append({'time_s':frame/24,'arms':errors})
maximum=max(value[key] for sample in samples for value in sample['arms'].values() for key in ('wrist_error_m','length_error_m'))
print('READY_DIAGNOSTIC',samples[0],samples[-1],flush=True)
assert maximum<.00002,maximum
rig.animation_data.action=None
track=rig.animation_data.nla_tracks.new()
track.name='CombatReadyStudy'
strip=track.strips.new('CombatReadyStudy',0,action)
strip.action_frame_start=0
strip.action_frame_end=48
strip.frame_start=0
strip.frame_end=48
scene.frame_set(0)
helpers={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\nNon-stretch arm ready-pose study; no weapon/finger-contact or final combat idle acceptance.\n'
bpy.data.texts.new('READY_POSE_STUDY').write(notice)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'ready_pose_report.json').write_text(json.dumps({'source_sha256':hashlib.sha256((source/'human.glb').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'maximum_wrist_or_length_error_m':maximum,'samples':samples,'limitations':['No finger rig, weapon contact or final combat idle acceptance','Source walk/run kept in Blend but muted in this isolated study']},indent=2),encoding='utf8')
print('CYBORG_READY_POSE_EXPORTED',maximum,flush=True)
