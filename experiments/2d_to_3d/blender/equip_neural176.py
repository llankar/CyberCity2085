"""Fit an existing pistol to the new wrist and inspect visible floor placement."""
from pathlib import Path
import json
import hashlib
import shutil
import sys
import bpy
from mathutils import Matrix, Vector
sys.path.insert(0,str(Path(__file__).parent.parent))

ROOT=Path('E:/CyberCity2085-3d-lab/generated/phase2')
OUT=ROOT/'rig176';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'rig175/human.blend'),use_scripts=False)
rig=bpy.data.objects['UnarmedRook175'];scene=bpy.context.scene
body=next(obj for obj in scene.objects if obj.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in obj.modifiers))
actions={strip.action.name:strip.action for track in rig.animation_data.nla_tracks for strip in track.strips}
for track in rig.animation_data.nla_tracks:track.mute=True
floor_samples={}
for name in ['Idle','Walk','Shoot','Melee','Death']:
    action=actions[name];rig.animation_data.action=action
    if action.slots:rig.animation_data.action_slot=action.slots[0]
    first,last=action.frame_range
    at=first+(last-first)*.25;scene.frame_set(int(at),subframe=at%1)
    evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    floor_samples[name]=min((evaluated.matrix_world@v.co).z for v in mesh.vertices)
    evaluated.to_mesh_clear()
print('NEURAL176_FLOOR_POSES',floor_samples,flush=True)
# Calibrate the prop in the actual animated wrist pose.
rig.animation_data.action=actions['Shoot']
if actions['Shoot'].slots:rig.animation_data.action_slot=actions['Shoot'].slots[0]
scene.frame_set(8);bpy.context.view_layer.update()
def position(name):return rig.matrix_world@rig.pose.bones[name].matrix.translation
# Generated glove proportions differ from the source skeleton's finger curls.
# Use its actual wrist and forearm aim, with an upright grip reference.
forward=(position('hand_r')-position('lowerarm_r')).normalized()
up=Vector((0,0,1));up=(up-forward*up.dot(forward)).normalized()
right=(-forward).cross(up).normalized();up=right.cross(-forward)
grip=position('hand_r')+forward*.055-up*.025
placement=Matrix((right,-forward,up)).transposed().to_4x4()
placement.translation=Vector(grip)-placement.to_3x3()@Vector((0,-.012,.052))
relative=(rig.matrix_world@rig.pose.bones['hand_r'].matrix).inverted()@placement
with bpy.data.libraries.load(str(ROOT/'firewarden_pistol01/pistol.blend'),link=False) as (available,loaded):
    loaded.objects=[name for name in available.objects if name in {'Pistol','trigger','barrel','hammer','magazine (loaded)','9mm.001','9mm','slide','night sights'}]
props=list(loaded.objects)
for prop in props:scene.collection.objects.link(prop)
bpy.context.view_layer.update()
bind=(rig.matrix_world@rig.data.bones['hand_r'].matrix_local)@relative
equipped=[];graph=bpy.context.evaluated_depsgraph_get()
for prop in props:
    geometry=bpy.data.meshes.new_from_object(prop.evaluated_get(graph),depsgraph=graph)
    geometry.transform(bind@prop.matrix_world)
    obj=bpy.data.objects.new('EquippedNeuralPistol_'+prop.name,geometry);scene.collection.objects.link(obj)
    obj.parent=rig;obj.matrix_world=Matrix.Identity(4)
    group=obj.vertex_groups.new(name='hand_r');group.add(list(range(len(geometry.vertices))),1,'REPLACE')
    modifier=obj.modifiers.new('RigidWristBinding','ARMATURE');modifier.object=rig
    equipped.append(obj)
for prop in props:scene.collection.objects.unlink(prop)
rig.animation_data.action=None
for obj in scene.objects:obj.select_set(obj in [rig,body,*equipped])
bpy.context.view_layer.objects.active=rig
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'human.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False)
shutil.copyfile(ROOT/'rig175/binding.json',OUT/'binding.json')
(OUT/'equipment.json').write_text(json.dumps({'source_body_sha256':hashlib.sha256((ROOT/'rig175/human.glb').read_bytes()).hexdigest(),'floor_pose_samples_m':floor_samples,'bone':'hand_r',
    'prop_parts':len(equipped),'placement_method':'Wrist/forearm aim with upright reference; generated glove contact approximate','scope':'One measured prop fit; hand contact needs visual review'},indent=2))
print('NEURAL176_EQUIPPED',len(equipped),flush=True)
