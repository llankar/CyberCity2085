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
from interior_furniture import (
    build_bed, build_containment_chamber, build_medical_scanner, build_rack, build_security_bay,
    build_checkpoint_fixture, build_industrial_fixture, build_safehouse_fixture, build_server_bank,
    build_facility_fixture,
)
from library_placement import place, reset_library_cache



def build_atrium_floor(geometry, floor, trim, grid, canvas):
    gw, gh = grid
    cw, ch = canvas

    def surface(label, polygons, levels, material):
        vertices, faces = [], []
        for polygon in polygons:
            first = len(vertices)
            vertices.extend((px*gw/cw-gw/2,gh/2-py*gh/ch,z) for (px,py),z in zip(polygon,levels))
            face = tuple(range(first,len(vertices)))
            if len(face) == 3:
                a,b,c = (Vector(vertices[index]) for index in face)
                if (b-a).cross(c-a).z < 0:
                    face = tuple(reversed(face))
            faces.append(face)
        mesh = bpy.data.meshes.new(label)
        mesh.from_pydata(vertices, [], faces)
        mesh.materials.append(material)
        uv = mesh.uv_layers.new()
        for loop in mesh.loops:
            x,y,_ = vertices[loop.vertex_index]
            uv.data[loop.index].uv = (x/gw+.5,y/gh+.5)
        bpy.context.collection.objects.link(bpy.data.objects.new(label, mesh))

    surface("Atrium upper floor", geometry["deck"], [-.025]*3, floor)
    surface("Atrium recessed level", geometry["street"], [-1.85]*3, floor)
    surface("Atrium shaft sides", [(a,b,b,a) for a,b in geometry["edges"]],
            [-.025,-.025,-1.85,-1.85], trim)


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
    metro = name == "city_transit_metro_interchange"
    steel = make_material("Interior service steel", (.038,.063,.075,1) if metro else (.13,.19,.22,1), .5,.68 if metro else .58)
    linen = make_material("Treatment linen", (.25,.22,.17,1) if ruined else (.48,.58,.60,1), 0,.85)
    trim = make_material("Equipment enamel", (.24,.15,.075,1) if ruined else (.05,.21,.28,1), .18,.65)
    partition_cap = make_material("Partition cap", (.047,.030,.018,1) if ruined else (.017,.032,.044,1), .28,.79)
    ballast = make_material("Track bed", (.014,.018,.020,1) if metro else (.047,.052,.053,1), .07,.93)
    sleeper_material = make_material("Carbon-stained sleepers", (.009,.014,.018,1), .02,.92) if metro else partition_cap
    rail = make_material("Rail steel", (.18,.22,.25,1), .82,.42)
    stair_nosing = make_material("Amber stair nosing", (.58,.29,.042,1), .29,.62) if (
        name in {"city_transit_metro_interchange", "cybercity_inner_13_warehouse_floor"}) else None
    upholstery = make_material("Lobby upholstery", (.16,.085,.045,1) if ruined else (.08,.20,.23,1), 0,.86)
    leaves = make_material("Indoor foliage", (.07,.19,.09,1), 0,.86)
    worktop = make_material("Brushed equipment worktop", (.055,.078,.090,1), .58,.63)
    console_glass = make_material("Console low-light display", (.018,.17,.22,1), .12,.40, .18)
    screen = make_material("Terminal display", (.035,.52,.67,1), .08,.32)
    shader = screen.node_tree.nodes["Principled BSDF"]
    shader.inputs["Emission Color"].default_value = (.035,.52,.67,1)
    shader.inputs["Emission Strength"].default_value = .4
    server_map = name in {
        "cybercity_inner_05_server_room", "cybercity_inner_15_data_vault", "city_interior_server_room",
    }
    server_housing = make_material("Server bank graphite", (.025,.041,.053,1), .59,.64) if server_map else None
    checkpoint = name == "city_industrial_security_checkpoint"
    warning = make_material("Checkpoint amber hardware", (.48,.24,.045,1), .55,.51) if checkpoint else None
    textured_partitions = name in {
        "city_interior_blacksite_lab", "city_interior_medical_clinic",
        "city_interior_safehouse", "city_interior_cyber_cafe", "city_industrial_service_tunnel",
        "cybercity_inner_05_server_room", "cybercity_inner_10_penthouse_atrium",
        "cybercity_inner_13_warehouse_floor",
    }
    partition_meshes = []
    for row in survey["walls"] + manifest.get("decorative", []):
        identifier = row["id"]
        kind = selected.get(identifier, row.get("model"))
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
            partition_height = .92 if identifier == "reception_counter" else 1.50
            top = [(x,y,partition_height if kind == "partition" else .42+(i%4)*.15)
                   for i,(x,y) in enumerate(outline)]
            mesh.from_pydata([(x,y,0) for x,y in outline]+top, [], faces)
            mesh.materials.append(steel)
            mesh.materials.append(partition_cap)
            mesh.polygons[1].material_index = 1
            if textured_partitions and kind == "partition":
                uv = mesh.uv_layers.new(name="Panel UV")
                for edge, face in enumerate(mesh.polygons[2:]):
                    start, end = outline[edge], outline[(edge+1) % count]
                    repeats = math.dist(start, end) / 1.7
                    for loop, coord in zip(face.loop_indices, (
                        (0, 0), (repeats, 0), (repeats, 1), (0, 1)
                    )):
                        uv.data[loop].uv = coord
                partition_meshes.append(mesh)
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
        if name == "city_interior_blacksite_lab" and identifier == "central_chamber":
            wall_finish = bpy.data.materials["Wall269 worn steel PBR"]
            build_containment_chamber(group, x, y, w, d, wall_finish, partition_cap, screen)
        elif name == "city_interior_medical_clinic" and identifier == "northeast_scanner":
            build_medical_scanner(group, x, y, w, d, linen, partition_cap, screen)
        elif checkpoint and identifier.startswith(("barrier_", "scanner_", "security_booth_")):
            build_checkpoint_fixture(group, identifier, x, y, w, d, steel, partition_cap, screen, warning)
        elif kind in {"floor_generator", "safehouse_generator"}:
            place(library / "industrial_generator265/model.glb", group, (x,y,0),
                  (length*.94,breadth*.94,1.12), yaw=yaw)
        elif kind in {"gym_weights", "bath_sink", "bath_shower", "bath_tub", "bath_toilet", "toilet_stalls", "stove"}:
            build_safehouse_fixture(group, kind, x, y, w, d, steel, linen, rail)
        elif kind in {"workbench", "drums", "service_valve"}:
            build_industrial_fixture(group, kind, x, y, w, d, steel, partition_cap, rail)
        elif kind == "low_vent":
            box("Decorative vent plinth", (x,y,.047), (w*.47,d*.47,.047), partition_cap).parent = group
            place(library / "roof_twin_fan/optimized.glb", group, (x,y,.09),
                  (length*.92,breadth*.92,.22), yaw=yaw, merge=True)
        elif kind == "vent_fan":
            box("Vent fan deck", (x,y,.34), (w*.48,d*.47,.34), partition_cap).parent = group
            place(library / "roof_twin_fan/optimized.glb", group, (x,y,.68),
                  (length*.92,breadth*.92,.38), yaw=yaw, merge=True)
        elif kind in {"meeting_table", "inspection_pit", "spare_tires", "command_console", "command_wall"}:
            build_facility_fixture(group, kind, x, y, w, d, steel, partition_cap, screen)
        elif kind == "security_bay":
            build_security_bay(group, identifier, x, y, w, d, wall, labs["crate"],
                               steel, partition_cap, screen)
        elif kind == "bed":
            build_bed(group, x, y, w, d, steel, linen, trim)
        elif server_map and identifier != "west_storage" and (
            identifier.startswith(("rack_", "server_")) or identifier.endswith(("_rack", "_server"))
        ):
            build_server_bank(group, x, y, w, d, server_housing, steel, screen)
        elif kind == "rack":
            build_rack(group, x, y, w, d, steel, trim)
        elif kind == "track":
            box(identifier+" ballast", (x,y,.012), (w/2,d/2,.012), ballast).parent = group
            count = max(1, round(w/.40))
            sleepers = []
            for i in range(count):
                offset = ((i+.5)/count-.5)*w
                sleeper = box(identifier+" sleeper", (x+offset,y,.046),
                              (.077,d*.34,.025), sleeper_material)
                sleeper.parent = group
                sleepers.append(sleeper)
            bpy.ops.object.select_all(action="DESELECT")
            for sleeper in sleepers:
                sleeper.select_set(True)
            bpy.context.view_layer.objects.active = sleepers[0]
            bpy.ops.object.convert(target="MESH")
            if len(sleepers) > 1:
                bpy.ops.object.join()
            bpy.context.object.name = identifier + " sleeper bed"
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
                if stair_nosing is not None:
                    edge = y+offset-direction*d*.048
                    box(identifier+" tread nosing", (x,edge,height+.009),
                        (w*.45,d*.010,.009), stair_nosing, .004).parent = group
            if stair_nosing is not None:
                for side in (-1,1):
                    rail_x = x+side*w*.425
                    end_points = []
                    for step in (1,6):
                        rail_y = y+((step+.5)/8-.5)*d*direction
                        tread_z = (step+1)*.13
                        box(identifier+" handrail post", (rail_x,rail_y,tread_z+.27),
                            (.019,.019,.27), rail, .006).parent = group
                        end_points.append(Vector((rail_x,rail_y,tread_z+.54)))
                    start, end = end_points
                    axis = end-start
                    handrail = box(identifier+" handrail", (start+end)/2,
                                   (.024,.024,axis.length/2), rail, .006)
                    handrail.rotation_euler = axis.to_track_quat("Z", "Y").to_euler()
                    handrail.parent = group
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
            box(identifier+" worktop", (x,y,.72), (w*.48,d*.46,.065), worktop).parent = group
            for sx in (-1,1):
                for sy in (-1,1):
                    box(identifier+" leg", (x+w*sx*.34,y+d*sy*.32,.34),
                        (min(.053,w*.1),min(.053,d*.1),.34), steel).parent = group
            if kind == "console":
                box(identifier+" terminal", (x,y+d*.19,.98), (w*.36,.074,.22), steel).parent = group
                box(identifier+" display bezel", (x,y+d*.19-.077,.99),
                    (w*.33,.025,.177), partition_cap).parent = group
                box(identifier+" display", (x,y+d*.19-.105,.99),
                    (w*.275,.013,.117), console_glass).parent = group
                box(identifier+" input tray", (x,y-d*.15,.796),
                    (w*.28,d*.13,.016), partition_cap).parent = group
                for index in range(4):
                    offset = (index-1.5)*w*.105
                    box(identifier+" control key", (x+offset,y-d*.15,.815),
                        (w*.039,d*.052,.009), rail,.004).parent = group
        elif kind == "wall":
            count = max(1, round(length/2))
            span = length/count
            for i in range(count):
                offset = (i+.5)*span-length/2
                place(wall, group, (x if vertical else x+offset, y+offset if vertical else y, 0),
                      (span,breadth,1.7), yaw=yaw)
        else:
            place(labs[kind], group, (x,y,0), (length*.97,breadth*.97,1.7), yaw=yaw)

    if partition_meshes:
        finish_name = "Wall269 worn steel PBR"
        if finish_name not in bpy.data.materials:
            # Some interiors use traced partitions throughout and have no
            # rectangular wall modules to bring in the shared material.
            retained = set(bpy.data.objects)
            bpy.ops.import_scene.gltf(filepath=str(wall))
            for obj in set(bpy.data.objects) - retained:
                bpy.data.objects.remove(obj, do_unlink=True)
        wall_finish = bpy.data.materials[finish_name]
        for mesh in partition_meshes:
            mesh.materials[0] = wall_finish

    if name == "city_transit_train_tunnel":
        # The two continuous tracks are visible in the source texture but have
        # no obstacle trace. Align the rails to the four painted running lines.
        tracks = ((.415,.465), (.551,.599))
        crossing_spans = ((.324,.375), (.645,.701))
        for track, (north, south) in enumerate(tracks, start=1):
            y_edges = [gh*(.5-fraction) for fraction in (north, south)]
            for index, y in enumerate(y_edges, start=1):
                box(f"Running rail {track}.{index}", (0,y,.081), (gw/2,.035,.026), rail)
            vertices, faces = [], []
            count = round(gw/.42)
            for index in range(count):
                fraction = (index+.5)/count
                # The lower track crosses two original maintenance walkways.
                if track == 2 and any(left < fraction < right for left,right in crossing_spans):
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

        crossing_north, crossing_south = .514, .624
        crossing_y = gh*(.5-(crossing_north+crossing_south)/2)
        crossing_depth = gh*(crossing_south-crossing_north)
        for index, (left,right) in enumerate(crossing_spans, start=1):
            width = gw*(right-left)
            x = gw*((left+right)/2-.5)
            label = f"Maintenance crossing {index}"
            box(label+" deck", (x,crossing_y,.085),
                (width*.48,crossing_depth*.49,.042), partition_cap)
            for side in (-1,1):
                box(label+" curb", (x+side*width*.438,crossing_y,.16),
                    (width*.035,crossing_depth*.49,.035), rail)
            for tread in range(8):
                offset = ((tread+.5)/8-.5)*crossing_depth
                box(label+" raised grip", (x,crossing_y+offset,.129),
                    (width*.38,.022,.01), steel, .006)

    floor = make_material("Original interior floor", (.13,.15,.17,1), .05,.84)
    nodes = floor.node_tree.nodes
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(out / "floor.png"))
    floor.node_tree.links.new(texture.outputs["Color"], nodes["Principled BSDF"].inputs["Base Color"])
    if manifest.get("floor_geometry"):
        build_atrium_floor(manifest["floor_geometry"], floor, partition_cap, (gw,gh), (cw,ch))
    else:
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
