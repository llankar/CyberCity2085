"""Reuse the existing wall vent mesh on residential blind facade sections."""
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from library_placement import place

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "residential311"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "residential284/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0
vent = phase.parents[1] / "environment-library/assets/wall_fixtures282/vent.glb"
count = 0
for shell in list(bpy.context.scene.objects):
    if shell.type != "MESH" or not shell.name.endswith(" shell") or not shell.parent:
        continue
    faces = [face for face in shell.data.polygons if abs(face.normal.z) < .15 and face.area > 3]
    if not faces:
        continue
    face = max(faces, key=lambda item: item.area)
    normal = (shell.matrix_world.to_3x3() @ face.normal).normalized()
    tangent = Vector((normal.y, -normal.x, 0))
    center = shell.matrix_world @ face.center
    face_points = [shell.matrix_world @ shell.data.vertices[i].co for i in face.vertices]
    width = max(v.dot(tangent) for v in face_points)-min(v.dot(tangent) for v in face_points)
    base = min(v.z for v in face_points)
    for offset in (-.27, .27):
        anchor = center + tangent*(width*offset) + normal*.10
        anchor.z = base+.23
        place(vent, shell.parent, tuple(anchor), (.68, .17, .32),
              yaw=math.atan2(tangent.y, tangent.x))
        count += 1
assert count
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.data.type == "POINT"
                   or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
print("RESIDENTIAL311_EXPORTED", count)
