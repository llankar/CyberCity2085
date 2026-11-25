"""Bake an explicit opaque game approximation of the layered film visor.

Preserves authored diffuse tint and glossy roughness/normal routes. Multi-layer refraction
is deliberately replaced by a coated opaque dielectric, not claimed identical.
"""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from charge_pbr import bake_object

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'security_pbr_robot02'; folder.mkdir(parents=True,exist_ok=True)
coverage=json.loads((root/'security_pbr_robot01/coverage.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(root/'security_pbr_robot01/robot_pbr.blend'),use_scripts=False)
scene=bpy.context.scene
with bpy.data.libraries.load(str(root/'security_geometry01/security_geometry.blend'),link=False) as (available,loaded):
    loaded.materials=['robot_glass']
original=loaded.materials[0]
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=1
scene.render.bake.use_clear=True; scene.render.bake.margin=4
for index,entry in enumerate(coverage['unresolved']):
    obj=bpy.data.objects[entry['object']]
    material=original.copy(); tree=material.node_tree
    glossy=tree.nodes.get('Glossy BSDF'); normal=tree.nodes.get('Reroute')
    diffuse=tree.nodes.get('Diffuse BSDF.001')
    output=next(n for n in tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
    assert glossy and glossy.type=='BSDF_GLOSSY' and normal and diffuse and diffuse.type=='BSDF_DIFFUSE'
    assert glossy.inputs['Color'].is_linked and glossy.inputs['Roughness'].is_linked
    for node in list(tree.nodes):
        if node.type=='BSDF_PRINCIPLED': tree.nodes.remove(node)
    shader=tree.nodes.new('ShaderNodeBsdfPrincipled')
    tint=diffuse.inputs['Color']
    if tint.links: tree.links.new(tint.links[0].from_socket,shader.inputs['Base Color'])
    else: shader.inputs['Base Color'].default_value=tint.default_value
    tree.links.new(glossy.inputs['Roughness'].links[0].from_socket,shader.inputs['Roughness'])
    tree.links.new(normal.outputs[0],shader.inputs['Normal'])
    shader.inputs['Metallic'].default_value=0
    shader.inputs['Coat Weight'].default_value=1
    shader.inputs['IOR'].default_value=1.45
    tree.links.new(shader.outputs[0],output.inputs['Surface'])
    obj.data.materials.clear(); obj.data.materials.append(material)
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    baked=bake_object(obj,folder,f'visor_{index:02d}',size=512)
    baked_shader=baked.node_tree.nodes['Principled BSDF']
    baked_shader.inputs['Coat Weight'].default_value=1
    baked_shader.inputs['Coat Roughness'].default_value=.03
    baked_shader.inputs['IOR'].default_value=1.45
    coverage['baked'].append(obj.name)
    print('ROBOT_VISOR_BAKED',obj.name,flush=True)
coverage['adapted_visor']=[entry['object'] for entry in coverage['unresolved']]
coverage['unresolved']=[]
coverage['approximation']='Opaque coated dielectric visor; authored diffuse tint and glossy roughness/normal baked, layered film refraction omitted'
coverage['remaining']=['Artistic fidelity not accepted','Original120 material bakes retain previous emission treatment','No rig or actions','Unoptimized geometry and material count']
for obj in scene.objects: obj.select_set(obj.type=='MESH')
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'robot_pbr.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'robot_pbr.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False)
(folder/'coverage.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
print('ROBOT_VISOR_STUDY_EXPORTED',flush=True)
