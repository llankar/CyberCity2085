"""Audit a real retargeted source pose before accepting any exported action."""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from ual_motion import UALMotion
from authored_scene import load_einar_scene
load_einar_scene()
target=bpy.data.objects['RIG-einar']
motion=UALMotion(target,'Pistol_Shoot')
motion.apply_fraction(.25)
report=motion.report()
report['controls']=[{'name':name,'rest_scale':list(motion.rest[name].to_scale()),
                     'constraints':[{'name':c.name,'type':c.type,'influence':c.influence} for c in target.pose.bones[name].constraints]}
                    for name,error in motion.control_errors.items() if error>.01]
path=Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_review/ual_pose_transfer_check.json')
path.write_text(json.dumps(report,indent=2),encoding='utf-8')
assert motion.max_rotation_error<.01
assert len(report['mapped_controls'])==48
assert len(report['unmapped_controls'])==3 and all('Ring' in pair[0] and pair[0].endswith('.L') for pair in report['unmapped_controls'])
print('UAL_CONTROL_POSE_AUDITED',report['max_control_rotation_error_radians'],report['controls'],flush=True)
