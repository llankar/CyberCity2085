"""Compare source outfit/body contact before judging a transferred garment."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent.parent))
from triangle_contact import segment_hit
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'diesel_candidate01/human.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST'
bpy.context.view_layer.update();geometry=[]
for name in ('retopo_body.002','jacket.003'):
    obj=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=obj.to_mesh();mesh.calc_loop_triangles()
    points=[obj.matrix_world@v.co for v in mesh.vertices];triangles=[tuple(t.vertices) for t in mesh.loop_triangles]
    obj.to_mesh_clear();geometry.append((points,triangles,BVHTree.FromPolygons(points,triangles,all_triangles=True)))
ap,at,ab=geometry[0];bp,bt,bb=geometry[1];pairs=ab.overlap(bb);crossings=0
for first,second in pairs:
    a=[ap[i] for i in at[first]];b=[bp[i] for i in bt[second]]
    if any(segment_hit(edge[i],edge[(i+1)%3],*triangle) is not None
           for edge,triangle in ((a,b),(b,a)) for i in range(3)):crossings+=1
report={'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate_pairs':len(pairs),
        'crossing_pairs':crossings,'scope':'Single original authored rest pose, full geometric body and jacket; alpha/hidden surface visibility not evaluated, not animated acceptance'}
(root/'rook_garment141/diesel_baseline_contacts.json').write_text(json.dumps(report,indent=2))
print('DIESEL_ORIGINAL_CONTACT_BASELINE',json.dumps(report),flush=True)
