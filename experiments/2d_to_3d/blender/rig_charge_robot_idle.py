"""Preserve authored mechanical/constraint motion in isolated action studies."""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion, Vector
from mathutils.kdtree import KDTree

sys.path.insert(0,str(Path(__file__).parent))
from authored_scene import load_authored_scene
from rigid_surface_fit import fit_surface
from robot_gait import gait
from robot_strike import strike_offset
from robot_hit import recoil_amount
from robot_shutdown import shutdown_pose

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
walk='--walk' in sys.argv
melee='--melee' in sys.argv
hit='--hit' in sys.argv
shutdown='--shutdown' in sys.argv
assert sum([walk,melee,hit,shutdown])<=1,'Choose one action'
clip='Death' if shutdown else ('Walk' if walk else ('Melee' if melee else ('Hit' if hit else 'Idle')))
fps=30 if walk or melee or hit or shutdown else 24
stem='robot_'+clip.lower()
folder=root/('security_'+clip.lower()+'01'); folder.mkdir(parents=True,exist_ok=True)
source_scene=load_authored_scene(Path('E:/CyberCity2085-3d-lab/sources/charge_studio/security_bot_v1/security_bot_release_v1.blend'))
coverage=json.loads((root/'security_pbr_robot02/coverage.json').read_text())
names=tuple(coverage['baked'])
sources={name:bpy.data.objects[name.removesuffix('_Evaluated')] for name in names}
with bpy.data.libraries.load(str(root/'security_pbr_robot02/robot_pbr.blend'),link=False) as (available,loaded):
    loaded.objects=list(names)
objects=list(loaded.objects)
assert len(objects)==124
frozen_arrays={}
if walk or melee or hit or shutdown:
    # Film cables use FIT_CURVE arrays, whose ring count changes with bending.
    # Freeze the neutral count in the derivative; keep original source untouched.
    bpy.context.window.scene=source_scene
    for obj in objects:
        source=sources[obj.name]
        arrays=[m for m in source.modifiers if m.type=='ARRAY' and m.fit_type!='FIXED_COUNT']
        if not arrays: continue
        assert len(arrays)==1,source.name
        modifier=arrays[0]; modifier.fit_type='FIXED_COUNT'
        def vertex_count(count):
            modifier.count=count; source.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
            evaluated=source.evaluated_get(bpy.context.evaluated_depsgraph_get())
            mesh=evaluated.to_mesh()
            try: return len(mesh.vertices)
            finally: evaluated.to_mesh_clear()
        first=vertex_count(1); step=vertex_count(2)-first
        expected=len(obj.data.vertices)
        assert step>0 and (expected-first)%step==0,(source.name,first,step,expected)
        count=1+(expected-first)//step
        assert vertex_count(count)==expected
        frozen_arrays[source.name]=count
source_index_remaps={}
if shutdown:
    # Array proximity merging changes under compressed knee poses. Preserve
    # neutral corner indices on the unmerged underlying rings; source untouched.
    for obj in objects:
        source=sources[obj.name]
        if source.name not in frozen_arrays:continue
        array=next(m for m in source.modifiers if m.type=='ARRAY')
        array.use_merge_vertices=False
        smooth=[m for m in source.modifiers if m.type=='NODES' and m.name=='Auto Smooth']
        assert len(smooth)==1,source.name
        smooth[0].show_viewport=False;source.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
        evaluated=source.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        vertices=[evaluated.matrix_world @ v.co for v in mesh.vertices]
        evaluated.to_mesh_clear()
        tree=KDTree(len(vertices))
        for index,point in enumerate(vertices):tree.insert(point,index)
        tree.balance();indices=[]
        for v in obj.data.vertices:
            _,index,distance=tree.find(v.co)
            assert distance<.00001,('Underlying cable surface changed',source.name,distance)
            indices.append(index)
        source_index_remaps[obj.name]=indices
