"""Place shared wall, laboratory, clinic and freight assets on surveyed interiors."""
import json
import math
from pathlib import Path
import sys

import bpy

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
from interior_batch import INTERIORS, MAPS, OUTPUT, fixtures
from create_hardsurface_crate import make_material
from interior_furniture import build_bed, build_rack
from library_placement import place, reset_library_cache


def build(name):
    reset_library_cache()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    survey, selected = fixtures(name)
    gw, gh = json.loads((MAPS / f"{name}.walls.json").read_text())["grid"]
    cw, ch = survey["canvas_size"]
    out = OUTPUT / name
    library = OUTPUT.parents[2] / "environment-library/assets"
    labs = {
        "pod": OUTPUT.parent / "blacksite339/shared_pods.glb",
        "crate": library / "cargo_crate274/model.glb",
        "machine": library / "industrial_service267/model.glb",
    }
    wall = library / "service_wall269_factory/model.glb"
    ruined = name.startswith("wasteland_")
    steel = make_material("Interior service steel", (.13,.19,.22,1), .5,.58)
    linen = make_material("Treatment linen", (.25,.22,.17,1) if ruined else (.48,.58,.60,1), 0,.85)
    trim = make_material("Equipment enamel", (.24,.15,.075,1) if ruined else (.05,.21,.28,1), .18,.65)
    for row in survey["walls"]:
        identifier = row["id"]
        kind = selected.get(identifier)
        if kind is None:
            continue
        x1,y1,x2,y2 = row["rect"]
        w,d = (x2-x1)*gw/cw, (y2-y1)*gh/ch
        x,y = (x1+x2)*gw/(2*cw)-gw/2, gh/2-(y1+y2)*gh/(2*ch)
        group = bpy.data.objects.new("Occludable_" + identifier, None)
        bpy.context.collection.objects.link(group)
        vertical = d > w
        length, breadth = (d,w) if vertical else (w,d)
        yaw = math.pi/2 if vertical else 0
        if kind == "bed":
            build_bed(group, x, y, w, d, steel, linen, trim)
        elif kind == "rack":
            build_rack(group, x, y, w, d, steel, trim)
        elif kind == "wall":
            count = max(1, round(length/2))
            span = length/count
            for i in range(count):
                offset = (i+.5)*span-length/2
                place(wall, group, (x if vertical else x+offset, y+offset if vertical else y, 0),
                      (span,breadth,1.7), yaw=yaw)
        else:
            place(labs[kind], group, (x,y,0), (length*.97,breadth*.97,1.7), yaw=yaw)

    floor = make_material("Original interior floor", (.13,.15,.17,1), .05,.84)
    nodes = floor.node_tree.nodes
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(out / "floor.png"))
    floor.node_tree.links.new(texture.outputs["Color"], nodes["Principled BSDF"].inputs["Base Color"])
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,-.025))
    bpy.context.object.scale = (gw/2,gh/2,1)
    bpy.context.object.data.materials.append(floor)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "environment.blend"))
    bpy.ops.export_scene.gltf(filepath=str(out / "environment.glb"), export_format="GLB")
    print("INTERIOR_EXPORTED", name, len(selected))


for name in sys.argv[sys.argv.index("--")+1:] or INTERIORS:
    if name not in INTERIORS:
        raise ValueError(f"Unconfigured interior: {name}")
    build(name)
