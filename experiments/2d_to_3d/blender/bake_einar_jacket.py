"""Test authored garment shader baking, without recoloring or replacing geometry."""
from pathlib import Path
import json
import bpy

folder = Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_jacket01')
folder.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/einar_geometry01/einar_evaluated.blend', use_scripts=False)
obj = bpy.data.objects['GEO-einar_jacket_main_GameStudy']
scene = bpy.data.scenes.new('IsolatedAuthoredGarmentBake')
bpy.context.window.scene = scene
scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 1
scene.render.bake.use_pass_direct = False
scene.render.bake.use_pass_indirect = False
scene.render.bake.use_pass_color = True
scene.render.bake.margin = 8
# Keep original UVs/named shader attributes. This first test checks their packing
# rather than silently changing coordinates used by the authored cloth shader.
uv = obj.data.uv_layers.active
assert uv is not None
targets = []
for slot in obj.material_slots:
    slot.material = slot.material.copy()
    node = slot.material.node_tree.nodes.new('ShaderNodeTexImage')
    slot.material.node_tree.nodes.active = node
    targets.append(node)
images = {}
for name, kind in [('DiffuseColor', 'DIFFUSE'), ('Roughness', 'ROUGHNESS'), ('Normal', 'NORMAL')]:
    image = bpy.data.images.new('EinarJacket_' + name, width=1024, height=1024)
    if name != 'DiffuseColor': image.colorspace_settings.name = 'Non-Color'
    for node in targets: node.image = image
    bpy.ops.object.bake(type=kind, uv_layer=uv.name)
    image.filepath_raw = str(folder / (name + '.png'))
    image.file_format = 'PNG'
    image.save()
    images[name] = image
material = bpy.data.materials.new('AuthoredJacket_GameBakeStudy')
material.use_nodes = True
tree = material.node_tree
shader = tree.nodes['Principled BSDF']
for key, socket in [('DiffuseColor', 'Base Color'), ('Roughness', 'Roughness')]:
    node = tree.nodes.new('ShaderNodeTexImage'); node.image = images[key]
    tree.links.new(node.outputs['Color'], shader.inputs[socket])
node = tree.nodes.new('ShaderNodeTexImage'); node.image = images['Normal']
normal = tree.nodes.new('ShaderNodeNormalMap'); normal.uv_map = uv.name
tree.links.new(node.outputs['Color'], normal.inputs['Color'])
tree.links.new(normal.outputs[0], shader.inputs['Normal'])
for slot in obj.material_slots: slot.material = material
bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'jacket.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder / 'jacket.glb'), export_format='GLB', use_selection=True,
                         use_active_scene=True, export_animations=False)
(folder / 'report.json').write_text(json.dumps({
    'credit': 'Einar Rig (CC-BY) Blender Foundation | studio.blender.org',
    'license': 'https://creativecommons.org/licenses/by/4.0/',
    'uv': uv.name, 'maps': list(images),
    'limitations': ['Diffuse pass is not valid albedo for metallic surfaces',
                    'Original UV overlap and full material fidelity require visual review',
                    'One garment only; no humanoid rig or animation acceptance']}, indent=2), encoding='utf-8')
print('EINAR_JACKET_BAKE_OK', flush=True)
