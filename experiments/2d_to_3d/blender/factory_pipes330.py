"""Swap the experimental factory ground texture while preserving authored models."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).parent))
from library_placement import place

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "factory330"
bpy.ops.wm.open_mainfile(filepath=str(phase / "factory278/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0
repo = Path(__file__).resolve().parents[3]
survey = json.loads((repo / "assets/maps/city_industrial_factory_floor.wall-traces.json").read_text())
cw, ch = survey["canvas_size"]
cargo = phase.parents[1] / "environment-library/assets/cargo_crate274/model.glb"
ids = {"north_crates_far", "west_crates", "east_crates"}
placed = 0
for item in survey["walls"]:
    if item["id"] not in ids:
        continue
    name = "Occludable_" + item["id"]
    group = bpy.data.objects.get(name)
    if group:
        for child in reversed(group.children_recursive):
            bpy.data.objects.remove(child, do_unlink=True)
    else:
        group = bpy.data.objects.new(name, None)
        bpy.context.collection.objects.link(group)
    x1,y1,x2,y2 = item["rect"]
    width, depth = (x2-x1)*40/cw, (y2-y1)*28/ch
    center = ((x1+x2)*20/cw-20, 14-(y1+y2)*14/ch, 0)
    if width >= depth:
        for offset in (-.25,.25):
            place(cargo, group, (center[0]+offset*width,center[1],0),
                  (width*.46,depth*.9,1.04))
            placed += 1
    else:
        for offset in (-.25,.25):
            place(cargo, group, (center[0],center[1]+offset*depth,0),
                  (depth*.46,width*.9,1.04),yaw=1.57079632679)
            placed += 1
assert placed == 6, placed
print("FACTORY329_CARGO", placed)
kit = phase.parents[1] / "sources/environment169/modular_industrial_pipes_01/modular_industrial_pipes_01_1k.gltf"
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(kit))
imported = set(bpy.data.objects) - before
pipe = next(obj for obj in imported if obj.name.startswith("modular_industrial_pipes_01_pipe01"))
data = pipe.data.copy()
data.transform(pipe.matrix_world)
for axis in (0, 2):
    spans = [max(v.co[k] for v in data.vertices)-min(v.co[k] for v in data.vertices) for k in range(3)]
    if spans[axis] > max(spans[k] for k in range(3) if k != axis):
        data.transform(Matrix.Rotation(math.pi/2, 4, "Z" if axis == 0 else "X"))
        break
lo = [min(v.co[k] for v in data.vertices) for k in range(3)]
hi = [max(v.co[k] for v in data.vertices) for k in range(3)]
for obj in imported:
    bpy.data.objects.remove(obj, do_unlink=True)
data.transform(Matrix.Translation((-(hi[0]+lo[0])/2, -(hi[1]+lo[1])/2, -lo[2])))
pipe_groups = 0
for item in survey["walls"]:
    if "_pipe_" not in item["id"]:
        continue
    name = "Occludable_" + item["id"]
    group = bpy.data.objects.get(name)
    if group is None:
        group = bpy.data.objects.new(name, None)
        bpy.context.collection.objects.link(group)
    for child in reversed(group.children_recursive):
        bpy.data.objects.remove(child, do_unlink=True)
    x1,y1,x2,y2 = item["rect"]
    width, depth = (x2-x1)*40/cw, (y2-y1)*28/ch
    x,y = (x1+x2)*20/cw-20, 14-(y1+y2)*14/ch
    scale = min(width*.42/(hi[0]-lo[0]), depth*.91/(hi[1]-lo[1]), .94/(hi[2]-lo[2]))
    for lane in (-.23,.23):
        run = bpy.data.objects.new("Textured industrial pipe run", data)
        bpy.context.collection.objects.link(run)
        run.parent = group
        run.matrix_parent_inverse = group.matrix_world.inverted()
        run.location = (x+width*lane,y,0)
        run.scale = (scale,)*3
    pipe_groups += 1
assert pipe_groups == 4
print("FACTORY330_PIPE_GROUPS", pipe_groups)
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
