"""Read-only source anatomy, skin/material and garment landmarks."""
import json
from pathlib import Path
import bpy
from mathutils import Vector
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'nathan_wardrobe01';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'renderpeople_nathan01/human.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
body=bpy.data.objects['Object_96'];points=[body.matrix_world @ v.co for v in body.data.vertices]
# Topological connected components, not material or spatial guesses.
parents=list(range(len(points)))
def find(i):
    while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
    return i
for edge in body.data.edges:
    a,b=map(find,edge.vertices);parents[a]=b
components={}
for i,p in enumerate(points):components.setdefault(find(i),[]).append(i)
report={'rig':rig.name,'bones':{b.name:{'head':list(rig.matrix_world @ b.head_local),'tail':list(rig.matrix_world @ b.tail_local)} for b in rig.data.bones},
 'materials':[],'components':[]}
for material in body.data.materials:
    report['materials'].append({'name':material.name,'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in material.node_tree.nodes]})
for ids in sorted(components.values(),key=len,reverse=True):
    report['components'].append({'vertices':len(ids),'bounds':[[min(points[j][i] for j in ids) for i in range(3)],[max(points[j][i] for j in ids) for i in range(3)]], 'first_vertex':ids[0]})
(out/'anatomy_audit.json').write_text(json.dumps(report,indent=2))
print('NATHAN_ANATOMY_AUDIT',rig.name, len(components),json.dumps(report['components'][:15]))
print('NATHAN_JOINTS',json.dumps(report['bones']))
