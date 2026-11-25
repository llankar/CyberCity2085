import json
from pathlib import Path
import bpy
p=Path('E:/CyberCity2085-3d-lab/generated/phase2/security_bundle01')
bpy.ops.wm.open_mainfile(filepath=str(p/'robot_actions.blend'),use_scripts=False)
r=bpy.data.objects['SecurityGameRig'];report={}
for t in r.animation_data.nla_tracks:
 report[t.name]=[{'frame_start':s.frame_start,'frame_end':s.frame_end,'action_start':s.action_frame_start,'action_end':s.action_frame_end,'scale':s.scale} for s in t.strips]
(p/'blender_action_timing.json').write_text(json.dumps(report,indent=2))
print('ROBOT_BLENDER_TIMING',json.dumps(report),flush=True)
