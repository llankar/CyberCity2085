"""Read eye component UV geometry without modifying the source."""
import json
from pathlib import Path
import bpy
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'nathan_eyes01';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'renderpeople_nathan01/human.blend'),use_scripts=False)
body=bpy.data.objects['Object_96'];rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST';bpy.context.view_layer.update()
parents=list(range(len(body.data.vertices)))
def find(i):
 while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
 return i
for edge in body.data.edges:
 a,b=map(find,edge.vertices);parents[a]=b
parts={}
for v in body.data.vertices:parts.setdefault(find(v.index),[]).append(v.index)
report=[]
for ids in parts.values():
 points=[body.matrix_world @ body.data.vertices[i].co for i in ids]
 if len(ids) not in (106,121) or min(p.z for p in points)<1.7:continue
 selected=set(ids);uvs=[list(body.data.uv_layers.active.data[l.index].uv) for l in body.data.loops if l.vertex_index in selected]
 front=min(ids,key=lambda i:(body.matrix_world @ body.data.vertices[i].co).y)
 report.append({'vertices':len(ids),'first_vertex':ids[0],'front_vertex':front,'front_position':list(body.matrix_world @ body.data.vertices[front].co),'uv_bounds':[[min(p[i] for p in uvs) for i in range(2)],[max(p[i] for p in uvs) for i in range(2)]],'front_uv':[list(body.data.uv_layers.active.data[l.index].uv) for l in body.data.loops if l.vertex_index==front]})
(out/'eye_uv_audit.json').write_text(json.dumps(report,indent=2));print('EYE_UV_AUDIT',json.dumps(report),flush=True)
