"""Swap the experimental factory ground texture while preserving authored models."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).parent))
from library_placement import place
from create_hardsurface_crate import box, make_material
from interior_furniture import build_rack

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
mount_steel = make_material("Factory pipe support steel", (.075,.088,.095,1), .62,.69)
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
    # Recessed support shoes stay on the ground when the pipes are cut away.
    run_length = scale*(hi[1]-lo[1])
    for offset in (-.34, .34):
        box(item["id"]+" retained pipe shoe", (x,y+run_length*offset,.026),
            (width*.435,depth*.06,.031), mount_steel, .012)
    for lane in (-.23,.23):
        run = bpy.data.objects.new("Textured industrial pipe run", data)
        bpy.context.collection.objects.link(run)
        run.parent = group
        run.matrix_parent_inverse = group.matrix_world.inverted()
        run.location = (x+width*lane,y,.057)
        run.scale = (scale,)*3
    pipe_groups += 1
assert pipe_groups == 4
print("FACTORY330_PIPE_GROUPS", pipe_groups)
cabinet = make_material("Factory console steel", (.047,.073,.09,1), .48,.58)
trim = make_material("Factory edge enamel", (.31,.145,.029,1), .47,.64)
display = make_material("Factory panel telemetry", (.014,.117,.15,1), .16,.54,.23)
detail_ids = {"west_console", "east_console", "mid_console", "north_left_shelf", "north_right_shelf"}
for item in survey["walls"]:
    identifier = item["id"]
    if identifier not in detail_ids:
        continue
    group = bpy.data.objects.new("Occludable_" + identifier, None)
    bpy.context.collection.objects.link(group)
    x1,y1,x2,y2 = item["rect"]
    w,d = (x2-x1)*40/cw, (y2-y1)*28/ch
    x,y = (x1+x2)*20/cw-20, 14-(y1+y2)*14/ch
    if identifier.endswith("_shelf"):
        build_rack(group, x, y, w, d, cabinet, trim)
        for height, offset in ((.42,-.24),(1.20,.21),(1.98,-.05)):
            place(cargo, group, (x,y+d*offset,height), (w*.70,d*.30,.50), merge=True)
    else:
        box(identifier+" chassis", (x,y,.43), (w*.44,d*.46,.43), cabinet).parent = group
        box(identifier+" recessed deck", (x,y,.874),
            (w*.34,d*.38,.022), mount_steel).parent = group
        for side in (-1, 1):
            box(identifier+" safety rail", (x+side*w*.37,y,.94),
                (w*.026,d*.40,.035), trim, .009).parent = group
        for offset in (-.29, -.15, -.01, .13):
            box(identifier+" deck crossbar", (x,y+d*offset,.913),
                (w*.35,d*.018,.022), cabinet, .008).parent = group
        box(identifier+" telemetry", (x,y-d*.36,.916),
            (w*.24,d*.028,.012), display).parent = group
        for offset in (-.22,0,.22):
            box(identifier+" control", (x+w*offset,y+d*.25,.883),
                (w*.041,d*.042,.025), trim, .006).parent = group
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
