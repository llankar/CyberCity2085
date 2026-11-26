"""Swap the experimental factory ground texture while preserving authored models."""
from pathlib import Path

import bpy

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "factory328"
bpy.ops.wm.open_mainfile(filepath=str(phase / "factory278/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0
floor = bpy.data.materials["Retained factory floor"]
texture = next(node for node in floor.node_tree.nodes if node.type == "TEX_IMAGE")
texture.image = bpy.data.images.load(str(output / "floor.png"))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.name.startswith("Wall270")
                   or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
