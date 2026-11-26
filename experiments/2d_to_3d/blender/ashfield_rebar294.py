"""Replace straight reinforcement stubs with bent steel in Ashfield."""
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "wasteland294"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "wasteland280/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0
rust = bpy.data.materials["Exposed oxidized reinforcement"]
rng = random.Random(294)
stubs = sorted((obj for obj in bpy.data.objects if " exposed rebar" in obj.name),
               key=lambda obj: obj.name)
for index, stub in enumerate(stubs):
    angle = rng.uniform(0, math.tau)
    direction = Vector((math.cos(angle), math.sin(angle), 0))
    points = [Vector((0, 0, -.23)), Vector((0, 0, .02)),
              direction * .08 + Vector((0, 0, .10)),
              direction * rng.uniform(.13, .23) + Vector((0, 0, .10 + .04*(index % 3)))]
    curve = bpy.data.curves.new("Fractured reinforcement", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = .019
    curve.bevel_resolution = 1
    curve.use_fill_caps = True
    spline = curve.splines.new("POLY")
    spline.points.add(len(points)-1)
    for point, location in zip(spline.points, points):
        point.co = (*location, 1)
    obj = bpy.data.objects.new("Bent reinforcement", curve)
    bpy.context.collection.objects.link(obj)
    obj.parent = stub.parent
    obj.matrix_world = stub.matrix_world.copy()
    curve.materials.append(rust)
    bpy.data.objects.remove(stub, do_unlink=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")

assert stubs
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True)
print("ASHFIELD294_EXPORTED", len(stubs))
