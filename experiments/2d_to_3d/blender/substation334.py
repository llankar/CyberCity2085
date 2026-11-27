"""Assemble substation transformer and wall modules from original map traces."""
import json
import math
from pathlib import Path
import sys
import time

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place

started = time.perf_counter()
root = Path(__file__).resolve().parents[3]
lab = Path("E:/CyberCity2085-3d-lab")
output = lab / "generated/phase2/substation334"
name = "city_industrial_power_substation"
source = root / "assets/maps" / name
survey = json.loads(source.with_suffix(".wall-traces.json").read_text())
gw, gh = json.loads(source.with_suffix(".walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
library = lab / "environment-library/assets"
transformer = library / "industrial_generator265/model.glb"
wall = library / "service_wall269_factory/model.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
service = library / "industrial_service267/model.glb"
steel = make_material("Substation switchgear casing", (.055,.09,.11,1), .65,.56)
copper = make_material("Substation conduit metal", (.15,.073,.033,1), .69,.60)
display = make_material("Substation telemetry", (.011,.095,.14,1), .12,.43,.24)
pad = make_material("Substation bolted service pad", (.06,.10,.12,1), .41,.74)
pad_nodes = pad.node_tree.nodes
pad_shader = pad_nodes.get("Principled BSDF")
pad_texture = pad_nodes.new("ShaderNodeTexImage")
pad_texture.image = bpy.data.images.load(str(lab / "sources/environment169/blue_metal_plate/diff.jpg"))
pad.node_tree.links.new(pad_texture.outputs["Color"], pad_shader.inputs["Base Color"])
equipment_count = wall_count = accessory_count = 0
for row in survey["walls"]:
    identifier = row["id"]
    is_wall = identifier.endswith("_wall")
    group = bpy.data.objects.new("Occludable_" + identifier, None)
    bpy.context.collection.objects.link(group)
    if "points" in row:
        radius = row["width"] * min(gw/cw, gh/ch) * .38
        points = [Vector((px*gw/cw-gw/2, gh/2-py*gh/ch, radius+.06))
                  for px,py in row["points"]]
        for start,end in zip(points, points[1:]):
            axis = end-start
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius,
                                                depth=axis.length, location=(start+end)/2)
            pipe = bpy.context.object
            pipe.name = identifier + " conduit"
            pipe.rotation_euler = axis.to_track_quat("Z","Y").to_euler()
            pipe.data.materials.append(copper)
            pipe.parent = group
        for point in points[1:-1]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=radius,
                                                 location=point)
            elbow = bpy.context.object
            elbow.name = identifier + " elbow"
            elbow.data.materials.append(copper)
            elbow.parent = group
        accessory_count += 1
        continue
    x1, y1, x2, y2 = row["rect"]
    w, d = (x2-x1)*gw/cw, (y2-y1)*gh/ch
    x, y = (x1+x2)*gw/(2*cw)-gw/2, gh/2-(y1+y2)*gh/(2*ch)
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
    elif identifier.endswith("_transformer"):
        # This low deck stays visible through cutaways of the equipment above it.
        box(identifier+" retained service pad", (x,y,.021),
            (w*.499,d*.499,.026), pad, .008)
        vertical = d > w
        length, width = (d,w) if vertical else (w,d)
        for side in (-1, 1):
            center = (x if vertical else x+side*w*.24,
                      y+side*d*.24 if vertical else y, .047)
            place(transformer, group, center, (length*.45,width*.92,1.85),
                  yaw=math.pi/2 if vertical else 0)
            equipment_count += 1
    else:
        vertical = d > w
        length, depth = max(w,d),min(w,d)
        if "console" in identifier or identifier == "central_control":
            height = .98 if identifier == "central_control" else .82
            box(identifier+" operator cabinet", (x,y,height/2),
                (w*.45,d*.42,height/2), steel).parent = group
            box(identifier+" telemetry bezel", (x,y-d*.10,height+.028),
                (w*.36,d*.18,.028), copper).parent = group
            box(identifier+" telemetry screen", (x,y-d*.10,height+.061),
                (w*.31,d*.135,.009), display).parent = group
            for index in (-1,0,1):
                box(identifier+" control button", (x+index*w*.17,y+d*.18,height+.014),
                    (w*.034,d*.034,.014), copper, .006).parent = group
        elif identifier.endswith("_tanks"):
            radius = min(w*.33,d*.16)
            for offset in (-.26,.26):
                bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=1.24,
                                                    location=(x,y+offset*d,.62))
                tank = bpy.context.object
                tank.name = identifier + " reservoir"
                tank.data.materials.append(steel)
                tank.parent = group
        elif identifier in {"west_substation", "east_substation"}:
            # The source banks flank the central aisle, with service panels facing it.
            inward = 1 if identifier == "west_substation" else -1
            box(identifier+" retained service pad", (x,y,.021),
                (w*.499,d*.499,.026), pad, .008)
            box(identifier+" switchgear base", (x,y,.18),
                (w*.46,d*.45,.13), steel).parent = group
            box(identifier+" bus duct", (x-inward*w*.18,y,.55),
                (w*.12,d*.40,.27), steel).parent = group
            for offset in (-.28, 0, .28):
                bay_y = y+offset*d
                box(identifier+" breaker module", (x+inward*w*.12,bay_y,.46),
                    (w*.16,d*.105,.30), steel, .025).parent = group
                box(identifier+" breaker indicator", (x+inward*w*.22,bay_y,.77),
                    (w*.05,d*.035,.012), display, .005).parent = group
        else:
            place(service, group, (x,y,0), (length*.94,depth*.94,1.60),
                  yaw=math.pi/2 if vertical else 0, merge=True)
        accessory_count += 1
assert equipment_count == 12 and accessory_count == 18
floor = make_material("Substation source ground", (.13,.15,.17,1), .05,.84)
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
    "map": name, "generator_instances": equipment_count, "wall_instances": wall_count,
    "accessory_groups": accessory_count, "reused_model_families": 3, "blender_seconds": elapsed
}, indent=2))
print("SUBSTATION334_EXPORTED", equipment_count, wall_count, elapsed)
