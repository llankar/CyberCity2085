"""Place shared wall, laboratory, clinic and freight assets on surveyed interiors."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
from interior_batch import AGED_CONCRETE_INTERIORS, INTERIORS, MAPS, OUTPUT
from create_hardsurface_crate import box, make_material
from interior_furniture import (
    build_bed, build_containment_chamber, build_medical_scanner, build_rack, build_security_bay,
    build_checkpoint_fixture, build_industrial_fixture, build_safehouse_fixture, build_server_bank,
    build_diagnostic_bench, build_facility_fixture, build_floor_grate, build_operating_table,
    merge_fixture_meshes,
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
    if ruined and name.endswith("_detention_block"):
        interlock = make_material("Wasteland cell red indicator", (.42,.055,.018,1), .15,.61,.36)
    metro = name == "city_transit_metro_interchange"
    steel = make_material("Interior service steel", (.038,.063,.075,1) if metro else (.13,.19,.22,1), .5,.68 if metro else .58)
    linen = make_material("Treatment linen", (.25,.22,.17,1) if ruined else (.48,.58,.60,1), 0,.85)
    trim = make_material("Equipment enamel", (.24,.15,.075,1) if ruined else (.05,.21,.28,1), .18,.65)
    ruined_clinic = name.endswith("_ruined_clinic")
    emergency_medbay = name.endswith("_emergency_medbay")
    salvaged_medical = ruined_clinic or emergency_medbay
    if salvaged_medical:
        stretcher_frame = make_material("Oxidized stretcher steel", (.048,.061,.056,1), .46,.76)
        stretcher_pad = make_material("Worn stretcher vinyl", (.032,.063,.057,1), 0,.89)
    partition_cap = make_material("Partition cap", (.047,.030,.018,1) if ruined else (.017,.032,.044,1), .28,.79)
    ballast = make_material("Track bed", (.014,.018,.020,1) if metro else (.047,.052,.053,1), .07,.93)
    sleeper_material = make_material("Carbon-stained sleepers", (.009,.014,.018,1), .02,.92) if metro else partition_cap
    rail = make_material("Rail steel", (.18,.22,.25,1), .82,.42)
    stair_nosing = make_material("Amber stair nosing", (.58,.29,.042,1), .29,.62) if (
        name in {"city_transit_metro_interchange", "cybercity_inner_13_warehouse_floor"}) else None
    upholstery = make_material("Lobby upholstery", (.16,.085,.045,1) if ruined else (.08,.20,.23,1), 0,.86)
    leaves = make_material("Indoor foliage", (.07,.19,.09,1), 0,.86)
    worktop = make_material("Brushed equipment worktop", (.055,.078,.090,1), .58,.63)
    cafe = name.endswith("_cyber_cafe")
    if cafe:
        cafe_worktop = make_material("Original cafe worktop artwork", (.2,.2,.2,1), 0,.83)
        nodes = cafe_worktop.node_tree.nodes
        artwork = nodes.new("ShaderNodeTexImage")
        artwork.image = bpy.data.images.load(str(MAPS / f"{name}.png"))
        cafe_worktop.node_tree.links.new(artwork.outputs["Color"], nodes["Principled BSDF"].inputs["Base Color"])
    console_glass = make_material("Console low-light display", (.018,.17,.22,1), .12,.40, .18)
    screen = make_material("Terminal display", (.035,.52,.67,1), .08,.32)
    shader = screen.node_tree.nodes["Principled BSDF"]
    shader.inputs["Emission Color"].default_value = (.035,.52,.67,1)
    shader.inputs["Emission Strength"].default_value = .4
    server_map = name in {
        "cybercity_inner_05_server_room", "cybercity_inner_15_data_vault", "city_interior_server_room",
        "city_industrial_data_vault",
    }
    bunker = name.endswith("_bunker_command_post")
    if bunker:
        bunker_canvas = make_material("Bunker worn sandbag canvas", (.15,.105,.060,1), 0,.93)
        bunker_display = make_material("Bunker dim terminal glass", (.018,.095,.075,1), .12,.49,.035)
    underground_market = name.endswith("_underground_market")
    apartment_shelter = name.endswith("_apartment_shelter")
    if apartment_shelter:
        shelter_wood = make_material("Shelter worn plank wood", (.14,.086,.045,1), 0,.86)
        shelter_iron = make_material("Shelter oxidized angle iron", (.055,.042,.031,1), .40,.81)
        bedding_canvas = make_material("Shelter faded canvas", (.092,.085,.061,1), 0,.94)
        bedding_blankets = (
            make_material("Shelter olive blanket", (.063,.071,.043,1), 0,.96),
            make_material("Shelter faded teal blanket", (.034,.063,.065,1), 0,.94),
            make_material("Shelter patched brown blanket", (.079,.055,.041,1), 0,.96),
        )
    looted_vault = name.endswith("_looted_vault")
    collapsed_tunnel = name.endswith("_collapsed_tunnel")
    if collapsed_tunnel:
        slab_top = make_material("Original tunnel slab artwork", (.15,.14,.12,1), 0,.93)
        artwork = slab_top.node_tree.nodes.new("ShaderNodeTexImage")
        artwork.image = bpy.data.images.load(str(MAPS / f"{name}.png"))
        slab_top.node_tree.links.new(artwork.outputs["Color"],
                                     slab_top.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    if looted_vault:
        steel = make_material("Vault oxidized steel", (.051,.045,.037,1), .46,.78)
        vault_marker = make_material("Vault red marker lens", (.48,.025,.012,1), .14,.48,.35)
    exposed_concrete_walls = bunker or apartment_shelter or looted_vault or name.endswith(
        ("_collapsed_tunnel", "_ruined_clinic", "_maintenance_depot")
    )
    concrete_partitions = name.endswith(AGED_CONCRETE_INTERIORS)
    if concrete_partitions:
        aged_concrete = make_material("Wasteland aged concrete", (.28,.25,.21,1), 0,.88)
        nodes = aged_concrete.node_tree.nodes
        links = aged_concrete.node_tree.links
        concrete = OUTPUT.parents[2] / "sources/environment169/concrete_wall_001"
        for filename, socket in (("diff.jpg", "Base Color"), ("rough.jpg", "Roughness")):
            layer = nodes.new("ShaderNodeTexImage")
            image_path = out / "aged_concrete_diffuse.jpg" if socket == "Base Color" else concrete / filename
            layer.image = bpy.data.images.load(str(image_path))
            if socket == "Roughness":
                layer.image.colorspace_settings.name = "Non-Color"
            links.new(layer.outputs["Color"], nodes["Principled BSDF"].inputs[socket])
        normal_texture = nodes.new("ShaderNodeTexImage")
        normal_texture.image = bpy.data.images.load(str(concrete / "nor_gl.jpg"))
        normal_texture.image.colorspace_settings.name = "Non-Color"
        normal = nodes.new("ShaderNodeNormalMap")
        normal.inputs["Strength"].default_value = .8
        links.new(normal_texture.outputs["Color"], normal.inputs["Color"])
        links.new(normal.outputs["Normal"], nodes["Principled BSDF"].inputs["Normal"])
    if underground_market:
        stall_canvas = []
        for color in ("olive", "rust", "tan"):
            material = make_material(f"Original market canvas {color}", (.08,.06,.04,1), 0,.95)
            nodes = material.node_tree.nodes
            texture = nodes.new("ShaderNodeTexImage")
            texture.image = bpy.data.images.load(str(out / f"stall_canvas_{color}.png"))
            material.node_tree.links.new(texture.outputs["Color"], nodes["Principled BSDF"].inputs["Base Color"])
            stall_canvas.append(material)
    relay_room = name.endswith("_data_relay_room")
    server_housing = make_material("Server bank graphite", (.025,.041,.053,1), .59,.64) if server_map or bunker or relay_room else None
    checkpoint = name == "city_industrial_security_checkpoint"
    warning = make_material("Checkpoint amber hardware", (.48,.24,.045,1), .55,.51) if checkpoint else None
    depot = name.endswith("_maintenance_depot")
    depot_warning = make_material("Depot worn yellow paint", (.65,.34,.035,1), .16,.71) if depot else None
    textured_partitions = metro or emergency_medbay or relay_room or server_map or name in {
        "city_interior_blacksite_lab", "city_interior_medical_clinic",
        "city_interior_safehouse", "city_interior_cyber_cafe", "city_industrial_service_tunnel",
        "cybercity_inner_10_penthouse_atrium",
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
        if kind == "cell_front":
            (left,row_y),(right,_) = row["points"]
            row_prefix = {
                "north_cells_front": "north_cell_",
                "south_cells_front": "south_cell_",
                "cells_n_front": "n_cell_",
                "cells_s_front": "s_cell_",
            }[identifier]
            dividers = sorted(
                wall["points"][0][0] for wall in survey["walls"]
                if wall["id"].startswith(row_prefix)
                and wall["id"][len(row_prefix):].isdigit()
            )
            boundaries = [left, *dividers, right]
            depth = row["width"]*gh/ch
            y = gh/2-row_y*gh/ch
            for bay, (start, end) in enumerate(zip(boundaries, boundaries[1:])):
                span = (end-start)*gw/cw
                x = (start+end)*gw/cw/2-gw/2
                for z in (.09,1.43):
                    box("Cell front steel frame", (x,y,z), (span/2,depth*.44,.09),steel,.018).parent = group
                for offset in (-.36,.36):
                    box("Cell front armor panel", (x+offset*span,y,.76),
                        (span*.13,depth*.39,.65),partition_cap,.02).parent = group
                for bar in (-2,-1,0,1,2):
                    box("Cell front vertical bar", (x+bar*span*.083,y,.76),
                        (.035,depth*.12,.64),steel,.008).parent = group
                if not ruined or bay in (1,3):
                    box("Cell interlock indicator", (x,y,1.43), (span*.13,depth*.47,.026),
                        interlock if ruined else screen,.008).parent = group
            merge_fixture_meshes(group, "Detention cell frontage")
            continue
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
                if name.endswith("_collapsed_tunnel") and axis.length > radius*4:
                    for fraction in (.18,.82):
                        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius*1.23,
                                                            depth=radius*.45, location=start.lerp(end,fraction))
                        collar = bpy.context.object
                        collar.name = identifier + " bolted coupling"
                        collar.rotation_euler = segment.rotation_euler
                        collar.data.materials.append(partition_cap)
                        collar.parent = group
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
            faces = [tuple(reversed(range(count)))]
            if kind == "rubble":
                triangles = tessellate_polygon([[Vector((x,y,0)) for x,y in outline]])
                faces.extend(tuple(index+count for index in triangle) for triangle in triangles)
            else:
                faces.append(tuple(range(count,2*count)))
            top_face_count = len(faces)
            faces.extend((i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count))
            mesh = bpy.data.meshes.new(identifier)
            partition_height = .92 if identifier == "reception_counter" else 1.50
            top = [(x,y,partition_height if kind == "partition" else .42+(i%4)*.15)
                   for i,(x,y) in enumerate(outline)]
            mesh.from_pydata([(x,y,0) for x,y in outline]+top, [], faces)
            concrete_rubble = concrete_partitions and kind == "rubble"
            concrete_top = concrete_rubble or (concrete_partitions and exposed_concrete_walls)
            projected_slab = collapsed_tunnel and kind == "rubble"
            mesh.materials.append(aged_concrete if concrete_partitions else steel)
            if projected_slab or not concrete_top:
                mesh.materials.append(slab_top if projected_slab else partition_cap)
                for face in mesh.polygons[1:top_face_count]:
                    face.material_index = 1
            if concrete_partitions or (textured_partitions and kind == "partition"):
                uv = mesh.uv_layers.new(name="Panel UV")
                if concrete_top:
                    for face in mesh.polygons[:top_face_count]:
                        for loop in face.loop_indices:
                            x,y,_ = mesh.vertices[mesh.loops[loop].vertex_index].co
                            uv.data[loop].uv = ((x/gw+.5,y/gh+.5) if projected_slab and face.index > 0
                                                 else (x/1.7,y/1.7))
                u_start = 0
                for edge, face in enumerate(mesh.polygons[top_face_count:]):
                    start, end = outline[edge], outline[(edge+1) % count]
                    repeats = math.dist(start, end) / 1.7
                    upper_left = top[edge][2]/1.5 if concrete_rubble else 1
                    upper_right = top[(edge+1)%count][2]/1.5 if concrete_rubble else 1
                    for loop, coord in zip(face.loop_indices, (
                        (u_start, 0), (u_start+repeats, 0), (u_start+repeats, upper_right), (u_start, upper_left)
                    )):
                        uv.data[loop].uv = coord
                    if exposed_concrete_walls:
                        u_start += repeats
                if not concrete_partitions:
                    partition_meshes.append(mesh)
            partition = bpy.data.objects.new(identifier, mesh)
            bpy.context.collection.objects.link(partition)
            partition.parent = group
            if kind == "rubble" and collapsed_tunnel:
                # Seat exposed reinforcement along the longest break in each slab.
                edge = max(range(count), key=lambda i: math.dist(outline[i],outline[(i+1)%count]))
                start = Vector(top[edge])
                end = Vector(top[(edge+1)%count])
                center = sum((Vector(point) for point in top), Vector((0,0,0)))/count
                for fraction in (.26,.48,.70):
                    lip = start.lerp(end,fraction)
                    inset = lip.lerp(center,.07)
                    tip = inset.lerp(lip,2.45)
                    tip.z = inset.z+.085
                    bar = box("Tunnel exposed slab reinforcement", (inset+tip)/2,
                              ((tip-inset).length/2,.024,.024),steel,.008)
                    bar.rotation_euler = (tip-inset).to_track_quat("X","Z").to_euler()
                    bar.parent = group
            if bunker and identifier in {"central_wall_w", "central_wall_e"}:
                start, end = [Vector((px*gw/cw-gw/2, gh/2-py*gh/ch))
                              for px, py in row["points"][:2]]
                inward = 1 if identifier.endswith("_w") else -1
                conduit_x = start.x+inward*(row["width"]*gw/cw/2+.025)
                conduit = box("Bunker command wall conduit",
                              (conduit_x,(start.y+end.y)/2,1.16),
                              (.046,abs(end.y-start.y)*.455,.036),partition_cap,.013)
                conduit.parent = group
                for fraction in (.23,.52,.78):
                    box("Bunker command wall junction",
                        (conduit_x+inward*.024,start.y+(end.y-start.y)*fraction,1.16),
                        (.060,.081,.089),steel,.015).parent = group
                flank_points = [Vector((px*gw/cw-gw/2, gh/2-py*gh/ch))
                                for px, py in row["points"][-3:]]
                bags = []
                for start, end in zip(flank_points, flank_points[1:]):
                    run = end-start
                    bag_count = max(1, round(run.length/.38))
                    for index in range(bag_count):
                        center = start+run*((index+.5)/bag_count)
                        bag = box("Bunker sandbag", (*center,partition_height+.055),
                                  (run.length/bag_count*.465,min(.12,row["width"]*gh/ch*.40),.08),
                                  bunker_canvas,.054)
                        bag.rotation_euler.z = math.atan2(run.y,run.x)
                        bag.parent = group
                        bags.append(bag)
                merge_fixture_meshes(group, "Bunker flank sandbags", pieces=bags)
            if looted_vault and identifier.startswith("vault_wall_"):
                spine = [Vector((px*gw/cw-gw/2, gh/2-py*gh/ch)) for px, py in row["points"]]
                for first, second in zip(spine, spine[1:]):
                    segment = second-first
                    midpoint = (first+second)/2
                    cap = box("Vault ring armor cap", (*midpoint,partition_height+.023),
                              (segment.length*.46,row["width"]*gw/cw*.36,.028),
                              partition_cap,.011)
                    cap.rotation_euler.z = math.atan2(segment.y,segment.x)
                    cap.parent = group
                edges = [(a,b) for a,b in zip(outline, outline[1:]+outline[:1])
                         if math.dist(a,b) > .65]
                start, end = min(edges, key=lambda edge: math.hypot(
                    (edge[0][0]+edge[1][0])/2, (edge[0][1]+edge[1][1])/2))
                dx, dy = end[0]-start[0], end[1]-start[1]
                span = math.hypot(dx,dy)
                for offset in (.014,.046):
                    midpoint = ((start[0]+end[0])/2+dy/span*offset,
                                (start[1]+end[1])/2-dx/span*offset, .85)
                    is_lens = offset > .02
                    marker = box("Vault ring marker lens" if is_lens else "Vault ring marker housing",
                                 midpoint, (.12,.02,.057) if is_lens else (.17,.034,.09),
                                 vault_marker if is_lens else steel,.009)
                    marker.rotation_euler.z = math.atan2(dy,dx)
                    marker.parent = group
            if name == "city_industrial_data_vault" and identifier.startswith("north_barrier_"):
                start, end = max(zip(outline,outline[1:]+outline[:1]), key=lambda edge: math.dist(*edge))
                dx,dy = end[0]-start[0],end[1]-start[1]
                length = math.hypot(dx,dy)
                midpoint = ((start[0]+end[0])/2+dy/length*.025,
                            (start[1]+end[1])/2-dx/length*.025, 1.04)
                strip = box("Vault barrier status light", midpoint,
                            (min(.42,length*.22),.035,.043),screen,.01)
                strip.rotation_euler.z = math.atan2(dy,dx)
                strip.parent = group
            if kind == "rubble":
                center_x = sum(x for x,y in outline)/count
                center_y = sum(y for x,y in outline)/count
                direction = 1 if identifier.endswith("_n") else -1
                for offset, tilt in ((-.48,.22),(.38,-.31)):
                    beam = box("Exposed collapsed tunnel support",
                               (center_x,center_y+offset,.65),(.90,.075,.095),steel,.02)
                    beam.rotation_euler = (0,tilt,direction*.37)
                    beam.parent = group
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
            scanner_enamel = make_material("Scanner blue steel enamel", (.16,.22,.29,1), .48,.46)
            scanner_glass = make_material("Scanner cyan glass", (.014,.24,.33,1), .12,.33)
            build_medical_scanner(group, x, y, w, d, scanner_enamel, partition_cap, scanner_glass)
        elif checkpoint and identifier.startswith(("barrier_", "scanner_", "security_booth_")):
            build_checkpoint_fixture(group, identifier, x, y, w, d, steel, partition_cap, screen, warning)
        elif emergency_medbay and (identifier.endswith("_desk") or kind == "console"):
            build_facility_fixture(group, "medbay_care_desk", x, y, w, d,
                                   stretcher_frame, partition_cap, console_glass)
        elif emergency_medbay and kind == "table":
            build_facility_fixture(group, "medbay_supply_table", x, y, w, d,
                                   stretcher_frame, partition_cap, linen)
        elif emergency_medbay and kind == "machine":
            build_diagnostic_bench(group, x, y, w, d, partition_cap, stretcher_frame, console_glass,
                                   telemetry=identifier == "central_machine")
        elif kind == "machine" and depot:
            place(labs[kind], group, (x,y,.11), (length*.82,breadth*.62,.82), yaw=yaw)
            for offset in (-.31, 0, .31):
                along = length*offset
                center = (x,y+along,.067) if vertical else (x+along,y,.067)
                size = (breadth*.415,length*.033,.067) if vertical else (length*.033,breadth*.415,.067)
                box("Depot machine bed crossmember", center, size, partition_cap,.015).parent = group
            for side in (-1, 1):
                offset = side*breadth*.40
                rail_center = (x+offset,y,.10) if vertical else (x,y+offset,.10)
                rail_size = (breadth*.044,length*.46,.10) if vertical else (length*.46,breadth*.044,.10)
                box("Depot machine guide rail", rail_center, rail_size, rail,.023).parent = group
            for side in (-1, 1):
                offset = side*length*.445
                stop_center = (x,y+offset,.17) if vertical else (x+offset,y,.17)
                stop_size = (breadth*.43,length*.035,.11) if vertical else (length*.035,breadth*.43,.11)
                box("Depot machine carriage stop", stop_center, stop_size, partition_cap,.016).parent = group
                marker_center = (*stop_center[:2], .29)
                marker_size = (stop_size[0]*.72,stop_size[1]*.64,.014)
                box("Depot machine stop marker", marker_center, marker_size, depot_warning,.006).parent = group
        elif kind in {"floor_generator", "safehouse_generator"}:
            place(library / "industrial_generator265/model.glb", group, (x,y,0),
                  (length*.94,breadth*.94,1.12), yaw=yaw)
        elif kind in {"gym_weights", "bath_sink", "bath_shower", "bath_tub", "bath_toilet", "toilet_stalls", "stove"}:
            build_safehouse_fixture(group, kind, x, y, w, d, steel, linen, rail)
        elif kind in {"workbench", "drums", "service_valve"}:
            build_industrial_fixture(group, kind, x, y, w, d, steel, partition_cap, rail,
                                     depot=depot)
        elif kind == "floor_grate":
            build_floor_grate(group, x, y, w, d, partition_cap, rail, steel)
        elif kind == "low_vent":
            box("Decorative vent plinth", (x,y,.047), (w*.47,d*.47,.047), partition_cap).parent = group
            place(library / "roof_twin_fan/optimized.glb", group, (x,y,.09),
                  (length*.92,breadth*.92,.22), yaw=yaw, merge=True)
        elif kind == "vent_fan":
            box("Vent fan deck", (x,y,.34), (w*.48,d*.47,.34), partition_cap).parent = group
            place(library / "roof_twin_fan/optimized.glb", group, (x,y,.68),
                  (length*.92,breadth*.92,.38), yaw=yaw, merge=True)
        elif kind == "vault_display":
            angle = {"table_nw": .36, "table_ne": -.36, "table_sw": -.36, "table_se": .36}.get(identifier, 0)
            if angle:
                build_facility_fixture(group, kind, x, y, w*.86, d*.67, steel, partition_cap, screen)
                pivot = Vector((x,y,0))
                group.matrix_world = Matrix.Translation(pivot) @ Matrix.Rotation(angle,4,"Z") @ Matrix.Translation(-pivot)
            else:
                build_facility_fixture(group, kind, x, y, w, d, steel, partition_cap, screen)
        elif relay_room and kind == "data_core":
            build_facility_fixture(group, "relay_core", x, y, w, d, server_housing, partition_cap, console_glass)
        elif kind in {"meeting_table", "inspection_pit", "spare_tires", "command_console", "command_wall", "command_table", "vault_core", "clinic_reception", "shelter_kitchen", "records_desk", "data_core"}:
            fixture_steel = stretcher_frame if kind == "clinic_reception" and ruined_clinic else steel
            fixture_display = depot_warning if kind == "inspection_pit" else bunker_display if bunker else screen
            build_facility_fixture(group, kind, x, y, w, d, fixture_steel, partition_cap, fixture_display)
            if bunker and identifier == "command_console":
                box("Bunker terminal bridge", (x,y+d*.29,1.06),
                    (w*.43,d*.12,.17),partition_cap,.023).parent = group
                for bay in range(5):
                    offset = (bay-2)*w*.163
                    box("Bunker upright terminal", (x+offset,y+d*.16,1.12),
                        (w*.066,d*.023,.104),bunker_display,.009).parent = group
            if kind == "command_table":
                artwork = make_material("Original bunker operations map", (.4,.4,.4,1), 0,.72)
                texture = artwork.node_tree.nodes.new("ShaderNodeTexImage")
                texture.image = bpy.data.images.load(str(out / "operations_map.png"))
                shader = artwork.node_tree.nodes["Principled BSDF"]
                artwork.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
                hx, hy = (w*.305,d*.345) if d > w else (w*.345,d*.305)
                bpy.ops.mesh.primitive_plane_add(size=2, location=(x,y,.844))
                map_surface = bpy.context.object
                map_surface.name = "Original operations map artwork"
                map_surface.scale = (hx,hy,1)
                map_surface.data.materials.append(artwork)
                map_surface.parent = group
                for sx in (-1, 1):
                    station_x = x+sx*w*.405
                    box("Operations map control housing", (station_x,y,.899),
                        (w*.047,d*.20,.061),partition_cap,.018).parent = group
                    box("Operations map control display", (station_x,y+d*.078,.961),
                        (w*.033,d*.070,.008),bunker_display,.005).parent = group
                    for key in (-1, 0, 1):
                        box("Operations map command key",
                            (station_x+key*w*.023,y-d*.070,.965),
                            (w*.008,d*.026,.011),steel,.005).parent = group
                    for sy in (-1, 1):
                        box("Operations map corner clamp", (x+sx*hx*.94,y+sy*hy*.93,.858),
                            (min(.09,hx*.15),min(.065,hy*.15),.022),partition_cap,.010).parent = group
        elif kind == "security_bay":
            build_security_bay(group, identifier, x, y, w, d, wall, labs["crate"],
                               steel, partition_cap, screen)
        elif kind == "rail_service_room":
            inward = -1 if identifier.startswith("north") else 1
            box("Rail service room rear wall", (x,y-inward*d*.45,.56),
                (w*.47,d*.047,.56),steel,.02).parent = group
            for side in (-1,1):
                box("Rail service room side wall", (x+side*w*.43,y,.56),
                    (w*.055,d*.43,.56),steel,.02).parent = group
                box("Rail service room skirting", (x+side*w*.366,y,.14),
                    (w*.019,d*.415,.105),partition_cap,.012).parent = group
                box("Rail service room conduit", (x+side*w*.366,y,.87),
                    (w*.019,d*.39,.023),rail,.008).parent = group
            box("Rail service desk", (x,y-inward*d*.25,.36),
                (w*.34,d*.14,.36),partition_cap,.025).parent = group
            box("Rail service display", (x-w*.18,y-inward*d*.25,.75),
                (w*.115,d*.081,.03),console_glass,.009).parent = group
            box("Rail service switchgear", (x+w*.20,y-inward*d*.28,.82),
                (w*.108,d*.075,.09),steel,.009).parent = group
            for slot in (-1, 0, 1):
                box("Rail service switchgear vent", (x+w*(.20+slot*.053),y-inward*d*.28,.912),
                    (w*.012,d*.046,.006),partition_cap,.004).parent = group
            box("Rail service threshold", (x,y+inward*d*.43,.021),
                (w*.33,d*.035,.022),rail,.008).parent = group
            merge_fixture_meshes(group, "Open rail service room")
        elif kind == "rail_signal":
            panel_y = y+(.13 if identifier.startswith("south") else -.13)*d
            box("Rail signal armored cabinet", (x,y,.31),
                (w*.45,d*.43,.31), partition_cap,.032).parent = group
            box("Rail signal panel bezel", (x,panel_y,.64),
                (w*.39,d*.24,.029), steel,.016).parent = group
            for side in (-1,1):
                box("Rail signal indicator", (x+side*w*.17,panel_y,.676),
                    (w*.105,d*.135,.009), rail if identifier.endswith("2") else screen,
                    .006).parent = group
            merge_fixture_meshes(group, "Trackside signal cabinet")
        elif kind == "diagnostic_bench":
            build_diagnostic_bench(group, x, y, w, d, partition_cap, steel, screen)
        elif kind == "operating_table":
            build_operating_table(group, x, y, w, d, partition_cap, steel, screen)
        elif kind == "bed":
            shelter_beds = ("bed_ne1", "bed_ne2", "bed_ne3")
            if apartment_shelter and identifier in shelter_beds:
                blanket = bedding_blankets[shelter_beds.index(identifier)]
                build_bed(group, x, y, w, d, steel, bedding_canvas, blanket, floor_bedding=True)
            else:
                privacy_side = {"bed_ww": -1, "bed_e": 1}.get(identifier, 0) if emergency_medbay else 0
                build_bed(group, x, y, w, d, stretcher_frame if salvaged_medical else steel, linen,
                          stretcher_pad if salvaged_medical else trim, stretcher=salvaged_medical,
                          privacy_side=privacy_side,
                          intensive_care=emergency_medbay and identifier == "bed_center")
        elif (relay_room and kind in {"relay_server", "rack"}) or (bunker and identifier in {"north_servers_w", "north_servers_e"}) or (server_map and (
            identifier.startswith(("rack_", "server_", "north_server_")) or identifier.endswith(("_rack", "_server"))
        )):
            build_server_bank(group, x, y, w, d, server_housing, steel, screen,
                              vented_lids=relay_room)
        elif apartment_shelter and kind == "rack":
            build_rack(group, x, y, w, d, shelter_iron, shelter_wood)
        elif kind == "rack":
            build_rack(group, x, y, w, d, steel, trim, records=name.endswith("_police_records"))
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
            if name == "city_transit_train_tunnel":
                for side in (-1, 1):
                    box("Tunnel column steel edge", (x+side*w*.387,y,.90),
                        (w*.043,d*.405,.76), partition_cap,.018).parent = group
                track_face = y-math.copysign(d*.404,y)
                box("Tunnel column lower armor", (x,track_face,.38),
                    (w*.34,d*.037,.23), partition_cap,.022).parent = group
                box("Tunnel column upper brace", (x,track_face,1.41),
                    (w*.34,d*.037,.11), rail,.018).parent = group
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
            if underground_market:
                box("Salvage market counter", (x,y,.39), (w*.45,d*.44,.39), partition_cap).parent = group
                for index, (dx,dy) in enumerate(((-.27,.20),(.03,-.18),(.29,.14))):
                    box("Salvage display bin", (x+w*dx,y+d*dy,.84),
                        (w*.115,d*.115,.064), steel if index == 1 else trim,.016).parent = group
                if identifier not in {"stall_center_e", "stall_sc", "south_stall_mid", "south_stall_far"}:
                    for dx in (-.42,.42):
                        for dy in (-.41,.41):
                            box("Salvage canopy upright", (x+w*dx,y+d*dy,.89),
                                (.036,.036,.89), steel,.008).parent = group
                    eaves = [(-.44,-.43),(.44,-.43),(.44,.43),(-.44,.43)]
                    vertices = [(x+w*dx,y+d*dy,1.78) for dx,dy in eaves] + [(x+w*.07,y,1.98)]
                    canopy = bpy.data.meshes.new("Patched market canopy")
                    canopy.from_pydata(vertices, [], [(i,(i+1)%4,4) for i in range(4)])
                    coords = ((0,0),(1,0),(1,1),(0,1),(.58,.5))
                    uv = canopy.uv_layers.new()
                    for loop in canopy.loops:
                        uv.data[loop.index].uv = coords[loop.vertex_index]
                    canopy.materials.append(stall_canvas[sum(map(ord,identifier))%len(stall_canvas)])
                    cloth = bpy.data.objects.new(canopy.name,canopy)
                    bpy.context.collection.objects.link(cloth)
                    cloth.parent = group
                # Bake the individual bevels before merging the stall. Keep
                # each footprint in its own group for the Godot cutaway.
                merge_fixture_meshes(group, "Salvage market stall")
                continue
            market = library / "market_southeast_display/shop.glb"
            place(market, group, (x,y,0), (length*.98,breadth*.98,1.8), yaw=yaw, merge=True)
        elif kind == "fountain":
            water = make_material("Atrium blue water", (.013,.12,.19,1), .20,.25,.10)
            box(identifier+" stone plinth", (x,y,.135), (w*.49,d*.49,.135), partition_cap).parent = group
            box(identifier+" inset water", (x,y,.282), (w*.406,d*.406,.015), water,.01).parent = group
            for side in (-1,1):
                box(identifier+" long coping", (x+side*w*.455,y,.327),
                    (w*.042,d*.49,.054), rail,.014).parent = group
                box(identifier+" short coping", (x,y+side*d*.455,.327),
                    (w*.414,d*.042,.054), rail,.014).parent = group
                box(identifier+" submerged light", (x+side*w*.344,y,.305),
                    (.015,d*.35,.009), console_glass,.004).parent = group
            box(identifier+" central jet housing", (x,y,.38), (w*.115,d*.115,.10), steel).parent = group
            bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=6,
                major_radius=min(w,d)*.18, minor_radius=.012, location=(x,y,.304))
            ripple = bpy.context.object
            ripple.name = identifier+" ripple"
            ripple.data.materials.append(console_glass)
            ripple.parent = group
            for frame, spread in ((1,.85),(20,1.22),(40,.85)):
                ripple.scale = (spread,spread,1)
                ripple.keyframe_insert(data_path="scale", frame=frame)
            ripple.animation_data.action.name = "AtriumWaterRipple"
        elif kind == "sofa" and apartment_shelter:
            build_facility_fixture(group, "shelter_sofa", x, y, w, d,
                                   shelter_iron, bedding_canvas, bedding_blankets[0])
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
        elif looted_vault and identifier == "sw_utility":
            box("Looted cabinet back", (x,y+d*.42,.68), (w*.45,d*.045,.68),steel).parent = group
            for side in (-1, 1):
                box("Looted cabinet side", (x+side*w*.42,y,.68),
                    (w*.035,d*.44,.68),steel).parent = group
            for height in (.12,.47,.82,1.34):
                box("Looted cabinet shelf", (x,y,height),
                    (w*.44,d*.44,.027),partition_cap).parent = group
            box("Abandoned cabinet bin", (x-w*.16,y+d*.11,.59),
                (w*.17,d*.23,.09),trim,.021).parent = group
            merge_fixture_meshes(group, "Looted open utility cabinet")
        elif apartment_shelter and identifier == "west_cabinet":
            build_facility_fixture(group, "shelter_pantry", x, y, w, d,
                                   shelter_wood, shelter_iron, bedding_canvas)
        elif kind == "cabinet":
            box(identifier, (x,y,.78), (w*.46,d*.44,.78), steel).parent = group
            for level in (.42,.73,1.04,1.35):
                box(identifier+" panel", (x,y-d*.45,level),
                    (w*.39,.026,.10), trim).parent = group
                box(identifier+" status", (x+w*.26,y-d*.49,level),
                    (w*.06,.019,.021), screen).parent = group
        elif metro and identifier == "center_kiosk":
            corner_bevel = min(w,d)*.12
            box("Metro kiosk raised plinth", (x,y,.10), (w*.48,d*.46,.10),
                partition_cap,corner_bevel).parent = group
            box("Metro kiosk information counter", (x,y-d*.29,.51), (w*.42,d*.135,.31),
                steel,.06).parent = group
            for side in (-1, 1):
                box("Metro kiosk armored side", (x+side*w*.363,y,.65), (w*.072,d*.34,.49),
                    steel,.065).parent = group
            box("Metro kiosk rear service panel", (x,y+d*.34,.48), (w*.31,d*.071,.28),
                partition_cap,.055).parent = group
            box("Metro kiosk reader", (x,y-d*.30,.84), (w*.22,d*.061,.025),
                console_glass,.012).parent = group
            merge_fixture_meshes(group, "Metro information kiosk")
        elif metro and (kind == "table" or identifier.startswith("ticket_")):
            fixture = "metro_bench" if kind == "table" else "metro_ticket_machine"
            build_facility_fixture(group, fixture, x, y, w, d, steel, partition_cap, console_glass)
        elif apartment_shelter and kind == "table":
            build_facility_fixture(group, "shelter_table", x, y, w, d, shelter_wood, shelter_iron, screen)
        elif looted_vault and kind == "table":
            build_facility_fixture(group, "vault_looters_table", x, y, w, d,
                                   steel, partition_cap, rail)
        elif relay_room and kind in {"table", "console"}:
            build_facility_fixture(group, "relay_console", x, y, w, d,
                                   server_housing, partition_cap, console_glass)
        elif kind in {"table","console"}:
            desktop = box(identifier+" worktop", (x,y,.72), (w*.48,d*.46,.065), worktop)
            desktop.parent = group
            if cafe:
                mesh = desktop.data
                mesh.materials.append(cafe_worktop)
                uv = mesh.uv_layers.active
                for face in mesh.polygons:
                    if face.normal.z < .9:
                        continue
                    face.material_index = 1
                    for index in face.loop_indices:
                        vertex = mesh.vertices[mesh.loops[index].vertex_index].co
                        uv.data[index].uv = ((x+vertex.x)/gw+.5, (y+vertex.y)/gh+.5)
            for sx in (-1,1):
                for sy in (-1,1):
                    box(identifier+" leg", (x+w*sx*.34,y+d*sy*.32,.34),
                        (min(.053,w*.1),min(.053,d*.1),.34), steel).parent = group
            if kind == "console":
                display_y = y+d*.19
                cafe_station = cafe
                display_z = 1.12 if cafe_station else .99
                if cafe_station:
                    box(identifier+" monitor foot", (x,display_y,.800),
                        (w*.22,min(.11,d*.16),.017),steel,.010).parent = group
                    box(identifier+" monitor stand", (x,display_y,.901),
                        (w*.053,.038,.111),steel,.010).parent = group
                box(identifier+" terminal", (x,display_y,display_z),
                    (w*.36,.052 if cafe_station else .074,.18 if cafe_station else .22),steel).parent = group
                bezel_y = display_y-(.055 if cafe_station else .077)
                box(identifier+" display bezel", (x,bezel_y,display_z),
                    (w*.33,.025,.177),partition_cap).parent = group
                box(identifier+" display", (x,bezel_y-.028,display_z),
                    (w*.275,.013,.117),console_glass).parent = group
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
            if name.endswith("_abandoned_safehouse") and identifier in {"north_wall", "south_wall"}:
                north = identifier == "north_wall"
                opening_centers = (168,369,591,842) if north else (122,487,822)
                inner_face = y-d/2-.045 if north else y+d/2+.045
                timber = make_material("Salvaged shelter timber", (.26,.145,.071,1), 0,.91)
                for center in opening_centers:
                    opening_x = center*gw/cw-gw/2
                    box("Boarded opening recess", (opening_x,inner_face,1.03),
                        (.94,.028,.43), partition_cap,.025).parent = group
                    for z, slope in ((.81,.15),(1.03,-.22),(1.26,.12)):
                        board_y = inner_face+(-.04 if north else .04)
                        board = box("Shelter nailed timber board", (opening_x,board_y,z),
                                    (1.01,.035,.064), timber,.016)
                        board.rotation_euler.y = slope
                        board.parent = group
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

    if relay_room:
        partitions = {row["id"]: row for row in survey["walls"]}
        for side in ("west", "east"):
            north = partitions[f"{side}_partition_n"]["points"][-1]
            south = partitions[f"{side}_partition_s"]["points"][0]
            x = (north[0]+south[0])*gw/(2*cw)-gw/2
            y = gh/2-(north[1]+south[1])*gh/(2*ch)
            half_span = (south[1]-north[1])*gh/(2*ch)-.20
            box(f"Relay {side} doorway threshold", (x,y,.008),
                (.17,half_span,.022),partition_cap,.009)
            for edge in (-1,1):
                box(f"Relay {side} threshold grip", (x+edge*.11,y,.032),
                    (.016,half_span*.92,.008),rail,.004)

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
