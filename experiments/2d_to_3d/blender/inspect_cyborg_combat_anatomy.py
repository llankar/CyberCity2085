"""Record actual rest landmarks before constructing a non-stretch combat rig."""
import json
from pathlib import Path
import bpy

root = Path('E:/CyberCity2085-3d-lab/generated/phase2')
bpy.ops.wm.open_mainfile(filepath=str(root/'grab3d_cyborg_lod01/human.blend'),use_scripts=False)
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
rig.data.pose_position = 'REST'
bpy.context.view_layer.update()
names = ['LeftShoulder','LeftArm','LeftForeArm','LeftHand','RightShoulder','RightArm','RightForeArm','RightHand']
report = {'rig':rig.name, 'rig_matrix':[list(row) for row in rig.matrix_world],
          'bones':{name:{'head':list(rig.matrix_world@rig.data.bones[name].head_local),
                        'matrix':[list(row) for row in rig.matrix_world@rig.data.bones[name].matrix_local]}
                   for name in names}}
(root/'grab3d_cyborg_lod01/combat_anatomy.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('CYBORG_COMBAT_ANATOMY',json.dumps(report),flush=True)
