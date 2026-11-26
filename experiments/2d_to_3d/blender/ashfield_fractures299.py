"""Improve lighting of Ashfield fractures while preserving their footprints."""
from pathlib import Path

import bmesh
import bpy

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "wasteland299"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "wasteland297/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0

count = 0
for obj in bpy.context.scene.objects:
    if obj.type != "MESH" or not any(tag in obj.name for tag in (" fractured slab", " broken wall")):
        continue
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    mesh.to_mesh(obj.data)
    mesh.free()
    bevel = obj.modifiers.new("Fracture edge wear", "BEVEL")
    bevel.width = .046 if " slab" in obj.name else .027
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    count += 1
assert count > 0
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"),
                          export_format="GLB", use_selection=True, export_apply=True)
print("ASHFIELD299_EXPORTED", count)
