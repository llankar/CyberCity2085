"""Measure foot-master source response and inspect any blocking constraints."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/sources/charge_studio/einar_release_v1.blend',use_scripts=False)
rig=bpy.data.objects['RIG-einar']; bpy.context.view_layer.update()
report={'action':rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,'feet':[]}
for name in ['IK-MSTR-Foot.L','IK-MSTR-C-Foot.L','IK-Foot.L']:
    control=rig.pose.bones[name]; target=rig.pose.bones['DEF-Foot.L']
    initial=control.matrix.copy(); baseline=target.matrix.translation.copy()
    wanted=initial.copy(); wanted.translation+=Vector((0,.15,.08))
    control.matrix=wanted; rig.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
    report['feet'].append({'control':name,'initial':list(initial.translation),
                           'actual':list(control.matrix.translation),'target_delta':list(target.matrix.translation-baseline),
                           'constraints':[{'name':c.name,'type':c.type,'influence':c.influence} for c in control.constraints]})
    control.matrix=initial; rig.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
path=Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_review/walk_control_probe.json')
path.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_WALK_CONTROL_PROBE',json.dumps(report),flush=True)
