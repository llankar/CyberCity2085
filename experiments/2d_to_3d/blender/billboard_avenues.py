"""Build original urban streets using shared facade and street furniture modules."""
import json
import math
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place, reset_library_cache

LAB = Path("E:/CyberCity2085-3d-lab")
MAPS = Path(__file__).resolve().parents[3] / "assets/maps"
BUILDING_EXCEPTIONS = {
    "ne_corner", "west_mid", "south_mid", "south_corner", "west_north",
    "west_south", "east_north", "east_mid", "east_south", "far_northwest",
    "far_northeast", "southwest_annex",
}


def textured_material(name, image, roughness):
    material = make_material(name, (.1, .1, .1, 1), .1, roughness)
    nodes = material.node_tree.nodes
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(image))
    material.node_tree.links.new(texture.outputs["Color"], nodes["Principled BSDF"].inputs["Base Color"])
    return material


def build(name):
    reset_library_cache()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    out = LAB / "generated/phase2/billboard_avenues" / name
    survey = json.loads((MAPS / f"{name}.wall-traces.json").read_text())
    gw, gh = json.loads((MAPS / f"{name}.walls.json").read_text())["grid"]
    cw, ch = survey["canvas_size"]
    library = LAB / "environment-library/assets"
    wall = make_material("Dark ceramic cladding", (.055, .079, .104, 1), .33, .68)
    frame = make_material("Anodized frames", (.09, .14, .18, 1), .73, .39)
    palette = ((.025, .60, .73, 1), (.63, .039, .31, 1), (.88, .36, .043, 1))
    signs = []
    for i, color in enumerate(palette):
        sign = make_material(f"Billboard phosphor {i}", color, .12, .4)
        shader = sign.node_tree.nodes["Principled BSDF"]
        shader.inputs["Emission Color"].default_value = color
        shader.inputs["Emission Strength"].default_value = .65
        signs.append(sign)

    seat = make_material("Blue enamel seating", (.047, .19, .25, 1), .38, .52)
    gravel = make_material("Planted gravel", (.086, .079, .058, 1), .05, .93)
    foliage = make_material("Hardy street shrubs", (.095, .19, .075, 1), .03, .84)
    roof = textured_material("Original rooftop artwork", MAPS / f"{name}.png", .8)
    for i, row in enumerate(survey["walls"]):
        identifier = row["id"]
        x1, y1, x2, y2 = row["rect"]
        x, y = (x1 + x2) * gw / (2*cw) - gw/2, gh/2 - (y1 + y2) * gh / (2*ch)
        w, d = (x2-x1)*gw/cw, (y2-y1)*gh/ch
        height = 3.0 + .65*(i % 3)
        group = bpy.data.objects.new("Occludable_" + identifier, None)
        bpy.context.collection.objects.link(group)
        if identifier.startswith("car_"):
            vertical = d > w
            place(library / "derelict_suv275/model.glb", group, (x, y, 0),
                  (max(w, d)*.95, min(w, d)*.95, .92), yaw=math.pi/2 if vertical else 0)
            continue
        if identifier == "crate_mid":
            place(library / "cargo_crate274/model.glb", group, (x, y, 0), (w, d, .55))
            continue
        if identifier.startswith("utility_"):
            vertical = d > w
            place(library / "industrial_service267/model.glb", group, (x, y, 0),
                  (max(w, d), min(w, d), 1.3), yaw=math.pi/2 if vertical else 0)
            continue
        if identifier.startswith("bin_"):
            box(identifier, (x, y, .25), (w*.45, d*.45, .25), wall).parent = group
            box(identifier + " lid", (x, y, .51), (w*.49, d*.49, .035), frame).parent = group
            continue
        if identifier.endswith(("_sign", "_kiosk")):
            is_kiosk = identifier.endswith("_kiosk")
            height = 1.55 if is_kiosk else .95
            box(identifier + " plinth", (x, y, .11), (w*.49, d*.47, .11), frame).parent = group
            box(identifier, (x, y, height/2), (w*.42, d*.29, height/2), wall).parent = group
            direction = -1 if y > 0 else 1
            box(identifier + " screen", (x, y+direction*d*.30, height*.72),
                (w*.36, .03, height*.20), signs[i % len(signs)]).parent = group
            continue
        if any(kind in identifier for kind in ("bench", "planter", "barrier")):
            if "bench" in identifier:
                parts = [
                    ("seat", (x, y, .36), (w*.46, d*.30, .065), seat),
                    ("backrest", (x, y+d*.27, .54), (w*.46, .055, .19), seat),
                ]
                parts.extend(("support", (x+w*offset, y, .17), (.08, d*.24, .17), frame)
                             for offset in (-.33, .33))
            else:
                parts = [
                    ("base", (x, y, .16), (w*.49, d*.48, .16), wall),
                    ("rim", (x, y, .33), (w*.50, d*.49, .045), frame),
                ]
                if "planter" in identifier:
                    parts.append(("gravel", (x, y, .375), (w*.43, d*.40, .02), gravel))
                    for offset in (-.31, 0, .31):
                        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1,
                            location=(x+w*offset, y, .48+abs(offset)*.12))
                        shrub = bpy.context.object
                        shrub.name = identifier + " shrub"
                        shrub.scale = (w*.13, d*.30, .19)
                        shrub.data.materials.append(foliage)
                        shrub.parent = group
                else:
                    parts.append(("reflector", (x, y, .38), (w*.38, .04, .02), signs[2]))
            for label, position, half_size, material in parts:
                box(f"{identifier} {label}", position, half_size, material).parent = group
            continue
        if not any(part in identifier for part in ("block", "building", "_roof")) and identifier not in BUILDING_EXCEPTIONS:
            raise ValueError(f"No avenue model for {identifier}")
        shell = box(identifier, (x, y, height/2), (w/2, d/2, height/2), wall)
        shell.parent = group
        shell.data.materials.append(roof)
        uv = shell.data.uv_layers.active
        for face in shell.data.polygons:
            if face.normal.z < .9:
                continue
            face.material_index = 1
            for loop_index in face.loop_indices:
                p = shell.data.vertices[shell.data.loops[loop_index].vertex_index].co
                uv.data[loop_index].uv = ((x+p.x)/gw+.5, (y+p.y)/gh+.5)
        direction = -1 if y > 0 else 1
        front = y + direction*d/2
        angle = 0 if direction < 0 else math.pi
        for offset in (-.3, .3):
            place(library / "urban_facade280/window.glb", group,
                  (x+w*offset, front+direction*.04, .9), (min(1.65,w*.33), .28, 1.7), yaw=angle)
        if "billboard" not in name and i % 3 != 0:
            continue
        sign_width = min(w*.75, 4.2)
        for label, offset, thickness, depth, material in (
            ("housing", .10, .16, .42, frame),
            ("screen", .19, .035, .35, signs[i % len(signs)]),
            ("divider", .22, .019, .025, frame),
        ):
            panel = box(f"{identifier} billboard {label}", (x, front+direction*offset, height-.65),
                        (sign_width/2, thickness, depth), material)
            panel.parent = group

    floor = textured_material("Original avenue pavement", out / "floor.png", .84)
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -.025))
    bpy.context.object.scale = (gw/2, gh/2, 1)
    bpy.context.object.data.materials.append(floor)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "environment.blend"))
    bpy.ops.export_scene.gltf(filepath=str(out / "environment.glb"), export_format="GLB")
    print("BILLBOARD_AVENUE_EXPORTED", name, len(survey["walls"]))


maps = sys.argv[sys.argv.index("--") + 1:]
if not maps or any(Path(name).name != name for name in maps):
    raise ValueError("Pass one or more original map IDs after --")
for map_name in maps:
    build(map_name)
