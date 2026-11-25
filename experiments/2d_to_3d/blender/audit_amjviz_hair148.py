"""Inspect actual authored scalp/hair and licensed replacement geometry before fitting."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'amjviz_hair148';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'amjviz_actions146/human_actions.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
def bounds(points):
    return {'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
materials=[]
for index,material in enumerate(body.data.materials):
    faces=[f for f in body.data.polygons if f.material_index==index]
    ids={i for f in faces for i in f.vertices}
    materials.append({'name':material.name,'faces':len(faces),'vertices':len(ids),
        'bounds':bounds([body.matrix_world@body.data.vertices[i].co for i in ids])})
head=rig.data.bones['DEF-spine.006']
with bpy.data.libraries.load(str(root/'rook_undercut133/human.blend'),link=False) as (_,data):data.objects=['ActualCopperQuiff']
hair=data.objects[0]
report={'body':body.name,'materials':materials,
    'head_bone':{'name':head.name,'head_world':list(rig.matrix_world@head.head_local),'tail_world':list(rig.matrix_world@head.tail_local)},
    'replacement':{'faces':len(hair.data.polygons),'vertices':len(hair.data.vertices),
       'bounds':bounds([hair.matrix_world@v.co for v in hair.data.vertices]),
       'materials':[m.name for m in hair.data.materials]},
    'scope':'Rest-space geometry inventory only; no body edits, fitting or art acceptance'}
(out/'geometry_audit.json').write_text(json.dumps(report,indent=2))
print('AUTHORED_HAIR_INVENTORY_READY',json.dumps(report),flush=True)
