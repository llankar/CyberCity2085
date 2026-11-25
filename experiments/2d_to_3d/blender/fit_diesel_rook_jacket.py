"""Measured authored-garment adaptation with explicit overlay/replacement studies."""
import hashlib,json,sys,shutil
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent.parent))
from garment_alignment import axial_segment_transform

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
replace_old='--replace-old-cloth' in sys.argv
assert '--clean-remnants' not in sys.argv or replace_old, 'Remnant cleanup requires replacement mode'
out=root/('rook_diesel_replacement141' if replace_old else 'rook_diesel_jacket141');out.mkdir(exist_ok=True)
cloth_source=root/'diesel_candidate01/human.blend';actor_source=root/'rook_pouches140/human.blend'
bpy.ops.wm.open_mainfile(filepath=str(cloth_source),use_scripts=False)
oldrig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');oldrig.data.pose_position='REST'
bpy.context.view_layer.update();cloth=bpy.data.objects['jacket.003']
oldpoints=[cloth.matrix_world@v.co for v in cloth.data.vertices]
oldweights=[{cloth.vertex_groups[g.group].name.removeprefix('mixamorig:'):g.weight for g in v.groups if g.weight>0} for v in cloth.data.vertices]
oldheads={b.name.removeprefix('mixamorig:'):oldrig.matrix_world@b.head_local for b in oldrig.data.bones}
original_uv=[[tuple(v.uv) for v in uv.data] for uv in cloth.data.uv_layers]
bpy.ops.wm.open_mainfile(filepath=str(actor_source),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST'
bpy.context.view_layer.update();target={b.name:rig.matrix_world@b.head_local for b in rig.data.bones}
mapping={name:({'Neck':'neck','Spine1':'Spine01','Spine2':'Spine02'}.get(name,name)) for w in oldweights for name in w}
for name in mapping:
    if name.endswith('HandThumb1'):mapping[name]=name.split('Hand')[0]+'Hand'
assert set(mapping.values())<=set(target),set(mapping.values())-set(target)
pairs={'Hips':'Spine','Spine':'Spine1','Spine1':'Spine2','Spine2':'Neck','Neck':'Head'}
for side in ('Left','Right'):
    for a,b in [('Shoulder','Arm'),('Arm','ForeArm'),('ForeArm','Hand')]:pairs[side+a]=side+b
transforms={}
radial=(target['LeftArm']-target['RightArm']).length/(oldheads['LeftArm']-oldheads['RightArm']).length
assert .7<radial<1.4
torso=Matrix(axial_segment_transform(oldheads['Hips'],oldheads['Neck'],target['Hips'],target['neck'],radial))
for name in mapping:
    canonical=name.split('Hand')[0]+'ForeArm' if 'Hand' in name else name
    if canonical in ('Hips','Spine','Spine1','Spine2','Neck','Head'):
        transforms[name]=torso
    elif canonical in pairs:
        child=pairs[canonical]
        transforms[name]=Matrix(axial_segment_transform(oldheads[canonical],oldheads[child],target[mapping[canonical]],target[mapping[child]],radial))
    else:
        transforms[name]=Matrix.Translation(target[mapping[name]]-oldheads[name])
with bpy.data.libraries.load(str(cloth_source),link=False) as (available,loaded):loaded.objects=['jacket.003']
jacket=loaded.objects[0];scene.collection.objects.link(jacket);jacket.parent=None;jacket.matrix_world=Matrix.Identity(4)
for modifier in list(jacket.modifiers):jacket.modifiers.remove(modifier)
for group in list(jacket.vertex_groups):jacket.vertex_groups.remove(group)
for vertex,point,weights in zip(jacket.data.vertices,oldpoints,oldweights):
    total=sum(weights.values());assert total>.99
    vertex.co=sum(((transforms[name]@point)*(weight/total) for name,weight in weights.items()),Vector())
    combined={}
    for name,weight in weights.items():combined[mapping[name]]=combined.get(mapping[name],0)+weight/total
    for name,weight in combined.items():
        group=jacket.vertex_groups.get(name) or jacket.vertex_groups.new(name=name);group.add([vertex.index],weight,'REPLACE')
assert original_uv==[[tuple(v.uv) for v in uv.data] for uv in jacket.data.uv_layers]
# Preserve the exposed cybernetic left arm: remove only source sleeve faces.
remove=[p.index for p in jacket.data.polygons if all(sum(w for n,w in oldweights[i].items() if n.startswith(('LeftArm','LeftForeArm','LeftHand')))> .5 for i in p.vertices)]
bm=bmesh.new();bm.from_mesh(jacket.data);bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in remove],context='FACES')
bm.to_mesh(jacket.data);bm.free();jacket.name='AuthoredDieselJacketStudy'
jacket.parent=rig;jacket.matrix_world=Matrix.Identity(4)
modifier=jacket.modifiers.new('ExistingActorSkeleton','ARMATURE');modifier.object=rig
bpy.context.view_layer.update()
evaluated=jacket.evaluated_get(bpy.context.evaluated_depsgraph_get());evaluated_mesh=evaluated.to_mesh()
rest_error=max((evaluated.matrix_world@v.co-jacket.data.vertices[v.index].co).length for v in evaluated_mesh.vertices)
evaluated.to_mesh_clear()
rig.data.pose_position='POSE'
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
removed_body=[];collar_faces=[];remnant_faces=[];annotated_count=0
if replace_old:
    body=bpy.data.objects['char1']
    removed_body=[p.index for p in body.data.polygons if body.data.materials[p.material_index].name=='RookFieldJacket']
    assert 10000<len(removed_body)<20000, 'Original annotated clothing region changed'
    annotated_count=len(removed_body)
    collar_faces=[p.index for p in body.data.polygons if
        all((body.matrix_world@body.data.vertices[i].co).z>1.48 and
            abs((body.matrix_world@body.data.vertices[i].co).x)<.16 for i in p.vertices)]
    removed_body=sorted(set(removed_body)|set(collar_faces))
    bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.faces[i] for i in removed_body],context='FACES')
    bm.to_mesh(body.data);bm.free()
    if '--clean-remnants' in sys.argv:
        selection=json.loads((out/'upper_remnant_selection.json').read_text())
        fingerprint=hashlib.sha256(repr([tuple(tuple(body.data.vertices[i].co) for i in face.vertices) for face in body.data.polygons]).encode()).hexdigest()
        assert fingerprint==selection['body_face_positions_sha256'], 'Reviewed upper remnant geometry changed'
        remnant_faces=selection['face_ids'];assert len(remnant_faces)==7
        bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm,geom=[bm.faces[i] for i in remnant_faces],context='FACES')
        bm.to_mesh(body.data);bm.free()
