"""Candidate: remove overlapping body skin, extend actual MIT head neck inside collar."""
import hashlib,json,sys
from pathlib import Path
import bpy,bmesh

sys.path.insert(0,str(Path(__file__).parent.parent))
from neck_extension import extended_height

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_undercut133';out=root/'rook_single_neck138';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;head=bpy.data.objects['MIT_HeadFitStudy'];body=bpy.data.objects['char1']
skin=head.data.materials[0]
selected=[p.index for p in body.data.polygons if body.data.materials[p.material_index]==skin]
assert len(selected)==196
body_positions=[tuple(v.co) for v in body.data.vertices]
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in selected],context='FACES_ONLY')
bm.to_mesh(body.data);bm.free()
assert body_positions==[tuple(v.co) for v in body.data.vertices]
# Remove unreferenced neck vertices: Blender bounds include them, glTF cannot.
bm=bmesh.new();bm.from_mesh(body.data)
unused=[v for v in bm.verts if not v.link_faces];unused_count=len(unused)
bmesh.ops.delete(bm,geom=unused,context='VERTS');bm.to_mesh(body.data);bm.free()
assert set(tuple(v.co) for v in body.data.vertices).issubset(set(body_positions))
old=[tuple(v.co) for v in head.data.vertices]
changed=[]
for v in head.data.vertices:
    p=head.matrix_world@v.co
    new=extended_height(p.z)
    if abs(new-p.z)<1e-9:continue
    p.z=new;v.co=head.matrix_world.inverted()@p;changed.append(v.index)
assert changed
assert all(tuple(v.co)==old[v.index] for v in head.data.vertices if old[v.index][2]>=1.535)
rig=next(o for o in scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
helpers={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\nCandidate138: remove196overlapping retained body neck faces; extend existing MIT head lower neck into collar, preserving original photograph UVs. No new primitive neck. Seam/contact/art not accepted until native review.\n'
bpy.data.texts.new('SINGLE_NECK_CREDITS').write(notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,
    export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf-8')
(out/'fit_report.json').write_text(json.dumps({'removed_overlapping_body_faces':selected,'changed_lower_head_vertices':changed,
    'retained_body_vertex_positions_unchanged':True,'removed_unreferenced_vertices':unused_count,
    'upper_head_vertices_unchanged':True,'existing_uvs_preserved':True,
    'maximum_extension_m':.045,'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),
    'limitations':['Candidate, not adopted','No new full314pose proof','Neck/collar intersection and photo stretch require artistic review']},indent=2))
print('SINGLE_NECK_CANDIDATE_EXPORTED',len(changed),flush=True)
