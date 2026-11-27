"""Reuse the existing wall vent mesh on residential blind facade sections."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from library_placement import place
from create_hardsurface_crate import box, make_material

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "residential317"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "residential284/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0
vent = phase.parents[1] / "environment-library/assets/wall_fixtures282/vent.glb"
cladding = [
    make_material("Facade skirting " + label, (*color, 1), .25, .66)
    for label, color in (("slate", (.09,.13,.18)), ("oxide", (.17,.071,.047)),
                         ("green ceramic", (.059,.136,.12)))
]
count = 0
facades = 0
for shell in list(bpy.context.scene.objects):
    if shell.type != "MESH" or not shell.name.endswith(" shell") or not shell.parent:
        continue
    faces = [face for face in shell.data.polygons if abs(face.normal.z) < .15 and face.area > 3]
    if not faces:
        continue
    face = max(faces, key=lambda item: item.area)
    normal = (shell.matrix_world.to_3x3() @ face.normal).normalized()
    tangent = Vector((normal.y, -normal.x, 0))
    center = shell.matrix_world @ face.center
    face_points = [shell.matrix_world @ shell.data.vertices[i].co for i in face.vertices]
    width = max(v.dot(tangent) for v in face_points)-min(v.dot(tangent) for v in face_points)
    base = min(v.z for v in face_points)
    # Two segments leave the center clear for the existing doorway.
    finish = cladding[facades % len(cladding)]
    for side in (-1, 1):
        anchor = center + tangent*(width*.29*side) + normal*.024
        anchor.z = base+.14
        strip = box("Facade skirting", tuple(anchor), (width*.16,.025,.11), finish, .012)
        strip.rotation_euler.z = math.atan2(tangent.y, tangent.x)
        strip.parent = shell.parent
        strip.matrix_parent_inverse = shell.parent.matrix_world.inverted()
    facades += 1
    for offset in (-.27, .27):
        anchor = center + tangent*(width*offset) + normal*.10
        anchor.z = base+.23
        place(vent, shell.parent, tuple(anchor), (.68, .17, .32),
              yaw=math.atan2(tangent.y, tangent.x))
        count += 1
assert count
fan = phase.parents[1] / "environment-library/assets/roof_twin_fan/optimized.glb"
repo = Path(__file__).resolve().parents[3]
survey = json.loads((repo / "experiments/2d_to_3d/residential_roofs317.json").read_text())
gw, gh = json.loads((repo / "assets/maps/city_district_apartment_block.walls.json").read_text())["grid"]
cw, ch = survey["canvas"]
for identifier, (x1,y1,x2,y2), _ in survey["fans"]:
    group = bpy.data.objects["Occludable_" + identifier]
    roof = next(obj for obj in group.children if obj.name.endswith(" shell"))
    height = max((roof.matrix_world @ vertex.co).z for vertex in roof.data.vertices)
    center = ((x1+x2)*gw/(2*cw)-gw/2, gh/2-(y1+y2)*gh/(2*ch), height)
    parts = place(fan, group, center, ((x2-x1)*gw/cw, (y2-y1)*gh/ch, .42))
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    bpy.context.object.name = "Residential rooftop twin fan"

roof_material = bpy.data.materials["Original residential roof artwork"]
texture = next(node for node in roof_material.node_tree.nodes if node.type == "TEX_IMAGE")
texture.image = bpy.data.images.load(str(output / "roof.png"))
print("RESIDENTIAL317_ROOF_FANS", len(survey["fans"]))
housing = make_material("Entry lamp housing", (.04,.05,.055,1), .6, .48)
diffuser = make_material("Entry lamp warm diffuser", (.75,.39,.16,1), .1, .38, 1.4)
entrances = [obj for obj in bpy.context.scene.objects
             if obj.type == "MESH" and " entrance" in obj.name and obj.parent]
for entry in entrances:
    points = [entry.matrix_world @ Vector(corner) for corner in entry.bound_box]
    lo = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    hi = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    center = (lo+hi)/2
    center.z = hi.z+.12
    x_aligned = hi.x-lo.x >= hi.y-lo.y
    half_size = (.23,.074,.055) if x_aligned else (.074,.23,.055)
    shell = box("Entry lamp body", tuple(center), half_size, housing, .012)
    lens = box("Entry lamp lens", tuple(center-Vector((0,0,.053))),
               (half_size[0]*.84,half_size[1]*.84,.012), diffuser, .008)
    # An exposed wraparound band remains visible from the elevated camera.
    band = box("Entry lamp visible band", tuple(center-Vector((0,0,.028))),
               (half_size[0]+.006,half_size[1]+.006,.015), diffuser, .005)
    for obj in (shell,lens,band):
        obj.parent = entry.parent
        obj.matrix_parent_inverse = entry.parent.matrix_world.inverted()
assert entrances
print("RESIDENTIAL317_ENTRIES", len(entrances))

street = json.loads((output / "street_fixtures.json").read_text(encoding="utf-8"))
cw, ch = street["canvas_size"]
library = phase.parents[1] / "environment-library/assets"
vehicle = library / "derelict_suv275/model.glb"
crate = library / "cargo_crate274/model.glb"
concrete = make_material("Planter concrete", (.15,.17,.16,1), .04,.84)
bark = make_material("Street tree bark", (.095,.057,.035,1), 0,.93)
leaves = [make_material("Street foliage " + str(i), color, 0,.88) for i, color in enumerate(
    ((.05,.13,.038,1), (.094,.19,.055,1), (.145,.24,.074,1))
)]
for row in street["walls"]:
    identifier = row["id"]
    if "rect" in row:
        x1,y1,x2,y2 = row["rect"]
    else:
        xs,ys = zip(*row["polygon"])
        x1,y1,x2,y2 = min(xs),min(ys),max(xs),max(ys)
    w,d = (x2-x1)*gw/cw,(y2-y1)*gh/ch
    x,y = (x1+x2)*gw/(2*cw)-gw/2,gh/2-(y1+y2)*gh/(2*ch)
    group = bpy.data.objects.new("Occludable_" + identifier, None)
    bpy.context.collection.objects.link(group)
    vertical = d > w
    length, width = (d,w) if vertical else (w,d)
    yaw = math.pi/2 if vertical else 0
    if "vehicle" in identifier:
        place(vehicle, group, (x,y,0), (length*.96,width*.93,1.02), yaw=yaw)
    elif "crate" in identifier:
        count = 2 if identifier.endswith("crates") else 1
        for i in range(count):
            offset = (i-(count-1)/2)*length*.45
            location = (x,y+offset,0) if vertical else (x+offset,y,0)
            place(crate, group, location, (length*.88/count,width*.88,.66), yaw=yaw)
    else:
        tree = "_tree" in identifier
        bed = box("Street planting bed", (x,y,.15), (w*.46,d*.46,.15), concrete,.08)
        bed.parent = group
        if tree:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=.09, depth=1.06, location=(x,y,.80))
            trunk = bpy.context.object
            trunk.name = "Street tree trunk"
            trunk.data.materials.append(bark)
            trunk.parent = group
        for i,offset in enumerate((-.25,0,.25)):
            cx,cy = (x,y+d*offset) if vertical else (x+w*offset,y)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1,
                                                location=(cx,cy,1.48 if tree else .39))
            shrub = bpy.context.object
            shrub.name = "Street foliage crown"
            shrub.scale = (min(w*.29,.64),min(d*.29,.64),.58 if tree else .24)
            shrub.data.materials.append(leaves[i])
            shrub.parent = group
roof_crate = next(row for row in json.loads(
    (repo / "assets/maps/city_district_apartment_block.wall-traces.json").read_text()
)["walls"] if row["id"] == "northwest_crate")
x1,y1,x2,y2 = roof_crate["rect"]
roof_group = bpy.data.objects["Occludable_northwest_building"]
roof_shell = next(obj for obj in roof_group.children if obj.name.endswith(" shell"))
height = max((roof_shell.matrix_world @ vertex.co).z for vertex in roof_shell.data.vertices)
center = ((x1+x2)*gw/(2*cw)-gw/2, gh/2-(y1+y2)*gh/(2*ch), height)
place(crate, roof_group, center, ((x2-x1)*gw/cw,(y2-y1)*gh/ch,.66))[0].name = "Northwest rooftop cargo"

floor = bpy.data.materials["Residential original street floor"]
next(node for node in floor.node_tree.nodes if node.type == "TEX_IMAGE").image = bpy.data.images.load(
    str(output / "street_floor.png")
)

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.data.type == "POINT"
                   or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
print("RESIDENTIAL317_EXPORTED", count, facades)
