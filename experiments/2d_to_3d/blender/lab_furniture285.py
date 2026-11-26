"""Build raised laboratory work surfaces and rack fronts within surveyed bounds."""
from pathlib import Path
import json
import math
import sys

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "lab291"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "lab282/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0

steel = make_material("Lab285 powder coated alloy", (.16, .22, .27, 1), .65, .38)
dark = bpy.data.materials["Lab recessed service panels"]
cyan = bpy.data.materials["Lab cyan instrumentation"]
amber = make_material("Lab285 rack status", (.6, .18, .02, 1), .2, .35, 1.5)

glass = bpy.data.materials["Lab containment blue glass"]
polymer = make_material("Lab cleanroom polymer", (.36, .43, .46, 1), .15, .32)
families = set()
lab = phase.parents[1]
medical = lab / "sources/environment169/medical_box/medical_box_1k.gltf"
cargo = lab / "environment-library/assets/cargo_crate274/model.glb"
crates = bpy.data.objects["Occludable_south_crates"]
old_crate_parts = list(crates.children)
crate_top = next(obj for obj in old_crate_parts if obj.name.endswith("source worktop"))
cx, cy, _ = crate_top.location
cw, cd = crate_top.scale.x, crate_top.scale.y
for obj in old_crate_parts:
    bpy.data.objects.remove(obj, do_unlink=True)
for offset in (-.59, 0, .59):
    place(cargo, crates, (cx + offset * cw, cy, 0), (cw * .54, cd * 1.7, 1.2))

# Replace the projected greenhouse image with raised hydroponic beds.
greenhouse = bpy.data.objects["Occludable_west_greenhouse"]
top = next(obj for obj in greenhouse.children if obj.name.endswith("source worktop"))
gx, gy, gz = top.location
gw, gd = top.scale.x, top.scale.y
bpy.data.objects.remove(top, do_unlink=True)
soil = make_material("Hydroponic substrate", (.037, .024, .014, 1), 0, .92)
foliage = make_material("Hydroponic foliage", (.052, .30, .09, 1), 0, .62)
vertices = []
faces = []
for index in range(9):
    angle = index * 2.39996
    length = .24 + .045 * (index % 4)
    dx, dy = math.cos(angle), math.sin(angle)
    start = len(vertices)
    vertices.extend([
        (0, 0, 0),
        (dx*length*.48 - dy*.075, dy*length*.48 + dx*.075, .19),
        (dx*length*.63, dy*length*.63, .25),
        (dx*length, dy*length, .18 + .055*(index % 3)),
        (dx*length*.48 + dy*.075, dy*length*.48 - dx*.075, .19),
    ])
    faces.extend((start, start+a, start+b) for a, b in ((1, 2), (2, 4), (2, 3), (3, 4)))
plant = bpy.data.meshes.new("Hydroponic rosette")
plant.from_pydata(vertices, [], faces)
plant.update()
plant.materials.append(foliage)
for row in (-1, 1):
    y = gy + row * gd * .44
    tray = box("Hydroponic bed", (gx, y, gz+.09), (gw*.84, gd*.34, .12), steel)
    tray.parent = greenhouse
    liner = box("Hydroponic liner", (gx, y, gz+.22), (gw*.76, gd*.27, .025), soil)
    liner.parent = greenhouse
    # The utility rail carries both the feed pipe and the overhead grow lamp.
    rail_y = y + gd * .25
    for side in (-1, 1):
        support = box("Grow rail support", (gx + side * gw*.73, rail_y, gz+.54),
                      (.035, .035, .35), dark)
        support.parent = greenhouse
    rail = box("Grow lamp housing", (gx, rail_y, gz+.88),
               (gw*.77, .062, .038), steel)
    rail.parent = greenhouse
    light_strip = box("Grow lamp diffuser", (gx, rail_y-.035, gz+.837),
                      (gw*.72, .035, .012), cyan)
    light_strip.parent = greenhouse
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.035, depth=gw*1.49,
                                        location=(gx, rail_y, gz+.30),
                                        rotation=(0, math.pi/2, 0))
    pipe = bpy.context.object
    pipe.name = "Hydroponic feed pipe"
    pipe.data.materials.append(steel)
    pipe.parent = greenhouse
    for index in range(5):
        obj = bpy.data.objects.new("Hydroponic plant", plant)
        bpy.context.collection.objects.link(obj)
        obj.parent = greenhouse
        obj.location = (gx+(index-2)*gw*.31, y, gz+.245)
        obj.rotation_euler.z = index * .72 + row
        obj.scale = (0.8 + .08*(index % 3),)*3

