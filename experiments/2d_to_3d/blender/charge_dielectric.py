"""Bake authored dielectric shaders; deliberately unsuitable for metallic albedo."""
import bpy


def bake_dielectric(obj, folder, prefix, size=1024):
    uv = obj.data.uv_layers.active
    if uv is None:
        raise ValueError('Missing source UV: ' + obj.name)
    if any(c < -.001 or c > 1.001 for item in uv.data for c in item.uv):
        raise ValueError('Source UV outside single tile: ' + obj.name)
    targets = []
    for slot in obj.material_slots:
        slot.material = slot.material.copy()
        node = slot.material.node_tree.nodes.new('ShaderNodeTexImage')
        slot.material.node_tree.nodes.active = node
        targets.append(node)
    images = {}
    for name, kind in [('DiffuseColor', 'DIFFUSE'), ('Roughness', 'ROUGHNESS'), ('Normal', 'NORMAL')]:
        image = bpy.data.images.new(prefix + '_' + name, width=size, height=size)
        if name != 'DiffuseColor': image.colorspace_settings.name = 'Non-Color'
        for node in targets: node.image = image
        bpy.ops.object.bake(type=kind, uv_layer=uv.name)
        image.filepath_raw = str(folder / (prefix + '_' + name + '.png'))
        image.file_format = 'PNG'; image.save()
        images[name] = image
    material = bpy.data.materials.new(prefix + '_DielectricStudy')
    material.use_nodes = True
    tree = material.node_tree; shader = tree.nodes['Principled BSDF']
    for key, socket in [('DiffuseColor', 'Base Color'), ('Roughness', 'Roughness')]:
        node = tree.nodes.new('ShaderNodeTexImage'); node.image = images[key]
        tree.links.new(node.outputs['Color'], shader.inputs[socket])
    node = tree.nodes.new('ShaderNodeTexImage'); node.image = images['Normal']
    normal = tree.nodes.new('ShaderNodeNormalMap'); normal.uv_map = uv.name
    tree.links.new(node.outputs['Color'], normal.inputs['Color'])
    tree.links.new(normal.outputs[0], shader.inputs['Normal'])
    for slot in obj.material_slots: slot.material = material
    return material
