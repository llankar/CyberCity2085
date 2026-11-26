"""Assemble clinic beds and perimeter from original map traces."""
import json
import math
from pathlib import Path
import sys
import time

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place
from interior_furniture import build_bed

started = time.perf_counter()
root = Path(__file__).resolve().parents[3]
lab = Path("E:/CyberCity2085-3d-lab")
output = lab / "generated/phase2/clinic340"
name = "city_interior_medical_clinic"
source = root / "assets/maps" / name
survey = json.loads(source.with_suffix(".wall-traces.json").read_text())
gw, gh = json.loads(source.with_suffix(".walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
library = lab / "environment-library/assets"
wall = library / "service_wall269_factory/model.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
steel = make_material("Clinic bed enamel frame", (.18,.27,.31,1), .44,.46)
linen = make_material("Clinic linen", (.48,.58,.60,1), .0,.85)
pad = make_material("Clinic bed blue covering", (.051,.21,.28,1), .05,.7)
bed_count = wall_count = 0
for row in survey["walls"]:
    identifier = row["id"]
    is_wall = identifier.endswith("_wall") and "rect" in row
    if not is_wall and not identifier.startswith("bed_") and identifier != "east_operating_table":
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
        build_bed(group, x, y, w, d, steel, linen, pad)
        bed_count += 1
assert bed_count == 6, bed_count
floor = make_material("Clinic source ground", (.13,.15,.17,1), .05,.84)
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
    "map": name, "beds": bed_count, "wall_instances": wall_count,
    "reused_model_families": 1, "new_model_families": 1, "blender_seconds": elapsed
},indent=2))
print("CLINIC340_EXPORTED", bed_count, wall_count, elapsed)
