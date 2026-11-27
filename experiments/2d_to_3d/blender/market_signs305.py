"""Add practical lighting and trade signage to existing market stalls."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "market325"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "showcase245/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0
housing = make_material("Market stall fixture housing", (.045, .057, .064, 1), .72, .42)
signs = [
    make_material("Market stall sign " + name, (*color, 1), .1, .45, .65)
    for name, color in (("amber", (.61,.23,.045)), ("teal", (.02,.42,.35)), ("rose", (.48,.08,.25)))
]
ink = make_material("Market sign dark lettering", (.009, .012, .016, 1), .1, .65)
# Food, supplies, electronics. Each icon stays within its sign face.
icons = (
    (("fork", -.12, 0, .018, .10), ("knife", .10, 0, .024, .10),
     ("prongs", -.12, .072, .055, .018)),
    (("parcel top", 0, .088, .14, .016), ("parcel bottom", 0, -.088, .14, .016),
     ("parcel left", -.124, 0, .016, .076), ("parcel right", .124, 0, .016, .076),
     ("parcel strap", 0, 0, .023, .076)),
    (),
)
tray_mat = make_material("Market food tray enamel", (.10,.12,.09,1), .2, .53)
produce = [make_material("Market produce "+name, (*color,1), 0, .68)
           for name,color in (("citrus",(.69,.23,.023)),("greens",(.12,.29,.04)))]
worktop_finishes = (
    make_material("Food stall glazed worktop", (.25,.30,.24,1), .12, .31),
    make_material("Supply stall oxidized worktop", (.18,.11,.067,1), .48, .58),
    make_material("Electronics antistatic worktop", (.032,.069,.102,1), .20, .76),
)
groups = sorted((obj for obj in bpy.data.objects if obj.name.startswith("Occludable_market_")),
                key=lambda obj: obj.name)
count = 0
trimmed = 0
trays = 0
finished_worktops = 0
for index, group in enumerate(groups):
    mesh = next((obj for obj in group.children_recursive if obj.name.startswith("PBR_Facade_")), None)
    if mesh is None:
        continue
    corners = [mesh.matrix_world @ Vector(corner) for corner in mesh.bound_box]
    x0, x1 = min(v.x for v in corners), max(v.x for v in corners)
    y0, y1 = min(v.y for v in corners), max(v.y for v in corners)
    top = max(v.z for v in corners)
    bottom = min(v.z for v in corners)
    # Move supported pieces together with the lowered deck.
    reduction = (top-bottom)*.38
    supported = []
    for child in group.children:
        if child == mesh:
            continue
        geometry = [node for node in (child, *child.children_recursive) if node.type == "MESH"]
        if geometry and min((node.matrix_world @ Vector(point)).z
                            for node in geometry for point in node.bound_box) >= top-.10:
            supported.append(child)
    if supported:
        mesh.data = mesh.data.copy()
        world = mesh.matrix_world.copy()
        inverse = world.inverted()
        supported_points = [
            node.matrix_world @ Vector(corner)
            for child in supported for node in (child, *child.children_recursive)
            if node.type == "MESH" for corner in node.bound_box
        ]
        new_x0 = max(x0, min(point.x for point in supported_points)-.12)
        new_x1 = min(x1, max(point.x for point in supported_points)+.12)
        new_y0 = max(y0, min(point.y for point in supported_points)-.12)
        new_y1 = min(y1, max(point.y for point in supported_points)+.12)
        if (new_x1 <= new_x0 or new_y1 <= new_y0
                or any(not (new_x0 <= point.x <= new_x1 and new_y0 <= point.y <= new_y1)
                       for point in supported_points)):
            new_x0, new_x1, new_y0, new_y1 = x0, x1, y0, y1
        if (new_x1-new_x0)*(new_y1-new_y0) < .99*(x1-x0)*(y1-y0):
            trimmed += 1
        for vertex in mesh.data.vertices:
            point = world @ vertex.co
            point.x = new_x0+(point.x-x0)/(x1-x0)*(new_x1-new_x0)
            point.y = new_y0+(point.y-y0)/(y1-y0)*(new_y1-new_y0)
            point.z = bottom + (point.z-bottom)*.62
            vertex.co = inverse @ point
        for child in supported:
            transform = child.matrix_world.copy()
            transform.translation.z -= reduction
            child.matrix_world = transform
        top -= reduction
        x0, x1, y0, y1 = new_x0, new_x1, new_y0, new_y1
    x = (x0+x1)/2
    y = y0+(y1-y0)*.12
    h = min(.58, (x1-x0)*.18)
    for name, position, size, material in [
        ("Trade sign frame", (x,y,top+.22), (h,.053,.21), housing),
        ("Trade sign face", (x,y-.055,top+.22), (h*.87,.009,.145), signs[index%len(signs)]),
        ("Trade sign stem", (x,y,top+.035), (.044,.044,.10), housing),
    ]:
        obj = box(name, position, size, material, .012)
        obj.parent = group
        obj.matrix_parent_inverse = group.matrix_world.inverted()
    for glyph, dx, dz, sx, sz in icons[index % len(icons)]:
        icon = box("Trade icon " + glyph, (x+dx, y-.067, top+.22+dz),
                   (sx, .005, sz), ink, .003)
        icon.parent = group
        icon.matrix_parent_inverse = group.matrix_world.inverted()
    if index % len(icons) == 2:
        outline = [(-.095,.015), (.027,.123), (.012,.032), (.099,.032),
                   (-.029,-.121), (-.011,-.021), (-.095,-.021)]
        mesh_data = bpy.data.meshes.new("Lightning sign silhouette")
        mesh_data.from_pydata([(x+u, y-.067, top+.22+v) for u,v in outline],
                              [], [tuple(reversed(range(len(outline))))])
        mesh_data.materials.append(ink)
        bolt = bpy.data.objects.new("Electronics lightning icon", mesh_data)
        bpy.context.collection.objects.link(bolt)
        bolt.parent = group
        bolt.matrix_parent_inverse = group.matrix_world.inverted()
    finish = worktop_finishes[index % len(worktop_finishes)]
    for obj in group.children_recursive:
        if obj.type != "MESH" or not obj.name.startswith("Store197 steel worktop"):
            continue
        obj.data = obj.data.copy()
        obj.data.materials.clear()
        obj.data.materials.append(finish)
        finished_worktops += 1
    if index % len(icons) == 0:
        stock = {}
        for obj in group.children:
            if obj.type == "MESH" and obj.name.startswith("Store197 rear stock"):
                key = tuple(round(value, 4) for value in obj.matrix_world.translation)
                stock.setdefault(key, []).append(obj)
        for contents in stock.values():
            points = [obj.matrix_world @ Vector(corner)
                      for obj in contents for corner in obj.bound_box]
            lo = Vector(tuple(min(point[i] for point in points) for i in range(3)))
            hi = Vector(tuple(max(point[i] for point in points) for i in range(3)))
            center = (hi+lo)/2
            width, depth = (hi.x-lo.x)/2, (hi.y-lo.y)/2
            for obj in contents:
                bpy.data.objects.remove(obj, do_unlink=True)
            tray = box("Open produce tray", (center.x, center.y, lo.z+.032),
                       (width, depth, .032), tray_mat, .014)
            items = [tray]
            for row in (-1,1):
                for column in (-1,0,1):
                    radius = min(width*.26, depth*.34)
                    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius,
                        location=(center.x+column*width*.58,center.y+row*depth*.47,lo.z+.064+radius*.65))
                    fruit = bpy.context.object
                    fruit.data.materials.append(produce[(index+row+column)%2])
                    items.append(fruit)
            bpy.ops.object.select_all(action="DESELECT")
            for obj in items:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = tray
            bpy.ops.object.join()
            tray.parent = group
            tray.matrix_parent_inverse = group.matrix_world.inverted()
            trays += 1
    count += 1
assert count >= 3 and trays > 0, (count, trays)
# Keep each stall as its own occlusion group. Join static leaf meshes
# and bake rigid bevels and normals before joining. Leave lights and animated parts separate.
for group in groups:
    parts = [obj for obj in group.children
             if obj.type == "MESH" and not obj.children and not obj.constraints
             and obj.animation_data is None and obj.data.shape_keys is None
             and all(modifier.type in {"BEVEL", "WEIGHTED_NORMAL"} for modifier in obj.modifiers)]
    if len(parts) < 2:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    bpy.context.object.name = group.name + " rigid surfaces"
maps = Path(__file__).resolve().parents[3] / "assets/maps"
map_name = "city_exterior_neon_market_alley"
survey = json.loads((maps / f"{map_name}.wall-traces.json").read_text())
gw, gh = json.loads((maps / f"{map_name}.walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
x1,y1,x2,y2 = next(row["rect"] for row in survey["walls"] if row["id"] == "west_awning")
x,y = (x1+x2)*gw/(2*cw)-gw/2,gh/2-(y1+y2)*gh/(2*ch)
w,d = (x2-x1)*gw/cw,(y2-y1)*gh/ch
awning = bpy.data.objects.new("Occludable_west_awning", None)
bpy.context.collection.objects.link(awning)
canvas = make_material("West awning weathered blue", (.024,.12,.23,1), .12,.78)
top = box("West awning canopy", (x,y,1.88), (w*.49,d*.49,.047), canvas)
top.rotation_euler.y = .12
top.parent = awning
for offset in (-.39,.39):
    box("West awning outer pole", (x+w*.43,y+offset*d,.89),
        (.034,.034,.89), housing).parent = awning
for index in range(5):
    offset = (index-2)*d*.194
    seam = box("West awning seam", (x,y+offset,1.93), (w*.47,.014,.012), housing,.004)
    seam.rotation_euler.y = .12
    seam.parent = awning
box("West awning valance", (x+w*.48,y,1.69), (.028,d*.48,.087), canvas).parent = awning

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.data.type == "POINT"
                   or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
print("MARKET325_EXPORTED", count, "trimmed", trimmed, "food trays", trays, "worktops", finished_worktops)
