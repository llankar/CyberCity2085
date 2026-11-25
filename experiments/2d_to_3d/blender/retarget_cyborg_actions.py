"""Retarget actual CC0 UAL melee/death onto the first equipped cyberpunk actor."""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from clearance_envelope import endpoint_lifts

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
library=Path('E:/CyberCity2085-3d-lab/sources/quaternius_ual_standard')
out=root/'cyborg_actions01'
out.mkdir(exist_ok=True)
if (out/'retarget_report.json').exists() and not (out/'raw_retarget123.json').exists():shutil.copyfile(out/'retarget_report.json',out/'raw_retarget123.json')
bpy.ops.wm.open_mainfile(filepath=str(root/'cyborg_fire01/human.blend'),use_scripts=False)
scene=bpy.context.scene
target=next(o for o in scene.objects if o.type=='ARMATURE')
for track in target.animation_data.nla_tracks:
    track.mute=True
    # glTF force-sampling emits linear tracks at source24fps. Avoid implicit
    # Blender Bezier overshoot between those keys in this combined derivative.
    for layer in track.strips[0].action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
target.animation_data.action=None
for bone in target.pose.bones:bone.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
with bpy.data.libraries.load(str(library/'animation_library.blend'),link=False) as (available,loaded):
    loaded.objects=['Armature']
source=loaded.objects[0]
scene.collection.objects.link(source)
clips={track.name:strip.action for track in source.animation_data.nla_tracks for strip in track.strips}
for track in source.animation_data.nla_tracks:track.mute=True
source.animation_data.action=None
bpy.context.view_layer.update()
mapping={'Hips':'pelvis','Spine02':'spine_01','Spine01':'spine_02','Spine':'spine_03','neck':'neck_01','Head':'Head'}
for side,suffix in [('Left','l'),('Right','r')]:
    for part,other in [('Shoulder','clavicle'),('Arm','upperarm'),('ForeArm','lowerarm'),('Hand','hand'),('UpLeg','thigh'),('Leg','calf'),('Foot','foot'),('ToeBase','ball')]:mapping[side+part]=other+'_'+suffix
assert all(name in target.pose.bones and other in source.pose.bones for name,other in mapping.items())
rest={name:target.matrix_world@target.data.bones[name].matrix_local for name in mapping}
source_rest={other:source.matrix_world@source.data.bones[other].matrix_local for other in mapping.values()}

def frame(values,left,right,hips,head):
    up=(values[head].translation-values[hips].translation).normalized()
    lateral=values[left].translation-values[right].translation
    lateral=(lateral-up*lateral.dot(up)).normalized()
    back=up.cross(lateral).normalized()
    result=Matrix((lateral,back,up)).transposed()
    assert abs(result.determinant()-1)<.00001
    return result

alignment=frame(rest,'LeftArm','RightArm','Hips','Head')@frame(source_rest,'upperarm_l','upperarm_r','pelvis','Head').inverted()
coordinate_rotation=alignment.to_quaternion()
calibrated={name:matrix.to_quaternion() for name,matrix in rest.items()}
for side in ('Left','Right'):
    for parent,child in [('Arm','ForeArm'),('ForeArm','Hand')]:
        name,child_name=side+parent,side+child
        actual=rest[child_name].translation-rest[name].translation
        desired=alignment@(source_rest[mapping[child_name]].translation-source_rest[mapping[name]].translation)
        swing=actual.rotation_difference(desired)
        calibrated[name]=swing@calibrated[name]
        if parent=='ForeArm':calibrated[side+'Hand']=swing@calibrated[side+'Hand']
