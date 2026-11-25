"""Correct sampled source-run floor penetration through pelvis translation only."""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from clearance_envelope import periodic_endpoint_lifts

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_neck_uv128';out=root/'rook_run129';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
body=bpy.data.objects['char1'];track=next(t for t in rig.animation_data.nla_tracks if t.name=='run')
for other in rig.animation_data.nla_tracks:other.mute=other!=track
strip=track.strips[0];first,last=strip.action.frame_range
assert abs(first-strip.frame_start)<1e-4 and abs(last-strip.frame_end)<1e-4
count=round(last-first);assert abs(count-(last-first))<1e-4

def sample(frame):
    scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()

def floor():
    evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    xyz=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',xyz)
    matrix=np.asarray(evaluated.matrix_world,dtype=np.float64)
    result=float(np.min(xyz.reshape(-1,3)@matrix[2,:3]+matrix[2,3]))
    evaluated.to_mesh_clear();return result

original=[];raw=[]
for index in range(count+1):
    sample(first+index);raw.append(floor())
    original.append((rig.matrix_world@rig.pose.bones['Hips'].matrix).copy())
raw_dense=[]
for index in range(count*8+1):
    sample(first+index/8);raw_dense.append(floor())
action=strip.action.copy();action.name='run_ClearanceStudy';strip.action=action
track.mute=True;rig.animation_data.action=action
if action.slots:rig.animation_data.action_slot=action.slots[0]
inverse=rig.matrix_world.inverted();lifts=[max(0.,.001-value) for value in raw]
for index,(world,lift) in enumerate(zip(original,lifts)):
    sample(first+index);desired=world.copy();desired.translation+=Vector((0,0,lift))
    rig.pose.bones['Hips'].matrix=inverse@desired
    rig.pose.bones['Hips'].keyframe_insert('location',frame=first+index)
for layer in action.layers:
    for action_strip in layer.strips:
        for bag in action_strip.channelbags:
            for curve in bag.fcurves:
                if curve.data_path=='pose.bones["Hips"].location':
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
rig.animation_data.action=None;track.mute=False
deficits=[]
for index in range(count):
    minimum=1.
    for fraction in (1/8,2/8,3/8,4/8,5/8,6/8,7/8):
        sample(first+index+fraction);minimum=min(minimum,floor())
    deficits.append(max(0.,.001-minimum))
additional=periodic_endpoint_lifts(lifts,deficits)
corrected=[]
for index in range(count+1):
    sample(first+index);corrected.append((rig.matrix_world@rig.pose.bones['Hips'].matrix).copy())
track.mute=True;rig.animation_data.action=action
if action.slots:rig.animation_data.action_slot=action.slots[0]
for index,(world,lift) in enumerate(zip(corrected,additional)):
    sample(first+index);desired=world.copy();desired.translation+=Vector((0,0,lift))
    rig.pose.bones['Hips'].matrix=inverse@desired
    rig.pose.bones['Hips'].keyframe_insert('location',frame=first+index)
rig.animation_data.action=None;track.mute=False
floors=[]
for index in range(count*8+1):
    sample(first+index/8);floors.append(floor())
assert min(floors)>=.0009,min(floors)
for other in rig.animation_data.nla_tracks:other.mute=other.name!='CombatReadyStudy'
sample(0)
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\nRun129: pelvis-only vertical clearance correction, eighth-key sampled envelope. Original limb rotations, geometry and UV retained. Not planted-foot, collision simulation or gait art acceptance.\n'
credits=bpy.data.texts.new('RUN_CLEARANCE_STUDY');credits.write(notice);credits.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'run_report.json').write_text(json.dumps({'key_count':count+1,'eighth_key_samples':len(floors),'raw_integer_minimum_m':min(raw),'raw_eighth_key_minimum_m':min(raw_dense),'corrected_minimum_m':min(floors),'maximum_pelvis_lift_m':max(a+b for a,b in zip(lifts,additional)),'added_lift_first_last_m':[lifts[0]+additional[0],lifts[-1]+additional[-1]],'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'scope':'Sampled vertical clearance only; no continuous collision/contact or gait acceptance'},indent=2))
print('ROOK_RUN_CLEARANCE_EXPORTED',min(floors),flush=True)
