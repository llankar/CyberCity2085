"""Update only the residential experimental floor image; preserve model geometry."""
from pathlib import Path
import bpy
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/residential284'
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/residential280/environment.blend'));bpy.context.preferences.filepaths.save_version=0
floor=bpy.data.materials['Residential original street floor']
next(n for n in floor.node_tree.nodes if n.type=='TEX_IMAGE').image=bpy.data.images.load(str(OUT/'floor.png'))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for obj in bpy.context.scene.objects:obj.select_set(obj.type=='MESH' or obj.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
print('CLEAR_SUBFLOOR284_EXPORTED no model regeneration')
