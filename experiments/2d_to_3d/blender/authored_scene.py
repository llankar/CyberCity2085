"""Load authored scene data before evaluation, keeping embedded scripts disabled."""
from pathlib import Path
import bpy


def load_einar_scene():
    source=Path('E:/CyberCity2085-3d-lab/sources/charge_studio/einar_release_v1.blend')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
        if len(available.scenes)!=1:
            raise ValueError('Expected one authored Einar scene: '+repr(available.scenes))
        loaded.scenes=list(available.scenes)
    scene=loaded.scenes[0]
    # Film-only camera/turntable drivers access the enclosing scene in Python.
    # Remove them from the in-memory derivative before its depsgraph is active.
    for obj in bpy.data.objects:
        if obj.animation_data:
            for driver in list(obj.animation_data.drivers):
                if 'depsgraph.scene' in driver.driver.expression:
                    obj.driver_remove(driver.data_path,driver.array_index)
    bpy.context.window.scene=scene
    bpy.context.view_layer.update()
    return scene
