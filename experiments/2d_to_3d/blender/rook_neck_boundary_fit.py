"""Extend actual head-neck boundary into collar; preserve all existing anatomy."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from head_skinning import neck_skull_weights

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'rook_neck_geometry127';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_head_fit126/human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
head=bpy.data.objects['MIT_HeadFitStudy']
old_positions=[tuple(v.co) for v in head.data.vertices]
bm=bmesh.new();bm.from_mesh(head.data);bm.verts.ensure_lookup_table()
boundary=[e for e in bm.edges if e.is_boundary and max(v.co.z for v in e.verts)<1.60]
vertices={v for e in boundary for v in e.verts}
assert len(boundary)==20 and len(vertices)==20
assert all(sum(e in boundary for e in v.link_edges)==2 for v in vertices)
uv_layer=bm.loops.layers.uv.active
uv_by_vertex={v:next(loop[uv_layer].uv.copy() for loop in v.link_loops) for v in vertices}
lower={}
for vertex in vertices:
    p=vertex.co.copy()
    p.x=(p.x+.0037)*1.08-.0037
    if p.y<.045:p.y=.045+(p.y-.045)*1.8
    p.z=1.46
    lower[vertex]=bm.verts.new(p)
for edge in boundary:
    a,b=edge.verts
    # Opposite direction to adjacent face keeps the new strip oriented outward.
    loop=next(iter(edge.link_loops))
    a,b=loop.vert,loop.link_loop_next.vert
    face=bm.faces.new((b,a,lower[a],lower[b]))
    face.material_index=edge.link_faces[0].material_index;face.smooth=True
    for corner in face.loops:
        original=corner.vert if corner.vert in vertices else next(v for v,n in lower.items() if n==corner.vert)
        corner[uv_layer].uv=uv_by_vertex[original]
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(head.data);bm.free()
assert old_positions==[tuple(v.co) for v in head.data.vertices[:len(old_positions)]]
neck=head.vertex_groups['neck'];skull=head.vertex_groups['Head']
for vertex in head.data.vertices[len(old_positions):]:
    n,s=neck_skull_weights(vertex.co.z)
    neck.add([vertex.index],n,'REPLACE')
assert len(head.data.vertices)==len(old_positions)+20
rig.data.pose_position='POSE'
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(root/'rook_head_fit126/CREDITS.txt').read_text()+'\nNeck-boundary127: twenty original neck boundary vertices extended into collar with20quads/20newverts; existing head vertices unchanged. New UV strip extends boundary colors, not a new photographic texture. No final seam/contact acceptance.\n'
credits=bpy.data.texts.new('ANATOMICAL_NECK_BOUNDARY');credits.write(notice);credits.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'neck_report.json').write_text(json.dumps({'preserved_original_head_vertices':len(old_positions),'new_boundary_vertices':20,'new_quads':20,'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'limitations':['Boundary color strip; not a newly photographed lower neck','Collar intersections and animated contact require review']},indent=2))
print('ANATOMICAL_NECK_BOUNDARY_EXPORTED',flush=True)
