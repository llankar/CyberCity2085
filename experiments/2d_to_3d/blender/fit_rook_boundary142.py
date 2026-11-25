"""Extend the existing anatomical boundary, preserving face topology and UVs."""
import hashlib,json,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent.parent))
from neck_boundary_fit import closed_loop,fit_boundary,neck_weights

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_diesel_replacement141';out=root/'rook_neck_boundary142';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
head=bpy.data.objects['MIT_HeadFitStudy']
bm=bmesh.new();bm.from_mesh(head.data);bm.verts.ensure_lookup_table()
boundary_edges=[tuple(v.index for v in e.verts) for e in bm.edges if e.is_boundary and max(v.co.z for v in e.verts)<1.6]
boundary=closed_loop(boundary_edges)
assert len(boundary)==20
edges=[tuple(v.index for v in e.verts) for e in bm.edges];bm.free()
points=[tuple(head.matrix_world@v.co) for v in head.data.vertices]
uvs=[tuple(x.uv) for x in head.data.uv_layers.active.data]
protected=[i for i,p in enumerate(points) if p[2]>=1.60 or (p[1]<-.02 and p[2]>1.54)]
fitted,drop=fit_boundary(points,edges,boundary,1.43,protected)
changed=[i for i,d in enumerate(drop) if abs(d)>1e-9]
assert changed
inverse=head.matrix_world.inverted()
for i in changed:
    head.data.vertices[i].co=inverse@Vector(fitted[i])
    for group in head.vertex_groups:group.remove([i])
    for name,weight in neck_weights(fitted[i,2]).items():
        if weight>0:
            group=head.vertex_groups.get(name) or head.vertex_groups.new(name=name)
            group.add([i],weight,'REPLACE')
assert uvs==[tuple(x.uv) for x in head.data.uv_layers.active.data]
assert all(tuple(head.matrix_world@head.data.vertices[i].co)==points[i] for i in protected)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in bpy.context.scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text(encoding='utf-8')+'\nCandidate142: harmonic vertical extension of existing anatomical neck boundary; lower skin anchored to existing Spine02/neck/Head bones. Original topology/UVs retained. Artistic acceptance pending.\n'
bpy.data.texts.new('BOUNDARY142_CREDITS').write(notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,
    export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_all_influences=True,export_optimize_animation_size=False,
    export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf-8')
(out/'fit_report.json').write_text(json.dumps({'boundary_vertices':boundary,'changed_vertices':changed,
    'protected_vertices':len(protected),'maximum_extension_m':float(-drop.min()),
    'root_z':1.43,'uvs_and_topology_preserved':True,
    'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),
    'limitations':['Candidate only; artistic review and animation gate outstanding','UV stretching possible']},indent=2))
print('BOUNDARY142_EXPORTED',len(changed),flush=True)
