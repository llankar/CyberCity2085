"""Assemble warehouse cargo and wall modules from original map traces."""
import json
import math
from pathlib import Path
import sys
import time

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place

started = time.perf_counter()
root = Path(__file__).resolve().parents[3]
lab = Path("E:/CyberCity2085-3d-lab")
output = lab / "generated/phase2/warehouse332"
name = "city_industrial_warehouse_floor"
source = root / "assets/maps" / name
survey = json.loads(source.with_suffix(".wall-traces.json").read_text())
gw, gh = json.loads(source.with_suffix(".walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
library = lab / "environment-library/assets"
cargo = library / "cargo_crate274/model.glb"
wall = library / "service_wall269_factory/model.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
steel = make_material("Warehouse rack steel", (.075,.11,.15,1), .65,.48)
beam = make_material("Warehouse rack safety beam", (.52,.17,.028,1), .45,.48)
cargo_count = wall_count = rack_count = 0
for row in survey["walls"]:
    identifier = row["id"]
    is_wall = identifier.endswith("_wall")
    is_rack = identifier.startswith("row")
    if not is_wall and not is_rack and "crate" not in identifier:
        continue
    x1, y1, x2, y2 = row["rect"]
    w, d = (x2-x1)*gw/cw, (y2-y1)*gh/ch
    x, y = (x1+x2)*gw/(2*cw)-gw/2, gh/2-(y1+y2)*gh/(2*ch)
    group = bpy.data.objects.new("Occludable_" + identifier, None)
    bpy.context.collection.objects.link(group)
    if is_wall:
        vertical = d > w
        length, thickness = (d,w) if vertical else (w,d)
        count = max(1, round(length/2))
        span = length/count
        for index in range(count):
            offset = (index+.5)*span-length/2
            place(wall, group, (x if vertical else x+offset, y+offset if vertical else y, 0),
                  (span, thickness, 1.7), yaw=math.pi/2 if vertical else 0)
            wall_count += 1
    elif is_rack:
        rack_count += 1
        parts = []
        def rack_part(label, location, dimensions, material):
            parts.append(box(label, location, dimensions, material, .012))

        for side_x in (-1, 1):
            for side_y in (-1, 0, 1):
                rack_part("Rack upright", (x+side_x*w*.43,y+side_y*d*.44,1.12),
                          (.046,.05,1.12), steel)
        for height in (.38,1.16,1.94):
            rack_part("Slotted shelf deck", (x,y,height), (w*.43,d*.45,.038), steel)
            for side in (-1,1):
                rack_part("Safety shelf rail", (x+side*w*.42,y,height+.01),
                          (.048,d*.46,.065), beam)
        bpy.ops.object.select_all(action="DESELECT")
        for part in parts:
            part.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        bpy.ops.object.join()
        bpy.context.object.name = "Warehouse pallet rack"
        bpy.context.object.parent = group
        place(cargo, group, (x,y-d*.21,.42), (w*.72,d*.32,.67))
        place(cargo, group, (x,y+d*.21,1.20), (w*.72,d*.32,.67))
        cargo_count += 2
    else:
        nx, ny = max(1,round(w/1.4)), max(1,round(d/1.4))
        for ix in range(nx):
            for iy in range(ny):
                place(cargo, group, (x-w/2+(ix+.5)*w/nx, y-d/2+(iy+.5)*d/ny, 0),
                      (w/nx*.93,d/ny*.93,1.05))
                cargo_count += 1

assert rack_count == 10, rack_count
floor = make_material("Warehouse source ground", (.13,.15,.17,1), .05,.84)
nodes = floor.node_tree.nodes
texture = nodes.new("ShaderNodeTexImage")
texture.image = bpy.data.images.load(str(output / "floor.png"))
floor.node_tree.links.new(texture.outputs["Color"], nodes.get("Principled BSDF").inputs["Base Color"])
bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,-.025))
bpy.context.object.scale = (gw/2,gh/2,1)
bpy.context.object.data.materials.append(floor)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB")
elapsed = round(time.perf_counter()-started, 2)
(output / "assembly.json").write_text(json.dumps({
    "map":name, "cargo_instances":cargo_count, "wall_instances":wall_count, "rack_instances":rack_count,
    "reused_model_families":2, "new_model_families":1, "blender_seconds":elapsed,
    "remaining":"containers, forklifts, office, stairs and loading bay"
}, indent=2))
print("WAREHOUSE332_EXPORTED", cargo_count, wall_count, elapsed)
