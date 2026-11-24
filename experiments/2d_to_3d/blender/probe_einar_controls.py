"""Measure source FK responses before authoring any game motion."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Quaternion, Vector

bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/sources/charge_studio/einar_release_v1.blend',use_scripts=False)
rig=bpy.data.objects['RIG-einar']; report=[]
if '--fk' in sys.argv:
    for key in ['ik_left_upperarm','ik_right_upperarm','ik_left_thigh','ik_right_thigh']:
        rig.pose.bones['Properties'][key]=0.0
    rig.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
for control_name,target_name,angle in [('FK-UpperArm.R','DEF-Forearm.R',-1.0),
                                       ('FK-UpperArm.L','ORG-Forearm.L',1.0),
                                       ('FK-Thigh.L','DEF-Foot.L',.4),
                                       ('FK-Thigh.R','DEF-Foot.R',-.4)]:
    bpy.context.view_layer.update()
    control=rig.pose.bones[control_name]; target=rig.pose.bones[target_name]
    baseline=target.matrix.translation.copy()
    control.rotation_mode='QUATERNION'; initial=control.rotation_quaternion.copy()
    world_axis=Vector((0,1,0)) if 'Arm' in control_name else Vector((1,0,0))
    local_axis=control.matrix.to_quaternion().inverted() @ world_axis
    control.rotation_quaternion=initial @ Quaternion(local_axis,angle)
    bpy.context.view_layer.update()
    moved=target.matrix.translation.copy()
    report.append({'control':control_name,'target':target_name,'baseline':list(baseline),
                   'moved':list(moved),'distance':(moved-baseline).length,
                   'local_axis':list(local_axis),'angle':angle})
    control.rotation_quaternion=initial
path=Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_review/control_probe.json')
path.write_text(json.dumps(report,indent=2),encoding='utf-8')
properties=[{'owner':item.name,'key':key,'value':repr(item[key])}
            for item in [rig,rig.data,*rig.pose.bones] for key in item.keys()
            if 'ik' in key.lower() or 'fk' in key.lower()]
(path.parent/'control_mode_properties.json').write_text(json.dumps(properties,indent=2),encoding='utf-8')
print('EINAR_FK_CONTROL_PROBED',[(r['control'],r['distance']) for r in report],flush=True)
