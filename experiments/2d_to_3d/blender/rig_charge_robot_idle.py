"""Preserve authored mechanical/constraint motion in an isolated idle study."""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Quaternion, Vector

sys.path.insert(0,str(Path(__file__).parent))
from authored_scene import load_authored_scene
from rigid_surface_fit import fit_surface

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'security_idle01'; folder.mkdir(parents=True,exist_ok=True)
source_scene=load_authored_scene(Path('E:/CyberCity2085-3d-lab/sources/charge_studio/security_bot_v1/security_bot_release_v1.blend'))
coverage=json.loads((root/'security_pbr_robot02/coverage.json').read_text())
names=tuple(coverage['baked'])
sources={name:bpy.data.objects[name.removesuffix('_Evaluated')] for name in names}
with bpy.data.libraries.load(str(root/'security_pbr_robot02/robot_pbr.blend'),link=False) as (available,loaded):
    loaded.objects=list(names)
objects=list(loaded.objects)
assert len(objects)==124
scene=bpy.data.scenes.new('Idle'); scene.render.fps=24
bpy.context.window.scene=scene
data=bpy.data.armatures.new('SecurityBakedSkeleton')
game=bpy.data.objects.new('SecurityGameRig',data); scene.collection.objects.link(game)
bpy.context.view_layer.objects.active=game; game.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for index,obj in enumerate(objects):
    bone=data.edit_bones.new(f'J{index:03d}')
    bone.head=(0,0,0); bone.tail=(0,0,.04)
bpy.ops.object.mode_set(mode='OBJECT')
for index,obj in enumerate(objects):
    scene.collection.objects.link(obj); obj.parent=game
    obj.vertex_groups.clear()
    group=obj.vertex_groups.new(name=f'J{index:03d}')
    group.add(list(range(len(obj.data.vertices))),1,'REPLACE')
    modifier=obj.modifiers.new('MechanicalSkin','ARMATURE'); modifier.object=game
    obj.select_set(True)
game.animation_data_create(); game.animation_data.action=bpy.data.actions.new('Idle')
rig=bpy.data.objects['RIG-security_bot']; control=rig.pose.bones['Head']
initial=control.matrix_basis.to_quaternion(); control.rotation_mode='QUATERNION'
frames=49; samples={name:[] for name in names}; residuals={name:0.0 for name in names}
max_neutral_error=0.0; head_motion=0.0
for frame in range(1,frames+1):
    bpy.context.window.scene=source_scene; source_scene.frame_set(frame)
    control.rotation_quaternion=initial @ Quaternion((0,1,0),.12*math.sin((frame-1)/(frames-1)*math.tau))
    rig.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    for index,obj in enumerate(objects):
        name=names[index]; source=sources[name]; evaluated=source.evaluated_get(graph)
        mesh=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=graph)
        try: points=[tuple(evaluated.matrix_world @ vertex.co) for vertex in mesh.vertices]
        finally: evaluated.to_mesh_clear()
        baseline=[tuple(v.co) for v in obj.data.vertices]
        delta,error=fit_surface(baseline,points)
        if frame==1:
            max_neutral_error=max(max_neutral_error,max((Vector(a)-Vector(b)).length for a,b in zip(baseline,points)))
        residuals[name]=max(residuals[name],error)
        samples[name].append((delta,points))
        pose=game.pose.bones[f'J{index:03d}']; pose.rotation_mode='QUATERNION'
        pose.matrix=delta @ pose.bone.matrix_local
        for path in ['location','rotation_quaternion','scale']: pose.keyframe_insert(path,frame=frame)
        if 'head_cover' in name: head_motion=max(head_motion,abs(delta.to_quaternion().angle))
assert max_neutral_error<.0001,('Neutral source mismatch',max_neutral_error)
assert head_motion>.03,('Head control failed',head_motion)
bpy.context.window.scene=scene
reference={}; corrections={}
for obj in objects:
    name=obj.name
    if residuals[name]>.001:
        obj.shape_key_add(name='Basis')
        for index,(delta,points) in enumerate(samples[name]):
            shape=obj.shape_key_add(name=f'Surface_{index:03d}'); inverse=delta.inverted()
            for vertex,point in zip(shape.data,points): vertex.co=inverse @ Vector(point)
            for key_frame,value in [(max(1,index),0.0),(index+1,1.0),(min(frames,index+2),0.0)]:
                if key_frame==index+1 and value==0: continue
                shape.value=value; shape.keyframe_insert('value',frame=key_frame)
            shape.value=0
        for layer in obj.data.shape_keys.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points: key.interpolation='LINEAR'
        corrections[name]=residuals[name]
    if name in corrections or 'head_cover' in name or 'shin.' in name:
        reference[name]=[{'time_s':index/24,'points':[points[i] for i in range(0,len(points),8)]}
                         for index,(delta,points) in enumerate(samples[name])]
scene.frame_start=1; scene.frame_end=frames; scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'robot_idle.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'robot_idle.glb'),export_format='GLB',use_selection=True,
    use_active_scene=True,export_animations=True,export_animation_mode='SCENE',
    export_anim_scene_split_object=False,export_anim_single_armature=False,export_anim_slide_to_zero=True)
(folder/'surface_reference.json').write_text(json.dumps(reference),encoding='utf-8')
coverage['rig_actions']='Idle head scan study only'
(folder/'coverage.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
(folder/'rig_report.json').write_text(json.dumps({'meshes':124,'joints':124,'clip':'Idle','duration_s':2,
    'neutral_max_vertex_error':max_neutral_error,'source_head_rotation_radians':head_motion,
    'rigid_surface_max_residual_m':residuals,'surface_corrections':corrections,
    'credit':coverage['credit'],'license':coverage['license'],
    'limitations':['Head scan idle only, not a gameplay action set','Opaque visor approximation','Source cables use sampled corrective morphs where required','Artistic and performance acceptance not verified']},indent=2),encoding='utf-8')
print('SECURITY_ROBOT_IDLE_EXPORTED',head_motion,max_neutral_error,len(corrections),flush=True)
