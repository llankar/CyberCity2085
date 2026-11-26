"""Fit the existing authored UAL skeleton to one unarmed neural candidate."""
from pathlib import Path
import json
import math
import bpy
import bmesh
from mathutils import Matrix, Vector

LAB = Path('E:/CyberCity2085-3d-lab')
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(LAB/'sources/quaternius_ual_standard/animation_library.blend'), link=False) as (_, loaded):
    loaded.objects = ['Armature']
source = loaded.objects[0]
bpy.context.scene.collection.objects.link(source)
for track in source.animation_data.nla_tracks:
    track.mute = True
source.animation_data.action = None
clips = {strip.action.name: strip.action for track in source.animation_data.nla_tracks for strip in track.strips}
for bone in source.pose.bones:bone.matrix_basis = Matrix.Identity(4)
folder = LAB/'generated/phase2/rig175'; folder.mkdir(exist_ok=True)
material_mesh = LAB/'generated/phase2/paint175/rook_unarmed/painted_material.glb'
assert material_mesh.is_file(), 'Finish colour generation before binding'
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(material_mesh))
body = next(obj for obj in set(bpy.data.objects)-before if obj.type == 'MESH')
body.data.transform(body.matrix_world); body.parent = None; body.matrix_world = Matrix.Identity(4)
points = [vertex.co for vertex in body.data.vertices]
low = Vector([min(p[i] for p in points) for i in range(3)])
high = Vector([max(p[i] for p in points) for i in range(3)])
scale = 1.8/(high.z-low.z)
offset = Vector(((low.x+high.x)/2, (low.y+high.y)/2, low.z))
for vertex in body.data.vertices:vertex.co = (vertex.co-offset)*scale
# Paint GLB splits triangle vertices at UV seams; heat binding needs adjacency.
# Merge only coincident positions; UVs remain per face-loop and are preserved.
paint_vertices=len(body.data.vertices)
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
bm.to_mesh(body.data);bm.free();body.data.update()
print('UNARMED175_WELDED',paint_vertices,len(body.data.vertices),flush=True)
target = source.copy(); target.data = source.data.copy(); target.animation_data_clear()
target.name = 'UnarmedRook175'; bpy.context.scene.collection.objects.link(target)
for bone in target.pose.bones:bone.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.objects.active = target
bpy.ops.object.select_all(action='DESELECT'); target.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for side, degrees in [('r', -55), ('l', 55)]:
    upper = target.data.edit_bones['upperarm_'+side]
    pivot = upper.head.copy()
    rotation = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(degrees),4,'Y') @ Matrix.Translation(-pivot)
    family = [upper]+list(upper.children_recursive)
    matrices = {bone.name:bone.matrix.copy() for bone in family}
    for bone in family:bone.use_connect=False
    for bone in family:bone.matrix=rotation@matrices[bone.name]
bpy.ops.object.mode_set(mode='OBJECT')
for bone in target.data.bones:
    if bone.name=='root' or bone.name.startswith('ik_'):bone.use_deform=False
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True);target.select_set(True)
bpy.context.view_layer.objects.active=target
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
# Restrict arm influence on the central coat, using the fitted open-pose gap.
# UVs/geometry are unchanged; retain the heat solver's remaining torso weights.
arm_names={name for name in target.data.bones.keys() if name.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))}
arm_groups={group.index for group in body.vertex_groups if group.name in arm_names}
coat_corrected=0
for vertex in body.data.vertices:
    z=vertex.co.z;limit=.20+.20*max(0,min(1,(1.35-z)/.5))
    if z>=1.35 or abs(vertex.co.x)>=limit:continue
    bad=[weight.group for weight in vertex.groups if weight.group in arm_groups and weight.weight>0]
    if not bad:continue
    for group in bad:body.vertex_groups[group].remove([vertex.index])
    remaining=[(weight.group,weight.weight) for weight in vertex.groups if weight.weight>0]
    if not remaining:
        spine=min(['pelvis','spine_01','spine_02','spine_03'],key=lambda name:abs(target.data.bones[name].head_local.z-z))
        body.vertex_groups[spine].add([vertex.index],1,'REPLACE')
    else:
        total=sum(weight for group,weight in remaining)
        for group,weight in remaining:body.vertex_groups[group].add([vertex.index],weight/total,'REPLACE')
    coat_corrected+=1
print('UNARMED175_COAT_WEIGHTS',coat_corrected,flush=True)
unweighted=sum(not vertex.groups for vertex in body.data.vertices)
assert unweighted==0, f'Automatic binding left {unweighted} vertices without weights'
source.hide_render=True
source_rest={bone.name:bone.matrix_local.copy() for bone in source.data.bones}
order=sorted(target.pose.bones,key=lambda bone:len(bone.parent_recursive))
baked=[]; scene=bpy.context.scene;scene.render.fps=24
for label, original in [('Idle','Idle_Loop'),('Walk','Walk_Loop'),('Shoot','Pistol_Shoot'),('Melee','Punch_Cross'),('Death','Death01')]:
    action=clips[original];source.animation_data.action=action
    if action.slots:source.animation_data.action_slot=action.slots[0]
    first,last=action.frame_range;count=max(1,round(last-first))
    output=bpy.data.actions.new(label);output.use_fake_user=True
    target.animation_data_create();target.animation_data.action=output
    previous={}
    for frame in range(count+1):
        at=first+(last-first)*frame/count;scene.frame_set(math.floor(at),subframe=at-math.floor(at))
        poses={}
        for bone in order:
            rest=bone.bone.matrix_local
            desired=source.pose.bones[bone.name].matrix.to_quaternion().to_matrix().to_4x4()
            if bone.parent:
                relative=bone.parent.bone.matrix_local.inverted()@rest
                head_transform=poses[bone.parent.name]@relative
            else:head_transform=rest
            desired.translation=head_transform@source.pose.bones[bone.name].location
            poses[bone.name]=desired
            options={} if bone.parent is None else {'parent_matrix':poses[bone.parent.name], 'parent_matrix_local':bone.parent.bone.matrix_local}
            bone.matrix_basis=bone.bone.convert_local_to_pose(desired,rest,invert=True,**options)
            bone.rotation_mode='QUATERNION'
            if bone.name in previous:bone.rotation_quaternion.make_compatible(previous[bone.name])
            previous[bone.name]=bone.rotation_quaternion.copy()
            bone.keyframe_insert('location',frame=frame);bone.keyframe_insert('rotation_quaternion',frame=frame)
    baked.append(output)
    print('UNARMED175_CLIP',label,count+1,flush=True)
target.animation_data.action=None
for action in baked:
    track=target.animation_data.nla_tracks.new();track.name=action.name
    strip=track.strips.new(action.name,0,action);track.mute=True
for obj in bpy.context.scene.objects:obj.select_set(obj in [target,body])
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False)
(folder/'binding.json').write_text(json.dumps({'vertices':len(body.data.vertices),'unweighted':unweighted,'coat_vertices_corrected':coat_corrected,
    'clips':[action.name for action in baked],'scope':'First automatic binding; deformation/artistic review required'},indent=2))
print('UNARMED175_BOUND',flush=True)
