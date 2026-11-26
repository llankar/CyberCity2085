"""Build the three original billboard avenues using shared facade modules."""
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
AVENUES = (
    "city_exterior_billboard_avenue",
    "cybercity_street_15_billboard_avenue",
    "cybercity_street_16_billboard_avenue",
)


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

    building_rows = [row for row in survey["walls"] if "block" in row["id"] or row["id"] in {
        "ne_corner", "west_mid", "south_mid"
    }]
    roof = textured_material("Original rooftop artwork", MAPS / f"{name}.png", .8)
    for i, row in enumerate(building_rows):
        identifier = row["id"]
        x1, y1, x2, y2 = row["rect"]
        x, y = (x1 + x2) * gw / (2*cw) - gw/2, gh/2 - (y1 + y2) * gh / (2*ch)
        w, d = (x2-x1)*gw/cw, (y2-y1)*gh/ch
        height = 3.0 + .65*(i % 3)
        group = bpy.data.objects.new("Occludable_" + identifier, None)
        bpy.context.collection.objects.link(group)
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
    print("BILLBOARD_AVENUE_EXPORTED", name, len(building_rows))


for avenue in AVENUES:
    build(avenue)
