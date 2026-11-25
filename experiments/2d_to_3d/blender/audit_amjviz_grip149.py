"""Measure actual posed anatomy and weapon landmarks before support-hand correction."""
import json
from pathlib import Path
import bpy
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=root/'amjviz_grip149';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'amjviz_hair148/human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=track.name!='ShootStudy'
rig.animation_data.action=None;scene.frame_set(38);bpy.context.view_layer.update()
names=['DEF-upper_arm','DEF-forearm','DEF-hand']+[f'DEF-f_{digit}.{j:02d}' for digit in ('index','middle','ring','pinky') for j in (1,2,3)]
report={}
for side in ('L','R'):
    report[side]={}
    for stem in names:
        bone=rig.pose.bones.get(stem+'.'+side)
        if bone:report[side][stem]={'head':list(rig.matrix_world@bone.head),'tail':list(rig.matrix_world@bone.tail),'matrix':[list(row) for row in (rig.matrix_world@bone.matrix)]}
report['scope']='Evaluated bone landmarks, not skin contact or artistic validation'
(out/'landmarks.json').write_text(json.dumps(report,indent=2))
print('AMJVIZ_GRIP_LANDMARKS_READY',flush=True)
