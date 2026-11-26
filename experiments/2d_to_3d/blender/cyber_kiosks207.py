"""Replace contemporary cloth stalls with one coherent cyberpunk kiosk pass."""
from pathlib import Path
import bpy
import math
import json
import numpy as np
from mathutils import Vector, Matrix

LAB = Path("E:/CyberCity2085-3d-lab")
OUT = LAB / "generated/phase2/showcase207"
OUT.mkdir(exist_ok=True)
REPO = Path(__file__).resolve().parents[3]
bpy.ops.wm.open_mainfile(filepath=str(LAB / "generated/phase2/showcase206/environment.blend"))


def material(name, color, emission=0, alpha=1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, alpha)
    shader.inputs["Roughness"].default_value = .7
    shader.inputs["Metallic"].default_value = .45 if not emission else .05
    if emission:
        shader.inputs["Emission Color"].default_value = (*color, 1)
        shader.inputs["Emission Strength"].default_value = emission
    if alpha < 1:
        shader.inputs["Alpha"].default_value = alpha
        mat.surface_render_method = "DITHERED"
    return mat


steel = material("Kiosk207_WeatheredSteel", (.035, .055, .075))
shader = steel.node_tree.nodes.get("Principled BSDF")
for filename, socket in [("diff.jpg", "Base Color"), ("rough.jpg", "Roughness")]:
    tex = steel.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(LAB / "sources/environment169/blue_metal_plate" / filename))
    if filename == "rough.jpg":
        tex.image.colorspace_settings.name = "Non-Color"
    steel.node_tree.links.new(tex.outputs["Color"], shader.inputs[socket])
tex = steel.node_tree.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(str(LAB / "sources/environment169/blue_metal_plate/nor_gl.jpg"))
tex.image.colorspace_settings.name = "Non-Color"
normal = steel.node_tree.nodes.new("ShaderNodeNormalMap")
normal.inputs["Strength"].default_value = .5
steel.node_tree.links.new(tex.outputs["Color"], normal.inputs["Color"])
steel.node_tree.links.new(normal.outputs["Normal"], shader.inputs["Normal"])
rubber = material("Kiosk207_CableRubber", (.008, .013, .015))
lights = [material("Kiosk207_Cyan", (.015, .65, .6), 2),
          material("Kiosk207_Amber", (.65, .18, .018), 2),
          material("Kiosk207_Violet", (.42, .035, .65), 2)]

# A real game illustration is used as screen content, not as a humanoid model.
# Bake only a luminance alpha mask; retain the original image unchanged.
image = bpy.data.images.load(str(REPO / "assets/ui/cyberware/cyberware_body_map_v1.png"))
image = image.copy()
pixels = np.empty(len(image.pixels), dtype=np.float32)
image.pixels.foreach_get(pixels)
rgba = pixels.reshape(-1, 4)
rgba[:, 3] = np.clip(rgba[:, :3].max(axis=1) * 2.4 - .08, 0, .8)
image.pixels.foreach_set(pixels)
image.update()
image.filepath_raw = str(OUT / "medical_hologram.png")
image.file_format = "PNG"
image.save()
image.pack()
holo = material("Holo207_Medical", (.05, .8, .8), 1.3, .75)
tex = holo.node_tree.nodes.new("ShaderNodeTexImage")
tex.image = image
shader = holo.node_tree.nodes.get("Principled BSDF")
for output, socket in [("Color", "Base Color"), ("Color", "Emission Color"), ("Alpha", "Alpha")]:
    holo.node_tree.links.new(tex.outputs[output], shader.inputs[socket])
glass = material("Holo207_DataGlass", (.02, .18, .24), .6, .18)


def attach(obj, root):
    bpy.context.view_layer.update()
    world = obj.matrix_world.copy()
    obj.parent = root
    obj.matrix_world = world
    return obj