scene=bpy.data.scenes.new(clip); scene.render.fps=fps
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
game.animation_data_create(); game.animation_data.action=bpy.data.actions.new(clip)
rig=bpy.data.objects['RIG-security_bot']; control=rig.pose.bones['Head']
initial=control.matrix_basis.to_quaternion(); control.rotation_mode='QUATERNION'
bpy.context.window.scene=source_scene; source_scene.frame_set(1); bpy.context.view_layer.update()
root_control=rig.pose.bones['Root']
root_world=rig.matrix_world @ root_control.matrix.copy()
feet=[rig.pose.bones['IK-Foot.'+side] for side in ['L','R']]
foot_world=[rig.matrix_world @ foot.matrix.copy() for foot in feet]
hand=rig.pose.bones['IK-Wrist.L']
hand_world=rig.matrix_world @ hand.matrix.copy()
strike_targets=[]
foot_targets=[]; target_error=0.
frames=61 if shutdown else (37 if walk else (31 if melee else (25 if hit else 49)))
ground_samples=[]
samples={name:[] for name in names}; residuals={name:0.0 for name in names}
max_neutral_error=0.0; head_motion=0.0
for frame in range(1,frames+1):
    bpy.context.window.scene=source_scene; source_scene.frame_set(frame)
    control.rotation_quaternion=initial @ Quaternion((0,1,0),.12*math.sin((frame-1)/(frames-1)*math.tau))
    if shutdown:
        death=shutdown_pose((frame-1)/fps)
        control.rotation_quaternion=initial @ Quaternion((1,0,0),death['head_tilt'])
        root_control.matrix=rig.matrix_world.inverted() @ Matrix.Translation((0,0,-.4*death['buckle'])) @ root_world
        rig.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
        for foot,target in zip(feet,foot_world):foot.matrix=rig.matrix_world.inverted() @ target
    if hit:
        amount=recoil_amount((frame-1)/fps)
        control.rotation_quaternion=initial @ Quaternion((1,0,0),.12*amount)
        root_control.matrix=rig.matrix_world.inverted() @ Matrix.Translation((0,.08*amount,-.02*amount)) @ root_world @ Matrix.Rotation(-.08*amount,4,'X')
        rig.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
        for foot,target in zip(feet,foot_world):foot.matrix=rig.matrix_world.inverted() @ target
    if walk:
        time_s=(frame-1)/fps
        travel=gait(time_s)[0]
        root_control.matrix=rig.matrix_world.inverted() @ Matrix.Translation((0,travel,0)) @ root_world
        rig.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
        targets=[]
        for side,foot in enumerate(feet):
            travel,relative,height,stance=gait(time_s,side)
            target=Matrix.Translation((0,travel+relative,height)) @ foot_world[side]
            foot.matrix=rig.matrix_world.inverted() @ target
            targets.append((target,stance))
    if melee:
        offset=strike_offset((frame-1)/fps)
        # Align the actual authored open fingers with the strike, rather than
        # leaving the wrist hanging down at full extension.
        angle=-math.pi/2*offset[2]/.52
        desired_hand=(Matrix.Translation(hand_world.translation+Vector(offset))
                      @ Matrix.Rotation(angle,4,'X') @ hand_world.to_3x3().to_4x4())
        hand.matrix=rig.matrix_world.inverted() @ desired_hand
    rig.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
    if melee:
        actual=(rig.matrix_world @ hand.matrix).translation
        error=(actual-desired_hand.translation).length
        assert error<.0001,('Strike target unreachable',frame,error)
        strike_targets.append({'time_s':(frame-1)/fps,'world':list(actual),'target_error_m':error})
    if walk:
        measured=[]
        for foot,(target,stance) in zip(feet,targets):
            actual=(rig.matrix_world @ foot.matrix).translation
            error=(actual-target.translation).length
            target_error=max(target_error,error)
            measured.append({'world':list(actual),'stance':stance,'target_error_m':error})
        foot_targets.append({'time_s':time_s,'feet':measured})
    graph=bpy.context.evaluated_depsgraph_get()
    shutdown_transform=Matrix.Identity(4)
    if shutdown:
        rotation=Matrix.Rotation(-death['fall_angle'],4,'X')
        floor=float('inf')
        for source in sources.values():
            evaluated=source.evaluated_get(graph);floor_mesh=evaluated.to_mesh()
            floor=min(floor,min((rotation @ evaluated.matrix_world @ v.co).z for v in floor_mesh.vertices))
            evaluated.to_mesh_clear()
        shutdown_transform=Matrix.Translation((0,0,-floor)) @ rotation
        ground_samples.append({'time_s':(frame-1)/fps,'floor_lift_m':-floor,'fall_angle':death['fall_angle']})
    for index,obj in enumerate(objects):
        name=names[index]; source=sources[name]; evaluated=source.evaluated_get(graph)
        mesh=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=graph)
        try: points=[tuple(shutdown_transform @ evaluated.matrix_world @ vertex.co) for vertex in mesh.vertices]
        finally: evaluated.to_mesh_clear()
        if name in source_index_remaps:
            assert max(source_index_remaps[name])<len(points),('Cable remap topology changed',name,frame,len(points),max(source_index_remaps[name]),[(m.name,m.show_viewport,getattr(m,'count',None)) for m in source.modifiers])
            points=[points[i] for i in source_index_remaps[name]]
        baseline=[tuple(v.co) for v in obj.data.vertices]
        assert len(baseline)==len(points),('Topology changed',name,frame,len(baseline),len(points),[(m.name,m.type,getattr(m,'count',None),getattr(m,'fit_type',None)) for m in source.modifiers])
        delta,error=fit_surface(baseline,points)
        if frame==1:
            max_neutral_error=max(max_neutral_error,max((Vector(a)-Vector(b)).length for a,b in zip(baseline,points)))
        residuals[name]=max(residuals[name],error)
        samples[name].append((delta,points))
        pose=game.pose.bones[f'J{index:03d}']; pose.rotation_mode='QUATERNION'
        pose.matrix=delta @ pose.bone.matrix_local
        for path in ['location','rotation_quaternion','scale']: pose.keyframe_insert(path,frame=frame)
        if 'head_cover' in name: head_motion=max(head_motion,abs(delta.to_quaternion().angle))
