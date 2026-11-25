"""Stepped, length-preserving leg IK on existing cover transitions; private contact study."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from two_bone_ik import solve as limb_solve
from glb_document import Glb
from game_materials import restore
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');source=root/'cover_transitions160';out=root/'foot_contact161';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');base=Matrix(json.loads((root/'amjviz_actions146/bake_report.json').read_text())['base_game_world'])
reports={};actions=[]
def capture(track,frame):
 for other in rig.animation_data.nla_tracks:other.mute=other!=track
 rig.animation_data.action=None;rig.matrix_world=base.copy()
 for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
 scene.frame_set(frame);bpy.context.view_layer.update()
 return rig.matrix_world.copy(),{b.name:(rig.matrix_world@b.matrix).copy() for b in rig.pose.bones}
def blend(a,b,w):
 p,q,s=a.decompose();pp,qq,ss=b.decompose();return Matrix.LocRotScale(p.lerp(pp,w),q.slerp(qq,w),s.lerp(ss,w))
for label in ('CoverEnterStudy','CoverExitStudy'):
 track=next(t for t in rig.animation_data.nla_tracks if t.name==label);frames=72
 poses=[capture(track,frame) for frame in range(frames+1)]
 first,last=poses[0][1],poses[-1][1];modified=[];max_reach=0.;max_length=0.
 phases={'L':(.08,.46),'R':(.54,.92)} if label=='CoverEnterStudy' else {'R':(.08,.46),'L':(.54,.92)}
 for frame,(world,original) in enumerate(poses):
  desired={n:m.copy() for n,m in original.items()};t=frame/frames
  if frame not in (0,frames):
   for side,phase in phases.items():
    start,end=phase;s=max(0.,min(1.,(t-start)/(end-start)));w=s*s*(3-2*s)
    foot_name='DEF-foot.'+side;toe_name='DEF-toe.'+side
    rotation_phase=max(0.,min(1.,(s-.15)/.70));rotation_weight=rotation_phase*rotation_phase*(3-2*rotation_phase)
    foot=blend(first[foot_name],last[foot_name],rotation_weight)
    foot.translation=first[foot_name].translation.lerp(last[foot_name].translation,w)
    foot.translation.z+=.06*math.sin(math.pi*s)
    hip=original['DEF-thigh.'+side].translation;knee=original['DEF-shin.'+side].translation;ankle=original[foot_name].translation
    new_knee,new_ankle=map(Vector,limb_solve(hip,knee,ankle,foot.translation))
    max_reach=max(max_reach,(new_ankle-foot.translation).length)
    max_length=max(max_length,abs((new_knee-hip).length-(knee-hip).length),abs((new_ankle-new_knee).length-(ankle-knee).length))
    upper=(knee-hip).rotation_difference(new_knee-hip).to_matrix().to_4x4()
    lower=(ankle-knee).rotation_difference(new_ankle-new_knee).to_matrix().to_4x4()
    for suffix in ('','.001'):
     name='DEF-thigh.'+side+suffix;desired[name]=Matrix.Translation(hip)@upper@Matrix.Translation(-hip)@original[name]
     name='DEF-shin.'+side+suffix;desired[name]=Matrix.Translation(new_knee)@lower@Matrix.Translation(-knee)@original[name]
    foot.translation=new_ankle;desired[foot_name]=foot
    relative=blend(first[foot_name].inverted()@first[toe_name],last[foot_name].inverted()@last[toe_name],rotation_weight)
    desired[toe_name]=foot@relative
  local={name:world.inverted()@m for name,m in desired.items()};basis={}
  for bone in rig.pose.bones:
   kwargs={'invert':True}
   if bone.parent:kwargs.update(parent_matrix=local[bone.parent.name],parent_matrix_local=bone.parent.bone.matrix_local)
   basis[bone.name]=bone.bone.convert_local_to_pose(local[bone.name],bone.bone.matrix_local,**kwargs)
  modified.append((world,basis))
 for other in rig.animation_data.nla_tracks:other.mute=True
 action=bpy.data.actions.new(label+'_Foot161');action.use_fake_user=True;rig.animation_data.action=action;previous={}
 for frame,(world,basis) in enumerate(modified):
  scene.frame_set(frame);rig.matrix_world=world
  for bone in rig.pose.bones:
   bone.rotation_mode='QUATERNION';bone.matrix_basis=basis[bone.name]
   if bone.name in previous:bone.rotation_quaternion.make_compatible(previous[bone.name])
   previous[bone.name]=bone.rotation_quaternion.copy()
   for channel in ('location','rotation_quaternion','scale'):bone.keyframe_insert(channel,frame=frame,group=bone.name)
  for channel in ('location','rotation_quaternion','scale'):rig.keyframe_insert(channel,frame=frame,group='FootPlacement')
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     for key in curve.keyframe_points:key.interpolation='LINEAR'
 assert max_reach<.005 and max_length<1e-5,'IK target/length failure'
 actions.append((label,action));reports[label]={'frames':len(modified),'maximum_ankle_target_reach_error_m':max_reach,'maximum_two_link_length_error_m':max_length,'step_lift_m':.06,'rotation_airborne_window':[.15,.85],'phases':phases}
 print('FOOT161_BAKED',label,json.dumps(reports[label]),flush=True)
rig.animation_data.action=None
for label,action in actions:
 for track in list(rig.animation_data.nla_tracks):
  if track.name==label:rig.animation_data.nla_tracks.remove(track)
 track=rig.animation_data.nla_tracks.new();track.name=label;strip=track.strips.new(label,0,action);strip.action_frame_end=72;strip.frame_end=72;track.mute=True
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Hard stand'
rig.matrix_world=base.copy();scene.frame_set(0);bpy.context.view_layer.update()
notice=(source/'CREDITS.txt').read_text()+'\n161: analytical two-link leg correction, left/right6cm step arcs, existing bone lengths retained; actual sole contact/art review required. Source160 retained.\n'
(out/'CREDITS.txt').write_text(notice);bpy.data.texts.new('FOOT161_CHANGES').write(notice)
for o in scene.objects:o.select_set(o==rig or o.type=='MESH')
bpy.context.view_layer.objects.active=rig;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_raw.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,export_rest_position_armature=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_optimize_animation_keep_anim_object=True,export_all_influences=True)
g=Glb(out/'human_raw.glb');restore(g,Glb(source/'human.glb'));g.save(out/'human.glb')
(out/'correction.json').write_text(json.dumps(reports,indent=2));print('FOOT161_EXPORT_READY')
