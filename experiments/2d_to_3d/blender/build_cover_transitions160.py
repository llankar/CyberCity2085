"""Blend actual authored standing/crouch poses into grounded cover transitions."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from game_materials import restore
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');source=root/'motion_extension159';out=root/'cover_transitions160';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');body=max((o for o in scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices));scene.render.fps=120
base=Matrix(json.loads((root/'amjviz_actions146/bake_report.json').read_text())['base_game_world'])
def pose(label,last=False):
 track=next(t for t in rig.animation_data.nla_tracks if t.name==label)
 for other in rig.animation_data.nla_tracks:other.mute=other!=track
 rig.animation_data.action=None;rig.matrix_world=base.copy()
 for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
 strip=track.strips[0];frame=strip.frame_end if last else strip.frame_start
 scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
 return {'object':rig.matrix_world.decompose(),'bones':{b.name:b.matrix_basis.decompose() for b in rig.pose.bones}}
standing=pose('Hard stand');crouch_start=pose('CoverStudy');crouch_end=pose('CoverStudy',True)
new_actions=[];reports={};frames=72
for label,start,end in [('CoverEnterStudy',standing,crouch_start),('CoverExitStudy',crouch_end,standing)]:
 for track in rig.animation_data.nla_tracks:track.mute=True
 action=bpy.data.actions.new(label);action.use_fake_user=True;rig.animation_data.action=action;rig.rotation_mode='QUATERNION';previous={};maximum_offset=0.
 for frame in range(frames+1):
  t=frame/frames;w=t*t*(3-2*t)
  scene.frame_set(frame)
  loc,rot,scale=start['object'];other_loc,other_rot,other_scale=end['object']
  rig.location=loc.lerp(other_loc,w);rig.rotation_quaternion=rot.slerp(other_rot,w);rig.scale=scale.lerp(other_scale,w)
  for b in rig.pose.bones:
   loc,rot,scale=start['bones'][b.name];other_loc,other_rot,other_scale=end['bones'][b.name]
   b.rotation_mode='QUATERNION';b.location=loc.lerp(other_loc,w);b.rotation_quaternion=rot.slerp(other_rot,w);b.scale=scale.lerp(other_scale,w)
   if b.name in previous:b.rotation_quaternion.make_compatible(previous[b.name])
   previous[b.name]=b.rotation_quaternion.copy()
  rig.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
  evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();floor=min((evaluated.matrix_world@v.co).z for v in mesh.vertices);evaluated.to_mesh_clear()
  delta=.001-floor if frame not in (0,frames) else 0.;rig.location.z+=delta;maximum_offset=max(maximum_offset,abs(delta))
  for b in rig.pose.bones:
   for channel in ('location','rotation_quaternion','scale'):b.keyframe_insert(channel,frame=frame,group=b.name)
  for channel in ('location','rotation_quaternion','scale'):rig.keyframe_insert(channel,frame=frame,group='TransitionPlacement')
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     for key in curve.keyframe_points:key.interpolation='LINEAR'
 new_actions.append(action);reports[label]={'frames':frames+1,'duration_s':frames/120,'maximum_ground_offset_m':maximum_offset,'source_poses':'Hard stand and grounded CC0 Crouch_Idle_Loop'}
 print('COVER160_TRANSITION_BAKED',label,flush=True)
rig.animation_data.action=None
for action in new_actions:
 track=rig.animation_data.nla_tracks.new();track.name=action.name;strip=track.strips.new(action.name,0,action);strip.action_frame_start=0;strip.action_frame_end=frames;strip.frame_start=0;strip.frame_end=frames;track.mute=True
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Hard stand'
rig.matrix_world=base.copy();scene.frame_set(0);bpy.context.view_layer.update()
notice=(source/'CREDITS.txt').read_text()+'\n160: pose-blended .6s cover enter/exit, grounded on actual body. No new geometry; source9clips retained. Foot sliding/contact and artistic acceptance pending.\n'
(out/'CREDITS.txt').write_text(notice);bpy.data.texts.new('COVER160_CHANGES').write(notice)
for o in scene.objects:o.select_set(o==rig or o.type=='MESH')
bpy.context.view_layer.objects.active=rig;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_raw.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,export_rest_position_armature=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_optimize_animation_keep_anim_object=True,export_all_influences=True)
g=Glb(out/'human_raw.glb');restore(g,Glb(source/'human.glb'));g.save(out/'human.glb')
(out/'transitions.json').write_text(json.dumps({'new_clips':reports,'variant_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'scope':'Pose-blended transitions, native/endpoints/contact/art review pending'},indent=2));print('COVER160_EXPORT_READY',flush=True)
