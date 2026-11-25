"""Inspect and export the author-linked fictional CC0 pistol, preserving parts."""
import json
from pathlib import Path
import bpy

source=Path('E:/CyberCity2085-3d-lab/sources/firewarden_pistol')
folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/firewarden_pistol01')
folder.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'Blend/Pistol.blend'),use_scripts=False)
objects=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
report={'objects':[{'name':o.name,'parent':o.parent.name if o.parent else None,
                    'visible':o.visible_get(),'hidden_render':o.hide_render,
                    'location':list(o.matrix_world.translation),'dimensions':list(o.dimensions),
                    'vertices':len(o.data.vertices)} for o in objects],
        'author':'FireWarden','source':'https://opengameart.org/content/lowpoly-pistol','license':'CC0 1.0'}
(folder/'source_inventory.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for image in bpy.data.images:
    if 'PaletteAtlas' in image.name:
        image.filepath=str(source/'Texture/PaletteAtlas.png'); image.reload()
atlas=bpy.data.images.load(str(source/'Texture/PaletteAtlas.png'),check_existing=True)
for material in bpy.data.materials:
    material.use_nodes=True
    material.node_tree.nodes.clear()
    shader=material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    output=material.node_tree.nodes.new('ShaderNodeOutputMaterial')
    material.node_tree.links.new(shader.outputs[0],output.inputs['Surface'])
    if shader:
        texture=material.node_tree.nodes.new('ShaderNodeTexImage'); texture.image=atlas
        material.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
        shader.inputs['Metallic'].default_value=.6
        shader.inputs['Roughness'].default_value=.45
scene=bpy.data.scenes.new('FictionalPistolGameExport'); bpy.context.window.scene=scene
selected=[o for o in objects if not o.hide_render and o.visible_get(view_layer=bpy.data.scenes[0].view_layers[0])]
if not selected: selected=objects
selected=[o for o in selected if o.name not in {'magazine (empty)','suppressor'}]
for obj in selected: scene.collection.objects.link(obj); obj.select_set(True)
bpy.context.view_layer.objects.active=selected[0]
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'pistol.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'pistol.glb'),export_format='GLB',use_selection=True,
                        use_active_scene=True,export_animations=False)
print('FIREWARDEN_PISTOL_EXPORTED',len(selected),flush=True)
