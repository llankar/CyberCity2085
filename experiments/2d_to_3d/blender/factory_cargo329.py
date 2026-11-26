"""Swap the experimental factory ground texture while preserving authored models."""
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from library_placement import place

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "factory329"
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
