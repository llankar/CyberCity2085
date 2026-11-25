"""Sample actual deformed pouch/body triangle crossings, not a full collision proof."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).parent.parent))
from triangle_contact import segment_hit
parser=argparse.ArgumentParser();parser.add_argument('--folder',default='rook_pouches140')
parser.add_argument('--include-jacket',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
labroot=Path('E:/CyberCity2085-3d-lab/generated/phase2').resolve();root=(labroot/args.folder).resolve()
assert root.is_relative_to(labroot) and root!=labroot
bpy.ops.wm.open_mainfile(filepath=str(root/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
body=bpy.data.objects['char1'];pouches=[o for o in scene.objects if o.name.startswith('MIT_Pouch_')]
assert len(pouches)==2
if args.include_jacket:pouches.append(bpy.data.objects['AuthoredDieselJacketStudy'])

def geometry(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
    points=[evaluated.matrix_world@v.co for v in mesh.vertices]
    triangles=[tuple(t.vertices) for t in mesh.loop_triangles];evaluated.to_mesh_clear()
    return points,triangles,BVHTree.FromPolygons(points,triangles,all_triangles=True)

def compare(first_geometry,second_geometry):
    bp,bt,tree=first_geometry;pp,pt,other_tree=second_geometry
    pairs=tree.overlap(other_tree);crossings=[]
    for first,second in pairs:
        a=[bp[i] for i in bt[first]];b=[pp[i] for i in pt[second]]
        hit=None
        for edge,triangle in ((a,b),(b,a)):
            for i in range(3):
                hit=segment_hit(edge[i],edge[(i+1)%3],*triangle)
                if hit is not None:break
            if hit is not None:break
        if hit is not None:crossings.append([float(v) for v in hit])
    return {'candidate_pairs':len(pairs),'crossing_pairs':len(crossings),'points':crossings}

rows=[];mutual=[]
for track in rig.animation_data.nla_tracks:
    for other in rig.animation_data.nla_tracks:other.mute=other!=track
    strip=track.strips[0]
    for fraction in (0,.5,1):
        frame=strip.frame_start+(strip.frame_end-strip.frame_start)*fraction
        scene.frame_set(int(frame),subframe=frame%1);bpy.context.view_layer.update()
        body_geometry=geometry(body)
        pouch_geometry={pouch.name:geometry(pouch) for pouch in pouches}
        for pouch in pouches:
            rows.append({'clip':track.name,'fraction':fraction,'pouch':pouch.name,
                         **compare(body_geometry,pouch_geometry[pouch.name])})
        for first in range(len(pouches)):
            for second in range(first+1,len(pouches)):
                mutual.append({'clip':track.name,'fraction':fraction,'objects':[pouches[first].name,pouches[second].name],
                               **compare(pouch_geometry[pouches[first].name],pouch_geometry[pouches[second].name])})
        print('POUCH_CONTACT_SAMPLE',track.name,fraction,flush=True)
(root/'contact_samples.json').write_text(json.dumps({'glb_sha256':hashlib.sha256((root/'human.glb').read_bytes()).hexdigest(),
    'samples':rows,'mutual_pouch_samples':mutual,'determinant_epsilon':1e-12,
    'subjects':[obj.name for obj in pouches],
    'scope':'18actual deformed poses,listed subjects against char1 and each other; coplanar cases/containment/other props and between-sample collisions NOT VERIFIED'},indent=2))
print('POUCH_TRIANGLE_CONTACT_AUDIT',len(rows),'crossing_pairs',sum(r['crossing_pairs'] for r in rows),
      'mutual_crossing_pairs',sum(r['crossing_pairs'] for r in mutual),flush=True)