count = 0
for top in list(bpy.data.objects):
    if not top.name.endswith(" source worktop"):
        continue
    root = top.parent
    name = root.name
    rack = "rack" in name
    if not rack and not any(kind in name for kind in ("desk", "table", "console")):
        continue
    x, y, z = top.location
    w, d = top.scale.x, top.scale.y
    bpy.data.objects.remove(top, do_unlink=True)

    def part(label, offset, half_size, material):
        dx, dy, dz = offset
        obj = box("Lab285 " + label, (x + dx, y + dy, dz), half_size, material, .012)
        obj.parent = root

    part("solid worktop", (0, 0, z - .02), (w, d, .024), steel)
    if rack:
        families.add("server")
        face = w * (.90 if x > 0 else -.90)
        part("rack fascia", (face, 0, .69), (w * .075, d * .88, .60), steel)
        for index in range(8):
            height = .19 + index * .136
            part("server sled", (face * 1.06, 0, height), (w * .04, d * .76, .057), dark)
            part("server status", (face * 1.105, d * .63, height), (w * .012, .028, .017),
                 amber if index % 3 == 0 else cyan)
    elif "console" in name:
        families.add("control")
        part("sloped control housing", (0, -d * .52, z + .094), (w * .72, d * .23, .085), dark)
        for index in range(5):
            part("control key", (w * (index - 2) * .22, -d * .57, z + .182),
                 (w * .06, d * .07, .012), cyan if index < 4 else amber)
    elif "central" in name:
        families.add("analysis")
        part("analyzer chassis", (w * .35, -d * .30, z + .22),
             (w * .43, d * .43, .22), polymer)
        part("sample chamber", (w * .35, -d * .30, z + .45),
             (w * .32, d * .32, .07), glass)
        part("analyzer readout", (w * .35, -d * .735, z + .25),
             (w * .22, .009, .055), amber)
    else:
        families.add("preparation")
        part("instrument tray", (0, -d * .48, z + .026), (w * .48, d * .22, .026), dark)
        place(medical, root, (x, y - d * .48, z + .055), (w * .72, d * .38, .35))
        part("tray status strip", (0, -d * .66, z + .053), (w * .37, .014, .009), cyan)
    count += 1

assert count == 18 and len(families) == 4, (count, families)
# Replace overlapping proxy groups and add independent surveyed fixtures.
repo = Path(__file__).resolve().parents[3]
survey = json.loads((repo / "experiments/2d_to_3d/lab_fixtures290.json").read_text())
grid_w, grid_h = json.loads((repo / "assets/maps/city_interior_research_lab.walls.json").read_text())["grid"]
canvas_w, canvas_h = survey["canvas_size"]
for fixture in survey["fixtures"]:
    for identifier in fixture["existing_overlaps"]:
        old_group = bpy.data.objects["Occludable_" + identifier]
        for obj in reversed(old_group.children_recursive):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.objects.remove(old_group, do_unlink=True)
    x1, y1, x2, y2 = fixture["rect"]
    x = ((x1+x2)/2/canvas_w-.5)*grid_w
    y = (.5-(y1+y2)/2/canvas_h)*grid_h
    w, d = (x2-x1)/canvas_w*grid_w/2, (y2-y1)/canvas_h*grid_h/2
    group = bpy.data.objects.new("Occludable_" + fixture["id"], None)
    bpy.context.collection.objects.link(group)
    if fixture["family"] == "storage":
        for offset in (-.5, .5):
            place(cargo, group, (x, y+offset*d, 0), (w*1.85, d*.88, .9))
        continue
    rack = fixture["family"] == "sample_rack"
    body = box("Wall cabinet", (x, y, .52), (w*.94, d*.90, .52), dark)
    body.parent = group
    cap = box("Cabinet top trim", (x, y, 1.055), (w*.92, d*.89, .031), steel)
    cap.parent = group
    for index in range(3):
        column = x+(index-1)*w*.58
        front = box("Sample drawer" if rack else "Control display",
                    (column, y-d*.90+.005, .73 if rack else .79),
                    (w*.23, .05, .20), steel if rack else cyan)
        front.parent = group
        if rack:
            latch = box("Sample latch", (column, y-d*.90-.074, .75),
                        (w*.09, .018, .022), amber)
            latch.parent = group

floor = bpy.data.materials["Original laboratory floor"]
texture = next(node for node in floor.node_tree.nodes if node.type == "TEX_IMAGE")
texture.image = bpy.data.images.load(str(phase / "lab291/floor.png"))
for light in bpy.data.lights:
    if light.type == "POINT":
        light.energy *= .25
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.data.type == "POINT"
                   or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
print("LAB291_EXPORTED", count, "surveyed furniture groups")
