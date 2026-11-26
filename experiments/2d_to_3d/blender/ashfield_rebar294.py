"""Replace straight reinforcement stubs with bent steel and add concrete fragments in Ashfield."""
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import convex_hull_2d

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "wasteland295"
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
# Cluster irregular convex chips on each triangular slab. Combine them per
# occlusion group so the additional rubble does not add one draw per chip.
fragment_material = bpy.data.materials.new("Ashfield exposed aggregate")
fragment_material.diffuse_color = (.19, .16, .13, 1)
clusters = {}
for slab in bpy.data.objects:
    if slab.type != "MESH" or " fractured slab" not in slab.name:
        continue
    a, b, c = [slab.matrix_world @ vertex.co for vertex in slab.data.vertices[:3]]
    vertices, faces = clusters.setdefault(slab.parent, ([], []))
    for _ in range(4):
        t, u = rng.uniform(.23,.38), rng.uniform(.23,.38)
        center = a*t+b*u+c*(1-t-u)
        radius = rng.uniform(.065,.16)
        ring = [Vector((math.cos(i*math.tau/6), math.sin(i*math.tau/6))) *
                rng.uniform(radius*.55,radius) for i in range(6)]
        ring = [ring[i] for i in convex_hull_2d(ring)]
        offset = len(vertices)
        vertices.extend((center.x+v.x, center.y+v.y, center.z-.03) for v in ring)
        vertices.append((center.x+radius*.18, center.y-radius*.2, center.z+radius*.72))
        faces.extend((offset+i, offset+(i+1)%len(ring), offset+len(ring))
                     for i in range(len(ring)))
for group, (vertices, faces) in clusters.items():
    mesh = bpy.data.meshes.new("Concrete chips")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(fragment_material)
    obj = bpy.data.objects.new("Scattered concrete chips", mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = group
    obj.matrix_parent_inverse = group.matrix_world.inverted()
assert clusters
print("ASHFIELD295_RUBBLE_GROUPS", len(clusters))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True)
print("ASHFIELD295_EXPORTED", len(stubs))