order=sorted(mapping,key=lambda name:len(target.pose.bones[name].parent_recursive))
scale=rest['Hips'].translation.z/source_rest['pelvis'].translation.z
inverse=target.matrix_world.inverted()
helpers={bone.custom_shape for bone in target.pose.bones if bone.custom_shape}
meshes=[obj for obj in scene.objects if obj.type=='MESH' and obj not in helpers]
reports={}
for label,clip in [('MeleeStudy','Punch_Cross'),('DeathStudy','Death01')]:
    source.animation_data.action=clips[clip]
    if clips[clip].slots:source.animation_data.action_slot=clips[clip].slots[0]
    first,last=clips[clip].frame_range
    duration=(last-first)/24
    count=round(duration*24)
    action=bpy.data.actions.new(label)
    target.animation_data.action=action
    floors=[];lifts=[]
    previous={}
    for index in range(count+1):
        source_frame=first+(last-first)*index/count
        scene.frame_set(math.floor(source_frame),subframe=source_frame%1)
        for bone in target.pose.bones:bone.matrix_basis=Matrix.Identity(4)
        bpy.context.view_layer.update()
        graph=bpy.context.evaluated_depsgraph_get()
        evaluated=source.evaluated_get(graph)
        poses={other:evaluated.matrix_world@evaluated.pose.bones[other].matrix for other in mapping.values()}
        for name in order:
            other=mapping[name]
            pose=target.pose.bones[name]
            delta=coordinate_rotation@(poses[other].to_quaternion()@source_rest[other].to_quaternion().inverted())@coordinate_rotation.inverted()
            desired=(delta@calibrated[name]).to_matrix().to_4x4()
            desired.translation=target.matrix_world@pose.matrix.translation
            if name=='Hips':desired.translation=rest[name].translation+alignment@(poses[other].translation-source_rest[other].translation)*scale
            pose.matrix=inverse@desired
            if name!='Hips':pose.location=Vector()
            pose.scale=Vector((1,1,1))
            bpy.context.view_layer.update()
        # Record raw clearance first. No hidden floor correction or physics claim.
        graph=bpy.context.evaluated_depsgraph_get()
        points=[]
        for obj in meshes:
            evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
            points.extend(evaluated.matrix_world@v.co for v in data.vertices)
            evaluated.to_mesh_clear()
        raw_floor=min(p.z for p in points)
        floors.append(raw_floor)
        lift=max(0.,.001-raw_floor)
        if lift:
            hip=target.pose.bones['Hips']
            world=target.matrix_world@hip.matrix
            world.translation+=Vector((0,0,lift))
            hip.matrix=inverse@world
            bpy.context.view_layer.update()
        lifts.append(lift)
        for bone in target.pose.bones:
            bone.rotation_mode='QUATERNION'
            if bone.name in previous:bone.rotation_quaternion.make_compatible(previous[bone.name])
            previous[bone.name]=bone.rotation_quaternion.copy()
            for channel in ('location','rotation_quaternion','scale'):bone.keyframe_insert(channel,frame=index,group=bone.name)
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    target.animation_data.action=None
    track=target.animation_data.nla_tracks.new();track.name=label
    strip=track.strips.new(label,0,action)
    strip.action_frame_start=0;strip.action_frame_end=count;strip.frame_start=0;strip.frame_end=count
    track.mute=False
    deficits=[]
    for interval in range(count):
        minimum=1.
        for fraction in (.25,.5,.75):
            scene.frame_set(interval,subframe=fraction);bpy.context.view_layer.update()
            graph=bpy.context.evaluated_depsgraph_get()
            for obj in meshes:
                evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
                minimum=min(minimum,min((evaluated.matrix_world@v.co).z for v in data.vertices))
                evaluated.to_mesh_clear()
        deficits.append(max(0.,.001-minimum))
    additional=endpoint_lifts(deficits)
    track.mute=True
    target.animation_data.action=action
    for index,lift in enumerate(additional):
        if not lift:continue
        scene.frame_set(index);bpy.context.view_layer.update()
        hip=target.pose.bones['Hips']
        world=target.matrix_world@hip.matrix
        world.translation+=Vector((0,0,lift))
        hip.matrix=inverse@world
        hip.keyframe_insert('location',frame=index,group=hip.name)
    target.animation_data.action=None
    reports[label]={'source_clip':clip,'source_duration_s':duration,'duration_s':count/24,'frames':count+1,'minimum_raw_floor_m':min(floors),'final_raw_floor_m':floors[-1],'maximum_vertical_floor_lift_m':max(a+b for a,b in zip(lifts,additional)),'final_vertical_floor_lift_m':lifts[-1]+additional[-1],'maximum_additional_interkey_lift_m':max(additional),'interkey_probe_fractions':[.25,.5,.75]}
    print('CYBORG_LICENSED_MOTION_BAKED',label,reports[label],flush=True)
bpy.data.objects.remove(source,do_unlink=True)
references={}
for selected in target.animation_data.nla_tracks:
    for track in target.animation_data.nla_tracks:track.mute=track!=selected
    strip=selected.strips[0]
    samples=[]
    sample_count=round((strip.frame_end-strip.frame_start)*2)+1 if selected.name in ('MeleeStudy','DeathStudy') else 9
    for index in range(sample_count):
        value=strip.frame_start+(strip.frame_end-strip.frame_start)*index/(sample_count-1)
        scene.frame_set(math.floor(value),subframe=value%1)
        bpy.context.view_layer.update()
        graph=bpy.context.evaluated_depsgraph_get()
        boxes={}
        for obj in meshes:
            evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
            points=[evaluated.matrix_world@v.co for v in data.vertices]
            boxes[obj.name.replace('.','_').replace(' ','_')]=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
            evaluated.to_mesh_clear()
        samples.append({'time_s':(value-strip.frame_start)/24,'mesh_bounds_blender':boxes})
    references[selected.name]=samples
(out/'native_reference.json').write_text(json.dumps(references,indent=2),encoding='utf8')
for track in target.animation_data.nla_tracks:track.mute=track.name!='MeleeStudy'
scene.frame_set(0);bpy.context.view_layer.update()
for obj in scene.objects:obj.select_set(obj==target or obj in meshes)
bpy.context.view_layer.objects.active=target
notice=(root/'cyborg_fire01/CREDITS.txt').read_text()+'\nMelee/death motion: Quaternius Universal Animation Library Standard, CC0 https://quaternius.com/packs/universalanimationlibrary.html\n'+(library/'License.txt').read_text()+'\nGlobal rotation retarget with explicit whole-body vertical floor-clearance correction; no collision/ragdoll/contact or artistic acceptance.\n'
credits=bpy.data.texts.new('QUATERNIUS_MOTION_CREDITS');credits.write(notice);credits.use_fake_user=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'retarget_report.json').write_text(json.dumps({'mapping':mapping,'pelvis_scale':scale,'coordinate_rotation':[list(row) for row in alignment],'clips':reports,'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'limitations':['No planted-foot or hand-contact correction','Vertical floor lift is not collision simulation','No artistic acceptance or production integration']},indent=2),encoding='utf8')
print('CYBORG_ACTIONS_EXPORTED',flush=True)
