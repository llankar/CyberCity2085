"""Author aim/recoil/slide/return on actual equipped licensed geometry."""
import json
import hashlib
import sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector,Quaternion
sys.path.insert(0,str(Path(__file__).parent.parent))
from two_bone_ik import elbow_target
from cyborg_fire_motion import sample

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'cyborg_pistol01'
out=root/'cyborg_fire01'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
ready=next(track for track in rig.animation_data.nla_tracks if track.name=='CombatReadyStudy')
for track in rig.animation_data.nla_tracks:track.mute=track!=ready
scene.frame_set(0);bpy.context.view_layer.update()
base={bone.name:bone.matrix_basis.copy() for bone in rig.pose.bones}
orientations={side:(rig.matrix_world@rig.pose.bones[side+'Hand'].matrix).to_quaternion() for side in ('Right','Left')}
bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
slide=rig.data.edit_bones.new('PistolSlide')
slide.parent=rig.data.edit_bones['RightHand']
slide.matrix=slide.parent.matrix.copy()
slide.length=1
bpy.ops.object.mode_set(mode='OBJECT')
slide_mesh=next(o for o in scene.objects if o.name.startswith('Pistol_EquippedPistol_slide'))
slide_mesh.vertex_groups.clear()
slide_mesh.vertex_groups.new(name='PistolSlide').add(list(range(len(slide_mesh.data.vertices))),1,'REPLACE')
for track in rig.animation_data.nla_tracks:track.mute=True
for previous in rig.animation_data.nla_tracks:
    rig.animation_data.action=previous.strips[0].action
    control=rig.pose.bones['PistolSlide']
    control.rotation_mode='QUATERNION'
    control.matrix_basis=Matrix.Identity(4)
    for frame in (previous.strips[0].action_frame_start,previous.strips[0].action_frame_end):
        for channel in ('location','rotation_quaternion','scale'):control.keyframe_insert(channel,frame=frame,group=control.name)
action=bpy.data.actions.new('PistolFireStudy')
rig.animation_data.action=action

def point(name):return rig.matrix_world@rig.pose.bones[name].matrix.translation

def rotate(name,target,endpoint):
    pivot=point(name)
    rotation=(point(endpoint)-pivot).rotation_difference(target-pivot)
    world=rig.matrix_world@rig.pose.bones[name].matrix
    rig.pose.bones[name].matrix=rig.matrix_world.inverted()@Matrix.Translation(pivot)@rotation.to_matrix().to_4x4()@Matrix.Translation(-pivot)@world
    bpy.context.view_layer.update()

errors=[]
for frame in range(19):
    scene.frame_set(frame)
    for bone in rig.pose.bones:bone.matrix_basis=base.get(bone.name,Matrix.Identity(4))
    bpy.context.view_layer.update()
    motion=sample(frame)
    pitch=Quaternion((1,0,0),motion['pitch_rad'])
    arm_errors=[]
    for side,low,high in [('Right',(-.105,-.35,1.31),(-.105,-.27,1.63)),('Left',(.075,-.32,1.24),(.075,-.24,1.56))]:
        upper,lower,hand=[side+part for part in ('Arm','ForeArm','Hand')]
        a,b,c=point(upper),point(lower),point(hand)
        lengths=[(b-a).length,(c-b).length]
        target=Vector(low).lerp(Vector(high),motion['raise'])+Vector((0,.025*motion['recoil'],.008*motion['recoil']))
        elbow=Vector(elbow_target(a,target,[0,0,-1],*lengths))
        rotate(upper,elbow,lower)
        rotate(lower,target,hand)
        world=rig.matrix_world@rig.pose.bones[hand].matrix
        rig.pose.bones[hand].matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(world.translation,pitch@orientations[side],world.to_scale())
        bpy.context.view_layer.update()
        arm_errors.append(max((point(hand)-target).length,abs((point(lower)-point(upper)).length-lengths[0]),abs((point(hand)-point(lower)).length-lengths[1])))
    slide=rig.pose.bones['PistolSlide']
    slide.location=(rig.matrix_world@slide.matrix).to_3x3().inverted()@(pitch@Vector((0,motion['slide_back_m'],0)))
    bpy.context.view_layer.update()
    for bone in rig.pose.bones:
        bone.rotation_mode='QUATERNION'
        for channel in ('location','rotation_quaternion','scale'):bone.keyframe_insert(channel,frame=frame,group=bone.name)
    errors.append(max(arm_errors))
assert max(errors)<.00002,max(errors)
rig.animation_data.action=None
track=rig.animation_data.nla_tracks.new();track.name='PistolFireStudy'
strip=track.strips.new('PistolFireStudy',0,action)
strip.action_frame_start=0;strip.action_frame_end=18;strip.frame_start=0;strip.frame_end=18
helpers={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
meshes=[o for o in scene.objects if o.type=='MESH' and o not in helpers]
references=[]
for frame in range(19):
    scene.frame_set(frame);bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    boxes={}
    for obj in meshes:
        evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
        points=[evaluated.matrix_world@v.co for v in data.vertices]
        boxes[obj.name.replace('.','_').replace(' ','_')]=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
        evaluated.to_mesh_clear()
    references.append({'time_s':frame/24,'mesh_bounds_blender':boxes})
(out/'native_reference.json').write_text(json.dumps(references,indent=2),encoding='utf8')
scene.frame_set(0)
for obj in scene.objects:obj.select_set(obj==rig or obj in meshes)
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\nOriginal experimental aim/recoil/return and20mm pistol slide animation. No animated trigger finger or final art acceptance.\n'
credits=bpy.data.texts.new('FIRING_STUDY_CREDITS');credits.write(notice);credits.use_fake_user=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'fire_report.json').write_text(json.dumps({'maximum_arm_error_m':max(errors),'bones':len(rig.data.bones),'duration_s':.75,'slide_travel_m':.02,'samples':19,'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'limitations':['Wrist seam and support-hand surface contact not accepted','No independently animated trigger finger','Animation only; no combat rule or production change']},indent=2),encoding='utf8')
print('CYBORG_FIRE_STUDY_EXPORTED',max(errors),flush=True)
