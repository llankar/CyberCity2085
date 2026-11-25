"""Inspect authored garment topology on an in-memory welded audit copy only."""
import json
from pathlib import Path
import bmesh
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/trebejo_jacket')
bpy.ops.wm.open_mainfile(filepath=str(root/'jacket.blend'),use_scripts=False)
obj=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
original_vertices=len(obj.data.vertices)
mesh=obj.data.copy()
bm=bmesh.new();bm.from_mesh(mesh)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
bm.to_mesh(mesh);bm.free()
parents=list(range(len(mesh.vertices)))
def find(i):
    while parents[i]!=i:
        parents[i]=parents[parents[i]];i=parents[i]
    return i
for edge in mesh.edges:
    first,second=map(find,edge.vertices)
    if first!=second:parents[second]=first
parts={}
for vertex in mesh.vertices:parts.setdefault(find(vertex.index),[]).append(vertex.index)
result=[]
for key,indices in parts.items():
    points=[mesh.vertices[i].co for i in indices]
    low=[min(p[axis] for p in points) for axis in range(3)]
    high=[max(p[axis] for p in points) for axis in range(3)]
    faces=[p for p in mesh.polygons if find(p.vertices[0])==key]
    result.append({'component':key,'vertices':len(indices),'faces':len(faces),'bounds':[low,high]})
result.sort(key=lambda part:part['vertices'],reverse=True)
report={'source_vertices':original_vertices,'audit_welded_vertices':len(mesh.vertices),
        'weld_distance_m':1e-6,'components':result,
        'scope':'Topology audit only. Source unchanged; no inferred material semantics or garment rigging.'}
(root/'component_audit.json').write_text(json.dumps(report,indent=2))
print('JACKET_TOPOLOGY_AUDIT',json.dumps(report),flush=True)
