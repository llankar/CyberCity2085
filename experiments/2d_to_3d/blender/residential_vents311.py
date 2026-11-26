"""Reuse the existing wall vent mesh on residential blind facade sections."""
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from library_placement import place
from create_hardsurface_crate import box, make_material

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "residential312"
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
housing = make_material("Entry lamp housing", (.04,.05,.055,1), .6, .48)
diffuser = make_material("Entry lamp warm diffuser", (.75,.39,.16,1), .1, .38, 1.4)
entrances = [obj for obj in bpy.context.scene.objects
             if obj.type == "MESH" and " entrance" in obj.name and obj.parent]
for entry in entrances:
    points = [entry.matrix_world @ Vector(corner) for corner in entry.bound_box]
    lo = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    hi = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    center = (lo+hi)/2
    center.z = hi.z+.12
    x_aligned = hi.x-lo.x >= hi.y-lo.y
    half_size = (.23,.074,.055) if x_aligned else (.074,.23,.055)
    shell = box("Entry lamp body", tuple(center), half_size, housing, .012)
    lens = box("Entry lamp lens", tuple(center-Vector((0,0,.053))),
               (half_size[0]*.84,half_size[1]*.84,.012), diffuser, .008)
    for obj in (shell,lens):
        obj.parent = entry.parent
        obj.matrix_parent_inverse = entry.parent.matrix_world.inverted()
assert entrances
print("RESIDENTIAL312_ENTRIES", len(entrances))

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.data.type == "POINT"
                   or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
print("RESIDENTIAL312_EXPORTED", count)
