"""Measure candidate bind anatomy before fitting any replacement assets."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/diesel_candidate01')
bpy.ops.wm.open_mainfile(filepath=str(root/'human.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST'
bpy.context.view_layer.update()
body=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'retopo_body' in o.name)
eyes=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'eyes.' in o.name)
eye_points=[eyes.matrix_world@v.co for v in eyes.data.vertices]
eye_centres=[sum((p for p in eye_points if (p.x>0)==right),Vector())/sum((p.x>0)==right for p in eye_points) for right in (False,True)]
groups={g.index:g.name for g in body.vertex_groups}
head_points=[body.matrix_world@v.co for v in body.data.vertices if sum(g.weight for g in v.groups if groups[g.group].endswith(':Head'))>.5]
low=[min(p[i] for p in head_points) for i in range(3)]
high=[max(p[i] for p in head_points) for i in range(3)]
report={'rig':rig.name,'body':body.name,'eyes':eyes.name,'eye_centres':[list(p) for p in eye_centres],'head_weighted_bounds':[low,high],'bones':{bone.name:{'head':list(rig.matrix_world@bone.head_local),'tail':list(rig.matrix_world@bone.tail_local)} for bone in rig.data.bones if bone.name.endswith((':Head',':Neck'))}}
(root/'anatomy_review.json').write_text(json.dumps(report,indent=2))
print('DIESEL_ANATOMY_REVIEW',json.dumps(report),flush=True)
