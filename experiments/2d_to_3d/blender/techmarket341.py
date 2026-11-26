"""Assemble technology market stalls from shared market geometry from original map traces."""
import json
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
output = lab / "generated/phase2/techmarket341"
name = "city_district_tech_market"
source = root / "assets/maps" / name
survey = json.loads(source.with_suffix(".wall-traces.json").read_text())
gw, gh = json.loads(source.with_suffix(".walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
stall = output / "shared_electronics_stall.glb"
bpy.ops.wm.open_mainfile(filepath=str(lab / "generated/phase2/market325/environment.blend"))
source_group = bpy.data.objects["Occludable_market_ne"]
descendants = set(source_group.children_recursive)
for obj in bpy.context.scene.objects:
    obj.select_set(obj in descendants and obj.type == "MESH")
bpy.ops.export_scene.gltf(filepath=str(stall), export_format="GLB", use_selection=True, export_apply=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0

selected = {"northwestern_shop", "western_small_stall", "center_north_stall", "southeast_bottom_stall"}
placed = []
for row in survey["walls"]:
    identifier = row["id"]
    if identifier not in selected:
        continue
    x1,y1,x2,y2 = row["rect"]
    w,d = (x2-x1)*gw/cw,(y2-y1)*gh/ch
    x,y = (x1+x2)*gw/(2*cw)-gw/2,gh/2-(y1+y2)*gh/(2*ch)
    group = bpy.data.objects.new("Occludable_"+identifier,None)
    bpy.context.collection.objects.link(group)
    place(stall,group,(x,y,0),(w*.96,d*.96,2.5))
    placed.append(identifier)
assert set(placed) == selected
floor = make_material("Tech market source ground", (.13,.15,.17,1), .05,.84)
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
elapsed = round(time.perf_counter()-started,2)
(output / "assembly.json").write_text(json.dumps({
    "map": name, "stall_groups": placed, "reused_model_families": 1,
    "new_model_families": 0, "blender_seconds": elapsed
},indent=2))
print("TECHMARKET341_EXPORTED", len(placed), elapsed)
