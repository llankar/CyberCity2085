"""Read-only boundary/source skin inventory before repairing neck topology."""
import hashlib,json
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=root/'rook_neck_boundary142';out.mkdir(exist_ok=True)
source=root/'rocketbox_military03/character_dielectric.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST'
bpy.context.view_layer.update();obj=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.vertex_groups)
evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
pivot=Vector((0,0,1.54));mapping=Matrix.Translation(Vector((-.0037,.045,-.015)))@Matrix.Translation(pivot)@Matrix.Scale(.95,4)@Matrix.Translation(-pivot)
skin=next(i for i,m in enumerate(mesh.materials) if m.name=='sm004_head')
source_points=[mapping@evaluated.matrix_world@mesh.vertices[i].co for face in mesh.polygons if face.material_index==skin
               for i in face.vertices if abs((evaluated.matrix_world@mesh.vertices[i].co).x)<.15 and (evaluated.matrix_world@mesh.vertices[i].co).z>1.25]
evaluated.to_mesh_clear()
candidate=root/'rook_diesel_replacement141/human.blend'
bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False)
head=bpy.data.objects['MIT_HeadFitStudy'];bm=bmesh.new();bm.from_mesh(head.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
edges=[e for e in bm.edges if e.is_boundary and max(v.co.z for v in e.verts)<1.6]
points=[head.matrix_world@v.co for e in edges for v in e.verts]
report={'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'candidate_blend_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
        'neck_boundary_edges':len(edges),'boundary_segments':[[list(head.matrix_world@v.co) for v in e.verts] for e in edges],
        'source_skin_min_z':min(p.z for p in source_points),'candidate_boundary_min_z':min(p.z for p in points),
        'source_rear_min_z':min(p.z for p in source_points if p.y>.03),
        'candidate_rear_boundary_min_z':min(p.z for p in points if p.y>.03),
        'scope':'Rest-space geometry, positional weld for analysis only; no source modification'}
bm.free();(out/'boundary_audit.json').write_text(json.dumps(report,indent=2))
print('NECK_BOUNDARY_SOURCE_AUDIT',json.dumps({k:v for k,v in report.items() if k!='boundary_segments'}),flush=True)