def box(name, point, size, mat, root):
    bpy.ops.mesh.primitive_cube_add(size=1, location=point)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("Manufactured edges", "BEVEL")
    bevel.width = .018
    bevel.segments = 3
    return attach(obj, root)


def panel(name, point, width, height, mat, root):
    x, y, z = point
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x-width/2, y, z-height/2), (x+width/2, y, z-height/2),
                     (x+width/2, y, z+height/2), (x-width/2, y, z+height/2)], [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new()
    for i, value in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = value
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(mat)
    return attach(obj, root)


def label(text, point, mat, root, size=.16):
    curve = bpy.data.curves.new("Kiosk207_Type", "FONT")
    curve.body = text
    curve.size = size
    curve.align_x = "CENTER"
    curve.extrude = .001
    obj = bpy.data.objects.new("Kiosk207_Sign", curve)
    bpy.context.collection.objects.link(obj)
    obj.location = point
    obj.rotation_euler.x = math.pi/2
    obj.data.materials.append(mat)
    return attach(obj, root)


def cable(points, root):
    curve = bpy.data.curves.new("Kiosk207_Cable", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = .018
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points)-1)
    for point, position in zip(spline.bezier_points, points):
        point.co = position
        point.handle_left_type = point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new("Kiosk207_ExposedCable", curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(rubber)
    return attach(obj, root)


def template(pack, wanted):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(LAB / "sources/environment169" / pack / (pack+"_1k.gltf")))
    imported = set(bpy.data.objects)-before
    source = next(o for o in imported if o.type == "MESH" and o.name == wanted)
    mesh = source.data.copy()
    mesh.transform(source.matrix_world)
    points = [v.co for v in mesh.vertices]
    lo = Vector([min(p[i] for p in points) for i in range(3)])
    hi = Vector([max(p[i] for p in points) for i in range(3)])
    mesh.transform(Matrix.Translation(-(lo+hi)/2))
    for obj in imported:
        bpy.data.objects.remove(obj, do_unlink=True)
    return mesh, hi-lo


vent = template("modular_airduct_rectangular_01", "modular_airduct_rectangular_01_vent_01")
pipe = template("modular_industrial_pipes_01", "modular_industrial_pipes_01_pipe01")