if not walk and not shutdown: assert max_neutral_error<.0001,('Neutral source mismatch',max_neutral_error)
if walk: assert target_error<.0001,('IK controls failed to reach targets',target_error)
return_error=max(max((Vector(a)-Vector(b)).length for a,b in zip(samples[name][0][1],samples[name][-1][1])) for name in names)
if melee or hit: assert return_error<.0001,('Action failed to return to neutral',return_error)
strike_surface_displacement=0.
if melee:
    points=samples['GEO-hand_joint.L_Evaluated']
    strike_surface_displacement=max((Vector(a)-Vector(b)).length for _,current in points for a,b in zip(points[0][1],current))
    assert strike_surface_displacement>.6,('Actual hand failed to strike',strike_surface_displacement)
assert head_motion>.03,('Head control failed',head_motion)
bpy.context.window.scene=scene
reference={}; corrections={}; contact={}
if shutdown:
    minimum=min(p[2] for frameset in samples.values() for _,points in frameset for p in points)
    settled_error=max(max((Vector(a)-Vector(b)).length for a,b in zip(samples[name][40][1],samples[name][-1][1])) for name in names)
    assert minimum>-.00001 and settled_error<.0001,('Shutdown ground/settle failed',minimum,settled_error)
    (folder/'ground_contact.json').write_text(json.dumps({'minimum_all_source_vertices_z_m':minimum,'settled_max_vertex_drift_m':settled_error,'frames':ground_samples,'scope':'All124source surfaces at30Hz, flat ground only; no continuous/inter-part collision guarantee'},indent=2))
if hit:
    for side in ['L','R']:
        for part in ['toes','heel']:
            name=f'GEO-{part}.{side}_Evaluated'
            worst=max(max((Vector(a)-Vector(b)).length for a,b in zip(samples[name][0][1],points)) for _,points in samples[name])
            assert worst<.0001,('Hit foot slipped',name,worst)
            contact[name]={'max_stance_vertex_drift_m':worst,'scope':'All corresponding source foot vertices at30Hz hit poses'}
