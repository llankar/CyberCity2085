"""Retarget two actual CC0 UAL motions onto the unchanged current authored actor."""
import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));sys.path.insert(0,str(Path(__file__).parent.parent))
from amjviz_fk import load,solve
from glb_document import Glb
from game_materials import restore
c=load();out=c.root/'generated/phase2/motion_extension159';out.mkdir(exist_ok=True)
scene=c.scene;game=c.game;scene.render.fps=120
for track in list(game.animation_data.nla_tracks):game.animation_data.nla_tracks.remove(track)
body=max((o for o in scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
reports={};actions=[]
for label,source in [('HitStudy','Hit_Chest'),('CoverStudy','Crouch_Idle_Loop')]:
 source_action=c.clips[source];first,last=source_action.frame_range
 frames=max(1,round((last-first)/24*120));action=bpy.data.actions.new(label);action.use_fake_user=True;game.animation_data.action=action
 previous={};worst=0.;max_lift=0.
 for sample in range(frames+1):
  worst=max(worst,solve(c,source,first+(last-first)*sample/frames))
  evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();floor=min((evaluated.matrix_world@v.co).z for v in mesh.vertices);evaluated.to_mesh_clear()
  lift=max(0.,.001-floor);max_lift=max(max_lift,lift);matrix=c.game_world.copy();matrix.translation.z+=lift;game.matrix_world=matrix
  for bone in game.pose.bones:
   if bone.name in previous:bone.rotation_quaternion.make_compatible(previous[bone.name])
   previous[bone.name]=bone.rotation_quaternion.copy()
   for channel in ('location','rotation_quaternion','scale'):bone.keyframe_insert(channel,frame=sample,group=bone.name)
  game.keyframe_insert('location',frame=sample,group='ExportFloorPlacement')
  if sample%30==0:print('MOTION159_BAKE',label,sample,frames,flush=True)
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     for key in curve.keyframe_points:key.interpolation='LINEAR'
 actions.append(action);reports[label]={'source_clip':source,'source_fps':24,'source_frames':[first,last],'duration_s':frames/120,'samples':frames+1,'maximum_game_transfer_error_m':worst,'maximum_floor_lift_m':max_lift}
bpy.data.libraries.write(str(out/'retargeted_actions.blend'),set(actions),fake_user=True)
root=c.root/'generated/phase2';bpy.ops.wm.open_mainfile(filepath=str(root/'face_review156/human_face035.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');scene.render.fps=120
with bpy.data.libraries.load(str(out/'retargeted_actions.blend'),link=False) as (_,data):data.actions=['HitStudy','CoverStudy']
for action in data.actions:
 track=rig.animation_data.nla_tracks.new();track.name=action.name;first,last=action.frame_range
 strip=track.strips.new(action.name,int(first),action);strip.action_frame_start=first;strip.action_frame_end=last;strip.frame_start=first;strip.frame_end=last;track.mute=True
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Hard stand'
rig.animation_data.action=None;scene.frame_set(0);bpy.context.view_layer.update()
notice=(root/'face_review156/CREDITS.txt').read_text()+'\n159: HitStudy retargeted from Quaternius UAL CC0 Hit_Chest; CoverStudy from Crouch_Idle_Loop. Existing original actor/geometry and seven clips retained. CoverStudy is only crouched motion, no tactical rule change. Healing absent, not replaced by repair animation.\n'
(out/'CREDITS.txt').write_text(notice);bpy.data.texts.new('MOTION159_CHANGES').write(notice)
for obj in scene.objects:obj.select_set(obj==rig or obj.type=='MESH')
bpy.context.view_layer.objects.active=rig;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_raw.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,export_rest_position_armature=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_optimize_animation_keep_anim_object=True,export_all_influences=True)
g=Glb(out/'human_raw.glb');restore(g,Glb(root/'face_review156/human_face035.glb'));g.save(out/'human.glb')
(out/'motions.json').write_text(json.dumps({'new_clips':reports,'source_actor_sha256':hashlib.sha256((root/'face_review156/human_face035.glb').read_bytes()).hexdigest(),'variant_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'scope':'Actual authored motion retarget/export, native and artistic acceptance pending'},indent=2))
print('MOTION159_EXPORT_READY',flush=True)
