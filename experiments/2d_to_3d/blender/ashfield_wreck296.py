"""Fit a salvaged section of the SUV in the surveyed Ashfield wreck footprint."""
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "wasteland296"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "wasteland295/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0
source = phase.parents[1] / "environment-library/assets/derelict_suv275/model.glb"
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(source))
imported = set(bpy.data.objects) - before
repo = Path(__file__).resolve().parents[3]
map_file = repo / "assets/maps/wasteland_outdoor_02_ashfield_ruins"
survey = json.loads(map_file.with_suffix(".wall-traces.json").read_text())
gw, gh = json.loads(map_file.with_suffix(".walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
x1, y1, x2, y2 = next(row["rect"] for row in survey["walls"] if row["id"] == "wreck_e")
width, depth = (x2-x1)*gw/cw, (y2-y1)*gh/ch
target = Vector(((x1+x2)*gw/(2*cw)-gw/2, gh/2-(y1+y2)*gh/(2*ch), 0))
root = bpy.data.objects.new("Occludable_wreck_e", None)
bpy.context.collection.objects.link(root)
root.location = target
pieces = []
for original in imported:
    if original.type != "MESH":
        continue
    data = original.data.copy()
    data.transform(original.matrix_world)
    mesh = bmesh.new()
    mesh.from_mesh(data)
    bmesh.ops.bisect_plane(mesh, geom=[*mesh.verts, *mesh.edges, *mesh.faces],
                          dist=.0001, plane_co=(.22, 0, 0), plane_no=(1, 0, 0),
                          clear_inner=True)
    mesh.to_mesh(data)
    mesh.free()
    if data.polygons:
        data.transform(Matrix.Rotation(math.pi/2, 4, "Z"))
        pieces.append(data)
points = [vertex.co.copy() for data in pieces for vertex in data.vertices]
lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
extent = hi-lo
factor = min(1, width*.97/extent.x, depth*.97/extent.y)
assert factor >= .7, factor
for data in pieces:
    data.transform(Matrix.Scale(factor, 4) @ Matrix.Translation(
        Vector((-(lo.x+hi.x)/2, -(lo.y+hi.y)/2, -lo.z))))
    obj = bpy.data.objects.new("Salvaged SUV fragment", data)
    bpy.context.collection.objects.link(obj)
    obj.parent = root
for obj in imported:
    bpy.data.objects.remove(obj, do_unlink=True)
floor = bpy.data.materials["Original ashfield ground"]
texture = next(node for node in floor.node_tree.nodes if node.type == "TEX_IMAGE")
texture.image = bpy.data.images.load(str(output / "floor.png"))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True)
print("ASHFIELD296_EXPORTED", factor, list(extent*factor))
