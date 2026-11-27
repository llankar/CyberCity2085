"""Build original urban streets using shared facade and street furniture modules."""
import json
import math
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place, reset_library_cache
from loading_crane import build_crane
from shipping_container import build_container
from wasteland_outdoor import WastelandOutdoors

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


def build(name):
    reset_library_cache()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    out = LAB / "generated/phase2/billboard_avenues" / name
    survey = json.loads((MAPS / f"{name}.wall-traces.json").read_text())
    gw, gh = json.loads((MAPS / f"{name}.walls.json").read_text())["grid"]
    cw, ch = survey["canvas_size"]
    industrial = name.endswith(("freight_yard", "industrial_district"))
    library = LAB / "environment-library/assets"
    wasteland = (WastelandOutdoors(library, (gw,gh), (cw,ch), city=name.startswith("wasteland_city_"))
                 if name.startswith(("wasteland_outdoor_", "wasteland_city_")) else None)
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
    foliage = make_material("Hardy street shrubs", (.062, .116, .043, 1), .03, .84)
    leaf_tips = make_material("New shrub growth", (.14, .22, .072, 1), .03, .88)
    shipping_skins = [make_material("Shipping enamel", color, .55, .64) for color in (
        (.07,.17,.19,1), (.27,.081,.05,1), (.17,.21,.095,1)
    )]
    roof = textured_material("Original rooftop artwork", MAPS / f"{name}.png", .8)
    for i, row in enumerate(survey["walls"]):
        identifier = row["id"]
        if row.get("kind") == "water":
            continue
        if wasteland is not None:
            wasteland.add(row)
            continue
        if "points" in row:
            points = [(px*gw/cw-gw/2, gh/2-py*gh/ch) for px, py in row["points"]]
            for (ax,ay),(bx,by) in zip(points, points[1:]):
                width = row["width"] * gw/cw
                length = math.hypot(bx-ax, by-ay)
                rail = box(identifier, ((ax+bx)/2,(ay+by)/2,.24),
                           (length/2,width/2,.24), frame)
                rail.rotation_euler.z = math.atan2(by-ay,bx-ax)
            continue
        if "polygon" in row and not identifier.endswith("_car"):
            points = [(px*gw/cw-gw/2, gh/2-py*gh/ch) for px, py in row["polygon"]]
            if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points, points[1:]+points[:1])) < 0:
                points.reverse()
            count = len(points)
            faces = [tuple(reversed(range(count))), tuple(range(count, 2*count))]
            faces.extend((j, (j+1)%count, (j+1)%count+count, j+count) for j in range(count))
            mesh = bpy.data.meshes.new(identifier)
            is_planter = "planter" in identifier
            is_building = "building" in identifier
            height = 2.8+i%3*.5 if is_building else .68 if identifier.endswith("_high") else .31 if is_planter else .22
            mesh.from_pydata([(x,y,z) for z in (0,height) for x,y in points], [], faces)
            mesh.materials.append(wall)
            if is_planter:
                mesh.materials.append(foliage)
                mesh.polygons[1].material_index = 1
            island = bpy.data.objects.new(identifier, mesh)
            bpy.context.collection.objects.link(island)
            if is_building:
                mesh.materials.append(roof)
                mesh.polygons[1].material_index = 1
                uv = mesh.uv_layers.new()
                for loop in mesh.polygons[1].loop_indices:
                    vx,vy,_ = mesh.vertices[mesh.loops[loop].vertex_index].co
                    uv.data[loop].uv = (vx/gw+.5, vy/gh+.5)
            if identifier.startswith("sign_") or "holo_platform" in identifier:
                sx = sum(px for px,_ in points)/count
                sy = sum(py for _,py in points)/count
                widths = [px for px,_ in points]
                depth = [py for _,py in points]
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
            vertical = d > w
            length, width = (d,w) if vertical else (w,d)
            group.location = (x,y,0)
            group.rotation_euler.z = math.pi/2 if vertical else 0
            skin = shipping_skins[1]
            parts = [
                ("counterweight", (-length*.19,0,.28), (length*.27,width*.40,.23), skin),
                ("cab", (-length*.11,0,.66), (length*.21,width*.32,.24), frame),
                ("mast", (length*.14,0,.58), (.055,width*.31,.57), frame),
            ]
            parts.extend(("fork", (length*.30,width*side*.19,.09),
                          (length*.19,width*.064,.034), frame) for side in (-1,1))
            for label, position, size, material in parts:
                box(identifier + " " + label, position, size, material).parent = group
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
            box(identifier + " plinth", (x, y, .11), (w*.49, d*.47, .11), frame).parent = group
            box(identifier, (x, y, height/2), (w*.42, d*.29, height/2), wall).parent = group
            direction = -1 if y > 0 else 1
            box(identifier + " screen", (x, y+direction*d*.30, height*.72),
                (w*.36, .03, height*.20), signs[i % len(signs)]).parent = group
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
