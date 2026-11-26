"""Add practical lighting and trade signage to existing market stalls."""
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "market321"
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
groups = sorted((obj for obj in bpy.data.objects if obj.name.startswith("Occludable_market_")),
                key=lambda obj: obj.name)
count = 0
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
        for vertex in mesh.data.vertices:
            point = world @ vertex.co
            point.z = bottom + (point.z-bottom)*.62
            vertex.co = inverse @ point
        for child in supported:
            transform = child.matrix_world.copy()
            transform.translation.z -= reduction
            child.matrix_world = transform
        top -= reduction
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
    count += 1
assert count >= 3, count
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.data.type == "POINT"
                   or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
print("MARKET321_EXPORTED", count)
