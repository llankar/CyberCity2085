"""Inventory actual connected geometry before claiming modular equipment."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03')
bpy.ops.wm.open_mainfile(filepath=str(root/'character_dielectric.blend'),use_scripts=False)
obj=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
mesh=obj.data; mesh.calc_loop_triangles()
parents=list(range(len(mesh.vertices)))
def find(index):
    while parents[index]!=index:
        parents[index]=parents[parents[index]]; index=parents[index]
    return index
for edge in mesh.edges:
    a,b=map(find,edge.vertices)
    if a!=b: parents[b]=a
groups={}
for vertex in mesh.vertices: groups.setdefault(find(vertex.index),[]).append(vertex.index)
faces={key:[] for key in groups}
for face in mesh.polygons: faces[find(face.vertices[0])].append(face)
report=[]
for key,indices in groups.items():
    points=[obj.matrix_world @ mesh.vertices[index].co for index in indices]
    low=[min(point[axis] for point in points) for axis in range(3)]
    high=[max(point[axis] for point in points) for axis in range(3)]
    mats=sorted({obj.material_slots[face.material_index].material.name for face in faces[key]})
    influences={}
    for index in indices:
        for group in mesh.vertices[index].groups:
            name=obj.vertex_groups[group.group].name
            influences[name]=influences.get(name,0)+group.weight
    report.append({'component':key,'vertices':len(indices),'faces':len(faces[key]),'bounds':[low,high],
        'materials':mats,'dominant_bones':sorted(influences,key=influences.get,reverse=True)[:5]})
report.sort(key=lambda item:item['vertices'],reverse=True)
(root/'component_audit.json').write_text(json.dumps({'components':report,
    'source_vertices':len(mesh.vertices),'note':'Connectivity only; semantics and separable clothing require inspection. No new modular asset claimed.'},indent=2),encoding='utf-8')
print('ROCKETBOX_CONNECTED_COMPONENTS',len(report),flush=True)
for part in report[:15]: print(part,flush=True)
