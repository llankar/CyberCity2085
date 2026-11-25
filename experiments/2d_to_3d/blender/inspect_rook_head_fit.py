"""Measure real rest landmarks before replacing any licensed anatomy."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_material01/human.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
body=bpy.data.objects['char1']
points=[body.matrix_world@v.co for v in body.data.vertices]
head=[p for p in points if p.z>1.53 and abs(p.x)<.15]
report={'bones':{b.name:list(rig.matrix_world@b.head_local) for b in rig.data.bones if 'head' in b.name.lower() or 'neck' in b.name.lower()},
        'head_bounds':[[min(p[i] for p in head) for i in range(3)],[max(p[i] for p in head) for i in range(3)]],
        'slices':[]}
for z in (1.48,1.50,1.52,1.54,1.56,1.60,1.65,1.70,1.75):
    sample=[p for p in points if abs(p.z-z)<.005 and abs(p.x)<.13]
    report['slices'].append({'z':z,'count':len(sample),'bounds':[[min(p[i] for p in sample) for i in range(3)],[max(p[i] for p in sample) for i in range(3)]] if sample else None})
out=root/'rook_head_fit126';out.mkdir(exist_ok=True)
(out/'landmarks.json').write_text(json.dumps(report,indent=2))
print('ROOK_HEAD_LANDMARKS',json.dumps(report),flush=True)
