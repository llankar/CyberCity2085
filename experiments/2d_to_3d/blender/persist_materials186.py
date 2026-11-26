from pathlib import Path
import bpy
out=Path('E:/CyberCity2085-3d-lab/generated/phase2/showcase186')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(out/'environment.glb'))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'environment.blend'))
print('MATERIAL186_BLEND_READY',flush=True)
