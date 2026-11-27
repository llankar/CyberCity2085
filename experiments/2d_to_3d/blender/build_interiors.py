"""Place shared wall, laboratory, clinic and freight assets on surveyed interiors."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

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
    partition_cap = make_material("Partition cap", (.047,.030,.018,1) if ruined else (.017,.032,.044,1), .28,.79)
    ballast = make_material("Track bed", (.047,.052,.053,1), .07,.93)
    rail = make_material("Rail steel", (.18,.22,.25,1), .82,.42)
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
        if kind == "pipe":
            radius = row["width"] * gw/cw/2
            points = [Vector((px*gw/cw-gw/2, gh/2-py*gh/ch, radius+.07))
                      for px,py in row["points"]]
            for start,end in zip(points,points[1:]):
                axis = end-start
                bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius,
                                                    depth=axis.length, location=(start+end)/2)
                segment = bpy.context.object
                segment.name = identifier
                segment.rotation_euler = axis.to_track_quat("Z","Y").to_euler()
                segment.data.materials.append(steel)
                segment.parent = group
            for point in points:
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=point)
                joint = bpy.context.object
                joint.name = identifier + " elbow"
                joint.data.materials.append(steel)
                joint.parent = group
            continue
        if kind in {"partition", "rubble"}:
            outline = manifest["outlines"][identifier]
            outline = [(px*gw/cw-gw/2, gh/2-py*gh/ch) for px,py in outline]
            if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outline, outline[1:]+outline[:1])) < 0:
                outline.reverse()
            count = len(outline)
            faces = [tuple(reversed(range(count))), tuple(range(count,2*count))]
            faces.extend((i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count))
            mesh = bpy.data.meshes.new(identifier)
            top = [(x,y,1.50 if kind == "partition" else .42+(i%4)*.15)
                   for i,(x,y) in enumerate(outline)]
            mesh.from_pydata([(x,y,0) for x,y in outline]+top, [], faces)
            mesh.materials.append(steel)
            mesh.materials.append(partition_cap)
            mesh.polygons[1].material_index = 1
            partition = bpy.data.objects.new(identifier, mesh)
            bpy.context.collection.objects.link(partition)
            partition.parent = group
            continue
        if "rect" in row:
            x1,y1,x2,y2 = row["rect"]
        else:
            xs,ys = zip(*row["polygon"])
            x1,y1,x2,y2 = min(xs),min(ys),max(xs),max(ys)
        w,d = (x2-x1)*gw/cw, (y2-y1)*gh/ch
        x,y = (x1+x2)*gw/(2*cw)-gw/2, gh/2-(y1+y2)*gh/(2*ch)
        vertical = d > w
        length, breadth = (d,w) if vertical else (w,d)
        yaw = math.pi/2 if vertical else 0
        if kind == "bed":
            build_bed(group, x, y, w, d, steel, linen, trim)
        elif kind == "rack":
            build_rack(group, x, y, w, d, steel, trim)
        elif kind == "track":
            box(identifier+" ballast", (x,y,.012), (w/2,d/2,.012), ballast).parent = group
            count = max(1, round(w/.40))
            for i in range(count):
                offset = ((i+.5)/count-.5)*w
                box(identifier+" sleeper", (x+offset,y,.046),
                    (.077,d*.34,.025), partition_cap).parent = group
            for side in (-1,1):
                box(identifier+" rail", (x,y+side*d*.23,.104),
                    (w/2,.044,.032), rail).parent = group
        elif kind == "column":
            box(identifier+" base", (x,y,.10), (w*.49,d*.49,.10), ballast).parent = group
            box(identifier+" upright", (x,y,.88), (w*.39,d*.39,.80), steel).parent = group
            box(identifier+" cap", (x,y,1.67), (w*.45,d*.45,.09), partition_cap).parent = group
            if name == "city_transit_metro_interchange":
                facing = -1 if y > 0 else 1
                front = y + facing*d*.39
                box(identifier+" inset equipment panel", (x,front,1.01),
                    (w*.28,d*.025,.45), partition_cap).parent = group
                box(identifier+" station marker", (x,front+facing*d*.031,1.32),
                    (w*.23,d*.012,.075), screen).parent = group
                for level in range(3):
                    box(identifier+" cooling louver", (x,front+facing*d*.031,.77+level*.08),
                        (w*.19,d*.012,.016), trim).parent = group
        elif kind == "stair":
            direction = 1 if y > 0 else -1
            for i in range(8):
                offset = ((i+.5)/8-.5)*d*direction
                height = (i+1)*.13
                box(identifier+" tread", (x,y+offset,height/2),
                    (w*.47,d/16,height/2), steel).parent = group
        elif kind == "stall":
            market = library / "market_southeast_display/shop.glb"
            place(market, group, (x,y,0), (length*.98,breadth*.98,1.8), yaw=yaw, merge=True)
        elif kind == "fountain":
            for label, z, depth, scale, material in (
                ("basin", .18, .36, .47, steel), ("water", .36, .025, .39, screen),
                ("fountain head", .58, .44, .14, trim),
            ):
                bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=depth, location=(x,y,z))
                piece = bpy.context.object
                piece.name = identifier + " " + label
                piece.scale = (w*scale, d*scale, 1)
                piece.data.materials.append(material)
                piece.parent = group
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
        elif kind == "barrier":
            box(identifier, (x,y,.24), (w*.49,d*.49,.24), steel).parent = group
            box(identifier+" coping", (x,y,.49), (w*.48,d*.48,.025), trim).parent = group
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

    if name == "city_transit_train_tunnel":
        # The two continuous tracks are visible in the source texture but have
        # no obstacle trace. Align the rails to the four painted running lines.
        tracks = ((.415,.465), (.551,.599))
        for track, (north, south) in enumerate(tracks, start=1):
            y_edges = [gh*(.5-fraction) for fraction in (north, south)]
            for index, y in enumerate(y_edges, start=1):
                box(f"Running rail {track}.{index}", (0,y,.081), (gw/2,.035,.026), rail)
            vertices, faces = [], []
            count = round(gw/.42)
            for index in range(count):
                fraction = (index+.5)/count
                # The lower track crosses two original maintenance walkways.
                if track == 2 and (.324 < fraction < .375 or .645 < fraction < .701):
                    continue
                x = gw*(fraction-.5)
                start = len(vertices)
                vertices.extend((x+dx,y,z) for z in (.008,.052)
                                for dx,y in ((-.065,y_edges[1]-.12),(.065,y_edges[1]-.12),
                                             (.065,y_edges[0]+.12),(-.065,y_edges[0]+.12)))
                faces.extend(tuple(start+i for i in face) for face in (
                    (3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)))
            sleepers = bpy.data.meshes.new(f"Track {track} sleeper bed")
            sleepers.from_pydata(vertices, [], faces)
            sleepers.materials.append(partition_cap)
            obj = bpy.data.objects.new(f"Track {track} sleeper bed", sleepers)
            bpy.context.collection.objects.link(obj)

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
