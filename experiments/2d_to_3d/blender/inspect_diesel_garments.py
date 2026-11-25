"""Inventory authored cloth geometry and its existing bind weights before fitting."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
bpy.ops.wm.open_mainfile(filepath=str(root/'diesel_candidate01/human.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST'
bpy.context.view_layer.update();rows=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    points=[obj.matrix_world@v.co for v in obj.data.vertices]
    groups={}
    for v in obj.data.vertices:
        for group in v.groups:
            name=obj.vertex_groups[group.group].name
            groups[name]=groups.get(name,0)+group.weight
    rows.append({'name':obj.name,'vertices':len(points),'faces':len(obj.data.polygons),
                 'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],
                 'materials':[m.name for m in obj.data.materials],
                 'bones':dict(sorted(groups.items(),key=lambda r:-r[1]))})
out=root/'rook_garment141';out.mkdir(exist_ok=True)
(out/'source_garments.json').write_text(json.dumps(rows,indent=2))
for row in rows:print('DIESEL_GARMENT_PART',row['name'],row['vertices'],row['faces'],list(row['bones'])[:8],flush=True)
