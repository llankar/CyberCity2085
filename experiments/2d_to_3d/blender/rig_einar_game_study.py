"""Bake authored bone/rigid transforms into an independent game skeleton study.

Flat baked joints preserve film constraint results without shipping CloudRig.
Motion profiles are experimental; native and artistic gates remain separate.
"""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Quaternion, Vector
sys.path.insert(0,str(Path(__file__).parent))
from rigid_surface_fit import fit_surface
from ual_motion import UALMotion
from authored_scene import load_einar_scene

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
walk='--walk' in sys.argv
surface_corrections='--surface-corrections' in sys.argv
idle='--idle' in sys.argv or walk
ual_name=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--ual=')),None)
if ual_name and not all(c.isalnum() or c=='_' for c in ual_name): raise ValueError('Invalid animation name')
folder=root/((f'einar_ual_{ual_name}01' if ual_name else 'einar_walk01' if walk else 'einar_idle01' if idle else 'einar_rig01')+('_surfaces' if surface_corrections else '')); folder.mkdir(parents=True,exist_ok=True)
source_scene=load_einar_scene()
bpy.context.view_layer.update()
coverage=json.loads((root/'einar_pbr01/coverage.json').read_text())
names=tuple(coverage['dielectric_baked']+coverage['mechanical_baked'])
sources={name:bpy.data.objects[name.removesuffix('_GameStudy')] for name in names}
with bpy.data.libraries.load(str(root/'einar_pbr01/human_pbr.blend'),link=False) as (available,loaded):
    loaded.objects=list(names)
objects=list(loaded.objects)
bindings={}; mesh_records=[]
weight_stats={'vertices_over_8':0,'max_discarded_fraction':0.0,'max_influences':0}
for obj in objects:
    original=sources[obj.name]
    armatures=[m.object for m in original.modifiers if m.type=='ARMATURE' and m.object]
    deform={g.index:(armatures[0],g.name) for g in original.vertex_groups
            if armatures and g.name in armatures[0].data.bones and armatures[0].data.bones[g.name].use_deform}
    weights=[[(deform[g.group],g.weight) for g in v.groups if g.group in deform and g.weight>0]
             for v in obj.data.vertices]
    used={key for vertex in weights for key,weight in vertex}
    if used:
        for rig,name in used:
            key=(rig.name,name)
            bindings[key]={'kind':'bone','object':rig,'bone':name,
                           'baseline':rig.matrix_world @ rig.pose.bones[name].matrix}
    # Rigid bodies and uncovered vertices follow the actual authored object
    # transform, including all hydraulic/constraint chains during each sample.
    rigid_key=('rigid',original.name)
    if not used or any(not vertex for vertex in weights):
        bindings[rigid_key]={'kind':'object','object':original,'baseline':original.matrix_world.copy(),
                             'surface_baseline':[tuple(v.co) for v in obj.data.vertices]}
        weights=[vertex if vertex else [(rigid_key,1.0)] for vertex in weights]
    normalized=[]
    for vertex in weights:
        ordered=sorted(vertex,key=lambda item:item[1],reverse=True)
        total=sum(weight for key,weight in ordered)
        kept=ordered[:8]; kept_total=sum(weight for key,weight in kept)
        assert kept_total>0
        if len(ordered)>8: weight_stats['vertices_over_8']+=1
        weight_stats['max_discarded_fraction']=max(weight_stats['max_discarded_fraction'],(total-kept_total)/total)
        weight_stats['max_influences']=max(weight_stats['max_influences'],len(kept))
        normalized.append([((key[0].name,key[1]) if not isinstance(key[0],str) else key,weight/kept_total)
                           for key,weight in kept])
    mesh_records.append((obj,normalized))

game_scene=bpy.data.scenes.new('EinarGameSkeletonStudy')
bpy.context.window.scene=game_scene
armature=bpy.data.armatures.new('EinarBakedSkeleton')
game=bpy.data.objects.new('EinarGameRig',armature); game_scene.collection.objects.link(game)
bpy.context.view_layer.objects.active=game; game.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for index,(key,binding) in enumerate(sorted(bindings.items())):
    name=f'J{index:03d}_'+key[1][:52]
    bone=armature.edit_bones.new(name)
    rest=binding['baseline'].normalized()
    bone.head=rest.translation; bone.tail=rest @ Vector((0,.04,0)); bone.matrix=rest
    binding['joint']=bone.name; binding['rest']=bone.matrix.copy()
bpy.ops.object.mode_set(mode='OBJECT')
for obj,weights in mesh_records:
    game_scene.collection.objects.link(obj)
    world=obj.matrix_world.copy(); obj.parent=game; obj.matrix_world=world
    obj.vertex_groups.clear()
    groups={key:obj.vertex_groups.new(name=bindings[key]['joint'])
            for key in {key for vertex in weights for key,weight in vertex}}
    for index,vertex in enumerate(weights):
        for key,weight in vertex: groups[key].add([index],weight,'REPLACE')
    modifier=obj.modifiers.new('GameSkeleton','ARMATURE'); modifier.object=game
    obj.select_set(True)
bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()
neutral_error=0.0
for obj,weights in mesh_records:
    evaluated=obj.evaluated_get(graph)
    neutral_error=max(neutral_error,max((a.co-b.co).length for a,b in zip(obj.data.vertices,evaluated.data.vertices)))
assert neutral_error<.0001,neutral_error

game.animation_data_create()
clip=ual_name or ('Walk' if walk else 'Idle' if idle else 'FittingStressTest')
action=bpy.data.actions.new(clip); game.animation_data.action=action
source=bpy.data.objects['RIG-einar']; control=source.pose.bones['FK-Head']
control.rotation_mode='QUATERNION'; initial=control.rotation_quaternion.copy()
arms=[]
if idle:
    for key in ['ik_left_upperarm','ik_right_upperarm']: source.pose.bones['Properties'][key]=0.0
    source.update_tag(refresh={'OBJECT'})
    bpy.context.window.scene=source_scene; bpy.context.view_layer.update()
    for name,angle in [('FK-UpperArm.R',-1.05),('FK-UpperArm.L',1.05)]:
        arm=source.pose.bones[name]; arm.rotation_mode='QUATERNION'
        arms.append((arm,arm.rotation_quaternion.copy(),arm.matrix.to_quaternion().inverted() @ Vector((0,1,0)),angle))
max_source_delta=0.0
surface_errors={}
surface_samples={}
foot_goal_error=0.0
frames=33 if walk else 49
provider=None
if ual_name:
    bpy.context.window.scene=source_scene
    provider=UALMotion(source,ual_name)
    game_scene.render.fps=30
    frames=round(provider.duration*30)+1
feet=[]; torso=None
if walk:
    for name,offset in [('IK-MSTR-Foot.L',0.0),('IK-MSTR-Foot.R',.5)]:
        foot=source.pose.bones[name]; feet.append((foot,foot.matrix.copy(),offset))
    torso=source.pose.bones['MSTR-Spine_Torso']; torso_base=torso.matrix.copy()
    swing_axes={arm.name:arm.matrix.to_quaternion().inverted() @ Vector((1,0,0)) for arm,base,axis,angle in arms}
for frame in range(1,frames+1):
    bpy.context.window.scene=source_scene; source_scene.frame_set(frame)
    cycle=(frame-1)/(frames-1)
    phase=math.sin(cycle*math.tau)
    control.rotation_quaternion=initial @ Quaternion((0,1,0),(.025 if idle else .26)*phase)
    for arm,base,axis,angle in arms:
        lower=Quaternion(axis,angle*(1+.012*phase))
        if walk:
            swing=Quaternion(swing_axes[arm.name],(.18 if arm.name.endswith('.R') else -.18)*math.cos(cycle*math.tau))
            arm.rotation_quaternion=base @ swing @ lower
        else: arm.rotation_quaternion=base @ lower
    if walk:
        body=torso_base.copy(); body.translation.z+=-.04+.008*math.cos(cycle*math.tau*2)
        torso.matrix=body
        # Pose-space setters must see the newly evaluated parent transforms.
        source.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
        foot_targets=[]
        for foot,base,offset in feet:
            position=(cycle+offset)%1.0
            target=base.copy()
            if position<=.5:
                target.translation.y+=-.175+.7*position
            else:
                swing_phase=(position-.5)*2
                # Smooth lift, constant-velocity stance:0.7m virtual root travel/cycle.
                target.translation.y+=.175-.35*swing_phase
                target.translation.z+=.085*math.sin(math.pi*swing_phase)
            foot.matrix=target
            foot_targets.append((foot,target.translation.copy()))
    if idle: source.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
    if provider: provider.apply_fraction(cycle)
    if walk:
        for foot,target in foot_targets: foot_goal_error=max(foot_goal_error,(foot.matrix.translation-target).length)
    source_graph=bpy.context.evaluated_depsgraph_get()
    for binding in bindings.values():
        obj=binding['object']
        if binding['kind']=='bone':
            matrix=obj.matrix_world @ obj.pose.bones[binding['bone']].matrix
            delta=matrix @ binding['baseline'].inverted()
        else:
            evaluated=obj.evaluated_get(source_graph)
            mesh=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=source_graph)
            try:
                points=[tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices]
                delta,error=fit_surface(binding['surface_baseline'],points)
                surface_errors[obj.name]=max(surface_errors.get(obj.name,0),error)
                if surface_corrections:
                    surface_samples.setdefault(obj.name,[]).append((delta.copy(),points))
            finally: evaluated.to_mesh_clear()
        if binding.get('bone')=='DEF-Head': max_source_delta=max(max_source_delta,abs(delta.to_quaternion().angle))
        pose=game.pose.bones[binding['joint']]; pose.rotation_mode='QUATERNION'
        pose.matrix=delta @ binding['rest']
        for path in ['location','rotation_quaternion','scale']: pose.keyframe_insert(data_path=path,frame=frame,group=pose.name)