def part(source, point, length, root, upright=False):
    mesh, dims = source
    obj = bpy.data.objects.new("Kiosk207_AuthoredServicePart", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = point
    obj.scale = Vector((1, 1, 1)) * (length/max(dims))
    if upright:
        axis = Vector((1, 0, 0)) if dims.x == max(dims) else Vector((0, 1, 0)) if dims.y == max(dims) else Vector((0, 0, 1))
        obj.rotation_euler = axis.rotation_difference(Vector((0, 0, 1))).to_euler()
    return attach(obj, root)


removed = []
for obj in list(bpy.data.objects):
    if obj.name.startswith("Market195"):
        removed.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
records = []
names = ["market_nmid", "market_nw", "market_ne", "market_sw",
         "market_smid", "market_se", "market_east"]
for index, name in enumerate(names):
    root = bpy.data.objects["Occludable_"+name]
    body = next(o for o in root.children_recursive if o.name.startswith("PBR_Facade_"))
    points = [body.matrix_world @ Vector(p) for p in body.bound_box]
    lo = Vector([min(p[i] for p in points) for i in range(3)])
    hi = Vector([max(p[i] for p in points) for i in range(3)])
    x, y = (lo.x+hi.x)/2, (lo.y+hi.y)/2
    width, depth = min(hi.x-lo.x-.3, 5.5), min(hi.y-lo.y-.3, 3.4)
    front = y-depth/2
    light = lights[index % 3]
    # Narrow rigid service cap with cut corners, instead of cloth spanning a stall.
    d, cut = 1.25, .22
    outline = [(-width/2+cut, 0), (width/2-cut, 0), (width/2, cut),
               (width/2, d-cut), (width/2-cut, d), (-width/2+cut, d),
               (-width/2, d-cut), (-width/2, cut)]
    mesh = bpy.data.meshes.new("Kiosk207_ArmoredCap")
    verts = [(x+a, front+b, 2.38+.12*b/d+dz) for dz in [0, .09] for a, b in outline]
    faces = [tuple(range(7, -1, -1)), tuple(range(8, 16))]
    faces += [(i, (i+1)%8, (i+1)%8+8, i+8) for i in range(8)]
    mesh.from_pydata(verts, [], faces)
    uv = mesh.uv_layers.new()
    for face in mesh.polygons:
        for li in face.loop_indices:
            p = mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv = (p.x, p.y)
    obj = bpy.data.objects.new("Kiosk207_ArmoredCap", mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(steel)
    attach(obj, root)
    for dx in [-width/2+.18, width/2-.18]:
        box("Kiosk207_Support", (x+dx, front+1.02, 1.54), (.12, .16, 1.68), steel, root)
    box("Kiosk207_LuminousValance", (x, front+.018, 2.41), (width-.46, .025, .025), light, root)
    label(["CHROME // CLINIC", "CELL // EXCHANGE", "BLACK // CIRCUIT"][index % 3],
          (x, front-.04, 2.18), light, root)
    part(vent, (x-width*.28, front+.62, 2.65), .7, root)
    cable([(x-width*.3, front+.9, .8), (x-width*.35, front+.95, 1.45),
           (x-width*.25, front+.95, 2.3)], root)
    if index % 3 == 0:
        panel("Holo207_Medical", (x, y+.45, 2.4), .95, 1.45, holo, root)
        box("Scan207_Medical", (x, y+.43, 1.68), (.9, .012, .012), light, root)
        box("Kiosk207_ProjectionBase", (x, y+.45, 1.52), (1.05, .32, .12), steel, root)
    elif index % 3 == 1:
        for dx in [-.25, .25]:
            part(pipe, (x+dx, y+.5, 1.6), 1.65, root, upright=True)
        panel("Holo207_Energy", (x, y+.12, 2.05), 1.3, .75, glass, root)
        for j in range(4):
            box("Kiosk207_EnergyReadout", (x-.42+j*.28, y+.1, 2.05), (.045, .015, .22+j*.06), light, root)
    else:
        panel("Holo207_Data", (x, y+.35, 2.02), 1.5, .8, glass, root)
        for j in range(5):
            box("Kiosk207_DataTrace", (x, y+.32, 1.78+j*.12), (.9-j*.1, .015, .012), light, root)
        label("NEURAL // ACCESS", (x, y+.3, 2.52), light, root, .12)
    records.append({"counter": name, "type": ["cyberclinic", "power station", "neural terminal"][index % 3]})

# A real in-world electronic advertisement replaces another blank facade patch.
root = bpy.data.objects["Occludable_east_building"]
panel("Holo207_NetworkAdvert", (17, 2.88, 1.9), 3.6, 1.45, glass, root)
label("GHOST / NET", (17, 2.84, 2.05), lights[2], root, .36)
label("YOUR CITY. YOUR SIGNAL.", (17, 2.84, 1.67), lights[0], root, .15)
for z in [1.18, 2.63]:
    box("Kiosk207_AdvertBorder", (17, 2.85, z), (3.6, .02, .018), lights[0], root)
box("Scan207_Network", (17, 2.83, 1.2), (3.5, .012, .012), lights[2], root)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "environment.blend"))
bpy.ops.export_scene.gltf(filepath=str(OUT / "environment.glb"), export_format="GLB", use_selection=True)
(OUT / "kiosks.json").write_text(json.dumps({
    "kiosks": records, "removed_cloth_structure_parts": len(removed),
    "sources": ["retained Poly Haven vent/pipe/metal textures", "existing game cyberware illustration"],
    "scope": "same showcase map; cosmetic structures, not production tactical rule changes"}, indent=2))
print("CYBER_KIOSKS207_READY", len(records), flush=True)
