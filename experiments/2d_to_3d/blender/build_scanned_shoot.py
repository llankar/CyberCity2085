"""Consolidate a real, level-aim firing study onto the same first human candidate."""
import json,sys,math
from pathlib import Path
import bpy
from mathutils import Matrix,Quaternion
sys.path.insert(0,str(Path(__file__).parent.parent))
from aim_geometry import horizontal_aim_correction

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=root/'scanned_armor_shoot01';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'scanned_armor_hair01/human_actions.blend'),use_scripts=False)
scene=bpy.data.scenes['AuthoredGameActions'];bpy.context.window.scene=scene
rig=bpy.data.objects['AuthoredGameRig'];assert len(rig.pose.bones)==122
with bpy.data.libraries.load(str(root/'unvanquished_weapon01/human_actions.blend'),link=False) as (available,loaded):
 assert 'Baked_Pistol_Attack_Study' in available.actions
 loaded.actions=['Baked_Pistol_Attack_Study']
source_action=loaded.actions[0]
for track in rig.animation_data.nla_tracks:track.mute=True
rig.animation_data.action=source_action
if source_action.slots:rig.animation_data.action_slot=source_action.slots[0]
poses=[]
for frame in range(9):
 scene.frame_set(frame);bpy.context.view_layer.update()
 poses.append({bone.name:bone.matrix.copy() for bone in rig.pose.bones})
rig.animation_data.action=bpy.data.actions.new('Rook_Level_Aim_Study')
nominal=(rig.matrix_world@poses[0]['hand.R']).translation-(rig.matrix_world@poses[0]['forearm.R']).translation
correction=Quaternion(horizontal_aim_correction(nominal))
errors=[];direction_errors=[];previous={}
for frame,pose in enumerate(poses):
 scene.frame_set(frame)
 for bone in rig.pose.bones:
  args={'matrix':pose[bone.name],'matrix_local':bone.bone.matrix_local,'invert':True}
  if bone.parent:args.update(parent_matrix=pose[bone.parent.name],parent_matrix_local=bone.parent.bone.matrix_local)
  bone.matrix_basis=bone.bone.convert_local_to_pose(**args)
 bpy.context.view_layer.update()
 def position(name):return (rig.matrix_world@rig.pose.bones[name].matrix).translation
 before=position('hand.R')-position('forearm.R')
 upper=rig.pose.bones['upper_arm.R'];world=rig.matrix_world@upper.matrix;pivot=world.translation.copy()
 corrected=Matrix.Translation(pivot)@correction.to_matrix().to_4x4()@Matrix.Translation(-pivot)@world
 upper.matrix=rig.matrix_world.inverted()@corrected
 bpy.context.view_layer.update()
 after=(position('hand.R')-position('forearm.R')).normalized()
 expected=correction@before.normalized()
 direction_error=(after-expected).length
 assert direction_error<1e-5,('Authored recoil changed',frame,direction_error)
 if frame==0:assert abs(after.z)<1e-5,'Nominal aim not level'
 errors.append(abs(after.z));direction_errors.append(direction_error)
 for bone in rig.pose.bones:
  quaternion=bone.rotation_quaternion.copy()
  if bone.name in previous and quaternion.dot(previous[bone.name])<0:quaternion.negate();bone.rotation_quaternion=quaternion
  previous[bone.name]=quaternion.copy()
  for path in ['location','rotation_quaternion','scale']:bone.keyframe_insert(path,frame=frame)
action=rig.animation_data.action
for layer in action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for curve in bag.fcurves:
    for key in curve.keyframe_points:key.interpolation='LINEAR'
track=rig.animation_data.nla_tracks.new();track.name='Shoot'
strip=track.strips.new('Shoot',0,action);strip.scale=2
rig.animation_data.action=None
for track in rig.animation_data.nla_tracks:track.mute=False
notice=(root/'scanned_armor_hair01/CREDITS.txt').read_text()+'\nAdded: source blaster-attack hand-delta study transferred by identical122bone game hierarchy. One constant world-space upper-arm correction levels nominal aim and preserves source angular recoil. Source six body actions retained. Firing grip/contact/art remain experimental.\n'
bpy.data.texts.new('LEVEL_AIM_CREDITS').write(notice)
for obj in scene.objects:obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(out/'human_actions.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_keep_anim_armature=True,export_extras=True,export_copyright=notice)
references={};durations={};meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==18
for track in rig.animation_data.nla_tracks:
 for other in rig.animation_data.nla_tracks:other.mute=other!=track
 duration=track.strips[0].frame_end/120;durations[track.name]=duration;samples=[]
 sample_count=17 if track.name=='Shoot' else 9
 for index in range(sample_count):
  fraction=index/(sample_count-1);frame=duration*120*fraction;scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
  graph=bpy.context.evaluated_depsgraph_get();geometry={}
  for obj in meshes:
   e=obj.evaluated_get(graph);data=e.to_mesh()
   geometry[obj.name]=[list(e.matrix_world@data.vertices[i].co) for i in range(0,len(data.vertices),max(1,len(data.vertices)//12))];e.to_mesh_clear()
  samples.append({'time_s':duration*fraction,'meshes':geometry})
 references[track.name]=samples
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Idle'
scene.frame_set(0);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human_actions.blend'))
(out/'source_surface_reference.json').write_text(json.dumps(references))
(out/'aim_report.json').write_text(json.dumps({'constant_right_upper_arm_correction_degrees':math.degrees(correction.angle),'nominal_vertical_aim_component':errors[0],'max_recoil_vertical_aim_component':max(errors),'max_recoil_direction_error':max(direction_errors),'clip_durations_s':durations,'bones':122,'meshes':18,'source_six_body_clips_preserved':True,'limitations':['Nominal aiming/recoil preservation is not trigger/contact or final artistic acceptance','No weapon included in body GLB; separate real prop attachment follows']},indent=2))
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
print('SCANNED_HUMAN_LEVEL_SHOOT_EXPORTED',max(direction_errors),math.degrees(correction.angle),durations,flush=True)
