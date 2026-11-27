"""Build original urban streets using shared facade and street furniture modules."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place, reset_library_cache
from loading_crane import build_crane
from shipping_container import build_container
from wasteland_outdoor import WastelandOutdoors
from industrial_forklift import build_forklift

LAB = Path("E:/CyberCity2085-3d-lab")
MAPS = Path(__file__).resolve().parents[3] / "assets/maps"
# Equipment footprints measured on the 960 x 540 original avenue art.
BILLBOARD_ROOF_FANS = {
    "north_east_block": ((550, 14, 591, 40),),
    "south_west_block": ((274, 416, 301, 463), (372, 445, 421, 498)),
}

# Both street variants share the same art and surveyed building footprints.
ALTERNATE_BILLBOARD_ROOF_FANS = {
    "nw_block": ((31, 65, 88, 91),),
    "north_block": ((251, 17, 286, 78),),
    "ne_block": ((577, 61, 632, 100),),
}
MARKET_02_ROOF_FANS = {
    "northeast_block": ((592, 18, 641, 49),),
    "north_east_block": ((892, 5, 929, 54),),
}
MARKET_07_08_ROOF_FANS = {
    "north_block": ((249, 34, 286, 94),),
    "ne_block": ((708, 44, 742, 86),),
    "west_mid_block": ((38, 240, 70, 298),),
}
ROOF_FANS_BY_MAP = {
    "city_exterior_billboard_avenue": BILLBOARD_ROOF_FANS,
    "cybercity_street_15_billboard_avenue": ALTERNATE_BILLBOARD_ROOF_FANS,
    "cybercity_street_16_billboard_avenue": ALTERNATE_BILLBOARD_ROOF_FANS,
    "cybercity_street_02_neon_market_alley": MARKET_02_ROOF_FANS,
    "cybercity_street_07_neon_market_alley": MARKET_07_08_ROOF_FANS,
    "cybercity_street_08_neon_market_alley": MARKET_07_08_ROOF_FANS,
}

BUILDING_EXCEPTIONS = {
    "ne_corner", "west_mid", "south_mid", "south_corner", "west_north",
    "west_south", "east_north", "east_mid", "east_south", "far_northwest",
    "far_northeast", "southwest_annex", "north_mid", "se_corner", "nw_tower",
    "west_middle", "east_middle",
    "sw_corner", "north_entry_w", "north_entry_e", "north_civic", "south_civic",
}
ROOFTOPS = {"city_exterior_rooftop_access", "city_rooftop_skybridge_spine"}


def textured_material(name, image, roughness):
    material = make_material(name, (.1, .1, .1, 1), .1, roughness)
    nodes = material.node_tree.nodes
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(image))
    material.node_tree.links.new(texture.outputs["Color"], nodes["Principled BSDF"].inputs["Base Color"])
    return material


def build_rooftop_ground(out, floor, grid, canvas, library):
    terrain = json.loads((out / "rooftop_terrain.json").read_text())
    gw,gh = grid
    cw,ch = canvas
    deck_z, street_z = -.025, -3.6

    def vertex(point, height):
        x,y = point
        return (x*gw/cw-gw/2, gh/2-y*gh/ch, height)

    for surface, height in (("deck",deck_z), ("street",street_z)):
        vertices, faces = [], []
        for triangle in terrain[surface]:
            first = len(vertices)
            vertices.extend(vertex(point,height) for point in triangle)
            a,b,c = vertices[-3:]
            winding = (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            faces.append((first,first+1,first+2) if winding > 0 else (first,first+2,first+1))
        mesh = bpy.data.meshes.new(surface)
        mesh.from_pydata(vertices, [], faces)
        mesh.materials.append(floor)
        uv = mesh.uv_layers.new()
        for loop in mesh.loops:
            x,y,_ = vertices[loop.vertex_index]
            uv.data[loop.index].uv = (x/gw+.5,y/gh+.5)
        bpy.context.collection.objects.link(bpy.data.objects.new("Rooftop "+surface,mesh))

    vertices, faces = [], []
    for a,b in terrain["edges"]:
        first = len(vertices)
        vertices.extend((vertex(a,street_z),vertex(b,street_z),vertex(b,deck_z),vertex(a,deck_z)))
        faces.append(tuple(range(first,first+4)))
    mesh = bpy.data.meshes.new("Canyon retaining walls")
    mesh.from_pydata(vertices, [], faces)
    retaining = make_material("Canyon retaining concrete", (.046,.062,.078,1), .15,.86)
    mesh.materials.append(retaining)
    bpy.context.collection.objects.link(bpy.data.objects.new("Rooftop canyon retaining walls",mesh))
    facade = bpy.data.objects.new("Canyon facade details", None)
    bpy.context.collection.objects.link(facade)
    rail = make_material("Facade floor divisions", (.027,.039,.050,1), .51,.57)
    window_asset = library / "urban_facade280/window.glb"
    for a,b in terrain["edges"]:
        ax,ay,_ = vertex(a,0)
        bx,by,_ = vertex(b,0)
        dx,dy = bx-ax,by-ay
        length = math.hypot(dx,dy)
        if length < .85:
            continue
        nx,ny = dy/length,-dx/length
        yaw = math.atan2(dy,dx)
        for height in (-2.46,-1.18):
            band = box("Canyon floor division", ((ax+bx)/2+nx*.037,(ay+by)/2+ny*.037,height),
                       (length/2,.044,.038), rail, .008)
            band.rotation_euler.z = yaw
            band.parent = facade
        if length < 1.65:
            continue
        bays = max(1, int(length/1.85))
        for index in range(bays):
            fraction = (index+.5)/bays
            x,y = ax+fraction*dx+nx*.035,ay+fraction*dy+ny*.035
            for height in (-2.22,-.98):
                place(window_asset, facade, (x,y,height), (min(1.38,length/bays*.73),.22,.72),
                      yaw=yaw, merge=True)



def build_freeway_deck(floor, wall, frame, grid, canvas, rail_rows):
    gw, gh = grid
    _, ch = canvas
    north, south = (gh/2-row*gh/ch for row in rail_rows)
    recess = gh/ch*11
    street_level, road_level = -1.78, -.025

    def pavement(label, high, low, height):
        mesh = bpy.data.meshes.new(label)
        mesh.from_pydata(
            [(-gw/2,low,height),(gw/2,low,height),(gw/2,high,height),(-gw/2,high,height)],
            [], [(0,1,2,3)],
        )
        mesh.materials.append(floor)
        uv = mesh.uv_layers.new()
        for loop in mesh.loops:
            x,y,_ = mesh.vertices[loop.vertex_index].co
            uv.data[loop.index].uv = (x/gw+.5,y/gh+.5)
        bpy.context.collection.objects.link(bpy.data.objects.new(label, mesh))

    pavement("Freeway main deck", north, south, road_level)
    pavement("North avenue pavement", gh/2, north+recess, road_level)
    pavement("South avenue pavement", south-recess, -gh/2, road_level)
    pavement("North under-deck strip", north+recess, north, street_level)
    pavement("South under-deck strip", south, south-recess, street_level)
    box("Freeway structural slab", (0,(north+south)/2,-.295),
        (gw/2,(north-south)/2,.27), wall,.035)
    for edge, side in ((north,1),(south,-1)):
        box("Freeway edge girder", (0,edge-side*.075,-.42),
            (gw/2,.10,.16), frame,.02)
        box("Freeway lower retaining wall", (0,edge+side*recess,-.90),
            (gw/2,.035,.88), wall,.02)
        for i in range(8):
            x = ((i+.5)/8-.5)*gw
            box("Freeway pier footing", (x,edge+side*.12,-1.66),
                (.32,.21,.12), frame,.025)
            box("Freeway pier shaft", (x,edge+side*.11,-1.075),
                (.19,.16,.50), wall,.018)
            box("Freeway pier bearing", (x,edge,-.60),
                (.33,.24,.083), frame,.02)



def build_freeway_ramps(floor, wall, grid, canvas, traces, rail_rows):
    gw, gh = grid
    cw, ch = canvas
    # Inner edges measured against the original overpass artwork, ordered
    # alongside the existing outer rail survey. Both variants use this footprint.
    inner_edges = {
        "ramp_outer_w": ((108,540),(129,466),(158,412),(201,369),(256,337),(332,301),(418,257)),
        "ramp_outer_e": ((552,212),(641,144),(686,111),(711,65),(714,30),(693,0)),
    }
    for identifier, inner in inner_edges.items():
        outer = [tuple(point) for point in traces[identifier]]
        outer_index = -1 if identifier.endswith("_w") else 0
        rail_row = rail_rows[1] if identifier.endswith("_w") else rail_rows[0]
        outer[outer_index] = (outer[outer_index][0],rail_row)
        outline = outer + list(reversed(inner))
        points = [Vector((px*gw/cw-gw/2,gh/2-py*gh/ch,0)) for px,py in outline]
        if sum(a.x*b.y-b.x*a.y for a,b in zip(points,points[1:]+points[:1])) < 0:
            points.reverse()
        count = len(points)
        top, bottom = -.012, -.42
        faces = list(tessellate_polygon([points]))
        top_count = len(faces)
        faces.extend(((i+1)%count,i,i+count,(i+1)%count+count) for i in range(count))
        mesh = bpy.data.meshes.new(identifier+" deck")
        mesh.from_pydata([(p.x,p.y,z) for z in (top,bottom) for p in points], [], faces)
        mesh.materials.append(floor)
        mesh.materials.append(wall)
        uv = mesh.uv_layers.new()
        for poly in mesh.polygons:
            poly.material_index = int(poly.index >= top_count)
            for loop in poly.loop_indices:
                x,y,_ = mesh.vertices[mesh.loops[loop].vertex_index].co
                uv.data[loop].uv = (x/gw+.5,y/gh+.5)
        name = "West feeder ramp deck" if identifier.endswith("_w") else "East feeder ramp deck"
        bpy.context.collection.objects.link(bpy.data.objects.new(name, mesh))


def build(name):
    reset_library_cache()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    out = LAB / "generated/phase2/billboard_avenues" / name
    survey = json.loads((MAPS / f"{name}.wall-traces.json").read_text())
    gw, gh = json.loads((MAPS / f"{name}.walls.json").read_text())["grid"]
    cw, ch = survey["canvas_size"]
    freeway = name.endswith("_elevated_freeway")
    deck_rails = {row["id"]: row["points"][0][1] for row in survey["walls"]
                  if row["id"] in {"highway_north_rail", "highway_south_rail"}}
    riot_square = name == "city_district_riot_square"
    civic = name in {"city_district_civic_center", "city_district_riot_square"} or name.endswith("_civic_plaza")
    industrial = name.endswith(("freight_yard", "industrial_district"))
    library = LAB / "environment-library/assets"
    wasteland = (WastelandOutdoors(library, (gw,gh), (cw,ch), city=name.startswith("wasteland_city_"),
                                   overpass=name.endswith("_collapsed_overpass"),
                                   wrecked_highway=name.endswith("_wrecked_highway"),
                                   trainyard=name.endswith("_rusted_trainyard"))
                 if name.startswith(("wasteland_outdoor_", "wasteland_city_")) else None)
    wall = make_material("Dark ceramic cladding", (.055, .079, .104, 1), .33, .68)
    civic_surface = textured_material(
        "Civic weathered concrete", LAB / "generated/phase2/techmarket341/facade_concrete.png", .83
    ) if civic else wall
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
    foliage = make_material("Hardy street shrubs", (.062, .116, .043, 1), .03, .84)
    leaf_tips = make_material("New shrub growth", (.14, .22, .072, 1), .03, .88)
    shipping_skins = [make_material("Shipping enamel", color, .55, .64) for color in (
        (.07,.17,.19,1), (.27,.081,.05,1), (.17,.21,.095,1)
    )]
    roof = textured_material("Original rooftop artwork", MAPS / f"{name}.png", .8)
    if wasteland and wasteland.trainyard:
        wasteland.workshop_surface = roof
    guardrail_steel = make_material("Freeway galvanized steel", (.25,.30,.34,1), .73,.53) if freeway else None
    for i, row in enumerate(survey["walls"]):
        identifier = row["id"]
        if row.get("kind") == "water":
            continue
        if wasteland is not None:
            wasteland.add(row)
            continue
        if "points" in row:
            points = [(px*gw/cw-gw/2, gh/2-py*gh/ch) for px, py in row["points"]]
            group = None
            if freeway or name in ROOFTOPS or name == "city_district_civic_center":
                group = bpy.data.objects.new("Occludable_" + identifier, None)
                bpy.context.collection.objects.link(group)
            for segment, ((ax,ay),(bx,by)) in enumerate(zip(points, points[1:])):
                width = row["width"] * gw/cw
                length = math.hypot(bx-ax, by-ay)
                yaw = math.atan2(by-ay,bx-ax)
                if freeway:
                    beam = box(identifier+" steel beam", ((ax+bx)/2,(ay+by)/2,.54),
                               (length/2,width*.37,.067), guardrail_steel,.015)
                    beam.rotation_euler.z = yaw
                    beam.parent = group
                    spans = max(1,math.ceil(length/1.6))
                    start = 0 if segment == 0 else 1
                    for index in range(start,spans+1):
                        t = index/spans
                        x,y = ax+(bx-ax)*t,ay+(by-ay)*t
                        post = box(identifier+" post", (x,y,.276),
                                   (min(width*.23,.065),width*.30,.276), frame,.012)
                        post.rotation_euler.z = yaw
                        post.parent = group
                        if index % 3 == 1:
                            box(identifier+" reflector", (x,y,.627), (.035,.045,.018),
                                signs[2],.007).parent = group
                elif name in ROOFTOPS:
                    for label, z, half_width, depth, material in (
                        ("parapet body", .23, width*.43, .23, wall),
                        ("coping", .467, width*.48, .037, frame),
                    ):
                        piece = box(identifier+" "+label, ((ax+bx)/2,(ay+by)/2,z),
                                    (length/2,half_width,depth), material,.016)
                        piece.rotation_euler.z = yaw
                        piece.parent = group
                else:
                    rail = box(identifier, ((ax+bx)/2,(ay+by)/2,.24),
                               (length/2,width/2,.24), frame)
                    rail.rotation_euler.z = yaw
                    rail.parent = group
            continue
        if name == "city_district_holo_square" and identifier.startswith("bench_"):
            xs, ys = zip(*row["polygon"])
            row = {**row, "rect": (min(xs), min(ys), max(xs), max(ys))}
            row.pop("polygon")
        if "polygon" in row and not identifier.endswith("_car"):
            points = [(px*gw/cw-gw/2, gh/2-py*gh/ch) for px, py in row["polygon"]]
            if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points, points[1:]+points[:1])) < 0:
                points.reverse()
            count = len(points)
            faces = [tuple(reversed(range(count))), tuple(range(count, 2*count))]
            faces.extend((j, (j+1)%count, (j+1)%count+count, j+count) for j in range(count))
            mesh = bpy.data.meshes.new(identifier)
            is_planter = "planter" in identifier or (civic and identifier in {"nw_island", "sw_approach", "se_approach"})
            is_building = "building" in identifier
            height = 2.8+i%3*.5 if is_building else .68 if identifier.endswith("_high") else .31 if is_planter else .22
            polygon_bench = riot_square and identifier.startswith("bench_")
            base, top = (.34,.43) if polygon_bench else (0,height)
            mesh.from_pydata([(x,y,z) for z in (base,top) for x,y in points], [], faces)
            mesh.materials.append(seat if polygon_bench else civic_surface if is_building else wall)
            if is_planter:
                mesh.materials.append(gravel if civic else foliage)
                mesh.polygons[1].material_index = 1
            island = bpy.data.objects.new(identifier, mesh)
            bpy.context.collection.objects.link(island)
            group = bpy.data.objects.new("Occludable_" + identifier, None)
            bpy.context.collection.objects.link(group)
            island.parent = group
            if polygon_bench:
                vertices = [Vector((x,y,0)) for x,y in points]
                for triangle in tessellate_polygon([vertices]):
                    a,b,c = (vertices[index] for index in triangle)
                    x,y,_ = (a+b+c)/3
                    box(identifier + " seat support", (x,y,.17), (.073,.068,.17), frame).parent = group
            if civic and (is_planter or "_tree" in identifier):
                if "_tree" in identifier or identifier in {"monument_planter", "statue_planter"}:
                    x = sum(px for px,_ in points)/count
                    y = sum(py for _,py in points)/count
                    box(identifier + " central support", (x,y,.58), (.10,.10,.36), frame).parent = group
                    if identifier == "statue_planter":
                        bronze = make_material("Riot Square aged bronze", (.18,.107,.058,1), .72,.51)
                        for label, radius, z, depth, material in (
                            ("Monument lower octagon", .92, .39, .16, frame),
                            ("Monument bronze molding", .73, .51, .082, bronze),
                            ("Monument upper plinth", .55, .64, .21, wall),
                        ):
                            bpy.ops.mesh.primitive_cylinder_add(
                                vertices=8, radius=radius, depth=depth, location=(x,y,z)
                            )
                            piece = bpy.context.object
                            piece.name = label
                            piece.data.materials.append(material)
                            piece.parent = group
                        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=.37, radius2=.18,
                                                        depth=.72, location=(x,y,1.10))
                        column = bpy.context.object
                        column.name = "Monument tapered bronze sculpture"
                        column.rotation_euler.y = -.19
                        column.data.materials.append(bronze)
                        column.parent = group
                        bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=8,
                            major_radius=.31, minor_radius=.064, location=(x-.07,y,1.46),
                            rotation=(math.pi/2,.12,0))
                        crest = bpy.context.object
                        crest.name = "Monument bronze crest"
                        crest.data.materials.append(bronze)
                        crest.parent = group
                        monument_center = Vector((x,y,0))
                    elif identifier == "monument_planter":
                        box("Civic monument pedestal", (x,y,.47), (.58,.54,.19), frame).parent = group
                        box("Civic monument beacon", (x,y,1.02), (.14,.14,.11), signs[2]).parent = group
                vertices = [Vector((x,y,0)) for x,y in points]
                for triangle in tessellate_polygon([vertices]):
                    a,b,c = (vertices[index] for index in triangle)
                    area = (b-a).cross(c-a).length/2
                    if area < .022:
                        continue
                    center = (a+b+c)/3
                    cluster = (center,) if area < .36 else tuple(center.lerp(v,.40) for v in (a,b,c))
                    radius = min(.31,math.sqrt(area)*.47)
                    z = 1.03 if "_tree" in identifier else height+.11
                    for index, point in enumerate(cluster):
                        if identifier == "statue_planter" and (point-monument_center).length < 1.10:
                            continue
                        bpy.ops.mesh.primitive_ico_sphere_add(
                            subdivisions=2, radius=1, location=(point.x,point.y,z)
                        )
                        shrub = bpy.context.object
                        shrub.name = identifier + " foliage"
                        shrub.scale = (radius,radius*(.82+index*.09),radius*.76)
                        shrub.data.materials.append(leaf_tips if index == 1 else foliage)
                        shrub.parent = group
            if is_building:
                mesh.materials.append(roof)
                mesh.polygons[1].material_index = 1
                uv = mesh.uv_layers.new()
                for loop in mesh.polygons[1].loop_indices:
                    vx,vy,_ = mesh.vertices[mesh.loops[loop].vertex_index].co
                    uv.data[loop].uv = (vx/gw+.5, vy/gh+.5)
                if civic:
                    edges = zip(points,points[1:]+points[:1])
                    for ((ax,ay),(bx,by)), face in zip(edges,mesh.polygons[2:]):
                        dx,dy = bx-ax,by-ay
                        length = math.hypot(dx,dy)
                        repeat = length/2.7
                        for loop, coord in zip(face.loop_indices, ((0,0),(repeat,0),(repeat,height/2.7),(0,height/2.7))):
                            uv.data[loop].uv = coord
                        if length < 1.4:
                            continue
                        yaw = math.atan2(dy,dx)
                        nx,ny = dy/length,-dx/length
                        for z in (.28,height-.25):
                            band = box(identifier+" civic facade band",
                                       ((ax+bx)/2+nx*.038,(ay+by)/2+ny*.038,z),
                                       (length/2,.037,.052),frame,.01)
                            band.rotation_euler.z = yaw
                            band.parent = group
                        bays = max(1,int(length/2.15))
                        for index in range(bays):
                            portion = (index+.5)/bays
                            place(library / "urban_facade280/window.glb", group,
                                  (ax+portion*dx+nx*.054,ay+portion*dy+ny*.054,height*.51),
                                  (min(1.35,length/bays*.75),.28,.70), yaw=yaw, merge=True)

            if identifier.startswith("sign_") or identifier == "holo_platform":
                sx = sum(px for px,_ in points)/count
                sy = sum(py for _,py in points)/count
                widths = [px for px,_ in points]
                depth = [py for _,py in points]
                if identifier == "holo_platform":
                    radius = min(max(widths)-min(widths), max(depth)-min(depth))*.27
                    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=.28,
                                                        location=(sx,sy,.36))
                    emitter = bpy.context.object
                    emitter.name = "Holo Square emitter"
                    emitter.data.materials.append(frame)
                    emitter.parent = island
                    for i, (scale,z) in enumerate(((.94,.55),(.84,.90),(.68,1.25),(.50,1.60))):
                        bpy.ops.mesh.primitive_torus_add(major_segments=8, minor_segments=6,
                                                        major_radius=radius*scale, minor_radius=.024,
                                                        location=(sx,sy,z))
                        halo = bpy.context.object
                        halo.name = f"Holo Square projection ring {i+1}"
                        halo.data.materials.append(signs[0])
                        halo.parent = island
                    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=radius*.60, radius2=radius*.25,
                                                    depth=1.35, location=(sx,sy,1.18))
                    core = bpy.context.object
                    core.name = "Holo Square projection core"
                    core.data.materials.append(signs[0])
                    core.parent = island
                else:
                    box(identifier+" projector", (sx,sy,.55),
                        ((max(widths)-min(widths))*.18,(max(depth)-min(depth))*.16,.32), frame).parent = island
                    box(identifier+" display", (sx,sy,1.04),
                        ((max(widths)-min(widths))*.26,.026,.29), signs[i%len(signs)]).parent = island
            continue
        if "rect" in row:
            x1, y1, x2, y2 = row["rect"]
        else:
            px,py = zip(*row["polygon"])
            x1,y1,x2,y2 = min(px),min(py),max(px),max(py)
        x, y = (x1 + x2) * gw / (2*cw) - gw/2, gh/2 - (y1 + y2) * gh / (2*ch)
        w, d = (x2-x1)*gw/cw, (y2-y1)*gh/ch
        height = 3.0 + .65*(i % 3)
        group = bpy.data.objects.new("Occludable_" + identifier, None)
        bpy.context.collection.objects.link(group)
        if any(part in identifier for part in ("_fans", "_duct", "_vent")):
            fixture = ("roof_twin_fan/optimized.glb" if "_fans" in identifier else
                       "wall_fixtures282/duct.glb" if "_duct" in identifier else "wall_fixtures282/vent.glb")
            vertical = d > w
            place(library / fixture, group, (x,y,0), (max(w,d)*.97,min(w,d)*.97,1.3),
                  yaw=math.pi/2 if vertical else 0)
            continue
        if identifier.endswith(("_lift", "_plant", "_box", "_boxes", "_dish", "_antenna")):
            height = 1.8 if identifier.endswith(("_lift","_antenna")) else .87
            box(identifier+" housing", (x,y,height/2), (w*.46,d*.46,height/2), wall).parent = group
            box(identifier+" access panel", (x,y-d*.47,height*.57),
                (w*.31,.03,height*.17), frame).parent = group
            if identifier.endswith(("_dish", "_antenna")):
                bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=.07, radius2=min(w,d)*.36,
                                                depth=.31, location=(x,y,height+.15))
                mount = bpy.context.object
                mount.rotation_euler.x = .25
                mount.data.materials.append(frame)
                mount.parent = group
            continue
        if identifier.endswith("_stair"):
            for step in range(7):
                rise = (step+1)*.15
                box(identifier, (x,y+(((step+.5)/7)-.5)*d,rise/2),
                    (w*.47,d/14,rise/2), frame).parent = group
            continue
        if identifier.endswith("_rail"):
            box(identifier, (x,y,.23), (w*.49,d*.49,.23), frame).parent = group
            continue
        if "crate" in identifier:
            place(library / "cargo_crate274/model.glb", group, (x,y,0), (w,d,.74))
            continue
        if "tree" in identifier:
            box(identifier+" pot", (x,y,.16), (w*.43,d*.43,.16), frame).parent = group
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(x,y,.78))
            crown = bpy.context.object
            crown.scale = (w*.42,d*.42,.46)
            crown.data.materials.append(foliage)
            crown.parent = group
            continue
        if identifier.startswith("market_") or identifier.endswith("_stall"):
            market_models = (
                LAB / "generated/phase2/techmarket341/shared_electronics_stall.glb",
                library / "market_southeast_display/shop.glb",
                library / "market_three_canopies/shop.glb",
            )
            place(market_models[i % 3], group, (x,y,0), (w*.96,d*.96,2.05), merge=True)
            continue
        if name.endswith("_civic_plaza") and identifier.endswith("_monument"):
            radius = min(w,d)*.47
            accent = signs[1] if identifier == "east_monument" else signs[0]
            height = 1.68 if identifier == "east_monument" else 2.17
            for label, scale, z, depth, material in (
                ("outer octagon", 1.0, .13, .26, wall),
                ("exposed molding", .88, .275, .055, frame),
                ("raised dais", .70, .345, .10, wall),
                ("signal collar", .38, .44, .09, accent),
                ("luminous core", .125, (height+.50)/2, height-.50, accent),
                ("top cap", .16, height+.038, .076, frame),
            ):
                bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius*scale,
                                                    depth=depth, location=(x,y,z))
                part = bpy.context.object
                part.name = identifier+" "+label
                part.data.materials.append(material)
                part.parent = group
            for side in (-1,1):
                box(identifier+" core frame", (x+side*radius*.19,y,(height+.51)/2),
                    (radius*.035,radius*.057,(height-.51)/2),frame,.01).parent = group
            continue
        if identifier.endswith("_monument") or identifier == "monument":
            radius = min(w,d)*.40
            box(identifier + " base", (x,y,.20), (w*.48,d*.48,.20), wall).parent = group
            for label, height, lower, upper, center, material in (
                ("shaft", 1.65, radius*.56, radius*.32, 1.22, frame),
                ("light", .12, radius*.34, radius*.34, 2.08, signs[0]),
                ("spire", .62, radius*.34, .02, 2.45, frame),
            ):
                bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=lower, radius2=upper,
                                                depth=height, location=(x,y,center))
                piece = bpy.context.object
                piece.name = identifier + " " + label
                piece.data.materials.append(material)
                piece.parent = group
            continue
        if industrial and identifier.endswith("_wall"):
            box(identifier, (x,y,.7), (w/2,d/2,.7), wall).parent = group
            box(identifier + " coping", (x,y,1.4), (w/2,d/2,.055), frame).parent = group
            continue
        if identifier.endswith("_machine"):
            vertical = d > w
            place(library / "industrial_generator265/model.glb", group, (x,y,0),
                  (max(w,d),min(w,d),1.7), yaw=math.pi/2 if vertical else 0)
            continue
        if identifier.startswith("forklift_"):
            build_forklift(group, identifier, x, y, w, d, shipping_skins[1], frame)
            continue
        if identifier.startswith(("car_", "north_car", "south_car")) or identifier.endswith("_car"):
            vertical = d > w
            place(library / "derelict_suv275/model.glb", group, (x, y, 0),
                  (max(w, d)*.95, min(w, d)*.95, .92), yaw=math.pi/2 if vertical else 0)
            continue
        if "crane" in identifier:
            build_crane(group, x, y, w, d, frame, shipping_skins[1],
                        height=3.8, outreach=min(2.65, max(w,d)))
            continue
        if "container" in identifier or "cargo" in identifier:
            vertical = d > w
            build_container(group, x, y, max(w,d), min(w,d),
                            shipping_skins[i % len(shipping_skins)], frame, wall,
                            yaw=math.pi/2 if vertical else 0)
            continue
        if identifier.startswith(("bus_", "truck_", "station_")):
            shelter = identifier.startswith("station_")
            height = 1.68 if shelter else 1.27
            box(identifier + " roof", (x,y,height), (w*.48,d*.47,.065), frame).parent = group
            if shelter:
                for sx in (-1,1):
                    for sy in (-1,1):
                        box(identifier + " post", (x+sx*w*.38,y+sy*d*.37,height/2),
                            (.045,.045,height/2), frame).parent = group
                box(identifier + " seat", (x,y+d*.24,.41), (w*.36,d*.13,.055), seat).parent = group
            else:
                box(identifier + " chassis", (x,y,.49), (w*.46,d*.44,.31), wall).parent = group
                box(identifier + " glazing", (x,y,.95), (w*.45,d*.43,.19), seat).parent = group
                for sx in (-1,1):
                    for sy in (-1,1):
                        box(identifier + " wheel", (x+sx*w*.32,y+sy*d*.31,.18),
                            (w*.10,d*.16,.18), wall).parent = group
            continue
        if identifier.startswith(("pillar_", "platform_", "ramp_outer_")) or "_rail" in identifier:
            height = 1.8 if identifier.startswith("pillar_") else .22 if identifier.startswith("platform_") else .48
            box(identifier, (x,y,height/2), (w*.49,d*.49,height/2), wall).parent = group
            box(identifier + " trim", (x,y,height), (w*.49,d*.49,.035), frame).parent = group
            continue
        if "crate" in identifier:
            place(library / "cargo_crate274/model.glb", group, (x, y, 0), (w, d, .55))
            continue
        if identifier.startswith("utility_"):
            vertical = d > w
            place(library / "industrial_service267/model.glb", group, (x, y, 0),
                  (max(w, d), min(w, d), 1.3), yaw=math.pi/2 if vertical else 0)
            continue
        if identifier.startswith("bin_") or identifier.endswith("_bins"):
            box(identifier, (x, y, .25), (w*.45, d*.45, .25), wall).parent = group
            box(identifier + " lid", (x, y, .51), (w*.49, d*.49, .035), frame).parent = group
            continue
        if identifier.endswith(("_sign", "_kiosk", "_guard", "_terminal")) or identifier.startswith("ticket_"):
            is_kiosk = not identifier.endswith("_sign")
            height = 1.55 if is_kiosk else .95
            width, depth = max(w,d), min(w,d)
            vertical = d > w
            accent = signs[i % len(signs)]
            parts = [
                ("plinth", (0,0,.075), (width*.49,depth*.47,.075), frame),
                ("housing", (0,0,height*.5), (width*.42,depth*.27,height*.5), wall),
                ("screen bezel", (0,-depth*.282,height*.71),
                 (width*.38,depth*.038,height*.225), frame),
                ("screen", (0,-depth*.324,height*.71),
                 (width*.33,depth*.011,height*.17), accent),
                ("hood", (0,-depth*.075,height+.035), (width*.46,depth*.385,.04), frame),
            ]
            if is_kiosk:
                parts.append(("control shelf", (0,-depth*.35,height*.43),
                              (width*.34,depth*.085,.039), frame))
                for slot in range(3):
                    parts.append(("service vent", (0,-depth*.281,height*(.17+slot*.05)),
                                  (width*.25,depth*.012,.012), frame))
            for label, position, half_size, material in parts:
                box(f"{identifier} {label}", position, half_size, material).parent = group
            group.location = (x,y,0)
            outward_back = x < 0 if vertical else y > 0
            group.rotation_euler.z = (math.pi/2 if vertical else 0) + (0 if outward_back else math.pi)
            continue
        if any(kind in identifier for kind in ("bench", "planter", "barrier", "barricade", "_seat")):
            if "bench" in identifier or identifier.endswith("_seat"):
                length, depth = max(w,d), min(w,d)
                vertical = d > w
                facing = (x < 0) if vertical else (y > 0)
                direction = 1 if facing else -1
                parts = [
                    ("crossbeam", (0,0,.31), (length*.45,depth*.23,.045), frame),
                ]
                sections = 3 if length >= 2.1 else 2
                for index in range(sections):
                    offset = ((index+.5)/sections-.5)*length*.92
                    parts.append(("seat panel", (offset,0,.38),
                                  (length*.43/sections,depth*.31,.045), seat))
                    parts.append(("back panel", (offset,depth*.29,.56),
                                  (length*.43/sections,depth*.07,.12), seat))
                for offset in (-.39,.39):
                    parts.extend((
                        ("foot", (length*offset,0,.17), (length*.045,depth*.32,.17), frame),
                        ("back support", (length*offset,depth*.29,.45),
                         (length*.035,depth*.035,.18), frame),
                    ))
                for label, position, half_size, material in parts:
                    box(f"{identifier} {label}", position, half_size, material).parent = group
                group.location = (x,y,0)
                group.rotation_euler.z = (math.pi/2 if vertical else 0) + (math.pi if direction < 0 else 0)
                continue
            else:
                parts = [
                    ("base", (x, y, .16), (w*.49, d*.48, .16), wall),
                    ("rim", (x, y, .33), (w*.50, d*.49, .045), frame),
                ]
                if "planter" in identifier:
                    parts.append(("gravel", (x, y, .375), (w*.43, d*.40, .02), gravel))
                    vertices, faces = [], []
                    vertical = d > w
                    for cluster in (-1, 0, 1):
                        center_x = x if vertical else x+cluster*w*.27
                        center_y = y+cluster*d*.27 if vertical else y
                        radius_x = w*(.30 if vertical else .15)
                        radius_y = d*(.15 if vertical else .30)
                        for leaf in range(18):
                            angle = leaf * 2.39996 + cluster*.75 + i*.18
                            radius = math.sqrt((leaf+.5)/18)
                            sx, sy = math.cos(angle), math.sin(angle)
                            dx, dy = radius_x*sx, radius_y*sy
                            px, py = center_x+dx*radius*.80, center_y+dy*radius*.80
                            z = .40 + .14*(1-radius) + (leaf%4)*.025
                            start = len(vertices)
                            vertices.extend((
                                (px-dx*.19, py-dy*.19, z),
                                (px-dy*.09, py+dx*.09, z+.052),
                                (px+dx*.21, py+dy*.21, z+.077),
                                (px+dy*.09, py-dx*.09, z+.035),
                            ))
                            faces.append((start, start+3, start+2, start+1))
                    shrub_mesh = bpy.data.meshes.new(identifier + " shrub foliage")
                    shrub_mesh.from_pydata(vertices, [], faces)
                    shrub_mesh.materials.append(foliage)
                    shrub_mesh.materials.append(leaf_tips)
                    for face in shrub_mesh.polygons:
                        face.material_index = int(face.index % 4 == 0)
                    shrub = bpy.data.objects.new(identifier + " shrub foliage", shrub_mesh)
                    bpy.context.collection.objects.link(shrub)
                    shrub.parent = group
                else:
                    parts.append(("reflector", (x, y, .38), (w*.38, .04, .02), signs[2]))
            for label, position, half_size, material in parts:
                box(f"{identifier} {label}", position, half_size, material).parent = group
            continue
        if not any(part in identifier for part in ("block", "building", "_roof", "warehouse", "_factory", "_tower")) and identifier not in BUILDING_EXCEPTIONS:
            raise ValueError(f"No avenue model for {identifier}")
        shell = box(identifier, (x, y, height/2), (w/2, d/2, height/2), civic_surface)
        shell.parent = group
        shell.data.materials.append(roof)
        uv = shell.data.uv_layers.active
        for face in shell.data.polygons:
            if face.normal.z < .9:
                if civic and abs(face.normal.z) < .1:
                    for loop_index in face.loop_indices:
                        point = shell.data.vertices[shell.data.loops[loop_index].vertex_index].co
                        along = point.y if abs(face.normal.x) > .5 else point.x
                        uv.data[loop_index].uv = (along/2.7, (point.z+height/2)/2.7)
                continue
            face.material_index = 1
            for loop_index in face.loop_indices:
                p = shell.data.vertices[shell.data.loops[loop_index].vertex_index].co
                uv.data[loop_index].uv = ((x+p.x)/gw+.5, (y+p.y)/gh+.5)
        if not industrial and min(w, d) >= 2.4:
            thickness = .08
            parapet_height = .12
            for side in (-1, 1):
                box(identifier + " roof parapet long",
                    (x, y+side*(d/2-thickness), height+parapet_height),
                    (w/2, thickness, parapet_height), frame).parent = group
                box(identifier + " roof parapet short",
                    (x+side*(w/2-thickness), y, height+parapet_height),
                    (thickness, d/2-2*thickness, parapet_height), frame).parent = group
        roof_fans = ROOF_FANS_BY_MAP.get(name, {}).get(identifier, ())
        for left, top, right, bottom in roof_fans:
            fan_x = (left+right)*gw/(2*cw)-gw/2
            fan_y = gh/2-(top+bottom)*gh/(2*ch)
            fan_w, fan_d = (right-left)*gw/cw, (bottom-top)*gh/ch
            box(identifier + " roof HVAC mounting curb", (fan_x,fan_y,height+.035),
                (fan_w/2,fan_d/2,.035), frame).parent = group
            fitted = place(library / "roof_twin_fan/optimized.glb", group,
                           (fan_x,fan_y,height+.07), (max(fan_w,fan_d),min(fan_w,fan_d),.55),
                           yaw=math.pi/2 if fan_d > fan_w else 0, merge=True)
            for obj in fitted:
                obj.name = identifier + " surveyed roof HVAC"
        direction = -1 if y > 0 else 1
        front = y + direction*d/2
        angle = 0 if direction < 0 else math.pi
        for offset in (-.3, .3):
            place(library / "urban_facade280/window.glb", group,
                  (x+w*offset, front+direction*.04, .9), (min(1.65,w*.33), .28, 1.7), yaw=angle)
        if not industrial and height >= 2.4:
            if d >= 2.4:
                for side in (-1, 1):
                    flank = x + side*w/2
                    for offset in (-.27, .27):
                        place(library / "urban_facade280/window.glb", group,
                              (flank+side*.035, y+d*offset, .88),
                              (min(1.65,d*.34), .28, 1.65), yaw=side*math.pi/2, merge=True)
                    box(identifier + " side facade band", (flank,y,height-.20),
                        (.035,d*.48,.06), frame).parent = group
            if w >= 2.4:
                back = y - direction*d/2
                service_width = min(.64, w*.15)
                door_x = x + w*.22
                box(identifier + " rear service frame", (door_x,back-direction*.045,.81),
                    (service_width,.065,.81), frame).parent = group
                box(identifier + " rear service door", (door_x,back-direction*.111,.77),
                    (service_width*.82,.022,.73), wall).parent = group
                box(identifier + " rear facade band", (x,back,height-.20),
                    (w*.48,.035,.06), frame).parent = group
                place(library / "urban_facade280/window.glb", group,
                      (x-w*.23, back-direction*.035, 1.10),
                      (min(1.65,w*.34), .28, 1.52), yaw=angle+math.pi, merge=True)
        if industrial:
            door_width = min(w*.48, 3.3)
            box(identifier + " loading shutter", (x,front+direction*.07,.95),
                (door_width/2,.08,.95), frame).parent = group
            for slat in range(1,9):
                box(identifier + " shutter slat", (x,front+direction*.157,slat*.20),
                    (door_width*.48,.012,.02), wall).parent = group
            continue
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
    if name in ROOFTOPS:
        build_rooftop_ground(out, floor, (gw,gh), (cw,ch), library)
    elif freeway and len(deck_rails) == 2:
        rail_rows = deck_rails["highway_north_rail"], deck_rails["highway_south_rail"]
        build_freeway_deck(floor, wall, frame, (gw,gh), (cw,ch), rail_rows)
        ramp_traces = {row["id"]: row["points"] for row in survey["walls"]
                       if row["id"] in {"ramp_outer_w", "ramp_outer_e"}}
        if len(ramp_traces) == 2:
            build_freeway_ramps(floor, wall, (gw,gh), (cw,ch), ramp_traces, rail_rows)
    else:
        bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -.025))
        bpy.context.object.scale = (gw/2, gh/2, 1)
        bpy.context.object.data.materials.append(floor)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "environment.blend"))
    bpy.ops.export_scene.gltf(filepath=str(out / "environment.glb"), export_format="GLB")
    print("BILLBOARD_AVENUE_EXPORTED", name, sum(row.get("kind") != "water" for row in survey["walls"]))


maps = sys.argv[sys.argv.index("--") + 1:]
if not maps or any(Path(name).name != name for name in maps):
    raise ValueError("Pass one or more original map IDs after --")
for map_name in maps:
    build(map_name)
