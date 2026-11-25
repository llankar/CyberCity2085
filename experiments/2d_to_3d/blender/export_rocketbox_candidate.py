"""Create a separate portable material/rig candidate from the audited MIT asset."""
import json
import shutil
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03')
source=Path('E:/CyberCity2085-3d-lab/sources/rocketbox/Military_Male_03')
bpy.ops.wm.open_mainfile(filepath=str(root/'imported_source.blend'),use_scripts=False)
meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
rigs=[obj for obj in bpy.context.scene.objects if obj.type=='ARMATURE']
assert len(meshes)==len(rigs)==1
mesh=meshes[0]; mesh.data.calc_loop_triangles()
assert len(mesh.data.loop_triangles)==15517 and 1.5<mesh.dimensions.z<2.2
weights=max(sum(g.weight>0 for g in vertex.groups) for vertex in mesh.data.vertices)
assert weights<=8,('Explicit weight conversion required',weights)
changes=[]
for material in bpy.data.materials:
    if not material.use_nodes: continue
    shader=next(node for node in material.node_tree.nodes if node.type=='BSDF_PRINCIPLED')
    original=shader.inputs['Metallic'].default_value
    assert not shader.inputs['Metallic'].links
    # Legacy FBX ReflectionFactor=1 imported as all-metal, including skin/fabric.
    # This explicit dielectric candidate keeps source shininess/specular/normal
    # routes. Mixed metal/polymer subregions still need authored material masks.
    shader.inputs['Metallic'].default_value=0
    changes.append({'material':material.name,'imported_metallic':original,'derived_metallic':0,
                    'retained_source_roughness':shader.inputs['Roughness'].default_value})
notice=(source/'LICENSE.md').read_text()
shutil.copyfile(source/'LICENSE.md',root/'LICENSE.md')
for obj in bpy.context.scene.objects: obj.select_set(obj in meshes or obj in rigs)
bpy.context.view_layer.objects.active=rigs[0]
bpy.ops.wm.save_as_mainfile(filepath=str(root/'character_dielectric.blend'))
bpy.ops.export_scene.gltf(filepath=str(root/'character_dielectric.glb'),export_format='GLB',
    use_selection=True,use_active_scene=True,export_animations=False,export_all_influences=True,
    export_try_sparse_sk=True,export_copyright='Copyright (c) 2020 Microsoft; MIT License')
glb=Glb(root/'character_dielectric.glb')
glb.doc['asset'].setdefault('extras',{}).update({'source':'https://github.com/microsoft/Microsoft-Rocketbox',
    'source_commit':'0943055db6ec570bcef9f2c8b41c9e5467c808f9','source_asset':'Military_Male_03',
    'source_license':'MIT','license_notice':notice,'modifications':'FBX conversion and explicit dielectric material candidate; original normals/specular/shininess routes retained'})
glb.save(root/'character_dielectric.glb')
(root/'export_report.json').write_text(json.dumps({'triangles':15517,'source_vertices':7928,'bones':80,
    'source_shape_keys':176,'source_max_weight_influences':weights,'materials':changes,
    'license':'MIT','license_notice_embedded':True,
    'limitations':['Candidate source uniform; not final Rook/Raider identity','Legacy specular workflow converted; normal handedness and mixed metal masks not accepted','No motion clips yet; facial morph behavior and artistic quality not verified']},indent=2),encoding='utf-8')
print('ROCKETBOX_DIELECTRIC_CANDIDATE_EXPORTED',len(glb.doc['meshes']),len(glb.doc['skins'][0]['joints']),len(glb.doc.get('images',[])),len((root/'character_dielectric.glb').read_bytes()),flush=True)
