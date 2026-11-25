"""Shared authored-controller retargeting for the isolated compiled game rig."""
from pathlib import Path
from types import SimpleNamespace
import bpy
from mathutils import Matrix


def load():
    root=Path('E:/CyberCity2085-3d-lab');base=root/'generated/phase2/amjviz_pruned145'
    bpy.ops.wm.open_mainfile(filepath=str(base/'human.blend'),use_scripts=False)
    scene=bpy.context.scene;game=next(o for o in scene.objects if o.type=='ARMATURE')
    game.animation_data.action=None
    for track in game.animation_data.nla_tracks:track.mute=True
    for bone in game.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    with bpy.data.libraries.load(str(root/'sources/blenderkit_cyberpunk143/source.blend'),link=False) as (_,data):data.objects=['rig']
    driver=data.objects[0];scene.collection.objects.link(driver);driver.animation_data.action=None
    for track in driver.animation_data.nla_tracks:track.mute=True
    for side in ('L','R'):
        for limb in ('thigh','upper_arm'):driver.pose.bones[limb+'_parent.'+side]['IK_FK']=1.
    with bpy.data.libraries.load(str(root/'sources/quaternius_ual_standard/animation_library.blend'),link=False) as (_,data):data.objects=['Armature']
    motion=data.objects[0];scene.collection.objects.link(motion)
    clips={s.action.name:s.action for t in motion.animation_data.nla_tracks for s in t.strips}
    for track in motion.animation_data.nla_tracks:track.mute=True
    mapping={'torso':'pelvis','hips':'pelvis','chest':'spine_03',
             'spine_fk.001':'spine_01','spine_fk.002':'spine_02','spine_fk.003':'spine_03','neck':'neck_01','head':'Head'}
    for side in ('L','R'):
        for name,other in [('shoulder','clavicle'),('upper_arm_fk','upperarm'),('forearm_fk','lowerarm'),
                           ('hand_fk','hand'),('thigh_fk','thigh'),('shin_fk','calf'),('foot_fk','foot'),('toe_fk','ball')]:
            mapping[name+'.'+side]=other+'_'+side.lower()
        for prefix,other in [('f_index','index'),('f_middle','middle'),('f_ring','ring'),('f_pinky','pinky'),('thumb','thumb')]:
            for joint in range(1,4):mapping[f'{prefix}.{joint:02d}.{side}']=f'{other}_{joint:02d}_{side.lower()}'
    assert all(n in driver.pose.bones and o in motion.pose.bones for n,o in mapping.items())
    source_rest={name:motion.matrix_world@bone.matrix_local for name,bone in motion.data.bones.items()}
    return SimpleNamespace(root=root,base=base,scene=scene,game=game,driver=driver,motion=motion,clips=clips,mapping=mapping,
        source_rest=source_rest,control_rest={n:driver.matrix_world@driver.data.bones[n].matrix_local for n in mapping},
        driver_rest={n:driver.matrix_world@driver.data.bones[n].matrix_local for n in game.pose.bones.keys()},
        game_rest={n:game.matrix_world@b.matrix_local for n,b in game.data.bones.items()},game_world=game.matrix_world.copy(),
        scale=(driver.matrix_world@driver.data.bones['DEF-spine'].head_local).z/source_rest['pelvis'].translation.z,
        order=sorted(mapping,key=lambda n:len(driver.pose.bones[n].parent_recursive)))


def solve(c,clip,frame,adjust_controls=None):
    action=c.clips[clip];c.motion.animation_data.action=action
    if action.slots:c.motion.animation_data.action_slot=action.slots[0]
    for bone in c.driver.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    c.scene.frame_set(int(frame),subframe=frame%1);c.game.matrix_world=c.game_world.copy()
    c.driver.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
    inverse=c.driver.matrix_world.inverted()
    for name in c.order:
        other=c.mapping[name];bone=c.driver.pose.bones[name]
        current=c.motion.matrix_world@c.motion.pose.bones[other].matrix
        delta=current.to_quaternion()@c.source_rest[other].to_quaternion().inverted()
        desired=(delta@c.control_rest[name].to_quaternion()).to_matrix().to_4x4()
        desired.translation=c.driver.matrix_world@bone.matrix.translation
        if name=='torso':desired.translation=c.control_rest[name].translation+(current.translation-c.source_rest[other].translation)*c.scale
        bone.matrix=inverse@desired
        c.driver.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
    if adjust_controls:
        adjust_controls(c)
        c.driver.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
    evaluated=c.driver.evaluated_get(bpy.context.evaluated_depsgraph_get())
    desired={n:c.game.matrix_world.inverted()@evaluated.matrix_world@evaluated.pose.bones[n].matrix@c.driver_rest[n].inverted()@c.game_rest[n]
             for n in c.game.pose.bones.keys()}
    for bone in c.game.pose.bones:
        kwargs={'invert':True}
        if bone.parent:kwargs.update(parent_matrix=desired[bone.parent.name],parent_matrix_local=bone.parent.bone.matrix_local)
        bone.matrix_basis=bone.bone.convert_local_to_pose(desired[bone.name],bone.bone.matrix_local,**kwargs)
    c.game.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
    error=max((c.game.matrix_world@b.matrix.translation-c.game.matrix_world@desired[b.name].translation).length for b in c.game.pose.bones)
    assert error<1e-5,error
    return error


def stabilize_original_locations(game,actions,world):
    """Prevent a new death floor offset leaking into unchanged source clips."""
    old=game.animation_data.action;added=[]
    for name,action in actions.items():
        curves=[f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
        if any(f.data_path=='location' for f in curves):continue
        game.animation_data.action=action
        if action.slots:game.animation_data.action_slot=action.slots[0]
        game.matrix_world=world.copy();start,end=action.frame_range
        game.keyframe_insert('location',frame=start,group='SourceBasePlacement')
        game.keyframe_insert('location',frame=max(end,start+.001),group='SourceBasePlacement')
        added.append(name)
    game.animation_data.action=old
    return added
