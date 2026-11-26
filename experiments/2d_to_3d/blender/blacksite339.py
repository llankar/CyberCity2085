"""Assemble blacksite containment pods and perimeter walls from original map traces."""
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
output = lab / "generated/phase2/blacksite339"
name = "city_interior_blacksite_lab"
source = root / "assets/maps" / name
survey = json.loads(source.with_suffix(".wall-traces.json").read_text())
gw, gh = json.loads(source.with_suffix(".walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
library = lab / "environment-library/assets"
pod = output / "shared_pods.glb"
bpy.ops.wm.open_mainfile(filepath=str(lab / "generated/phase2/lab291/environment.blend"))
original = bpy.data.objects["Occludable_north_pods"]
pod_meshes = set(original.children_recursive)
for obj in bpy.context.scene.objects:
    obj.select_set(obj in pod_meshes and obj.type == "MESH")
bpy.ops.export_scene.gltf(filepath=str(pod), export_format="GLB", use_selection=True, export_apply=True)

wall = library / "service_wall269_factory/model.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
pod_count = wall_count = 0
for row in survey["walls"]:
    identifier = row["id"]
    is_wall = "_wall" in identifier and "rect" in row
    if not is_wall and not identifier.endswith("_pods") and "_pods_" not in identifier:
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
    else:
        place(pod, group, (x,y,0), (w*.88,d*.87,2.10))
        pod_count += 1
assert pod_count == 7, pod_count
floor = make_material("Blacksite source ground", (.13,.15,.17,1), .05,.84)
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
    "map": name, "pod_groups": pod_count, "wall_instances": wall_count,
    "reused_model_families": 2, "new_model_families": 0, "blender_seconds": elapsed
}, indent=2))
print("BLACKSITE339_EXPORTED", pod_count, wall_count, elapsed)
