"""Read-only source/candidate geometry, UV and weight invariants for study138."""
import hashlib,json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_undercut133';candidate=root/'rook_single_neck138'

def vertex_signature(obj,v):
    return (tuple(v.co),tuple((obj.vertex_groups[g.group].name,round(g.weight,8)) for g in v.groups))

def faces(obj):
    uv=obj.data.uv_layers.active.data
    return {tuple(tuple(obj.data.vertices[i].co) for i in p.vertices):
            tuple(tuple(uv[i].uv) for i in p.loop_indices) for p in obj.data.polygons}

def mesh_hash(obj):
    return hashlib.sha256(repr(([vertex_signature(obj,v) for v in obj.data.vertices],
        [tuple(p.vertices) for p in obj.data.polygons],
        [[tuple(v.uv) for v in layer.data] for layer in obj.data.uv_layers])).encode()).hexdigest()

bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
head=bpy.data.objects['MIT_HeadFitStudy'];body=bpy.data.objects['char1']
head_vertices=[vertex_signature(head,v) for v in head.data.vertices]
head_uv=[tuple(v.uv) for v in head.data.uv_layers.active.data]
head_faces=[tuple(p.vertices) for p in head.data.polygons]
body_vertices=set(vertex_signature(body,v) for v in body.data.vertices)
body_faces=faces(body);source_face_count=len(body.data.polygons)
protected={o.name:mesh_hash(o) for o in bpy.context.scene.objects if o.type=='MESH' and o not in (head,body)}
bpy.ops.wm.open_mainfile(filepath=str(candidate/'human.blend'),use_scripts=False)
head=bpy.data.objects['MIT_HeadFitStudy'];body=bpy.data.objects['char1']
assert head_uv==[tuple(v.uv) for v in head.data.uv_layers.active.data]
assert head_faces==[tuple(p.vertices) for p in head.data.polygons]
changed=[]
for v in head.data.vertices:
    before,weights=head_vertices[v.index];now,current_weights=vertex_signature(head,v)
    assert weights==current_weights
    if before==now:continue
    assert before[2]<1.535 and before[:2]==now[:2] and 0<before[2]-now[2]<=.045001
    changed.append(v.index)
requested=json.loads((candidate/'fit_report.json').read_text())['changed_lower_head_vertices']
assert changed and set(changed).issubset(set(requested)), 'Unexpected changed vertex IDs'
assert all(vertex_signature(body,v) in body_vertices for v in body.data.vertices)
remaining=faces(body)
assert source_face_count-len(body.data.polygons)==196
assert all(key in body_faces and body_faces[key]==value for key,value in remaining.items())
assert protected=={o.name:mesh_hash(o) for o in bpy.context.scene.objects if o.type=='MESH' and o not in (head,body)}
result={'source_blend_sha256':hashlib.sha256((source/'human.blend').read_bytes()).hexdigest(),
        'candidate_blend_sha256':hashlib.sha256((candidate/'human.blend').read_bytes()).hexdigest(),
        'candidate_glb_sha256':hashlib.sha256((candidate/'human.glb').read_bytes()).hexdigest(),
        'protected_other_meshes':len(protected),'source_photo_uv_and_head_topology_exact':True,
        'retained_body_face_uv_and_vertex_weights_exact':True,'changed_existing_neck_vertices':len(changed),
        'requested_neck_vertex_edits':len(requested),
        'removed_body_faces':196,'scope':'Read-only geometry/UV/weight invariants; not watertight/collision/art acceptance'}
(candidate/'source_geometry_validation.json').write_text(json.dumps(result,indent=2))
print('SINGLE_NECK_SOURCE_GEOMETRY_UV_WEIGHTS_PASS',json.dumps(result),flush=True)
