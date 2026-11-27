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
from interior_furniture import build_rack
from industrial_forklift import build_forklift
from shipping_container import build_container

started = time.perf_counter()
root = Path(__file__).resolve().parents[3]
lab = Path("E:/CyberCity2085-3d-lab")
output = lab / "generated/phase2/warehouse333"
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
container_skin = make_material("Weathered container green", (.062,.15,.14,1), .65,.63)
office_tile = make_material("Office raised service floor", (.08,.13,.17,1), .25,.78)
tile_nodes = office_tile.node_tree.nodes
tile_shader = tile_nodes.get("Principled BSDF")
tile_sources = lab / "sources/environment169/blue_metal_plate"
for filename, socket in (("diff.jpg", "Base Color"), ("rough.jpg", "Roughness")):
    tile = tile_nodes.new("ShaderNodeTexImage")
    tile.image = bpy.data.images.load(str(tile_sources / filename))
    if socket == "Roughness":
        tile.image.colorspace_settings.name = "Non-Color"
    office_tile.node_tree.links.new(tile.outputs["Color"], tile_shader.inputs[socket])
service_rooms = {"east_office", "east_stair", "east_bay"}
cargo_count = wall_count = rack_count = container_count = rack_cargo_count = forklift_count = 0
for row in survey["walls"]:
    identifier = row["id"]
    is_wall = identifier.endswith("_wall")
    is_rack = identifier.startswith("row")
    is_container = identifier.startswith("west_container_")
    is_forklift = identifier.startswith("forklift_")
    if not (is_wall or is_rack or is_container or is_forklift or identifier in service_rooms
            or "crate" in identifier):
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
    elif is_forklift:
        build_forklift(group, identifier, x, y, w, d, beam, steel)
        forklift_count += 1
    elif is_container:
        build_container(group, x, y, w, d, container_skin, steel, beam)
        container_count += 1
    elif is_rack:
        rack_count += 1
        build_rack(group, x, y, w, d, steel, beam)
        vertical = d > w
        length, depth = max(w,d), min(w,d)
        for level, offsets in enumerate(((-.27,.19), (-.14,.27), (-.25,.15))):
            for offset in offsets:
                px = x if vertical else x+offset*length
                py = y+offset*length if vertical else y
                items = place(cargo, group, (px,py,.42+level*.78),
                              (length*.22,depth*.72,.56),
                              yaw=math.pi/2 if vertical else 0, merge=True)
                for item in items:
                    item.name = identifier + " shelf cargo"
                rack_cargo_count += 1
                cargo_count += 1
    elif identifier == "east_office":
        box(identifier+" service floor", (x,y,.005),
            (w*.499,d*.499,.018), office_tile, .003)
        for side in (-1,1):
            box(identifier+" partition", (x,y+side*d*.47,.56),
                (w*.47,.06,.56), steel).parent = group
        box(identifier+" inner partition", (x-w*.46,y+d*.18,.56),
            (.055,d*.28,.56), steel).parent = group
        box(identifier+" worktop", (x+w*.10,y+d*.28,.59),
            (w*.31,d*.09,.055), beam).parent = group
        for side in (-1,1):
            box(identifier+" desk pedestal", (x+w*side*.14,y+d*.28,.29),
                (w*.075,d*.064,.29), steel).parent = group
        box(identifier+" console housing", (x,y+d*.31,.79),
            (w*.10,.035,.14), steel).parent = group
    elif identifier == "east_stair":
        for step in range(8):
            z = (step+1)*.105
            tread_y = y+((step+.5)/8-.5)*d
            box(identifier+" tread", (x,tread_y,z/2),
                (w*.46,d/16,z/2), steel).parent = group
            box(identifier+" nosing", (x,tread_y-d*.047,z+.01),
                (w*.45,d*.01,.01), beam, .004).parent = group
    elif identifier == "east_bay":
        box(identifier+" loading deck", (x,y,.068),
            (w*.47,d*.47,.068), steel).parent = group
        box(identifier+" dock lip", (x-w*.45,y,.145),
            (.037,d*.45,.022), beam).parent = group
        for offset in (-.24,.24):
            place(cargo, group, (x+w*.10,y+d*offset,.14), (w*.54,d*.32,.53), merge=True)
            cargo_count += 1
    else:
        nx, ny = max(1,round(w/1.4)), max(1,round(d/1.4))
        for ix in range(nx):
            for iy in range(ny):
                place(cargo, group, (x-w/2+(ix+.5)*w/nx, y-d/2+(iy+.5)*d/ny, 0),
                      (w/nx*.93,d/ny*.93,1.05))
                cargo_count += 1

assert rack_count == 10 and container_count == 3, (rack_count, container_count)
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
    "map":name, "cargo_instances":cargo_count, "wall_instances":wall_count, "rack_instances":rack_count, "rack_cargo_instances":rack_cargo_count, "container_instances":container_count,
    "reused_model_families":2, "new_model_families":2, "blender_seconds":elapsed,
    "forklift_instances":forklift_count, "service_room_instances": len(service_rooms)
}, indent=2))
print("WAREHOUSE333_EXPORTED", cargo_count, wall_count, elapsed)
