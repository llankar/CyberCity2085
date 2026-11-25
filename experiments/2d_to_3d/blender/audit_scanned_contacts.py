"""Actual evaluated glove/weapon proximity and closed-part penetration diagnostic."""
import hashlib
import json
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

folder = Path('E:/CyberCity2085-3d-lab/generated/phase2/scanned_armor_contact01')
blend = folder/'pistol_fit01/human_pistol.blend'
bpy.ops.wm.open_mainfile(filepath=str(blend),use_scripts=False)
scene = bpy.data.scenes['AuthoredGameActions']
bpy.context.window.scene = scene
rig = bpy.data.objects['AuthoredGameRig']
gun = [obj for obj in scene.objects if obj.name.startswith('EquippedPistol_')]
assert len(gun) == 9
hand_vertices = {}
for obj in scene.objects:
    if obj.type != 'MESH' or obj in gun:
        continue
    groups = {g.index:g.name for g in obj.vertex_groups}
    sides = {}
    for side in ('R','L'):
        selected = {i for i,name in groups.items() if name == 'hand.'+side or (name.startswith('finger_') and name.endswith('.'+side))}
        indices = [v.index for v in obj.data.vertices if sum(g.weight for g in v.groups if g.group in selected) >= .5]
        if indices:
            sides[side] = indices
    if sides:
        hand_vertices[obj] = sides
assert hand_vertices


def inside(tree,point):
    # Odd/even ray parity on closed parts only, majority of three oblique rays.
    votes = []
    for direction in (Vector((1,.173,.319)),Vector((.217,1,.371)),Vector((.193,.277,1))):
        direction.normalize()
        start = point.copy()
        count = 0
        for _ in range(64):
            hit,normal,index,distance = tree.ray_cast(start,direction,10)
            if hit is None:
                break
            count += 1
            start = hit+direction*.000001
        else:
            raise AssertionError('Ray parity exceeded bounded crossing count')
        votes.append(count%2)
    return sum(votes) >= 2


cube_vertices = [Vector((x,y,z)) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
cube_faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
cube = BVHTree.FromPolygons(cube_vertices,cube_faces)
assert inside(cube,Vector((0,0,0)))
assert not inside(cube,Vector((2,0,0)))
assert inside(cube,Vector((.999,0,0)))


samples = []
closure = {}
for frame in range(17):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    trees = []
    for obj in gun:
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        for v in bm.verts:
            v.co = evaluated.matrix_world @ v.co
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        closed = all(edge.is_manifold for edge in bm.edges)
        closure[obj.name] = closed
        trees.append((obj.name,BVHTree.FromBMesh(bm),closed))
        bm.free()
        evaluated.to_mesh_clear()
    output = {}
    for side in ('R','L'):
        points = []
        for obj,sides in hand_vertices.items():
            if side not in sides:
                continue
            evaluated = obj.evaluated_get(graph)
            mesh = evaluated.to_mesh()
            assert len(mesh.vertices) == len(obj.data.vertices)
            points.extend(evaluated.matrix_world @ mesh.vertices[i].co for i in sides[side])
            evaluated.to_mesh_clear()
        distances = []
        penetrations = []
        for point in points:
            distances.append(min(tree.find_nearest(point)[3] for _,tree,_ in trees))
            for name,tree,closed in trees:
                if not closed:
                    continue
                distance = tree.find_nearest(point)[3]
                if distance > .001 and inside(tree,point):
                    penetrations.append({'part':name,'depth_m':distance,'position':list(point)})
        output[side] = {'selected_vertices':len(points),'minimum_surface_gap_m':min(distances),
                        'vertices_within_2mm':sum(distance <= .002 for distance in distances),
                        'closed_part_penetrations_over_1mm':len(penetrations),
                        'max_closed_part_depth_m':max((p['depth_m'] for p in penetrations),default=0),
                        'worst':sorted(penetrations,key=lambda p:-p['depth_m'])[:3]}
    def direction(name):
        b = rig.pose.bones[name]
        return rig.matrix_world.to_3x3() @ (b.tail-b.head)
    bends = [direction('finger_index.0'+str(i)+'.R').angle(direction('finger_index.0'+str(i+1)+'.R'))*180/3.141592653589793 for i in (1,2)]
    assert bends[0] <= 95.001 and bends[1] <= 75.001, ('Geometric bend limit exceeded',frame,bends)
    samples.append({'frame':frame,'time_s':frame/120,'hands':output,'right_index_segment_bend_degrees':bends})
(folder/'surface_contact_audit.json').write_text(json.dumps({
    'source_blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
    'closed_parts_after_1micrometre_seam_weld':closure,'samples':samples,
    'scope':'Evaluated selected hand vertices vs nine gun surfaces. Closed-part ray parity only; excludes open-part interior, hand/hand collision, triangle-only crossings and anatomical joint limits. Not artistic acceptance.'},indent=2))
print('SCANNED_CONTACT_SURFACE_AUDIT',json.dumps({'closed_parts':closure,'frames':len(samples),'selected_hand_meshes':[obj.name for obj in hand_vertices]}),flush=True)