unused_vertices={}
for obj in ([body,jacket] if replace_old else [jacket]):
    bm=bmesh.new();bm.from_mesh(obj.data)
    unused=[v for v in bm.verts if not v.link_faces];unused_vertices[obj.name]=len(unused)
    bmesh.ops.delete(bm,geom=unused,context='VERTS');bm.to_mesh(obj.data);bm.free()
notice=(root/'rook_pouches140/CREDITS.txt').read_text()+'\n'+(root/'diesel_candidate01/CREDITS.txt').read_text()+(
    '\n141candidate: original annotated green clothing faces removed; authored Diesel jacket replaces that region. Coverage/contacts/art not accepted before review.\n' if replace_old else
    '\n141jacket-only adaptation by measured bind segments. Source left sleeve removed to expose cyberarm. Old body clothing remains for overlay diagnosis, not accepted combined outfit.\n')
bpy.data.texts.new('DIESEL_GARMENT_SOURCE_CREDITS').write(notice)
bpy.context.view_layer.objects.active=rig;helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for garment_only,name in [(True,'garment'),(False,'human_overlay')]:
    for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers and (not garment_only or obj==jacket)))
    bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',use_selection=True,
        export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
        export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_all_influences=True,
        export_copyright=notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
if replace_old:shutil.copyfile(out/'human_overlay.glb',out/'human.glb')
(out/'CREDITS.txt').write_text(notice,encoding='utf-8')
(out/'fit_report.json').write_text(json.dumps({'cloth_source_sha256':hashlib.sha256(cloth_source.read_bytes()).hexdigest(),
    'actor_source_sha256':hashlib.sha256(actor_source.read_bytes()).hexdigest(),'source_vertices':len(oldpoints),
    'retained_vertices':len(jacket.data.vertices),'retained_faces':len(jacket.data.polygons),'removed_left_sleeve_faces':len(remove),
    'rest_binding_error_m':rest_error,'fit_scale_by_bone':{n:list(m.to_scale()) for n,m in transforms.items()},
    'measured_shoulder_width_scale':radial,'torso_alignment':'shared Hips-to-Neck landmarks, axial length independent of circumference',
    'shape_keys':list(jacket.data.shape_keys.key_blocks.keys()) if jacket.data.shape_keys else [],
    'bone_mapping':mapping,'source_uv_preserved_before_sleeve_cut':True,'base_actor_geometry_unchanged':not replace_old,
    'removed_annotated_body_clothing_faces':annotated_count,
    'removed_body_clothing_and_collar_faces':len(removed_body),
    'collar_region_face_count':len(set(collar_faces)),
    'additional_collar_faces':len(removed_body)-annotated_count,
    'removed_reviewed_upper_remnant_faces':remnant_faces,
    'removed_unreferenced_vertices':unused_vertices,
    'scope':'Candidate only; original actor untouched on disk; final coverage/contacts/art not accepted'},indent=2))
print('AUTHORED_DIESEL_JACKET_FIT_EXPORTED',len(jacket.data.vertices),len(remove),flush=True)
