"""First length-preserving support-arm fit through genuine source FK controls."""
import json,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
sys.path.insert(0,str(Path(__file__).parent))
from two_bone_ik import solve as elbow_solve
from amjviz_fk import load,solve
from glb_document import Glb
from game_materials import restore

c=load();root=c.root/'generated/phase2';out=root/'amjviz_grip149';out.mkdir(exist_ok=True)
curl_study='--curl-study' in sys.argv
animated='--animated' in sys.argv
assert not(animated and curl_study),'Finger curl diagnostic is not approved for full animation'
stem='human_actions' if animated else ('shoot_curl' if curl_study else 'shoot_support')
measurements={}
def adjust(context):
    driver=context.driver
    names=['upper_arm_fk.L','forearm_fk.L','hand_fk.L']
    original=[driver.matrix_world@driver.pose.bones[n].matrix for n in names]
    shoulder,elbow,wrist=[m.translation.copy() for m in original]
    right=(driver.matrix_world@driver.pose.bones['hand_fk.R'].matrix).translation
    target=right+Vector((.045,.030,-.025))
    new_elbow,new_wrist=map(Vector,elbow_solve(shoulder,elbow,wrist,target))
    rotations=[(elbow-shoulder).rotation_difference(new_elbow-shoulder),
               (wrist-elbow).rotation_difference(new_wrist-new_elbow)]
    desired=[Matrix.Translation(shoulder)@rotations[0].to_matrix().to_4x4()@Matrix.Translation(-shoulder)@original[0],
             Matrix.Translation(new_elbow)@rotations[1].to_matrix().to_4x4()@Matrix.Translation(-elbow)@original[1],
             original[2].copy()]
    desired[2].translation=new_wrist
    for name,matrix in zip(names,desired):
        driver.pose.bones[name].matrix=driver.matrix_world.inverted()@matrix
        driver.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
    actual=(driver.matrix_world@driver.pose.bones['hand_fk.L'].matrix).translation
    assert (actual-new_wrist).length<.0001,(actual-new_wrist).length
    measurements.update({'old_wrist':list(wrist),'target':list(target),'actual_wrist':list(actual),
        'wrist_displacement_m':(actual-wrist).length,'target_error_m':(actual-target).length,
        'upper_length_m':(elbow-shoulder).length,'new_upper_length_m':(new_elbow-shoulder).length,
        'lower_length_m':(wrist-elbow).length,'new_lower_length_m':(new_wrist-new_elbow).length})
    if curl_study:
        digits={}
        for digit in ('index','middle','ring','pinky'):
            controls=[driver.pose.bones[f'f_{digit}.{j:02d}.L'] for j in (1,2,3)]
            bases=[bone.matrix_basis.copy() for bone in controls]
            goal=driver.matrix_world@driver.pose.bones[f'f_{digit}.02.R'].head+Vector((.012,0,-.005))
            def evaluate(angle):
                for bone,base in zip(controls,bases):bone.matrix_basis=base@Matrix.Rotation(angle,4,'X')
                driver.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
                return ((driver.matrix_world@controls[-1].tail)-goal).length
            before=evaluate(0.)
            choices=[(evaluate(angle),angle) for angle in (0.,-.2,-.4,-.6,-.8,.2,.4,.6,.8)]
            error,angle=min(choices);evaluate(angle)
            digits[digit]={'angle_per_joint_rad':angle,'initial_tip_goal_m':before,'final_tip_goal_m':error}
        measurements['finger_landmark_fit']=digits

poses=[];fit_reports=[]
for sample in (range(77) if animated else [38]):
    solve(c,'Pistol_Shoot',15.1999998093*sample/76,adjust_controls=adjust)
    poses.append({bone.name:bone.matrix_basis.copy() for bone in c.game.pose.bones})
    fit_reports.append(dict(measurements))
    if animated and sample%20==0:print('SUPPORT_ARM_BAKE_PROGRESS',sample,76,flush=True)
basis=poses[0]
world=c.game.matrix_world.copy()
bpy.ops.wm.open_mainfile(filepath=str(root/'amjviz_hair148/human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.animation_data.action=None
for track in rig.animation_data.nla_tracks:track.mute=True
rig.matrix_world=world
for bone in rig.pose.bones:bone.matrix_basis=basis[bone.name]
bpy.context.view_layer.update()
if animated:
    for track in list(rig.animation_data.nla_tracks):
        if track.name=='ShootStudy':rig.animation_data.nla_tracks.remove(track)
    action=bpy.data.actions.new('SupportShoot149');action.use_fake_user=True;rig.animation_data.action=action
    previous={}
    for frame,pose in enumerate(poses):
        rig.matrix_world=world
        for bone in rig.pose.bones:
            bone.rotation_mode='QUATERNION';bone.matrix_basis=pose[bone.name]
            if bone.name in previous:bone.rotation_quaternion.make_compatible(previous[bone.name])
            previous[bone.name]=bone.rotation_quaternion.copy()
            for channel in ('location','rotation_quaternion','scale'):bone.keyframe_insert(channel,frame=frame,group=bone.name)
        rig.keyframe_insert('location',frame=frame,group='SourceBasePlacement')
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    rig.animation_data.action=None
    track=rig.animation_data.nla_tracks.new();track.name='ShootStudy'
    strip=track.strips.new('ShootStudy',0,action);strip.action_frame_start=0;strip.action_frame_end=76
    strip.frame_start=0;strip.frame_end=76
    scene.frame_set(38);bpy.context.view_layer.update()
notice=(root/'amjviz_hair148/CREDITS.txt').read_text()+ '\n149 support-arm fit through original FK controls, preserving two-link lengths. No collision/contact solver or final animation art acceptance.\n'
render_meshes=[o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
for obj in scene.objects:obj.select_set(obj==rig or obj in render_meshes)
bpy.context.view_layer.objects.active=rig
references={};graph=bpy.context.evaluated_depsgraph_get()
for obj in render_meshes:
    evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
    points=[evaluated.matrix_world@v.co for v in mesh.vertices]
    references[obj.name.replace('.','_').replace(' ','_')]=[[min(p[j] for p in points) for j in range(3)],[max(p[j] for p in points) for j in range(3)]]
    evaluated.to_mesh_clear()
(out/(stem+'_reference.json')).write_text(json.dumps(references))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/(stem+'.blend')))
bpy.ops.export_scene.gltf(filepath=str(out/(stem+'_raw.glb')),export_format='GLB',use_selection=True,
    export_animations=animated,export_current_frame=not animated,export_rest_position_armature=animated,
    export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,
    export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,
    export_optimize_animation_keep_anim_object=True,
    export_all_influences=True,export_copyright=notice)
compiled=Glb(out/(stem+'_raw.glb'));restore(compiled,Glb(root/'amjviz_hair148/human.glb'));compiled.save(out/(stem+'.glb'))
(out/'CREDITS.txt').write_text(notice)
measurements['scope']='Source FK support-arm fit; finger/contact and final artistic validation still required'
if animated:measurements['clip_samples']=fit_reports
(out/(stem+'_fit.json')).write_text(json.dumps(measurements,indent=2))
print('AMJVIZ_SUPPORT_ARM_STATIC_READY',json.dumps(measurements),flush=True)
