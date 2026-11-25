"""Inspect authored action coverage and evaluated limb positions before composing."""
import json
from pathlib import Path
import bpy
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=root/'unvanquished_motion01';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'unvanquished_human01/human_armor.blend'),use_scripts=False)
r=bpy.data.objects['Armature'];r.data.pose_position='POSE'
baseline={b.name:b.matrix_basis.copy() for b in r.pose.bones}
report={}
for name,frame in [('idle',0),('walk',35),('run',45),('attack',8),('die',40),('rifle_delta',0),('blaster_delta',0)]:
 r.animation_data.action=None
 for bone in r.pose.bones:bone.matrix_basis=baseline[bone.name]
 r.animation_data.action=bpy.data.actions[name];bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
 curves=[]
 for layer in r.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:curves += [c.data_path for c in bag.fcurves]
 report[name]={'frame':frame,'curve_count':len(curves),'keyed_bones':sorted({p.split('"')[1] for p in curves if p.startswith('pose.bones[')}),'bones':{b:{'world':list((r.matrix_world@r.pose.bones[b].matrix).translation),'basis':list(r.pose.bones[b].rotation_quaternion)} for b in ['head','hips','hand.R','hand.L','tag_weapon']}}
(out/'source_action_audit.json').write_text(json.dumps(report,indent=2))
print('UNV_ACTION_AUDIT',json.dumps({k:{'curves':v['curve_count'],'hand.R':v['bones']['hand.R']['world'],'head':v['bones']['head']['world']} for k,v in report.items()}),flush=True)
