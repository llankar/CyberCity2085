"""Bake authored bone/rigid transforms into an independent game skeleton study.

Only a head deformation diagnostic is authored here, not a gameplay animation.
Flat baked joints preserve film constraint results without shipping CloudRig.
"""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Quaternion, Vector

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
idle='--idle' in sys.argv
folder=root/('einar_idle01' if idle else 'einar_rig01'); folder.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/sources/charge_studio/einar_release_v1.blend',use_scripts=False)
source_scene=bpy.context.scene
for obj in bpy.data.objects:
    if obj.animation_data:
        for driver in obj.animation_data.drivers:
            if 'depsgraph.scene.camera' in driver.driver.expression: driver.mute=True
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
        bindings[rigid_key]={'kind':'object','object':original,'baseline':original.matrix_world.copy()}
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
clip='Idle' if idle else 'FittingStressTest'
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
for frame in range(1,50):
    bpy.context.window.scene=source_scene; source_scene.frame_set(frame)
    phase=math.sin((frame-1)*math.tau/48)
    control.rotation_quaternion=initial @ Quaternion((0,1,0),(.025 if idle else .26)*phase)
    for arm,base,axis,angle in arms:
        arm.rotation_quaternion=base @ Quaternion(axis,angle*(1+.012*phase))
    if idle: source.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
    for binding in bindings.values():
        obj=binding['object']
        matrix=obj.matrix_world @ obj.pose.bones[binding['bone']].matrix if binding['kind']=='bone' else obj.matrix_world.copy()
        delta=matrix @ binding['baseline'].inverted()
        if binding.get('bone')=='DEF-Head': max_source_delta=max(max_source_delta,abs(delta.to_quaternion().angle))
        pose=game.pose.bones[binding['joint']]; pose.rotation_mode='QUATERNION'
        pose.matrix=delta @ binding['rest']
        for path in ['location','rotation_quaternion','scale']: pose.keyframe_insert(data_path=path,frame=frame,group=pose.name)
assert max_source_delta>(.005 if idle else .05),('Source head control did not move',max_source_delta)
control.rotation_quaternion=initial
bpy.context.window.scene=game_scene; game_scene.frame_start=1; game_scene.frame_end=49; game_scene.frame_set(1)
game.select_set(True); bpy.context.view_layer.objects.active=game
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human_rig.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human_rig.glb'),export_format='GLB',use_selection=True,
                        use_active_scene=True,export_animations=True,export_animation_mode='ACTIONS',
                        export_anim_single_armature=False,export_all_influences=True)
report={'meshes':len(objects),'joints':len(bindings),'neutral_max_vertex_error':neutral_error,
        'source_head_rotation_radians':max_source_delta,'clip':clip,'frames':49,'loop_intended':idle,
        'weight_optimization':weight_stats,
        'joints_map':[{ 'joint':b['joint'],'source':list(key),'kind':b['kind']} for key,b in bindings.items()],
        'credit':coverage['credit'],'license':coverage['license'],
        'limitations':['Relaxed idle study only; no gameplay action acceptance' if idle else 'Head fitting diagnostic only; no gameplay action acceptance',
                       'Baked flat joints require sampled source motion',
                       'Static corrective shapes; no dynamic film surface-deform recreation',
                       'Hair is not included; rigid attachments require visual motion review']}
(folder/'rig_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_GAME_RIG_EXPORTED',len(bindings),neutral_error,flush=True)
