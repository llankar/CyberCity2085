"""Assemble dockside cargo and generator modules from original map traces."""
import json
import math
from pathlib import Path
import sys
import time

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place
from shipping_container import build_container
from loading_crane import build_crane
from industrial_forklift import build_forklift

started = time.perf_counter()
root = Path(__file__).resolve().parents[3]
lab = Path("E:/CyberCity2085-3d-lab")
output = lab / "generated/phase2/dockside338"
name = "city_industrial_dockside_terminal"
source = root / "assets/maps" / name
survey = json.loads(source.with_suffix(".wall-traces.json").read_text())
gw, gh = json.loads(source.with_suffix(".walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
library = lab / "environment-library/assets"
cargo = library / "cargo_crate274/model.glb"
generator = library / "industrial_generator265/model.glb"
wall = library / "service_wall269_factory/model.glb"
selected = {"northwest_top_crates", "central_generator", "south_cargo_generator"}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
skins = {key: make_material("Dockside container "+key, (*color,1), .65,.63)
         for key,color in (("green",(.062,.15,.14)),("blue",(.044,.093,.22)),("red",(.24,.063,.034)))}
steel = make_material("Dockside door hardware", (.075,.11,.15,1), .65,.48)
beam = make_material("Dockside locking rods", (.52,.17,.028,1), .45,.48)
instances = containers = barriers = cranes = forklifts = 0
converted = set()
for row in survey["walls"]:
    identifier = row["id"]
    is_container = "container" in identifier
    is_barrier = identifier.startswith("quay_barrier_")
    is_crane = identifier.startswith("crane_")
    is_forklift = identifier.endswith("_forklift")
    is_cargo = identifier.endswith(("_crates", "_crate"))
    if identifier not in selected and not (is_container or is_barrier or is_crane or is_forklift or is_cargo):
        continue
    converted.add(identifier)
    xs, ys = zip(*row["polygon"])
    a, c, b, d = min(xs), max(xs), min(ys), max(ys)
    if is_crane:
        # Narrow to the interval shared by the north and south edges.
        top_left, top_right, bottom_right, bottom_left = row["polygon"]
        a, c = max(top_left[0],bottom_left[0]), min(top_right[0],bottom_right[0])
    else:
        assert set(map(tuple,row["polygon"])) == {(a,b),(a,d),(c,b),(c,d)}
    width, depth = (c-a)*gw/cw, (d-b)*gh/ch
    x, y = (a+c)*gw/(2*cw)-gw/2, gh/2-(b+d)*gh/(2*ch)
    group = bpy.data.objects.new("Occludable_" + identifier, None)
    bpy.context.collection.objects.link(group)
    if is_crane:
        build_crane(group, x, y, width, depth, steel, beam,
                    height=3.8 if "north" in identifier else 4.4)
        cranes += 1
    elif is_barrier:
        count = max(1, math.ceil(depth / 2))
        span = depth/count
        for index in range(count):
            place(wall, group, (x, y + (index+.5)*span-depth/2, 0),
                  (span,width,.95), yaw=math.pi/2)
        barriers += 1
    elif is_container:
        color = next((key for key in skins if identifier.endswith(key)), "green")
        vertical = depth > width
        length, thickness = (depth,width) if vertical else (width,depth)
        build_container(group,x,y,length,thickness,skins[color],steel,beam,
                        yaw=math.pi/2 if vertical else 0)
        containers += 1
    elif is_forklift:
        build_forklift(group, identifier, x, y, width, depth, beam, steel)
        forklifts += 1
    elif identifier.endswith("generator"):
        vertical = depth > width
        length, thickness = (depth,width) if vertical else (width,depth)
        place(generator, group, (x,y,0), (length*.95,thickness*.95,1.55),
              yaw=math.pi/2 if vertical else 0)
        instances += 1
    else:
        vertical = depth > width
        length, thickness = (depth,width) if vertical else (width,depth)
        count = 1 if length < thickness*1.35 else 2
        for index in range(count):
            offset = ((index+.5)/count-.5)*length
            position = (x if vertical else x+offset, y+offset if vertical else y, 0)
            place(cargo, group, position, (length*.92/count,thickness*.92,1.05),
                  yaw=math.pi/2 if vertical else 0, merge=True)
            instances += 1
assert containers == 9 and barriers == 3 and cranes == 2 and forklifts == 8
floor = make_material("Dockside source ground", (.13,.15,.17,1), .05,.84)
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
    "map": name, "instances": instances, "containers": containers, "barriers": barriers, "cranes": cranes, "reused_model_families": 4,
    "new_model_families": 1, "blender_seconds": elapsed, "forklifts": forklifts, "converted_groups": sorted(converted)
}, indent=2))
print("DOCKSIDE338_EXPORTED", instances, elapsed)