if walk:
    for side,side_index in [('L',0),('R',1)]:
        for part in ['toes','heel']:
            name=f'GEO-{part}.{side}_Evaluated'
            worst=0.; anchor=None; airborne=[]
            for index,(_,points) in enumerate(samples[name]):
                stance=foot_targets[index]['feet'][side_index]['stance']
                if stance:
                    if anchor is None: anchor=points
                    worst=max(worst,max((Vector(a)-Vector(b)).length for a,b in zip(anchor,points)))
                else:
                    anchor=None; airborne.append(points)
            displacement=max((Vector(a)-Vector(b)).length for a,b in zip(samples[name][0][1],samples[name][-1][1]))
            assert worst<.0001 and displacement>.5 and airborne,(name,worst,displacement)
            contact[name]={'max_stance_vertex_drift_m':worst,'forward_surface_displacement_m':displacement,
                           'scope':'All corresponding source foot vertices at 30Hz; excludes continuous-time contact/collision validation'}
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
    if name in corrections or 'head_cover' in name or 'shin.' in name or ((walk or hit or shutdown) and any(k in name for k in ['toes.','heel.'])) or (melee and any(k in name for k in ['hand_joint.','index1.','thumb1.'])):
        reference[name]=[{'time_s':index/fps,'points':[points[i] for i in range(0,len(points),8)]}
                         for index,(delta,points) in enumerate(samples[name])]
scene.frame_start=1; scene.frame_end=frames; scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(folder/(stem+'.blend')))
bpy.ops.export_scene.gltf(filepath=str(folder/(stem+'.glb')),export_format='GLB',use_selection=True,
    use_active_scene=True,export_animations=True,export_animation_mode='SCENE',
    export_anim_scene_split_object=False,export_anim_single_armature=False,export_anim_slide_to_zero=True)
(folder/'surface_reference.json').write_text(json.dumps(reference),encoding='utf-8')
coverage['rig_actions']='Articulated buckle/topple/settled shutdown study' if shutdown else 'Planted mechanical hit recoil study' if hit else 'Forward mechanical IK walk study' if walk else ('Mechanical open-hand strike study' if melee else 'Idle head scan study only')
(folder/'coverage.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
(folder/'CREDITS.txt').write_text(coverage['credit']+'\n'+coverage['license']+'\nModifications: PBR bake, game joint bake, isolated '+clip+' motion; sampled cable corrections. Original source unchanged.\n',encoding='utf-8')
(folder/'foot_targets.json').write_text(json.dumps(foot_targets),encoding='utf-8')
(folder/'strike_targets.json').write_text(json.dumps(strike_targets),encoding='utf-8')
(folder/'rig_report.json').write_text(json.dumps({'meshes':124,'joints':124,'clip':clip,'duration_s':(frames-1)/fps,
    'ik_target_max_error_m':target_error,'motion_storage':'World motion baked per mechanical joint; no separate gameplay root track',
    'fixed_neutral_array_counts':frozen_arrays,'stable_cable_corner_maps':{name:len(ids) for name,ids in source_index_remaps.items()},
    'first_pose_vertex_delta_m':max_neutral_error,
    'neutral_max_vertex_error':None if walk else max_neutral_error,'source_head_rotation_radians':head_motion,
    'source_foot_contacts':contact,
    'action_return_max_vertex_error_m':return_error,
    'strike_hand_max_vertex_displacement_m':strike_surface_displacement,
    'rigid_surface_max_residual_m':residuals,'surface_corrections':corrections,
    'credit':coverage['credit'],'license':coverage['license'],
    'limitations':['Flat-ground shutdown only; no inter-part collision or gameplay damage/destruction effects' if shutdown else 'Hit recoil only; no damage gameplay/impact VFX or destruction' if hit else 'Single forward walk study, not a seamless gameplay loop' if walk else ('Open-hand strike only; no fist closure, target impact or gameplay effects' if melee else 'Head scan idle only, not a gameplay action set'),'Opaque visor approximation','Source cables use sampled corrective morphs where required','Artistic and performance acceptance not verified']},indent=2),encoding='utf-8')
print('SECURITY_ROBOT_EXPORTED',clip,head_motion,max_neutral_error,len(corrections),flush=True)
