"""Fit genuine licensed hair-card geometry using measured interocular landmarks."""
import json
import shutil
import sys
from pathlib import Path
import bpy
import bmesh
import numpy as np
from mathutils import Matrix

base=Path('E:/CyberCity2085-3d-lab')
source=base/'sources/rocketbox/Male_Adult_08'
out=base/'generated/phase2/rocketbox_hair08'; out.mkdir(exist_ok=True)
with_head='--with-head' in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(base/'generated/phase2/rocketbox_military03/character_dielectric.blend'),use_scripts=False)
target=next(obj for obj in bpy.context.scene.objects if obj.type=='ARMATURE')
target_eyes=[target.matrix_world @ target.data.bones['Bip01 '+side+'Eye'].head_local for side in ['R','L']]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(source/'Export/Male_Adult_08.fbx'),use_anim=False)
for imported_image in bpy.data.images:
    path=source/'Textures'/Path(imported_image.filepath.replace('\\','/')).name
    if path.exists(): imported_image.filepath=str(path); imported_image.reload()
rig=next(obj for obj in bpy.context.scene.objects if obj.type=='ARMATURE')
source_eyes=[rig.matrix_world @ rig.data.bones['Bip01 '+side+'Eye'].head_local for side in ['R','L']]
mesh=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
material=next(slot.material for slot in mesh.material_slots if slot.material.name=='m014_opacity')
index=list(mesh.data.materials).index(material)
head_material=next(slot.material for slot in mesh.material_slots if slot.material.name=='m014_head')
head_index=list(mesh.data.materials).index(head_material)
indices={index,head_index} if with_head else {index}
used={v for face in mesh.data.polygons if face.material_index in indices for v in face.vertices}
assert len(used)==(1905 if with_head else 354)
source_weights={v.index:[(mesh.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in mesh.data.vertices}
source_normals=[normal.vector.copy() for normal in mesh.data.corner_normals]
had_custom_normals=mesh.data.has_custom_normals
geometry=mesh.data.copy()
bm=bmesh.new(); bm.from_mesh(geometry); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
normal_layer=bm.loops.layers.float_vector.new('AuthoredCornerNormal')
for face in bm.faces:
    for loop,source_loop in zip(face.loops,mesh.data.polygons[face.index].loop_indices):
        loop[normal_layer]=source_normals[source_loop]
original_index=bm.verts.layers.int.new('SourceVertexIndex')
for vertex in bm.verts: vertex[original_index]=vertex.index
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in used],context='VERTS')
bm.to_mesh(geometry); bm.free()
assert len(geometry.vertices)==len(used)
scale=(target_eyes[0]-target_eyes[1]).length/(source_eyes[0]-source_eyes[1]).length
assert .85<scale<1.2
rotation=(source_eyes[0]-source_eyes[1]).rotation_difference(target_eyes[0]-target_eyes[1]).to_matrix().to_4x4()
fit=Matrix.Translation((target_eyes[0]+target_eyes[1])/2) @ rotation @ Matrix.Scale(scale,4) @ Matrix.Translation(-(source_eyes[0]+source_eyes[1])/2)
geometry.transform(fit @ mesh.matrix_world)
normal_matrix=(fit @ mesh.matrix_world).to_3x3().inverted().transposed()
geometry.normals_split_custom_set([(normal_matrix @ item.vector).normalized()
    for item in geometry.attributes['AuthoredCornerNormal'].data])
face_material_indices=[1 if with_head and face.material_index==index else 0 for face in geometry.polygons]
geometry.materials.clear()
if with_head: geometry.materials.append(head_material)
geometry.materials.append(material)
for face,material_index in zip(geometry.polygons,face_material_indices): face.material_index=material_index
assert len({face.material_index for face in geometry.polygons})==(2 if with_head else 1)
hair=bpy.data.objects.new('AuthoredHeadHair' if with_head else 'AuthoredQuiffCards',geometry); bpy.context.scene.collection.objects.link(hair)
hair.vertex_groups.clear() # copied mesh already carries source deform groups
groups={group.name:hair.vertex_groups.new(name=group.name) for group in mesh.vertex_groups}
for vertex in geometry.vertices:
    source_index=geometry.attributes['SourceVertexIndex'].data[vertex.index].value
    for group,weight in source_weights[source_index]: groups[group].add([vertex.index],weight,'REPLACE')
if with_head:
    shader=next(node for node in head_material.node_tree.nodes if node.type=='BSDF_PRINCIPLED')
    shader.inputs['Metallic'].default_value=0
hair['source_license']='Copyright (c) 2020 Microsoft; MIT'
hair['source_asset']='Rocketbox Male_Adult_08 opacity geometry, fitted by eye landmarks'
image=bpy.data.images.load(str(source/'Textures/m014_opacity_color.tga'),check_existing=True)
pixels=np.array(image.pixels[:],dtype=np.float32).reshape(-1,4)
alpha_min,alpha_max=float(pixels[:,3].min()),float(pixels[:,3].max())
nodes=material.node_tree.nodes; shader=next(node for node in nodes if node.type=='BSDF_PRINCIPLED')
texture=next(node for node in nodes if node.type=='TEX_IMAGE')
texture.image=image
for node in list(nodes):
    if node.type=='TEX_IMAGE' and node!=texture: nodes.remove(node)
for link in list(material.node_tree.links):
    if link.to_node==shader and link.to_socket.name in {'Base Color','Alpha'}: material.node_tree.links.remove(link)
material.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
alpha_output='Alpha' if alpha_min<.999 and alpha_max>alpha_min else 'Color'
material.node_tree.links.new(texture.outputs[alpha_output],shader.inputs['Alpha'])
shader.inputs['Metallic'].default_value=0
shader.inputs['Roughness'].default_value=.7
material.surface_render_method='DITHERED'; material.use_backface_culling=False
for obj in list(bpy.data.objects):
    if obj!=hair: bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
bpy.data.texts.new('SOURCE_MIT_LICENSE').write((source/'LICENSE.md').read_text())
geometry.calc_loop_triangles()
bpy.ops.file.pack_all()
hair.select_set(True); bpy.context.view_layer.objects.active=hair
stem='fitted_head_hair' if with_head else 'fitted_hair'
bpy.ops.wm.save_as_mainfile(filepath=str(out/(stem+'.blend')))
bpy.ops.export_scene.gltf(filepath=str(out/(stem+'.glb')),export_format='GLB',use_selection=True,
    export_animations=False,export_extras=True,export_copyright='Copyright (c) 2020 Microsoft; MIT')
shutil.copyfile(source/'LICENSE.md',out/'LICENSE.md')
(out/(stem+'_report.json')).write_text(json.dumps({'vertices':len(geometry.vertices),'triangles':len(geometry.loop_triangles),
    'interocular_scale':scale,'alpha_range':[alpha_min,alpha_max],'alpha_channel':alpha_output,
    'source_eye_centers':[list(v) for v in source_eyes],'target_eye_centers':[list(v) for v in target_eyes],
    'license':'MIT','with_authored_head':with_head,'preserved_weight_groups':len(groups),
    'captured_source_corner_normals':len(source_normals),'retained_source_corner_normals':len(geometry.loops),
    'source_custom_normals':had_custom_normals,
    'limitations':['Source scalp present only in with-head variant',
        'Uniform eye-landmark fit; scalp intersection/contact and temporal alpha quality not accepted',
        'Original hair color retained; not yet Rook identity']},indent=2),encoding='utf-8')
print('ROCKETBOX_AUTHORED_HAIR_FITTED',len(geometry.vertices),len(geometry.loop_triangles),scale,alpha_output,alpha_min,alpha_max,flush=True)
