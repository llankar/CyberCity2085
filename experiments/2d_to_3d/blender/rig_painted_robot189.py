"""One mechanical articulation trial of the already painted Hunyuan robot."""
from pathlib import Path
import bpy,sys,math,json
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from robot_gait import gait
from robot_shutdown import shutdown_pose
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/robot189';OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(LAB/'generated/phase2/paint168/robot_official/painted_material.glb'))
body=next(o for o in bpy.data.objects if o.type=='MESH');body.data.transform(body.matrix_world);body.parent=None;body.matrix_world=Matrix.Identity(4)
low=Vector([min(v.co[i] for v in body.data.vertices) for i in range(3)]);high=Vector([max(v.co[i] for v in body.data.vertices) for i in range(3)])
scale=2.4/(high.z-low.z);offset=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
for v in body.data.vertices:v.co=(v.co-offset)*scale
arm=bpy.data.armatures.new('Mechanical189');rig=bpy.data.objects.new('Mechanical189',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
 b=arm.edit_bones.new(name);b.head=head;b.tail=tail
 if parent:b.parent=arm.edit_bones[parent]
 return b
bone('root',(0,0,0),(0,0,.25));bone('pelvis',(0,0,1),(0,0,1.2),'root');bone('chest',(0,0,1.2),(0,0,1.85),'pelvis');bone('head',(0,0,1.85),(0,0,2.2),'chest')
for side,sign in [('L',1),('R',-1)]:
 bone('upper_arm.'+side,(sign*.5,0,1.8),(sign*.67,0,1.3),'chest')
 bone('forearm.'+side,(sign*.67,0,1.3),(sign*.65,-.08,.88),'upper_arm.'+side)
 bone('thigh.'+side,(sign*.28,0,1),(sign*.28,0,.53),'pelvis')
 bone('shin.'+side,(sign*.28,0,.53),(sign*.28,0,.08),'thigh.'+side)
 bone('foot.'+side,(sign*.28,0,.08),(sign*.28,-.25,.08),'shin.'+side)
bpy.ops.object.mode_set(mode='OBJECT')
segments={b.name:(b.head_local.copy(),b.tail_local.copy()) for b in arm.bones}
def distance(p,a,b):
 q=b-a;t=max(0,min(1,(p-a).dot(q)/q.length_squared));return (p-a-q*t).length
for name in segments:body.vertex_groups.new(name=name)
counts={name:0 for name in segments}
for v in body.data.vertices:
 p=v.co;side='L' if p.x>0 else 'R'
 if p.z<1.02 and abs(p.x)>.13:choices=['thigh.'+side,'shin.'+side,'foot.'+side]
 elif abs(p.x)>.43 and p.z>.8:choices=['upper_arm.'+side,'forearm.'+side]
 elif p.z>1.94:choices=['head']
 else:choices=['pelvis','chest']
 if .9<p.z<1.12 and p.z<1.3:choices=list(set(choices+['pelvis']))
 if .35<abs(p.x)<.58 and p.z>1.05:choices=list(set(choices+['chest']))
 ranked=sorted((distance(p,*segments[n]),n) for n in choices)
 if len(ranked)>1:
  weight=.5+.5*min(1,(ranked[1][0]-ranked[0][0])/.12)
  body.vertex_groups[ranked[0][1]].add([v.index],weight,'REPLACE')
  body.vertex_groups[ranked[1][1]].add([v.index],1-weight,'REPLACE')
 else:body.vertex_groups[ranked[0][1]].add([v.index],1,'REPLACE')
 counts[ranked[0][1]]+=1
body.parent=rig;mod=body.modifiers.new('Mechanical segment weights','ARMATURE');mod.object=rig
scene=bpy.context.scene;scene.render.fps=30;clips={}
for name,duration in [('Idle',2),('Walk',1.2),('Melee',1.2),('Hit',.7),('Death',1.5)]:
 action=bpy.data.actions.new(name);rig.animation_data_create();rig.animation_data.action=action;clips[name]=action
 for frame in range(1,int(duration*30)+2):
  t=(frame-1)/30
  for p in rig.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0)
  if name=='Idle':rig.pose.bones['chest'].rotation_euler.x=.015*math.sin(t*math.tau/2)
  elif name=='Walk':
   for i,side in enumerate(['L','R']):
    _,relative,lift,_=gait(t,i,stride=.28,lift=.07)
    y=relative;z=.08+lift;d=min(.919,max(.1,math.hypot(y,1-z)))
    hip=math.atan2(-y,1-z)-math.acos(max(-1,min(1,(.47**2+d*d-.45**2)/(2*.47*d))))
    knee=math.pi-math.acos(max(-1,min(1,(.47**2+.45**2-d*d)/(2*.47*.45))))
    rig.pose.bones['thigh.'+side].rotation_euler.x=hip
    rig.pose.bones['shin.'+side].rotation_euler.x=knee
    rig.pose.bones['foot.'+side].rotation_euler.x=-hip-knee
    rig.pose.bones['upper_arm.'+side].rotation_euler.x=-.12*math.sin(t*math.tau/1.2+i*math.pi)
  elif name=='Melee':
   a=max(0,math.sin(math.pi*t/duration));rig.pose.bones['upper_arm.R'].rotation_euler.x=-.65*a;rig.pose.bones['forearm.R'].rotation_euler.x=-.25*a;rig.pose.bones['chest'].rotation_euler.z=-.15*a
  elif name=='Hit':rig.pose.bones['chest'].rotation_euler.x=.16*math.sin(math.pi*t/duration)
  else:
   pose=shutdown_pose(t);rig.pose.bones['root'].rotation_euler.x=-pose['fall_angle'];rig.pose.bones['head'].rotation_euler.x=pose['head_tilt']
  for p in rig.pose.bones:
   p.keyframe_insert(data_path='rotation_euler',frame=frame);p.keyframe_insert(data_path='location',frame=frame)
 rig.animation_data.action=None
 track=rig.animation_data.nla_tracks.new();track.name=name;strip=track.strips.new(name,1,action);track.mute=True
for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
scene.frame_set(1);bpy.ops.object.select_all(action='DESELECT');body.select_set(True);rig.select_set(True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'robot_actions.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'robot_actions.glb'),export_format='GLB',use_selection=True,export_animation_mode='ACTIONS',export_force_sampling=True)
(OUT/'articulation.json').write_text(json.dumps({'groups':counts,'actions':list(clips),'scope':'first rigid segment articulation trial, review required; existing gait/shutdown helpers reused'},indent=2))
print('ROBOT189_READY',len(body.data.vertices),list(clips),flush=True)
