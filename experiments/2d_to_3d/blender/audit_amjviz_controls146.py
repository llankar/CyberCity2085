"""Inspect real Rigify FK controls before driving licensed combat motion."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab');out=root/'generated/phase2/amjviz_combat146';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'sources/blenderkit_cyberpunk143/source.blend'),use_scripts=False)
rig=bpy.data.objects['rig'];rows=[]
for bone in rig.pose.bones:
    if bone.name in ('root','torso','hips','chest','neck','head') or any(token in bone.name for token in ('_fk.','_parent.')):
        rows.append({'name':bone.name,'parent':bone.parent.name if bone.parent else None,
                     'head_world':list(rig.matrix_world@bone.bone.head_local),
                     'properties':{key:bone[key] for key in bone.keys() if isinstance(bone[key],(int,float,str))},
                     'constraints':[{'type':c.type,'influence':c.influence} for c in bone.constraints]})
report={'controls':rows,'invalid_drivers':[f.data_path for f in rig.animation_data.drivers if not f.driver.is_valid]}
(out/'control_audit.json').write_text(json.dumps(report,indent=2))
print('AMJVIZ_FK_CONTROL_AUDIT',json.dumps(report),flush=True)
