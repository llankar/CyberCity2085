"""Build original urban streets using shared facade and street furniture modules."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_tri_2d, tessellate_polygon

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place, reset_library_cache
from loading_crane import build_crane
from shipping_container import build_container
from freight_stock import SOUTH_SIDING_LOADS
from wasteland_outdoor import WastelandOutdoors
from industrial_forklift import build_forklift

LAB = Path("E:/CyberCity2085-3d-lab")
DOCK_BASIN_DEPTH = 1.35
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
TRANSIT_06_ROOF_FANS = {
    "north_block": ((340, 27, 399, 54),),
    "ne_block": ((607, 0, 650, 24),),
    "west_block": ((30, 276, 60, 305),),
    "south_block": ((394, 457, 417, 482),),
    "se_block": ((799, 470, 839, 506), (924, 470, 953, 492)),
}
TRANSIT_11_ROOF_FANS = {
    "nw_block": ((106, 16, 137, 43),),
    "north_block": ((247, 8, 280, 35),),
    "ne_corner": ((824, 8, 848, 30),),
    "west_mid": ((8, 190, 38, 219),),
    "east_south": ((918, 320, 941, 343),),
    "sw_block": ((104, 468, 129, 491),),
    "south_block": ((268, 484, 296, 513),),
}
ROOF_FANS_BY_MAP = {
    "cybercity_street_13_flood_prone_avenue": {
        "nw_block": ((273, 1, 299, 40),),
        "se_block": ((803, 354, 855, 384),),
    },
    "city_district_holo_square": {
        "building_east": ((1790, 434, 1874, 479),),
        "building_se": ((1818, 774, 1875, 855),),
    },
    "city_exterior_downtown_intersection": {
        "northwest_roof": ((175, 1, 211, 23),),
        "northeast_roof": ((618, 1, 653, 28),),
        "southwest_annex": ((139, 467, 185, 490),),
    },
    "city_exterior_parking_garage": {
        "north_roof_w": ((182, 47, 251, 88),),
    },
    "city_district_riot_square": {"east_south_building": ((1774, 950, 1882, 1008),)},
    "cybercity_street_12_industrial_district": {
        "nw_factory": ((210, 22, 264, 49),),
        "north_factory": ((331, 21, 355, 44),),
        "ne_factory": ((655, 23, 687, 51), (699, 4, 724, 29)),
        "sw_factory": ((207, 475, 237, 506),),
        "se_factory": ((689, 446, 718, 474), (734, 393, 793, 428)),
    },
    "city_exterior_billboard_avenue": BILLBOARD_ROOF_FANS,
    "cybercity_street_15_billboard_avenue": ALTERNATE_BILLBOARD_ROOF_FANS,
    "cybercity_street_16_billboard_avenue": ALTERNATE_BILLBOARD_ROOF_FANS,
    "cybercity_street_02_neon_market_alley": MARKET_02_ROOF_FANS,
    "cybercity_street_07_neon_market_alley": MARKET_07_08_ROOF_FANS,
    "cybercity_street_08_neon_market_alley": MARKET_07_08_ROOF_FANS,
    "cybercity_street_11_transit_interchange": TRANSIT_11_ROOF_FANS,
    "cybercity_street_06_transit_interchange": TRANSIT_06_ROOF_FANS,
}

SURVEYED_CAR_ANGLES = {
    "city_exterior_downtown_intersection": {
        "car_north": -57, "car_north_east": 68, "car_midwest": 61,
        "car_mideast": -48, "car_southwest": -18, "car_south": 68,
        "car_southeast": -40,
    },
    "city_exterior_parking_garage": {
        "car_n4": -57, "car_w": 19, "car_mideast": -22,
    },
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


def build_rooftop_ground(out, floor, grid, canvas, library, water=None, shallow=False):
    terrain = json.loads((out / "rooftop_terrain.json").read_text())
    gw,gh = grid
    cw,ch = canvas
    deck_z, street_z = -.025, -DOCK_BASIN_DEPTH if water else -3.6
    if shallow:
        street_z = -.075

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
        mesh.materials.append(water if water and surface == "street" else floor)
        uv = mesh.uv_layers.new()
        for loop in mesh.loops:
            x,y,_ = vertices[loop.vertex_index]
            uv.data[loop.index].uv = (x/gw+.5,y/gh+.5)
        label = {"deck": "Waterfront quay deck", "street": "Waterfront basin surface"}[surface] if water else "Rooftop "+surface
        if shallow:
            label = "Flooded avenue water surface" if surface == "street" else "Flooded avenue sidewalk"
        bpy.context.collection.objects.link(bpy.data.objects.new(label,mesh))

    vertices, faces = [], []
    for a,b in terrain["edges"]:
        first = len(vertices)
        vertices.extend((vertex(a,street_z),vertex(b,street_z),vertex(b,deck_z),vertex(a,deck_z)))
        faces.append(tuple(range(first,first+4)))
    mesh = bpy.data.meshes.new("Canyon retaining walls")
    mesh.from_pydata(vertices, [], faces)
    retaining = make_material("Canyon retaining concrete", (.046,.062,.078,1), .15,.86)
    mesh.materials.append(retaining)
    label = "Waterfront quay retaining walls" if water else "Rooftop canyon retaining walls"
    if shallow:
        label = "Flooded avenue curb edges"
    bpy.context.collection.objects.link(bpy.data.objects.new(label,mesh))
    if water:
        if shallow:
            return
        rubber = make_material("Weathered quay fender rubber", (.033,.041,.045,1), 0,.91)
        coping = make_material("Worn quay edge steel", (.082,.10,.11,1), .47,.75)
        for start, end in terrain["edges"]:
            a, b = Vector(vertex(start,deck_z)), Vector(vertex(end,deck_z))
            edge = b-a
            yaw = math.atan2(edge.y,edge.x)
            if edge.length > .20:
                cap = box("Quay steel coping", a.lerp(b,.5),
                          (edge.length*.497,.073,.038),coping,.012)
                cap.rotation_euler.z = yaw
            if edge.length < 2.5:
                continue
            normal = Vector((edge.y,-edge.x,0)).normalized()
            slots = max(1, int(edge.length/3.4))
            for index in range(slots):
                station = a.lerp(b,(index+.5)/slots)
                center = station + normal*.11
                center.z -= .46
                fender = box("Quay rubber fender",center,(.23,.16,.39),rubber,.055)
                fender.rotation_euler.z = yaw
                # Tie-off points sit inland of the wall and face the matching fenders.
                center = station-normal*.18
                center.z += .075
                bollard = box("Quay steel mooring bollard", center, (.102,.072,.075),coping,.040)
                bollard.rotation_euler.z = yaw
        return
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



def build_bridge_surfaces(floor, water, retaining, grid, canvas, north, south):
    gw, gh = grid
    cw, ch = canvas
    deck_z, river_z = -.025, -1.35
    # Each shoreline is the inside chain between the two map-edge vertices.
    north_bank = [north[0], *reversed(north[2:])]
    south_bank = [south[1], south[0], *reversed(south[4:])]
    land = [(0,0), *north_bank, *south_bank, (0,ch)]

    def point(p, z):
        return Vector((p[0]*gw/cw-gw/2, gh/2-p[1]*gh/ch, z))

    for label, outline, z, material in (
        ("Bridge pavement and approach", land, deck_z, floor),
        ("North river surface", north, river_z, water),
        ("South river surface", south, river_z, water),
    ):
        vertices = [point(p,z) for p in outline]
        if sum(a.x*b.y-b.x*a.y for a,b in zip(vertices,vertices[1:]+vertices[:1])) < 0:
            vertices.reverse()
        mesh = bpy.data.meshes.new(label)
        mesh.from_pydata(vertices, [], tessellate_polygon([vertices]))
        mesh.materials.append(material)
        uv = mesh.uv_layers.new()
        for loop in mesh.loops:
            x,y,_ = vertices[loop.vertex_index]
            uv.data[loop.index].uv = (x/gw+.5,y/gh+.5)
        bpy.context.collection.objects.link(bpy.data.objects.new(label,mesh))

    for label, bank in (("North bridge fascia", north_bank), ("South bridge fascia", south_bank)):
        vertices = [point(p,z) for z in (deck_z,river_z) for p in bank]
        count = len(bank)
        mesh = bpy.data.meshes.new(label)
        mesh.from_pydata(vertices, [], [(i,i+1,i+1+count,i+count) for i in range(count-1)])
        mesh.materials.append(retaining)
        bpy.context.collection.objects.link(bpy.data.objects.new(label,mesh))
        # The longest bank stretch along the water is the bridge edge.
        start, end = max(zip(bank, bank[1:]), key=lambda edge: math.dist(*edge))
        a, b = point(start, deck_z), point(end, deck_z)
        edge = b-a
        normal = Vector((-edge.y, edge.x, 0)).normalized()
        for height in (.22, .87):
            center = (a+b)/2 + normal*.045
            center.z -= height
            rib = box(label+" structural rib", center, (edge.length/2,.075,.064), retaining,.02)
            rib.rotation_euler.z = math.atan2(edge.y,edge.x)


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
    # Carry the deck load across the paired bearings at each pier station.
    for index in range(8):
        x = ((index+.5)/8-.5)*gw
        box("Freeway transverse pier cap", (x,(north+south)/2,-.595),
            (.30,(north-south)/2+.09,.077),frame,.025)
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
        faces.extend(tuple(index+count for index in reversed(face)) for face in faces[:top_count])
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
    waterfront = name.endswith("_waterfront_docks")
    basin_triangles = []
    if waterfront:
        terrain = json.loads((out / "rooftop_terrain.json").read_text())
        basin_triangles = [tuple(Vector(p) for p in triangle) for triangle in terrain["street"]]
    freeway = name.endswith("_elevated_freeway")
    flood_avenue = name.endswith("_flood_prone_avenue")
    transport_facades = freeway or name.endswith("_transit_interchange") or flood_avenue
    deck_rails = {row["id"]: row["points"][0][1] for row in survey["walls"]
                  if row["id"] in {"highway_north_rail", "highway_south_rail"}}
    riot_square = name == "city_district_riot_square"
    civic = name in {"city_district_civic_center", "city_district_riot_square"} or name.endswith("_civic_plaza")
    industrial = name.endswith(("freight_yard", "industrial_district"))
    library = LAB / "environment-library/assets"
    wasteland = (WastelandOutdoors(library, (gw,gh), (cw,ch), city=name.startswith("wasteland_city_"),
                                   overpass=name.endswith("_collapsed_overpass"),
                                   ruined_downtown=name.endswith("_ruined_downtown"),
                                   burned_market=name.endswith("_burned_market_block"),
                                   flooded_square=name.endswith("_flooded_civic_square"),
                                   scavenger_plaza=name.endswith("_scavenger_plaza"),
                                   ruined_transit=name.endswith("_ruined_transit_plaza"),
                                   cratered_waterfront=name == "wasteland_city_12_cratered_waterfront",
                                   salt_flat=name.endswith("_salt_flat_ambush"),
                                   dust_road=name.endswith("_dust_road_ambush"),
                                   wrecked_highway=name.endswith("_wrecked_highway"),
                                   trainyard=name.endswith("_rusted_trainyard"),
                                   convoy_crossing=name.endswith("_convoy_crossing"))
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
    bridge_access = name.endswith("_bridge_access")
    guardrail_steel = make_material("Galvanized guardrail steel", (.25,.30,.34,1), .73,.53) if freeway or bridge_access else None
    def add_roof_fans(identifier, group, height):
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

    for i, row in enumerate(survey["walls"]):
        identifier = row["id"]
        if row.get("kind") == "water":
            continue
        if wasteland is not None:
            wasteland.add(row)
            continue
        if "points" in row:
            points = [(px*gw/cw-gw/2, gh/2-py*gh/ch) for px, py in row["points"]]
            steel_guardrail = freeway or (bridge_access and identifier.startswith("bridge_") and identifier.endswith("_rail"))
            group = None
            if steel_guardrail or name in ROOFTOPS or name == "city_district_civic_center":
                group = bpy.data.objects.new("Occludable_" + identifier, None)
                bpy.context.collection.objects.link(group)
            for segment, ((ax,ay),(bx,by)) in enumerate(zip(points, points[1:])):
                width = row["width"] * gw/cw
                length = math.hypot(bx-ax, by-ay)
                yaw = math.atan2(by-ay,bx-ax)
                if steel_guardrail:
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
                add_roof_fans(identifier, group, height)
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
                        parapet = box(identifier+" civic roof coping",
                                     ((ax+bx)/2-nx*.045,(ay+by)/2-ny*.045,height+.046),
                                     (length*.496,.055,.052),frame,.012)
                        parapet.rotation_euler.z = yaw
                        parapet.parent = group
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
                    for tier, scale, elevation, material in (
                        ("lower plinth", 1.36, .28, wall),
                        ("upper plinth", 1.12, .39, frame),
                    ):
                        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius*scale,
                                                           depth=.12, location=(sx,sy,elevation))
                        plinth = bpy.context.object
                        plinth.name = "Holo Square "+tier
                        plinth.data.materials.append(material)
                        plinth.parent = island
                    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=.28,
                                                        location=(sx,sy,.57))
                    emitter = bpy.context.object
                    emitter.name = "Holo Square emitter"
                    emitter.data.materials.append(frame)
                    emitter.parent = island
                    for ring_index, (scale,z) in enumerate(((.94,.75),(.84,1.12),(.68,1.49),(.50,1.86)), 1):
                        bpy.ops.mesh.primitive_torus_add(major_segments=8, minor_segments=6,
                                                        major_radius=radius*scale, minor_radius=.024,
                                                        location=(sx,sy,z))
                        halo = bpy.context.object
                        halo.name = f"Holo Square projection ring {ring_index}"
                        halo.data.materials.append(signs[0])
                        halo.parent = island
                    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=radius*.60, radius2=radius*.25,
                                                    depth=1.35, location=(sx,sy,1.40))
                    core = bpy.context.object
                    core.name = "Holo Square projection core"
                    core.data.materials.append(signs[0])
                    core.parent = island
                else:
                    half_width = (max(widths)-min(widths))*.26
                    yaw = .52 if sx*sy > 0 else -.52
                    box(identifier+" projector", (sx,sy,.39),
                        (half_width*.69,.18,.22),frame,.028).parent = island
                    bezel = box(identifier+" display bezel", (sx,sy,.99),
                                (half_width,.061,.43),frame,.028)
                    bezel.rotation_euler.z = yaw
                    bezel.parent = island
                    sign_material = signs[1] if identifier == "sign_sw_base" else signs[0]
                    for side in (-1,1):
                        panel = box(identifier+" display", (sx-side*math.sin(yaw)*.064,
                                    sy+side*math.cos(yaw)*.064,1.02),
                                    (half_width*.84,.013,.35),sign_material,.014)
                        panel.rotation_euler.z = yaw
                        panel.parent = island
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
            if name == "city_exterior_parking_garage":
                across_x = identifier == "center_stair"
                length, width = (w,d) if across_x else (d,w)
                group.location = (x,y,0)
                group.rotation_euler.z = -math.pi/2 if across_x else 0
                for step in range(7):
                    rise = (step+1)*.15
                    along = ((step+.5)/7-.5)*length
                    box("Garage stair tread", (0,along,rise/2),
                        (width*.38,length/14,rise/2),frame).parent = group
                    box("Garage stair nosing", (0,along-length*.064,rise+.01),
                        (width*.36,length*.013,.016),signs[2],.006).parent = group
                for side in (-1,1):
                    box("Garage stair cheek wall", (side*width*.437,0,.58),
                        (width*.039,length*.49,.58),wall,.02).parent = group
                continue
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
        if name == "city_exterior_corporate_plaza" and identifier == "monument":
            box("Corporate monument stone basin", (x,y,.14),
                (w*.48,d*.48,.14),wall,.065).parent = group
            box("Corporate monument inset deck", (x,y,.29),
                (w*.41,d*.41,.025),frame,.026).parent = group
            radius = min(w,d)
            bronze = make_material("Corporate monument bronze", (.30,.132,.038,1), .69,.42)
            for size, elevation in ((.20,.54),(.16,.83),(.12,1.11)):
                tier = box("Corporate monument diamond tier", (x,y,elevation),
                           (radius*size,radius*size,.15),bronze,.023)
                tier.rotation_euler.z = math.pi/4
                tier.parent = group
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius*.105,
                                                 location=(x,y,1.53))
            crest = bpy.context.object
            crest.name = "Corporate monument luminous crest"
            crest.scale.z = 1.26
            crest.data.materials.append(signs[2])
            crest.parent = group
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
        if name.endswith("_industrial_district") and identifier in {"central_w_machine", "central_e_machine"}:
            box(identifier+" skid", (x,y,.115), (w*.48,d*.48,.115), frame,.022).parent = group
            if identifier == "central_e_machine":
                for side in (-1,1):
                    place(library / "roof_twin_fan/optimized.glb", group,
                          (x,y+side*d*.23,.23), (w*.84,d*.42,.53), merge=True)
            else:
                for side in (-1,1):
                    place(library / "industrial_service267/model.glb", group,
                          (x-w*.08,y+side*d*.22,.23), (w*.62,d*.39,1.03), merge=True)
                box("West machinery conduit trunk", (x+w*.35,y,.48),
                    (w*.09,d*.44,.25),frame,.022).parent = group
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
            length, breadth = max(w,d), min(w,d)
            yaw = math.pi/2 if vertical else 0
            surveyed_angle = SURVEYED_CAR_ANGLES.get(name, {}).get(identifier)
            if surveyed_angle is not None:
                yaw = math.radians(surveyed_angle)
                breadth = min(breadth,length*.49)
                c, s = abs(math.cos(yaw)), abs(math.sin(yaw))
                fit = min(w/(length*c+breadth*s),d/(length*s+breadth*c))
                length, breadth = length*fit, breadth*fit
            place(library / "derelict_suv275/model.glb", group, (x, y, 0),
                  (length*.95,breadth*.95,.92), yaw=yaw)
            continue
        if "crane" in identifier:
            submerged_feet = []
            for side in (-1, 1):
                foot = Vector(((x/gw+.5)*cw, (.5-(y+side*d*.32)/gh)*ch))
                if any(intersect_point_tri_2d(foot,*triangle) for triangle in basin_triangles):
                    submerged_feet.append(side)
            build_crane(group, x, y, w, d, frame, shipping_skins[1],
                        height=3.8, outreach=min(2.65, max(w,d)),
                        basin_depth=DOCK_BASIN_DEPTH, submerged_feet=submerged_feet,
                        compact_footings=name == "city_transit_freight_yard")
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
        if name == "city_exterior_downtown_intersection" and identifier == "southeast_kiosk":
            box("Garden kiosk shell", (x,y,.68), (w*.46,d*.46,.68),wall,.055).parent = group
            box("Garden kiosk roof slab", (x,y,1.39), (w*.49,d*.49,.07),frame,.03).parent = group
            green = make_material("Garden kiosk green canopy light", (.07,.55,.13,1), .15,.44, .88)
            for side in (-1,1):
                box("Garden kiosk luminous eave", (x,y+side*d*.467,1.28),
                    (w*.44,.038,.042),green,.013).parent = group
                terrace_y = y+side*d*.19
                box("Garden kiosk raised planter", (x,terrace_y,1.49),
                    (w*.31,d*.11,.067),wall,.024).parent = group
                for offset in (-.22,-.11,0,.11,.22):
                    bpy.ops.mesh.primitive_ico_sphere_add(
                        subdivisions=1, radius=min(w*.059,d*.091),
                        location=(x+offset*w,terrace_y,1.60),
                    )
                    shrub = bpy.context.object
                    shrub.name = "Garden kiosk roof planting"
                    shrub.data.materials.append(foliage)
                    shrub.parent = group
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
        if name == "city_exterior_downtown_intersection" and identifier in {"west_barrier", "east_barrier"}:
            box("Downtown barrier concrete base", (x,y,.13),
                (w*.49,d*.46,.13),wall,.023).parent = group
            box("Downtown barrier steel cap", (x,y,.38),
                (w*.48,d*.31,.047),frame,.012).parent = group
            bays = 5 if identifier == "west_barrier" else 3
            for index in range(bays):
                bay_x = x+w*((index+.5)/bays-.5)*.93
                box("Downtown barrier steel brace", (bay_x,y,.24),
                    (w*.045,d*.43,.17),frame,.013).parent = group
                box("Downtown barrier marker", (bay_x,y-d*.32,.345),
                    (w*.022,d*.035,.020),signs[0],.006).parent = group
            continue
        if name == "city_district_riot_square" and identifier.startswith("barricade_"):
            box("Riot barricade footing", (x,y,.105),
                (w*.46,d*.49,.105),wall,.025).parent = group
            for elevation in (.31,.64):
                box("Riot barricade rail", (x,y,elevation),
                    (w*.15,d*.49,.038),frame,.009).parent = group
            for offset in (-.44,-.22,0,.22,.44):
                box("Riot barricade upright", (x,y+d*offset,.40),
                    (w*.12,.055,.28),frame,.010).parent = group
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
                if (civic or transport_facades or industrial) and abs(face.normal.z) < .1:
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
        add_roof_fans(identifier, group, height)
        direction = -1 if y > 0 else 1
        front = y + direction*d/2
        angle = 0 if direction < 0 else math.pi
        if name == "city_exterior_corporate_plaza" and "_tower_" in identifier:
            inward = 1 if identifier.startswith("west") else -1
            if identifier.endswith("_middle"):
                duct_x = (135 if inward > 0 else 826)*gw/cw-gw/2
                duct_y = gh/2-254*gh/ch
                duct_length = 96*gh/ch
                duct_width = 15*gw/cw
                box(identifier+" rooftop duct curb", (duct_x,duct_y,height+.036),
                    (duct_width*.56,duct_length*.51,.041),frame,.016).parent = group
                for offset in (-.33,0,.33):
                    box(identifier+" rooftop duct section", (duct_x,duct_y+duct_length*offset,height+.13),
                        (duct_width*.43,duct_length*.161,.10),wall,.022).parent = group
            entrance_x = x+inward*w/2
            entry_width = min(.65,d*.16)
            box(identifier+" plaza entrance surround", (entrance_x+inward*.05,y,.99),
                (.075,entry_width, .99),frame,.023).parent = group
            box(identifier+" plaza entrance glazing", (entrance_x+inward*.128,y,.95),
                (.022,entry_width*.83,.86),wall,.012).parent = group
            box(identifier+" plaza entrance canopy", (entrance_x+inward*.19,y,2.03),
                (.22,entry_width*1.16,.075),frame,.016).parent = group
            box(identifier+" plaza entrance light", (entrance_x+inward*.40,y,2.015),
                (.024,entry_width*.99,.029),signs[1 if inward > 0 else 0],.007).parent = group
        if civic:
            for side in (-1,1):
                box(identifier+" civic roof coping", (x,y+side*(d/2-.055),height+.046),
                    (w*.496,.055,.052),frame,.012).parent = group
                box(identifier+" civic roof coping", (x+side*(w/2-.055),y,height+.046),
                    (.055,max(.05,d/2-.11),.052),frame,.012).parent = group
        for offset in (-.3, .3):
            place(library / "urban_facade280/window.glb", group,
                  (x+w*offset, front+direction*.04, .9), (min(1.65,w*.33), .28, 1.7), yaw=angle)
        if transport_facades and w >= 2.4 and height >= 3.2:
            if name.endswith("_transit_interchange"):
                entry_width = min(.48,w*.14)
                box(identifier+" transit entry surround", (x,front+direction*.045,.84),
                    (entry_width,.057,.84),frame,.015).parent = group
                box(identifier+" transit entry door", (x,front+direction*.112,.81),
                    (entry_width*.84,.018,.78),wall,.012).parent = group
                box(identifier+" transit entry canopy", (x,front+direction*.15,1.78),
                    (entry_width*1.17,.17,.052),frame,.016).parent = group
            upper_level = height*.62
            box(identifier + " transport facade lintel", (x,front+direction*.035,upper_level-.09),
                (w*.47,.065,.055), frame,.012).parent = group
            bays = (-.23,.23) if i % 2 else (0,)
            for offset in bays:
                place(library / "urban_facade280/window.glb", group,
                      (x+w*offset,front+direction*.05,upper_level),
                      (min(1.75,w*.34),.28,min(.85,height-upper_level-.22)), yaw=angle, merge=True)
        if name.endswith("_industrial_district") and height >= 2.4 and d >= 2.0:
            rear = y-direction*d/2
            door_width = min(.49,w*.17)
            box(identifier+" industrial rear door frame", (x,rear-direction*.036,.88),
                (door_width,.052,.88),frame,.014).parent = group
            box(identifier+" industrial rear door panel", (x,rear-direction*.084,.84),
                (door_width*.83,.021,.81),wall,.010).parent = group
            box(identifier+" industrial rear door hood", (x,rear-direction*.11,1.82),
                (door_width*1.12,.115,.052),frame,.012).parent = group
            for side in (-1,1):
                flank = x+side*w/2
                box(identifier+" industrial side lintel", (flank,y,height-.24),
                    (.045,d*.47,.058),frame,.012).parent = group
                for offset in (-.31,0,.31):
                    box(identifier+" industrial side pilaster",
                        (flank,y+d*offset,height*.48),
                        (.062,.05,height*.43),frame,.012).parent = group
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
                if freeway and height >= 3.2:
                    place(library / "urban_facade280/window.glb", group,
                          (door_x, back-direction*.05, height*.65),
                          (min(1.6,w*.35), .28, .72), yaw=angle+math.pi, merge=True)
                    box(identifier + " rear utility conduit", (x-w*.40,back-direction*.06,height*.46),
                        (.035,.045,height*.40), frame,.01).parent = group
        if industrial:
            if height >= 2.4:
                for side in (-1,1):
                    box(identifier + " warehouse eave flashing",
                        (x+side*w/2,y,height-.15),(.045,d*.49,.055),frame,.01).parent = group
                box(identifier + " warehouse rear eave flashing",
                    (x,y-direction*d/2,height-.15),(w*.49,.045,.055),frame,.01).parent = group
            door_width = min(w*.48, 3.3)
            box(identifier + " loading shutter", (x,front+direction*.07,.95),
                (door_width/2,.08,.95), frame).parent = group
            for slat in range(1,9):
                box(identifier + " shutter slat", (x,front+direction*.157,slat*.20),
                    (door_width*.48,.012,.02), wall).parent = group
            if w >= 3 and height >= 2.4:
                box(identifier + " loading shutter hood", (x,front+direction*.13,1.98),
                    (door_width*.54,.16,.10), frame,.025).parent = group
                for side in (-1,1):
                    jamb_x = x+side*door_width*.52
                    box(identifier + " loading shutter guide", (jamb_x,front+direction*.11,.94),
                        (.047,.077,.94), frame,.012).parent = group
                    box(identifier + " loading dock bumper", (jamb_x,front+direction*.18,.32),
                        (.085,.12,.23), wall,.028).parent = group
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
    if name.endswith("_irradiated_basin"):
        water = textured_material("Irradiated basin water", out / "floor.png", .31)
        wasteland.add_irradiated_basin_surfaces(water)
    if wasteland and wasteland.ruined_transit:
        wasteland.add_transit_south_carriage()
    if wasteland and wasteland.flooded_square:
        water = textured_material("Flooded paving under shallow water", out / "floor.png", .29)
        wasteland.add_flooded_square_surface(water)
    if wasteland and wasteland.cratered_waterfront:
        water = textured_material("Cratered waterfront water", out / "floor.png", .25)
        for row in survey["walls"]:
            if row.get("kind") == "water":
                wasteland.add_water_surface("Water surface "+row["id"], water, row["polygon"])
        wasteland.add_waterfront_wrecks()
    if wasteland and wasteland.overpass:
        wasteland.add_overpass_ramps(floor)
    if name in ROOFTOPS:
        build_rooftop_ground(out, floor, (gw,gh), (cw,ch), library)
    elif waterfront:
        water = textured_material("Waterfront basin water", out / "floor.png", .32)
        build_rooftop_ground(out, floor, (gw,gh), (cw,ch), library, water=water)
    elif flood_avenue:
        water = textured_material("Shallow avenue floodwater", out / "floor.png", .26)
        build_rooftop_ground(out, floor, (gw,gh), (cw,ch), library, water=water, shallow=True)
    elif bridge_access:
        rivers = {row["id"]: row["polygon"] for row in survey["walls"] if row.get("kind") == "water"}
        water = textured_material("Bridge river water", out / "floor.png", .32)
        build_bridge_surfaces(floor, water, wall, (gw,gh), (cw,ch), rivers["north_river"], rivers["south_river"])
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
    if name == "city_transit_freight_yard":
        railhead = make_material("Freight yard worn rail steel", (.14,.16,.17,1), .72,.48)
        rail_web = make_material("Freight yard oxidized rail web", (.063,.049,.035,1), .63,.76)
        # Keep the raised profiles over the painted rail lines and their original sleepers.
        for left, right, rows in ((83,860,(132,146)), (128,868,(332,346))):
            center_x = (left+right)*gw/(2*cw)-gw/2
            half_length = (right-left)*gw/(2*cw)
            for row in rows:
                rail_y = gh/2-row*gh/ch
                box("Freight yard rail foot", (center_x,rail_y,-.013),
                    (half_length,.037,.012),rail_web,.006)
                box("Freight yard rail web", (center_x,rail_y,.012),
                    (half_length,.012,.015),rail_web,.003)
                box("Freight yard running rail", (center_x,rail_y,.033),
                    (half_length,.022,.008),railhead,.005)
        wagon_skin = make_material("Freight wagon faded red", (.22,.052,.033,1), .55,.72)
        for index, (left, top, right, bottom) in enumerate(SOUTH_SIDING_LOADS, 1):
            wagon = bpy.data.objects.new(f"South siding cargo wagon {index}", None)
            bpy.context.collection.objects.link(wagon)
            x = (left+right)*gw/(2*cw)-gw/2
            y = gh/2-(top+bottom)*gh/(2*ch)
            length, width = (right-left)*gw/cw, (bottom-top)*gh/ch
            box("Freight wagon underframe", (x,y,.20),
                (length*.48,width*.44,.09),rail_web,.018).parent = wagon
            for side in (-1,1):
                bogie_x = x+side*length*.29
                box("Freight wagon bogie", (bogie_x,y,.134),
                    (length*.105,width*.29,.055),rail_web,.028).parent = wagon
                for axle in (-1,1):
                    for wheel_side in (-1,1):
                        bpy.ops.mesh.primitive_cylinder_add(
                            vertices=12, radius=.085, depth=.048,
                            location=(bogie_x+axle*length*.057,y+wheel_side*width*.30,.074),
                            rotation=(math.pi/2,0,0),
                        )
                        wheel = bpy.context.object
                        wheel.name = "Freight wagon steel wheel"
                        wheel.data.materials.append(railhead)
                        wheel.parent = wagon
            load = build_container(wagon, x, y, length*.95, width*.90,
                                   wagon_skin, railhead, rail_web)
            load.scale.z = .40
            load.location.z = .29+.88*load.scale.z
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "environment.blend"))
    bpy.ops.export_scene.gltf(filepath=str(out / "environment.glb"), export_format="GLB")
    print("BILLBOARD_AVENUE_EXPORTED", name, sum(row.get("kind") != "water" for row in survey["walls"]))


maps = sys.argv[sys.argv.index("--") + 1:]
if not maps or any(Path(name).name != name for name in maps):
    raise ValueError("Pass one or more original map IDs after --")
for map_name in maps:
    build(map_name)
