"""Trim real source hair geometry against a portrait-driven undercut line."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent.parent))
from hairline import planes,cutoff

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_run129';out=root/'rook_undercut133';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;hair=bpy.data.objects['ActualCopperQuiff']
def geometry_uv_hash(obj):
    coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',coords)
    uv=np.empty(len(obj.data.loops)*2 if obj.data.uv_layers.active else 0,dtype=np.float32)
    if len(uv):obj.data.uv_layers.active.data.foreach_get('uv',uv)
    return hashlib.sha256(coords.tobytes()+uv.tobytes()).hexdigest()
protected={o.name:geometry_uv_hash(o) for o in scene.objects if o.type=='MESH' and o!=hair}
assert all(o.data!=hair.data for o in scene.objects if o.type=='MESH' and o!=hair)
old_positions=[tuple(v.co) for v in hair.data.vertices];old_faces=len(hair.data.polygons)
bm=bmesh.new();bm.from_mesh(hair.data)
for point,normal in planes():
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=Vector(point),plane_no=Vector(normal).normalized(),dist=1e-7,clear_inner=True,clear_outer=False)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(hair.data);bm.free()
assert len(hair.data.polygons)<old_faces and len(hair.data.polygons)>300
assert hair.data.uv_layers.active
assert all(v.co.z>=cutoff(v.co.x,v.co.y)-1e-6 for v in hair.data.vertices)
old_set=set(old_positions)
retained=sum(tuple(v.co) in old_set for v in hair.data.vertices)
assert retained>300
head=bpy.data.objects['MIT_HeadFitStudy'];head.data.calc_loop_triangles()
points=[head.matrix_world@v.co for v in head.data.vertices]
triangles=[tuple(t.vertices) for t in head.data.loop_triangles if min(points[i].z for i in t.vertices)>1.69]
tree=BVHTree.FromPolygons(points,triangles,all_triangles=True)
root_fit=[]
for vertex in hair.data.vertices:
    p=hair.matrix_world@vertex.co
    band=p.z-cutoff(p.x,p.y)
    if band>=.025 or (p.y<.035 and abs(p.x)<.05):continue
    closest,normal,index,distance=tree.find_nearest(p)
    if index is None or distance>.035:continue
    t=max(0.,min(1.,1-band/.025));t=t*t*(3-2*t)
    fitted=p.lerp(closest+normal*.0015,t)
    root_fit.append((fitted-p).length)
    vertex.co=hair.matrix_world.inverted()@fitted
rig=next(o for o in scene.objects if o.type=='ARMATURE')
source_groups=[g.name for g in hair.vertex_groups]
for group in list(hair.vertex_groups):hair.vertex_groups.remove(group)
hair.vertex_groups.new(name='Head').add(list(range(len(hair.data.vertices))),1.,'REPLACE')
for v in hair.data.vertices:
    assert abs(sum(g.weight for g in v.groups)-1)<1e-5
assert protected=={o.name:geometry_uv_hash(o) for o in scene.objects if o.type=='MESH' and o!=hair}
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\nUndercut133: existing CC0 source quiff clipped with three undercut half-spaces, keeping actual hair strands/UV above cut; no primitive hair cap or new photograph. Portrait direction only; final likeness/art review required.\n'
credits=bpy.data.texts.new('UNDERCUT_SOURCE_GEOMETRY');credits.write(notice);credits.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'hairline_report.json').write_text(json.dumps({'source_faces':old_faces,'trimmed_faces':len(hair.data.polygons),'vertices':len(hair.data.vertices),'unchanged_source_vertices_retained_before_root_fit':retained,'root_fit_vertices':len(root_fit),'maximum_root_fit_m':max(root_fit,default=0.),'protected_mesh_geometry_uv_hashes':protected,'portrait_reference_sha256':hashlib.sha256((Path(__file__).resolve().parents[3]/'assets/ui/portraits/agent_male_14.png').read_bytes()).hexdigest(),'source_vertex_groups':source_groups,'new_binding':'Head1 for all remaining/cut vertices','planes':planes(),'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'scope':'Actual source haircut; face/body/animation clips unchanged, final art not accepted'},indent=2))
print('ACTUAL_UNDERCUT_EXPORTED',len(hair.data.polygons),retained,flush=True)
