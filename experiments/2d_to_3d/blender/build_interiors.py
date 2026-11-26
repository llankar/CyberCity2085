"""Place shared wall, laboratory, clinic and freight assets on surveyed interiors."""
import json
import math
from pathlib import Path
import sys

import bpy

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
from interior_batch import INTERIORS, MAPS, OUTPUT
from create_hardsurface_crate import box, make_material
from interior_furniture import build_bed, build_rack
from library_placement import place, reset_library_cache


def build(name):
    reset_library_cache()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    survey = json.loads((MAPS / f"{name}.wall-traces.json").read_text())
    gw, gh = json.loads((MAPS / f"{name}.walls.json").read_text())["grid"]
    cw, ch = survey["canvas_size"]
    out = OUTPUT / name
    manifest = json.loads((out / "fixtures.json").read_text())
    selected = manifest["selected"]
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
    upholstery = make_material("Lobby upholstery", (.16,.085,.045,1) if ruined else (.08,.20,.23,1), 0,.86)
    leaves = make_material("Indoor foliage", (.07,.19,.09,1), 0,.86)
    screen = make_material("Terminal display", (.035,.52,.67,1), .08,.32)
    shader = screen.node_tree.nodes["Principled BSDF"]
    shader.inputs["Emission Color"].default_value = (.035,.52,.67,1)
    shader.inputs["Emission Strength"].default_value = .4
    for row in survey["walls"]:
        identifier = row["id"]
        kind = selected.get(identifier)
        if kind is None:
            continue
        group = bpy.data.objects.new("Occludable_" + identifier, None)
        bpy.context.collection.objects.link(group)
        if kind == "partition":
            outline = manifest["outlines"][identifier]
            outline = [(px*gw/cw-gw/2, gh/2-py*gh/ch) for px,py in outline]
            if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outline, outline[1:]+outline[:1])) < 0:
                outline.reverse()
            count = len(outline)
            faces = [tuple(reversed(range(count))), tuple(range(count,2*count))]
            faces.extend((i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count))
            mesh = bpy.data.meshes.new(identifier)
            mesh.from_pydata([(x,y,z) for z in (0,1.50) for x,y in outline], [], faces)
            mesh.materials.append(steel)
            mesh.materials.append(trim)
            mesh.polygons[1].material_index = 1
            partition = bpy.data.objects.new(identifier, mesh)
            bpy.context.collection.objects.link(partition)
            partition.parent = group
            continue
        x1,y1,x2,y2 = row["rect"]
        w,d = (x2-x1)*gw/cw, (y2-y1)*gh/ch
        x,y = (x1+x2)*gw/(2*cw)-gw/2, gh/2-(y1+y2)*gh/(2*ch)
        vertical = d > w
        length, breadth = (d,w) if vertical else (w,d)
        yaw = math.pi/2 if vertical else 0
        if kind == "bed":
            build_bed(group, x, y, w, d, steel, linen, trim)
        elif kind == "rack":
            build_rack(group, x, y, w, d, steel, trim)
        elif kind == "sofa":
            box(identifier+" frame", (x,y,.18), (w*.47,d*.46,.16), steel).parent = group
            box(identifier+" cushions", (x,y,.37), (w*.43,d*.39,.088), upholstery).parent = group
            back = (x+w*.37,y,.55) if vertical else (x,y+d*.37,.55)
            size = (w*.085,d*.43,.23) if vertical else (w*.43,d*.085,.23)
            box(identifier+" back", back, size, upholstery).parent = group
        elif kind == "planter":
            box(identifier+" vessel", (x,y,.20), (w*.46,d*.46,.20), steel).parent = group
            for offset in (-.28,0,.28):
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(
                    x+(0 if vertical else offset*w), y+(offset*d if vertical else 0), .52
                ))
                shrub = bpy.context.object
                shrub.name = identifier+" foliage"
                shrub.scale = (min(w*.23,.38),min(d*.23,.38),.25)
                shrub.data.materials.append(leaves)
                shrub.parent = group
        elif kind == "gate":
            for side in (-1,1):
                box(identifier+" post", (x+side*w*.33,y,.48),
                    (w*.13,d*.42,.48), steel).parent = group
            box(identifier+" rail", (x,y,.72), (w*.31,.024,.028), trim).parent = group
            box(identifier+" indicator", (x+w*.33,y,.984),
                (w*.10,d*.17,.025), screen).parent = group
        elif kind == "cabinet":
            box(identifier, (x,y,.78), (w*.46,d*.44,.78), steel).parent = group
            for level in (.42,.73,1.04,1.35):
                box(identifier+" panel", (x,y-d*.45,level),
                    (w*.39,.026,.10), trim).parent = group
                box(identifier+" status", (x+w*.26,y-d*.49,level),
                    (w*.06,.019,.021), screen).parent = group
        elif kind in {"table","console"}:
            box(identifier+" worktop", (x,y,.72), (w*.48,d*.46,.065), trim).parent = group
            for sx in (-1,1):
                for sy in (-1,1):
                    box(identifier+" leg", (x+w*sx*.34,y+d*sy*.32,.34),
                        (min(.053,w*.1),min(.053,d*.1),.34), steel).parent = group
            if kind == "console":
                box(identifier+" terminal", (x,y+d*.19,.98), (w*.36,.074,.22), steel).parent = group
                box(identifier+" display", (x,y+d*.19-.08,.99),
                    (w*.31,.018,.16), screen).parent = group
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
