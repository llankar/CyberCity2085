"""Read-only connected-component inventory after old jacket-region removal."""
import json,hashlib
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/rook_diesel_replacement141')
bpy.ops.wm.open_mainfile(filepath=str(root/'human.blend'),use_scripts=False)
obj=bpy.data.objects['char1'];parents=list(range(len(obj.data.vertices)))
def find(i):
    while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
    return i
coincident={}
for vertex in obj.data.vertices:
    key=tuple(round(value,6) for value in vertex.co)
    if key in coincident:
        a,b=find(vertex.index),find(coincident[key])
        if a!=b:parents[b]=a
    else:coincident[key]=vertex.index
for edge in obj.data.edges:
    a,b=map(find,edge.vertices)
    if a!=b:parents[b]=a
groups={}
for face in obj.data.polygons:groups.setdefault(find(face.vertices[0]),[]).append(face)
rows=[]
for key,faces in groups.items():
    indices={i for face in faces for i in face.vertices};points=[obj.matrix_world@obj.data.vertices[i].co for i in indices]
    low=[min(p[i] for p in points) for i in range(3)];high=[max(p[i] for p in points) for i in range(3)]
    rows.append({'component':key,'faces':len(faces),'vertices':len(indices),'bounds':[low,high],
                 'face_ids':[face.index for face in faces]})
(root/'body_remnants.json').write_text(json.dumps(sorted(rows,key=lambda row:-row['faces']),indent=2))
selected=[row for row in rows if row['bounds'][0][2]>1.48 and row['faces']<10]
fingerprint=hashlib.sha256(repr([tuple(tuple(obj.data.vertices[i].co) for i in face.vertices) for face in obj.data.polygons]).encode()).hexdigest()
(root/'upper_remnant_selection.json').write_text(json.dumps({'body_face_positions_sha256':fingerprint,
    'components':[row['component'] for row in selected],
    'face_ids':sorted({i for row in selected for i in row['face_ids']}),
    'scope':'Four inspected disconnected upper-collar remnants after garment removal; body geometry hash required'},indent=2))
for row in rows:
    if row['bounds'][0][2]>1.48:print('UPPER_REMNANT',row['component'],row['faces'],row['bounds'],flush=True)
print('BODY_COMPONENTS_AFTER_CLOTH_REMOVAL',len(rows),flush=True)
