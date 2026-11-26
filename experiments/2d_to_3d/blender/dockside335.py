"""Assemble dockside cargo and generator modules from original map traces."""
import json
import math
from pathlib import Path
import sys
import time

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import make_material
from library_placement import place

started = time.perf_counter()
root = Path(__file__).resolve().parents[3]
lab = Path("E:/CyberCity2085-3d-lab")
output = lab / "generated/phase2/dockside335"
name = "city_industrial_dockside_terminal"
source = root / "assets/maps" / name
survey = json.loads(source.with_suffix(".wall-traces.json").read_text())
gw, gh = json.loads(source.with_suffix(".walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
library = lab / "environment-library/assets"
cargo = library / "cargo_crate274/model.glb"
generator = library / "industrial_generator265/model.glb"
selected = {"northwest_top_crates", "central_generator", "south_cargo_generator"}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
instances = 0
for row in survey["walls"]:
    identifier = row["id"]
    if identifier not in selected:
        continue
    xs, ys = zip(*row["polygon"])
    a, c, b, d = min(xs), max(xs), min(ys), max(ys)
    assert set(map(tuple,row["polygon"])) == {(a,b),(a,d),(c,b),(c,d)}
    width, depth = (c-a)*gw/cw, (d-b)*gh/ch
    x, y = (a+c)*gw/(2*cw)-gw/2, gh/2-(b+d)*gh/(2*ch)
    group = bpy.data.objects.new("Occludable_" + identifier, None)
    bpy.context.collection.objects.link(group)
    if identifier.endswith("generator"):
        vertical = depth > width
        length, thickness = (depth,width) if vertical else (width,depth)
        place(generator, group, (x,y,0), (length*.95,thickness*.95,1.55),
              yaw=math.pi/2 if vertical else 0)
        instances += 1
    else:
        for offset in (-.25,.25):
            place(cargo, group, (x+offset*width,y,0), (width*.45,depth*.92,1.05))
            instances += 1
assert instances == 4
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
    "map": name, "instances": instances, "reused_model_families": 2,
    "new_model_families": 0, "blender_seconds": elapsed, "converted_groups": sorted(selected)
}, indent=2))
print("DOCKSIDE335_EXPORTED", instances, elapsed)
