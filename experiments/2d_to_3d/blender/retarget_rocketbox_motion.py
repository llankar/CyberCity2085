"""Retarget licensed UAL rotations onto the actual Biped game rig; art study."""
import json
import math
import shutil
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03')
out=root/'motion01'; out.mkdir(exist_ok=True)
library=Path('E:/CyberCity2085-3d-lab/sources/quaternius_ual_standard')
bpy.ops.wm.open_mainfile(filepath=str(root/'character_dielectric.blend'),use_scripts=False)
target=next(obj for obj in bpy.context.scene.objects if obj.type=='ARMATURE')
mesh=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
with bpy.data.libraries.load(str(library/'animation_library.blend'),link=False) as (available,loaded):
    loaded.objects=['Armature']
source=loaded.objects[0]; bpy.context.scene.collection.objects.link(source)
clips={track.name:strip.action for track in source.animation_data.nla_tracks for strip in track.strips}
for track in source.animation_data.nla_tracks: track.mute=True
mapping={'Bip01 Pelvis':'pelvis','Bip01 Spine':'spine_01','Bip01 Spine1':'spine_02',
         'Bip01 Spine2':'spine_03','Bip01 Neck':'neck_01','Bip01 Head':'Head'}
for side in ['L','R']:
    for name,other in [('Clavicle','clavicle'),('UpperArm','upperarm'),('Forearm','lowerarm'),
                       ('Hand','hand'),('Thigh','thigh'),('Calf','calf'),('Foot','foot'),('Toe0','ball')]:
        mapping[f'Bip01 {side} {name}']=f'{other}_{side.lower()}'
    for digit,other in enumerate(['thumb','index','middle','ring','pinky']):
        for joint in range(3):
            suffix='' if joint==0 else str(joint)
            mapping[f'Bip01 {side} Finger{digit}{suffix}']=f'{other}_{joint+1:02d}_{side.lower()}'
assert all(name in target.pose.bones and other in source.pose.bones for name,other in mapping.items())
order=sorted(mapping,key=lambda name:len(target.pose.bones[name].parent_recursive))
rest={name:target.matrix_world @ target.data.bones[name].matrix_local for name in mapping}
source_rest={other:source.matrix_world @ source.data.bones[other].matrix_local for other in mapping.values()}
calibrated={name:matrix.to_quaternion() for name,matrix in rest.items()}
# Correct the genuine A-pose/T-pose discrepancy using anatomical child vectors,
# not imported FBX bone-tail display lengths or guessed constant Euler angles.
alignment={}
for side in ['L','R']:
    for parent,child in [('UpperArm','Forearm'),('Forearm','Hand')]:
        name=f'Bip01 {side} {parent}'; child_name=f'Bip01 {side} {child}'
        original=(rest[child_name].translation-rest[name].translation).normalized()
        desired=(source_rest[mapping[child_name]].translation-source_rest[mapping[name]].translation).normalized()
        swing=original.rotation_difference(desired)
        calibrated[name]=swing @ calibrated[name]
        alignment[name]=math.degrees(swing.angle)
scale=rest['Bip01 Pelvis'].translation.z/source_rest['pelvis'].translation.z
inverse_world=target.matrix_world.inverted()
scene=bpy.context.scene; scene.render.fps=30
actions=[]; reports={}
for label,clip in [('Idle','Idle_Loop'),('Walk','Walk_Loop'),('Pistol_Shoot','Pistol_Shoot'),
                   ('Punch_Cross','Punch_Cross'),('Death01','Death01')]:
    source.animation_data.action=clips[clip]
    if clips[clip].slots: source.animation_data.action_slot=clips[clip].slots[0]
    first,last=clips[clip].frame_range; duration=(last-first)/24.0
    frames=round(duration*30)
    action=bpy.data.actions.new('Rocketbox_'+label)
    target.animation_data_create(); target.animation_data.action=action
    previous={}
    for sample in range(frames+1):
        source_frame=first+(last-first)*sample/frames
        scene.frame_set(math.floor(source_frame),subframe=source_frame-math.floor(source_frame))
        for bone in target.pose.bones: bone.matrix_basis=Matrix.Identity(4)
        target.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
        for name in order:
            other=mapping[name]; pose=target.pose.bones[name]
            current=source.matrix_world @ source.pose.bones[other].matrix
            delta=current.to_quaternion() @ source_rest[other].to_quaternion().inverted()
            desired=(delta @ calibrated[name]).to_matrix().to_4x4()
            desired.translation=target.matrix_world @ pose.matrix.translation
            if name=='Bip01 Pelvis':
                desired.translation=rest[name].translation+(current.translation-source_rest[other].translation)*scale
            pose.matrix=inverse_world @ desired
            if name!='Bip01 Pelvis': pose.location=Vector((0,0,0))
            pose.scale=Vector((1,1,1))
            target.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
        for bone in target.pose.bones:
            bone.rotation_mode='QUATERNION'
            if bone.name in previous: bone.rotation_quaternion.make_compatible(previous[bone.name])
            previous[bone.name]=bone.rotation_quaternion.copy()
            for channel in ['location','rotation_quaternion','scale']:
                bone.keyframe_insert(channel,frame=sample,group=bone.name)
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points: key.interpolation='LINEAR'
    actions.append((label,action,frames))
    reports[label]={'source_clip':clip,'duration_s':duration,'frames':frames+1}
    print('ROCKETBOX_MOTION_BAKED',label,frames+1,flush=True)
target.animation_data.action=None
for label,action,frames in actions:
    track=target.animation_data.nla_tracks.new(); track.name=label
    strip=track.strips.new(label,0,action); strip.action_frame_start=0; strip.action_frame_end=frames
    track.mute=False
for obj in scene.objects: obj.select_set(obj in [target,mesh])
bpy.context.view_layer.objects.active=target
bpy.ops.export_scene.gltf(filepath=str(out/'human_motion.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_frame_range=False,export_try_sparse_sk=True,
    export_copyright='Microsoft Rocketbox MIT; Quaternius UAL CC0 1.0')
glb=Glb(out/'human_motion.glb')
glb.doc['asset'].setdefault('extras',{}).update({'source_license':'MIT',
    'source_commit':'0943055db6ec570bcef9f2c8b41c9e5467c808f9',
    'source_asset':'Microsoft Rocketbox Military_Male_03',
    'license_notice':(root/'LICENSE.md').read_text(),'motion_license':'CC0 1.0',
    'motion_source':'https://quaternius.com/packs/universalanimationlibrary.html',
    'motion_notice':(library/'License.txt').read_text()})
glb.save(out/'human_motion.glb')
for track in target.animation_data.nla_tracks: track.mute=track.name!='Idle'
source.hide_render=True; source.hide_set(True)
scene.frame_set(0); bpy.ops.file.pack_all()
bpy.data.texts.new('MOTION_SOURCE_CC0').write((library/'License.txt').read_text())
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human_motion.blend'))
shutil.copyfile(root/'LICENSE.md',out/'LICENSE.md')
shutil.copyfile(library/'License.txt',out/'MOTION_LICENSE.txt')
(out/'retarget_report.json').write_text(json.dumps({'mapping':mapping,'calibration_degrees':alignment,
    'pelvis_translation_scale':scale,'clips':reports,'source_license':'MIT','motion_license':'CC0 1.0',
    'limitations':['Retarget study, no artistic acceptance','Weapon fitting, contact and locomotion sliding not verified',
                   'Original face and outfit, not final Rook identity']},indent=2),encoding='utf-8')
print('ROCKETBOX_MOTION_EXPORTED',len(actions),len(mapping),flush=True)