if not provider: assert max_source_delta>(.005 if idle else .05),('Source head control did not move',max_source_delta)
if provider: assert provider.max_rotation_error<.01,('Retarget control mismatch',provider.report())
control.rotation_quaternion=initial
bpy.context.window.scene=game_scene; game_scene.frame_start=1; game_scene.frame_end=frames; game_scene.frame_set(1)

corrections={}; reference={}
if surface_corrections:
    game_scene.name=clip
    for obj,weights in mesh_records:
        source_name=obj.name.removesuffix('_GameStudy')
        if surface_errors.get(source_name,0)<=.001: continue
        # A residual morph can only invert a single rigid binding here. Mixed
        # skin weights require a different inverse-skin solve; never guess it.
        keys={key for vertex in weights for key,weight in vertex}
        assert keys=={('rigid',source_name)},('Mixed skin correction unsupported',source_name)
        samples=surface_samples[source_name]
        assert len(samples)==frames
        obj.shape_key_add(name='Basis')
        local_inverse=obj.matrix_world.inverted()
        targets=[]
        for index,(delta,points) in enumerate(samples):
            shape=obj.shape_key_add(name=f'Surface_{index:03d}')
            inverse=local_inverse @ delta.inverted()
            for vertex,point in zip(shape.data,points): vertex.co=inverse @ Vector(point)
            for key_frame,value in [(max(1,index),0.0),(index+1,1.0),(min(frames,index+2),0.0)]:
                # Endpoints have no zero key on their own active frame.
                if key_frame==index+1 and value==0: continue
                shape.value=value; shape.keyframe_insert('value',frame=key_frame)
            shape.value=0
            targets.append(shape)
        for layer in obj.data.shape_keys.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for point in curve.keyframe_points: point.interpolation='LINEAR'
        corrections[source_name]={'targets':len(targets),'uncorrected_max_residual_m':surface_errors[source_name]}
        reference[obj.name]=[{'time_s':index/(game_scene.render.fps/game_scene.render.fps_base),
                             'points':[points[i] for i in range(0,len(points),8)]}
                            for index,(delta,points) in enumerate(samples)]
    assert corrections,'No nonrigid surfaces found'
    game_scene.frame_set(1)
    (folder/'surface_reference.json').write_text(json.dumps(reference),encoding='utf-8')
game.select_set(True); bpy.context.view_layer.objects.active=game
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human_rig.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human_rig.glb'),export_format='GLB',use_selection=True,
                        use_active_scene=True,export_animations=True,export_animation_mode='SCENE' if surface_corrections else 'ACTIONS',
                        export_anim_scene_split_object=False,export_nla_strips_merged_animation_name=clip,
                        export_anim_single_armature=False,export_all_influences=True,
                        export_anim_slide_to_zero=True)
report={'meshes':len(objects),'joints':len(bindings),'neutral_max_vertex_error':neutral_error,
        'source_head_rotation_radians':max_source_delta,'clip':clip,'frames':frames,'loop_intended':idle,
        'virtual_root_travel_m':.7 if walk else 0,
        'duration_s':(frames-1)/(game_scene.render.fps/game_scene.render.fps_base),
        'weight_optimization':weight_stats,
        'rigid_surface_max_residual_m':surface_errors,
        'surface_corrections':corrections,
        'source_foot_master_goal_error_m':foot_goal_error,
        'licensed_motion_retarget':provider.report() if provider else None,
        'joints_map':[{ 'joint':b['joint'],'source':list(key),'kind':b['kind']} for key,b in bindings.items()],
        'credit':coverage['credit'],'license':coverage['license'],
        'limitations':['Licensed motion retarget study; weapon grips and artistic quality not accepted' if provider else 'In-place walk study; foot contacts and artistic quality require native review' if walk else 'Relaxed idle study only; no gameplay action acceptance' if idle else 'Head fitting diagnostic only; no gameplay action acceptance',
                       'Baked flat joints require sampled source motion',
                       'Sampled residual morphs reproduce selected rigid-bound surface deformation; interpolation and normals need visual review' if surface_corrections else 'Static corrective shapes; no dynamic film surface-deform recreation',
                       'Hair is not included; rigid attachments require visual motion review']}
(folder/'rig_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_GAME_RIG_EXPORTED',len(bindings),neutral_error,flush=True)
