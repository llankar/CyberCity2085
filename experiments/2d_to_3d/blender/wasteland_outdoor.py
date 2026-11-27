"""Build the surveyed props shared by the original outdoor wasteland maps."""
import math

import bpy
import numpy as np
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

from create_hardsurface_crate import box, make_material
from library_placement import place
from loading_crane import build_crane
from shipping_container import build_container
from waterfront_skiffs import SKIFFS


class WastelandOutdoors:
    def add_waterfront_wrecks(self):
        for name, stern, bow, beam in (
            ("West edge cargo wreck", (13,445), (204,345), 59),
            ("West basin wreck", (274,477), (340,390), 40),
            # Keep the hull on the water side of the quay running at x=557.
            ("East basin wreck", (522,482), (531,369), 38),
        ):
            ax, ay = self.coordinates(*stern)
            bx, by = self.coordinates(*bow)
            length = math.hypot(bx-ax,by-ay)
            width = beam*self.gw/self.cw
            outline = ((-.49,-.32), (.27,-.50), (.49,-.12), (.50,0),
                       (.49,.12), (.27,.50), (-.49,.32))
            vertices = [(x*length*taper,y*width*taper,z)
                        for taper,z in ((.84,-.025),(1,.33)) for x,y in outline]
            size = len(outline)
            faces = [tuple(range(size,2*size))]
            for i in range(size):
                j = (i+1)%size
                faces.append((i,j,j+size,i+size))
            mesh = bpy.data.meshes.new(name+" hull")
            mesh.from_pydata(vertices, [], faces)
            mesh.materials.append(self.dark)
            mesh.materials.append(self.steel)
            for face in list(mesh.polygons)[1:]:
                face.material_index = 1
            hull = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(hull)
            for offset in (-.28,-.02,.23):
                frame = box("Exposed shipwreck deck frame", (length*offset,0,.38),
                            (.044,width*.35,.042), self.steel,.012)
                frame.parent = hull
            if name == "West edge cargo wreck":
                for offset in (-.29, -.10, .09):
                    for side in (-1, 1):
                        box("Cargo hatch longitudinal coaming",
                            (length*offset,side*width*.245,.43),
                            (length*.07,width*.023,.09),self.steel,.016).parent = hull
                        box("Cargo hatch end coaming",
                            (length*(offset+side*.066),0,.43),
                            (length*.012,width*.224,.09),self.steel,.016).parent = hull
                    box("Exposed cargo hold floor", (length*offset,0,.347),
                        (length*.055,width*.220,.012),self.dark,.008).parent = hull
            else:
                for side in (-1, 1):
                    box("Basin wreck inner deck stringer", (-length*.06,side*width*.22,.389),
                        (length*.30,.030,.040),self.steel,.009).parent = hull
                for offset, angle in ((-.19,.23),(.12,-.29)):
                    plate = box("Basin wreck buckled deck plate", (length*offset,0,.405),
                                (length*.075,width*.14,.022),self.steel,.012)
                    plate.rotation_euler = (.16,0,angle)
                    plate.parent = hull
            hull.location = ((ax+bx)/2,(ay+by)/2,0)
            hull.rotation_euler.z = math.atan2(by-ay,bx-ax)

        for name, stern, bow, beam in SKIFFS:
            ax, ay = self.coordinates(*stern)
            bx, by = self.coordinates(*bow)
            length = math.hypot(bx-ax,by-ay)
            width = beam*self.gw/self.cw
            outline = ((-.5,-.36), (.18,-.5), (.5,0), (.18,.5), (-.5,.36))
            vertices = [(px*length*taper,py*width*taper,z)
                        for taper,z in ((.73,.04),(1,.22)) for px,py in outline]
            mesh = bpy.data.meshes.new("Landing skiff shell")
            mesh.from_pydata(vertices, [], [(0,1,2,3,4)] +
                             [(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)])
            mesh.materials.append(self.steel)
            hull = bpy.data.objects.new(f"East landing skiff {name}", mesh)
            bpy.context.collection.objects.link(hull)
            for offset in (-.24,.06):
                box("Landing skiff bench", (length*offset,0,.19),
                    (length*.07,width*.34,.026), self.dark,.008).parent = hull
            box("Landing skiff raised foredeck", (length*.235,0,.265),
                (length*.105,width*.32,.065), self.steel,.026).parent = hull
            for side in (-1,1):
                rail = box("Landing skiff worn gunwale", (-length*.16,side*width*.426,.225),
                           (length*.34,.024,.022), self.dark,.008)
                rail.rotation_euler.z = side*math.atan2(width*.14,length*.68)
                rail.parent = hull
            hull.location = ((ax+bx)/2,(ay+by)/2,0)
            hull.rotation_euler.z = math.atan2(by-ay,bx-ax)

    def add_flooded_square_surface(self, material):
        # The water follows the central plaza between the raised sidewalks.
        shoreline = ((151,209), (114,202), (110,158), (160,141), (192,102),
                     (232,107), (273,121), (367,119), (413,100), (450,82),
                     (528,85), (588,109), (697,116), (740,119), (781,148),
                     (825,159), (815,203), (789,218), (784,302), (790,390),
                     (765,419), (698,422), (624,421), (570,464), (379,464),
                     (327,424), (222,424), (181,447), (148,416), (144,346))
        self.add_water_surface("Flooded civic square water surface", material,
                               [(px*self.cw/960, py*self.ch/540) for px, py in shoreline])

    def add_irradiated_basin_surfaces(self, material):
        # Follow the green pools separately so the raised islands stay dry.
        pools = (
            ((181,87),(213,107),(261,132),(288,130),(312,177),(347,224),
             (321,262),(275,232),(234,202),(187,207),(165,161)),
            ((154,236),(181,237),(206,262),(196,300),(215,333),(267,361),
             (263,389),(208,420),(174,421),(142,392),(112,352),(100,307)),
            ((478,71),(533,72),(572,91),(632,81),(648,116),(598,153),
             (582,194),(599,232),(645,244),(668,288),(630,304),(589,272),
             (551,262),(523,227),(510,186),(490,151)),
            ((802,100),(816,110),(815,157),(787,194),(810,225),(833,239),
             (858,272),(843,304),(801,332),(775,378),(743,410),(697,380),
             (677,351),(698,310),(738,285),(775,262),(768,231),(764,198),
             (726,180),(712,154),(729,126),(766,111)),
        )
        for index, shoreline in enumerate(pools, 1):
            self.add_water_surface(f"Irradiated basin pool {index}", material,
                                   [(px*self.cw/960, py*self.ch/540) for px, py in shoreline])

    def add_water_surface(self, name, material, shoreline):
        points = [self.coordinates(*point) for point in shoreline]
        if sum(ax*by-bx*ay for (ax,ay),(bx,by) in zip(points, points[1:]+points[:1])) < 0:
            points.reverse()
        vertices = [(x,y,-.012) for x,y in points]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(vertices, [], [tuple(range(len(vertices)))])
        mesh.materials.append(material)
        uv = mesh.uv_layers.new()
        for loop in mesh.loops:
            x, y, _ = vertices[loop.vertex_index]
            uv.data[loop.index].uv = (x/self.gw+.5, y/self.gh+.5)
        bpy.context.collection.objects.link(bpy.data.objects.new(name, mesh))

    def add_overpass_ramps(self, floor):
        # Pairs follow the painted road shoulders on the 960 x 540 survey.
        shoulders = (
            (((60,237),(119,225)), ((70,157),(135,159)), ((106,90),(167,118)),
             ((169,42),(206,91)), ((242,16),(251,73)), ((313,16),(306,77)),
             ((372,48),(343,97)), ((408,106),(364,125)), ((430,173),(374,174))),
            (((529,199),(582,185)), ((543,128),(598,144)), ((581,64),(630,112)),
             ((642,27),(673,80)), ((719,15),(718,73)), ((786,31),(760,87)),
             ((837,69),(794,107)), ((869,122),(818,140))),
            (((57,371),(124,354)), ((89,424),(145,389)), ((138,475),(180,423)),
             ((207,500),(222,443)), ((276,501),(264,443)), ((339,479),(308,428)),
             ((381,432),(340,393)), ((414,358),(356,353))),
            (((960,349),(960,419)), ((899,336),(889,407)), ((831,331),(823,405)),
             ((758,335),(769,414)), ((697,354),(725,433)), ((649,387),(692,460)),
             ((617,428),(671,489)), ((620,493),(684,523)), ((657,540),(704,540))),
        )
        for number, ramp in enumerate(shoulders, 1):
            # Bring both approaches down to meet the painted junctions.
            heights = [.008 + .192*min(index/2, (len(ramp)-1-index)/2, 1)
                       for index in range(len(ramp))]
            vertices = [(*self.coordinates(px*self.cw/960, py*self.ch/540),
                         -.024 if underside else heights[index])
                        for underside in (False, True)
                        for index, pair in enumerate(ramp) for px, py in pair]
            bottom = len(vertices)//2
            faces = []
            for index in range(0, bottom-2, 2):
                face = (index, index+1, index+3, index+2)
                a, b, c = (Vector(vertices[i]) for i in face[:3])
                if (b-a).cross(c-a).z < 0:
                    face = face[::-1]
                faces.append(face)
            top_count = len(faces)
            for face in faces[:]:
                for a, b in zip(face, face[1:]+face[:1]):
                    if a//2 != b//2 or min(a,b) in (0,bottom-2):
                        faces.append((b,a,a+bottom,b+bottom))
                faces.append(tuple(index+bottom for index in reversed(face)))
            name = f"Collapsed overpass ramp {number}"
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(vertices, [], faces)
            mesh.materials.append(floor)
            mesh.materials.append(self.seam)
            uv = mesh.uv_layers.new()
            for face in mesh.polygons:
                face.material_index = int(face.index >= top_count)
                for loop in face.loop_indices:
                    x,y,_ = vertices[mesh.loops[loop].vertex_index]
                    uv.data[loop].uv = (x/self.gw+.5, y/self.gh+.5)
            bpy.context.collection.objects.link(bpy.data.objects.new(name, mesh))

    def __init__(self, library, grid, canvas, *, city=False, overpass=False,
                 ruined_downtown=False, burned_market=False, flooded_square=False,
                 scavenger_plaza=False, ruined_transit=False, cratered_waterfront=False,
                 salt_flat=False, dust_road=False, wrecked_highway=False, trainyard=False, irradiated_basin=False,
                 convoy_crossing=False):
        self.library = library
        self.gw, self.gh = grid
        self.cw, self.ch = canvas
        self.city = city
        self.overpass = overpass
        self.ruined_downtown = ruined_downtown
        self.burned_market = burned_market
        self.flooded_square = flooded_square
        if flooded_square:
            self.planter_silt = make_material("Flooded planter wet silt", (.085,.065,.034,1), 0,.79)
        self.scavenger_plaza = scavenger_plaza
        self.ruined_transit = ruined_transit
        if ruined_transit:
            self.platform_warning = make_material("Faded station safety yellow", (.42,.26,.05,1), .06,.86)
        self.cratered_waterfront = cratered_waterfront
        self.salt_flat = salt_flat
        self.dust_road = dust_road
        self.irradiated_basin = irradiated_basin
        if scavenger_plaza:
            self.stall_fabric = {
                label: make_material(f"Salvaged canvas {label}", (*color,1), .02,.93)
                for label, color in (("rust", (.13,.056,.041)), ("sand", (.15,.116,.078)),
                                     ("blue", (.038,.073,.094)), ("olive", (.072,.082,.047)))
            }
        if burned_market:
            self.scorched_canvas = make_material("Scorched market canvas", (.23,.16,.10,1), .03,.93)
            self.red_canvas = make_material("Scorched rust-red canvas", (.23,.065,.037,1), .03,.94)
            self.blue_sheet = make_material("Weathered blue corrugated steel", (.055,.13,.17,1), .52,.78)
        self.wrecked_highway = wrecked_highway
        self.trainyard = trainyard
        self.convoy_crossing = convoy_crossing
        if convoy_crossing:
            self.convoy_tarps = {
                "olive": make_material("Convoy weathered olive tarp", (.074,.082,.043,1), 0,.94),
                "tan": make_material("Convoy weathered tan tarp", (.15,.114,.075,1), 0,.94),
            }
        self.surveyed_surface = None
        self.stone = make_material("Fractured concrete", (.19,.14,.097,1), .09,.93)
        self.aggregate = make_material("Exposed concrete aggregate", (.28,.215,.151,1), .04,.96)
        concrete_path = library.parents[1] / "sources/environment169/concrete_wall_001"
        nodes = self.aggregate.node_tree.nodes
        links = self.aggregate.node_tree.links
        shader = nodes.get("Principled BSDF")
        diffuse = nodes.new("ShaderNodeTexImage")
        source = bpy.data.images.load(str(concrete_path / "diff.jpg"), check_existing=True)
        pixels = np.empty(len(source.pixels), dtype=np.float32)
        source.pixels.foreach_get(pixels)
        concrete_tint = (.62, .58, .54)
        if overpass or wrecked_highway:
            concrete_tint = (.40, .40, .38)
        elif flooded_square:
            concrete_tint = (.34, .40, .43)
        elif ruined_downtown:
            concrete_tint = (.37, .39, .40)
        pixels.reshape(-1, 4)[:, :3] *= concrete_tint
        diffuse.image = bpy.data.images.new("Weathered Wasteland concrete", *source.size)
        diffuse.image.pixels.foreach_set(pixels)
        diffuse.image.pack()
        links.new(diffuse.outputs["Color"], shader.inputs["Base Color"])
        roughness = nodes.new("ShaderNodeTexImage")
        roughness.image = bpy.data.images.load(str(concrete_path / "rough.jpg"), check_existing=True)
        roughness.image.colorspace_settings.name = "Non-Color"
        links.new(roughness.outputs["Color"], shader.inputs["Roughness"])
        if overpass or wrecked_highway or flooded_square or ruined_downtown:
            detail = nodes.new("ShaderNodeTexImage")
            detail.image = bpy.data.images.load(str(concrete_path / "nor_gl.jpg"), check_existing=True)
            detail.image.colorspace_settings.name = "Non-Color"
            normal = nodes.new("ShaderNodeNormalMap")
            normal.inputs["Strength"].default_value = .55
            links.new(detail.outputs["Color"], normal.inputs["Color"])
            links.new(normal.outputs["Normal"], shader.inputs["Normal"])
        self.seam = make_material("Dark fractured concrete edge", (.095,.073,.052,1), .04,.95)
        if overpass or wrecked_highway:
            self.deck_backing = self.seam.copy()
            self.deck_backing.name = "Road fracture backing"
        self.steel = make_material("Corroded steel", (.13,.073,.042,1), .62,.69)
        if convoy_crossing:
            self.convoy_steel = self.steel.copy()
            self.convoy_steel.name = "Convoy worn body steel"
            self.convoy_rubber = make_material("Convoy dusty tire rubber", (.016,.014,.012,1), 0,.91)
            self.convoy_glass = make_material("Convoy smoked cab glass", (.012,.025,.030,1), .14,.42)
            tree = self.convoy_steel.node_tree
            shader = tree.nodes["Principled BSDF"]
            texture_root = library.parents[1] / "sources/environment169/blue_metal_plate"
            normal = tree.nodes.new("ShaderNodeNormalMap")
            normal.inputs["Strength"].default_value = .34
            for filename, target in (("rough.jpg", shader.inputs["Roughness"]),
                                     ("nor_gl.jpg", normal.inputs["Color"])):
                image = tree.nodes.new("ShaderNodeTexImage")
                image.image = bpy.data.images.load(str(texture_root / filename), check_existing=True)
                image.image.colorspace_settings.name = "Non-Color"
                tree.links.new(image.outputs["Color"], target)
            tree.links.new(normal.outputs["Normal"], shader.inputs["Normal"])
        if self.ruined_downtown or self.flooded_square or self.ruined_transit or self.cratered_waterfront:
            self.facade_blue = make_material("Faded blue enamel", (.035,.115,.147,1), .54,.78)
        self.dark = make_material("Weathered undercarriage", (.046,.039,.032,1), .4,.82)
        self.canvas = make_material("Weathered sandbags", (.21,.17,.11,1), 0,.94)
        if dust_road:
            self.canvas = make_material("Dust Road stained canvas", (.105,.083,.054,1), 0,.96)
            self.canvas_faded = make_material("Dust Road faded canvas", (.154,.125,.082,1), 0,.95)

    @staticmethod
    def project_concrete_uv(mesh):
        mesh.update()
        uv = mesh.uv_layers.active or mesh.uv_layers.new()
        for face in mesh.polygons:
            dominant = max(range(3), key=lambda axis: abs(face.normal[axis]))
            axes = [axis for axis in range(3) if axis != dominant]
            for loop in face.loop_indices:
                point = mesh.vertices[mesh.loops[loop].vertex_index].co
                uv.data[loop].uv = tuple(point[axis] / 2 for axis in axes)

    def concrete_box(self, name, position, scale, bevel=.025):
        block = box(name, position, scale, self.aggregate, bevel)
        self.project_concrete_uv(block.data)
        return block

    def concrete_guardrail(self, name, length, width, height):
        profile = [(-width/2,0), (width/2,0), (width/2,height*.19),
                   (width*.30,height*.42), (width*.23,height),
                   (-width*.23,height), (-width*.30,height*.42), (-width/2,height*.19)]
        count = len(profile)
        vertices = [(end, y, z) for end in (-length/2,length/2) for y,z in profile]
        faces = [tuple(reversed(range(count))), tuple(range(count,2*count))]
        for index in range(count):
            following = (index+1)%count
            faces.append((index,following,following+count,index+count))
        mesh = bpy.data.meshes.new(name + " sloped guardrail")
        mesh.from_pydata(vertices, [], faces)
        self.project_concrete_uv(mesh)
        mesh.materials.append(self.aggregate)
        obj = bpy.data.objects.new(name + " sloped guardrail", mesh)
        bpy.context.collection.objects.link(obj)
        return obj

    def coordinates(self, px, py):
        return px*self.gw/self.cw-self.gw/2, self.gh/2-py*self.gh/self.ch

    def add(self, row):
        name = row["id"]
        group = bpy.data.objects.new("Occludable_" + name, None)
        bpy.context.collection.objects.link(group)
        if "points" in row:
            points = [self.coordinates(*point) for point in row["points"]]
            width = row["width"] * self.gw/self.cw
            if self.salt_flat:
                self.salt_flat_fence(group, points, width)
                return
            if self.ruined_transit:
                self.transit_boundary(group, name, points, width)
                return
            for i, ((ax,ay),(bx,by)) in enumerate(zip(points, points[1:])):
                height = .56 + .15*(i % 3)
                length = math.hypot(bx-ax,by-ay)
                if self.dust_road:
                    center = ((ax+bx)/2, (ay+by)/2)
                    yaw = math.atan2(by-ay,bx-ax)
                    segment = self.concrete_box("Dust road masonry base", (*center,.15),
                                                (length*.49,width*.46,.15))
                    rail = box("Dust road salvaged wall panel", (*center,.38),
                               (length*.44,width*.27,.12), self.steel,.024)
                    rail.rotation_euler.z = yaw
                    rail.parent = group
                    for offset in (-.38,.32):
                        post = box("Dust road wall brace",
                                   (center[0]+offset*(bx-ax),center[1]+offset*(by-ay),.26),
                                   (.045,width*.48,.26), self.dark,.013)
                        post.rotation_euler.z = yaw
                        post.parent = group
                elif name in {"northeast_barricade", "southwest_barricade"}:
                    midpoint = ((ax+bx)/2, (ay+by)/2)
                    yaw = math.atan2(by-ay,bx-ax)
                    segment = box("Scavenger scrap barricade", (*midpoint,height/2),
                                  (length*.48,width*.42,height*.45), self.steel,.035)
                    for offset, lift, material in ((-.28,.78,self.dark),(.04,.91,self.steel),(.33,.73,self.dark)):
                        plate = box("Scavenger overlapping scrap plate",
                                    (midpoint[0]+offset*(bx-ax),midpoint[1]+offset*(by-ay),height*lift),
                                    (length*.145,width*.44,height*.13),material,.014)
                        plate.rotation_euler.z = yaw
                        plate.parent = group
                    for offset in (-.36,.0,.36):
                        post = box("Scavenger barricade brace",
                                   (midpoint[0]+offset*(bx-ax), midpoint[1]+offset*(by-ay), height*.49),
                                   (min(.055,length*.06),width*.48,height*.49), self.dark,.012)
                        post.rotation_euler.z = yaw
                        post.parent = group
                elif name in {"quay_west", "quay_east", "quay_crater_w"}:
                    self.waterfront_quay_segment(group, name, ax, ay, bx, by, width)
                    continue
                elif self.irradiated_basin:
                    count = max(1, round(length/.62))
                    yaw = math.atan2(by-ay,bx-ax)
                    for block_index in range(count):
                        offset = (block_index+.5)/count
                        block_height = height*(.74,.90,1.0)[block_index%3]
                        block = self.concrete_box("Basin retaining masonry",
                                                  (ax+(bx-ax)*offset,ay+(by-ay)*offset,block_height/2),
                                                  (length*.485/count,width*.47,block_height/2),.035)
                        block.rotation_euler.z = yaw
                        block.parent = group
                    continue
                elif self.convoy_crossing:
                    count = max(1, round(length / .85))
                    yaw = math.atan2(by-ay,bx-ax)
                    for index in range(count):
                        offset = (index+.5)/count
                        block_height = (.38, .29, .35, .23)[(i+index)%4]
                        block = self.concrete_guardrail("Convoy chipped roadside barrier",
                                                       length*.95/count, width*.92, block_height)
                        block.location = (ax+(bx-ax)*offset, ay+(by-ay)*offset, 0)
                        block.rotation_euler.z = yaw
                        block.parent = group
                    continue
                elif self.overpass:
                    segment = self.concrete_guardrail(name,length,width,height)
                    segment.location = ((ax+bx)/2,(ay+by)/2,0)
                else:
                    segment = self.concrete_box(name, ((ax+bx)/2,(ay+by)/2,height/2),
                                                (length/2,width/2,height/2), .055)
                segment.rotation_euler.z = math.atan2(by-ay,bx-ax)
                segment.parent = group
            return
        if "polygon" in row:
            points = [self.coordinates(*point) for point in row["polygon"]]
            if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points, points[1:]+points[:1])) < 0:
                points.reverse()
            n = len(points)
            height = 1.3 if "span" in name or "ramp" in name else .68
            if "planter" in name:
                height = .24
            crest = [height + .19*(i%4) for i in range(n)]
            if self.wrecked_highway and ("span" in name or "ramp" in name):
                crest = [.44 + .13*(i%4) for i in range(n)]
            if self.flooded_square and name.startswith("planter_"):
                crest = [.14] * n
                for index, ((ax,ay), (bx,by)) in enumerate(zip(points, points[1:]+points[:1])):
                    top = (.31,.38,.35,.27)[index%4]
                    edge = self.concrete_box("Flooded planter coping", ((ax+bx)/2,(ay+by)/2,top/2),
                                             (math.hypot(bx-ax,by-ay)*.48,.055,top/2))
                    edge.rotation_euler.z = math.atan2(by-ay,bx-ax)
                    edge.parent = group
                triangles = tessellate_polygon([[Vector(point) for point in points]])
                for index, triangle in enumerate(triangles):
                    a, b, c = (Vector(points[corner]) for corner in triangle)
                    center = (a+b+c)/3
                    # Keep the debris inside each triangle of the surveyed bed.
                    radius = min(abs((end-start).cross(center-start))/(end-start).length
                                 for start,end in ((a,b),(b,c),(c,a)))
                    if radius < .06:
                        continue
                    radius = min(radius,.23)
                    fragment = self.concrete_box("Flooded planter broken masonry",
                                                 (*center,crest[0]+.034),
                                                 (radius*.76,radius*.53,.055),.013)
                    fragment.rotation_euler.z = index*.79
                    fragment.parent = group
            vertices = [(x,y,0) for x,y in points]
            vertices.extend((x,y,crest[i]*(.64+.08*(i%3))) for i,(x,y) in enumerate(points))
            vertices.extend((x,y,crest[i]) for i,(x,y) in enumerate(points))
            faces = [tuple(reversed(range(n))), tuple(range(2*n,3*n))]
            for layer in (0, n):
                for i in range(n):
                    j = (i+1)%n
                    faces.append((layer+i,layer+j,layer+j+n,layer+i+n))
            broken_deck = (self.overpass or self.wrecked_highway) and ("span" in name or "ramp" in name)
            if broken_deck:
                # A dark intact substrate separates the lifted fragments.
                # Each inset face stays inside the original surveyed outline.
                substrate = min(crest)-.06
                for index, triangle in enumerate(tessellate_polygon([[Vector(point) for point in points]])):
                    corners = [vertices[2*n+corner] for corner in triangle]
                    # The cap must face up for Godot's back-face culling.
                    a, b, c = (Vector(corner[:2]) for corner in corners)
                    if (b-a).cross(c-a) < 0:
                        corners[1], corners[2] = corners[2], corners[1]
                    center = tuple(sum(axis)/3 for axis in zip(*corners))
                    start = len(vertices)
                    for x,y,z in corners:
                        distance = math.hypot(center[0]-x,center[1]-y)
                        inset = min(.095,.052/max(distance,.01))
                        vertices.append((x+(center[0]-x)*inset,y+(center[1]-y)*inset,
                                         z+(center[2]-z)*inset+.032+(index%3)*.022))
                    vertices.extend((x,y,substrate) for x,y,_ in vertices[start:start+3])
                    faces.append((start,start+1,start+2))
                    for edge in range(3):
                        a, b = start+edge, start+(edge+1)%3
                        faces.append((a,a+3,b+3,b))
                # A separately triangulated, nonplanar cap can hide the textured fragments.
                for index, (x,y) in enumerate(points):
                    vertices[2*n+index] = (x,y,substrate)
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(vertices, [], faces)
            self.project_concrete_uv(mesh)
            for material in (self.stone, self.aggregate, self.seam):
                mesh.materials.append(material)
            mesh.polygons[1].material_index = 2 if broken_deck else 1
            if self.flooded_square and name.startswith("planter_"):
                mesh.materials.append(self.planter_silt)
                mesh.polygons[1].material_index = 3
            if broken_deck:
                textured_top = self.surveyed_surface is not None
                if textured_top:
                    mesh.materials.append(self.surveyed_surface)
                mesh.materials.append(self.deck_backing)
                mesh.polygons[1].material_index = len(mesh.materials)-1
                for index, face in enumerate(mesh.polygons[2+2*n:]):
                    face.material_index = 1 if index%4 == 0 else 0
                    if textured_top and index%4 == 0:
                        face.material_index = 3
                        for loop in face.loop_indices:
                            x,y,_ = mesh.vertices[mesh.loops[loop].vertex_index].co
                            mesh.uv_layers.active.data[loop].uv = (x/self.gw+.5,y/self.gh+.5)
            for i in range(n):
                mesh.polygons[2+n+i].material_index = 2 if i%3 == 0 else 1
            fragment = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(fragment)
            fragment.parent = group
            if self.wrecked_highway and broken_deck:
                for edge in range(0,n,3):
                    following = (edge+1)%n
                    start, end = Vector(points[edge]), Vector(points[following])
                    run = end-start
                    if run.length < .26:
                        continue
                    center = (start+end)/2
                    rod = box("Highway exposed edge reinforcement", (*center,(crest[edge]+crest[following])*.46),
                              (min(.29,run.length*.31),.017,.018),self.steel,.006)
                    rod.rotation_euler.z = math.atan2(run.y,run.x)
                    rod.parent = group
            if "span" in name or "ramp" in name:
                # Keep the shattered roadbed visible when the camera hides
                # the tall fragment. Its outline stays within the survey.
                roadbed_mesh = bpy.data.meshes.new(name + " roadbed")
                roadbed_mesh.from_pydata(
                    [(x, y, .035 + .018*(i%3)) for i,(x,y) in enumerate(points)],
                    [], [tuple(range(n))])
                roadbed_mesh.calc_loop_triangles()
                triangles = [tuple(face.vertices) for face in roadbed_mesh.loop_triangles]
                vertices = [(x, y, .035) for x,y in points]
                faces = [tuple(range(n))]
                for index, triangle in enumerate(triangles):
                    corners = [points[i] for i in triangle]
                    cx, cy = (sum(axis)/3 for axis in zip(*corners))
                    offset = len(vertices)
                    for x,y in corners:
                        length = math.hypot(cx-x, cy-y)
                        inset = min(.12, .035 / max(length, .001))
                        vertices.append((x+(cx-x)*inset, y+(cy-y)*inset, .052+.012*(index%4)))
                    faces.append((offset, offset+1, offset+2))
                roadbed_mesh.clear_geometry()
                roadbed_mesh.from_pydata(vertices, [], faces)
                self.project_concrete_uv(roadbed_mesh)
                roadbed_mesh.materials.append(self.seam)
                roadbed_mesh.materials.append(self.aggregate)
                for face in list(roadbed_mesh.polygons)[1:]:
                    face.material_index = 1
                roadbed = bpy.data.objects.new(name + " retained roadbed", roadbed_mesh)
                bpy.context.collection.objects.link(roadbed)
            return
        x1,y1,x2,y2 = row["rect"]
        x,y = self.coordinates((x1+x2)/2,(y1+y2)/2)
        w,d = (x2-x1)*self.gw/self.cw, (y2-y1)*self.gh/self.ch
        vertical = d > w
        length, breadth = (d,w) if vertical else (w,d)
        yaw = math.pi/2 if vertical else 0
        wreck_yaws = {"wreck_mid_w": -.16, "wreck_mid_e": -.34, "wreck_e": -.33,
                     "wreck_far_e": -.09, "wreck_middle5": -.12}
        convoy_flatbeds = {"wreck_w": .24, "wreck_ne": .37,
                           "wreck_se": -.46, "wreck_southwest": .22}
        salt_stripped = {"wreck_sw": .08, "wreck_e": .94, "wreck_southwest": .22}
        salt_roofed = {"wreck_nw": .08, "wreck_n": -1.33, "wreck_ne": -.63,
                       "wreck_mid_w": 1.27, "wreck_mid_c": -.34, "wreck_w": -1.01,
                       "wreck_se": -1.04}
        if self.trainyard and ("wagon" in name or name == "north_tank"):
            if name == "wagon_turntable":
                yaw = math.atan2(54*self.gh/self.ch, 66*self.gw/self.cw)
                length, breadth = w, d*.40
                c, s = math.cos(yaw), math.sin(yaw)
                fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
                length, breadth = length*fit, breadth*fit
                self.trainyard_turntable(x, y, yaw, breadth)
            self.trainyard_wagon(group, name, x, y, length, breadth, yaw)
        elif self.dust_road and name in {"wreck_se", "wreck_south", "truck_e"}:
            kind, angle = {"wreck_se": ("convoy_mw", .03),
                           "wreck_south": ("wreck_south", .34),
                           "truck_e": ("wreck_truck_e", .52)}[name]
            breadth = min(breadth, length*.32)
            c, s = math.cos(angle), math.sin(angle)
            fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            self.convoy_vehicle(group, kind, x, y, length*fit, breadth*fit, angle)
        elif self.salt_flat and name in {"wreck_mid_e", "wreck_south"}:
            if name == "wreck_mid_e":
                axis, tanker = (30, -32), False
            else:
                axis, tanker = (72, -31), True
            angle = math.atan2(-axis[1]*self.gh/self.ch, axis[0]*self.gw/self.cw)
            breadth = min(breadth, length*.34)
            c, s = abs(math.cos(angle)), abs(math.sin(angle))
            fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            # Counter the convoy placement half-turn so the cab follows the reference axis.
            self.convoy_vehicle(group, "convoy_mw" if tanker else name,
                                x, y, length*fit, breadth*fit, angle+math.pi)
        elif self.salt_flat and name in salt_stripped:
            angle = salt_stripped[name]
            breadth = min(breadth, length*.42)
            c, s = math.cos(angle), math.sin(angle)
            fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            self.stripped_car(group, x, y, length*fit, breadth*fit, angle)
        elif self.salt_flat and name in salt_roofed:
            angle = salt_roofed[name]
            breadth = min(breadth, length*.50)
            c, s = abs(math.cos(angle)), abs(math.sin(angle))
            fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            place(self.library / "derelict_suv275/model.glb", group, (x,y,0),
                  (length*fit,breadth*fit,1.22), yaw=angle)
        elif self.convoy_crossing and name in convoy_flatbeds:
            angle = convoy_flatbeds[name]
            breadth = min(breadth, length*.38)
            c, s = abs(math.cos(angle)), abs(math.sin(angle))
            fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            self.convoy_vehicle(group, name, x, y, length*fit, breadth*fit, angle)
        elif self.wrecked_highway and name in wreck_yaws:
            angle = -wreck_yaws[name]
            c,s = abs(math.cos(angle)),abs(math.sin(angle))
            scale = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            self.convoy_vehicle(group, name, x, y, length*scale, breadth*scale, angle)
        elif self.scavenger_plaza and name == "wreck_se":
            angle = math.atan2(-48*self.gh/self.ch, 38*self.gw/self.cw)
            breadth = min(breadth, length*.48)
            c, s = abs(math.cos(angle)), abs(math.sin(angle))
            fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            self.convoy_vehicle(group, name, x, y, length*fit, breadth*fit, angle)
        elif self.ruined_downtown and name in {"wreck_nw", "wreck_mid_w"}:
            angle = {"wreck_nw": -1.04, "wreck_mid_w": -.26}[name]
            breadth = min(breadth, length*.45)
            c, s = abs(math.cos(angle)), abs(math.sin(angle))
            fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            self.stripped_car(group, x, y, length*fit, breadth*fit, angle)
        elif self.ruined_downtown and name in {"bus_sw", "wreck_mid_e", "truck_mid"}:
            angle = {"bus_sw": .36, "wreck_mid_e": .29, "truck_mid": -.20}[name]
            breadth = min(breadth, length*.33)
            c, s = abs(math.cos(angle)), abs(math.sin(angle))
            fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            length, breadth = length*fit, breadth*fit
            if name == "truck_mid":
                self.convoy_vehicle(group, name, x, y, length, breadth, angle)
            else:
                self.open_bus_wreck(group, x, y, length, breadth, angle)
        elif name.startswith("convoy_"):
            self.convoy_vehicle(group, name, x, y, length, breadth, yaw)
        elif self.flooded_square and name == "bus_west":
            angle = math.radians(82)
            breadth = min(breadth, length*.28)
            c, s = math.cos(angle), math.sin(angle)
            fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            self.open_bus_wreck(group, x, y, length*fit, breadth*fit, angle)
        elif self.city and name.startswith(("bus_", "truck_")):
            self.vehicle(group, name, x,y,w,d)
        elif name.startswith(("wreck_", "truck_", "convoy_", "car_")):
            place(self.library / "derelict_suv275/model.glb", group, (x,y,0),
                  (length*.97,breadth*.97,1.55), yaw=yaw + (math.pi if x<0 else 0))
        elif self.ruined_transit and name == "west_train":
            self.transit_train(group, x, y, length, breadth, yaw)
        elif self.cratered_waterfront and name in {"cargo_e", "cargo_e2"}:
            self.waterfront_cargo(group, name, x, y, length, breadth, yaw)
        elif self.cratered_waterfront and name == "cargo_w":
            container = build_container(group,x,y,length,breadth,self.steel,self.dark,self.steel,yaw=yaw)
            container.scale.z = .48
            container.location.z *= container.scale.z
        elif any(part in name for part in ("wagon","container","cargo","_train")):
            base = build_container(group,x,y,length,breadth,self.steel,self.dark,self.steel,yaw=yaw)
            if "wagon" in name or "_train" in name:
                base.location.z += .19
                for side in (-1,1):
                    bogie = box("Wagon bogie", (x if vertical else x+side*w*.29,
                                                y+side*d*.29 if vertical else y,.17),
                                (w*(.40 if vertical else .10),d*(.10 if vertical else .40),.17), self.dark)
                    bogie.parent = group
        elif "crane" in name:
            build_crane(group,x,y,w,d,self.dark,self.steel,height=3.4,outreach=min(length,2.5),
                        lattice_jib=self.cratered_waterfront)
        elif name in {"west_pipe", "east_pipe", "east_pipe2", "south_pipe", "sw_tank"}:
            self.basin_drain(group, name, x, y, w, d)
        elif any(part in name for part in ("pipe","tank","shelf")):
            place(self.library / "industrial_service267/model.glb", group, (x,y,0),
                  (length*.97,breadth*.97,1.42), yaw=yaw)
        elif self.burned_market and "stall" in name:
            self.burned_market_stall(group, name, x, y, length, breadth, yaw)
        elif self.scavenger_plaza and (name.startswith("market_") or name == "table_w"):
            self.scavenger_stall(group, name, x, y, length, breadth, yaw)
        elif "stall" in name or name.startswith("market_"):
            place(self.library / "market_southeast_display/shop.glb", group, (x,y,0),
                  (length*.96,breadth*.96,1.6), yaw=yaw, merge=True)
        elif "crate" in name:
            place(self.library / "cargo_crate274/model.glb", group, (x,y,0),
                  (length*.94,breadth*.94,.8), yaw=yaw)
        elif self.ruined_transit and name in {"west_platform", "east_platform"}:
            self.transit_platform(group, name, x, y, w, d)
        elif name.startswith("stairs_"):
            direction = -1 if self.ruined_transit and name in {"stairs_s", "stairs_sw", "stairs_se"} else 1
            for step in range(6):
                height = (step+1)*.12
                tread_y = y+direction*d*((step+.5)/6-.5)
                if self.ruined_transit:
                    self.concrete_box(name, (x,tread_y,height/2),
                                      (w*.48,d/12,height/2), .012).parent = group
                    box("Station stair worn nosing",
                        (x,tread_y-direction*d*.071,height),
                        (w*.45,d*.012,.013), self.steel,.006).parent = group
                else:
                    box(name, (x,tread_y,height/2),
                        (w*.48,d/12,height/2), self.stone).parent = group
        elif self.flooded_square and name == "monument":
            radius = min(w,d)*.46
            for label, ratio, height, elevation, material in (
                ("Flooded monument outer step", 1, .16, .08, self.aggregate),
                ("Flooded monument inner step", .82, .19, .25, self.aggregate),
                ("Flooded monument pedestal", .58, .34, .51, self.stone),
                ("Flooded monument remnant", .23, .64, 1, self.steel),
            ):
                bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius*ratio,
                                                   depth=height, location=(x,y,elevation),
                                                   rotation=(0,0,math.pi/8))
                tier = bpy.context.object
                tier.name = label
                tier.data.materials.append(material)
                if material == self.aggregate:
                    self.project_concrete_uv(tier.data)
                tier.parent = group
        elif self.ruined_transit and name.startswith("column_"):
            self.transit_column(group, x, y, w, d)
        elif "column" in name or name == "monument":
            box(name+" footing", (x,y,.16), (w*.47,d*.47,.16), self.stone).parent = group
            box(name, (x,y,1.15), (w*.25,d*.25,1.0), self.stone).parent = group
        elif self.ruined_transit and name == "center_planter":
            box("Station planter bed", (x,y,.075),
                (w*.46,d*.46,.075), self.dark).parent = group
            for side in (-1,1):
                for offset, height in ((-.23,.39), (.22,.29)):
                    self.concrete_box("Station planter rim",
                                      (x+side*w*.40,y+offset*d,height/2),
                                      (w*.065,d*.20,height/2)).parent = group
                self.concrete_box("Station planter rim", (x,y+side*d*.40,.27),
                                  (w*.36,d*.065,.17)).parent = group
            for dx,dy in ((-.20,.12), (.06,-.22), (.24,.19)):
                fragment = self.concrete_box("Station planter rubble", (x+w*dx,y+d*dy,.19),
                                             (w*.095,d*.085,.07))
                fragment.rotation_euler.z = dx
                fragment.parent = group
        elif self.ruined_transit and name in {"bench_n", "bench_s"}:
            rear = 1 if name == "bench_n" else -1
            for side in (-1,1):
                self.concrete_box("Station bench support", (x+side*w*.34,y,.19),
                                  (w*.065,d*.34,.19)).parent = group
                box("Station bench back upright", (x+side*w*.34,y+rear*d*.32,.57),
                    (.027,d*.045,.19), self.steel,.010).parent = group
            for slat in (-1,0,1):
                box("Station bench slat", (x,y+slat*d*.23,.405),
                    (w*.46,d*.10,.033), self.facade_blue,.014).parent = group
            box("Station bench backrest", (x,y+rear*d*.34,.695),
                (w*.43,d*.062,.064), self.facade_blue,.012).parent = group
        elif any(part in name for part in ("platform","planter","bench","table")):
            height = .52 if name.startswith(("table","bench")) else .20
            box(name, (x,y,height/2), (w*.48,d*.48,height/2), self.stone).parent = group
        elif "barrel" in name:
            for offset in (-.31,0,.31):
                radius = min(breadth*.37,length*.145,.30)
                bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=.56,
                    location=(x+(0 if vertical else offset*w),y+(offset*d if vertical else 0),.28))
                barrel = bpy.context.object
                barrel.data.materials.append(self.steel)
                barrel.parent = group
        elif self.dust_road and "sandbag" in name:
            group.location = (x,y,0)
            group.rotation_euler.z = yaw
            for layer, offsets in enumerate(((-.36,-.12,.12,.36), (-.25,0,.25))):
                for index, offset in enumerate(offsets):
                    fabric = self.canvas_faded if (index+layer)%3 == 0 else self.canvas
                    bag = box("Dust road staggered sandbag",
                              (length*offset,breadth*.035*(-1)**index,.108+layer*.165),
                              (length*.117,breadth*(.38-layer*.055),.105), fabric,.078)
                    bag.rotation_euler.z = .07*(-1)**(index+layer)
                    bag.parent = group
        elif "sandbag" in name:
            for layer in range(2):
                for offset in (-.31,0,.31):
                    box(name, (x+(0 if vertical else offset*w),y+(offset*d if vertical else 0),.12+.19*layer),
                        (w*(.41 if vertical else .146),d*(.146 if vertical else .41),.11),
                        self.canvas, .08).parent = group
        elif self.trainyard and name in {"northwest_ruin", "northeast_ruin"}:
            self.trainyard_workshop_ruin(group, name, x, y, w, d)
        elif self.overpass and name.endswith("_ruin"):
            self.overpass_ruin(group, name, x, y, w, d)
        elif self.scavenger_plaza and ("ruin" in name or name == "ne_corner"):
            self.scavenger_perimeter_ruin(group, x, y, w, d)
        elif self.ruined_transit and name in {"top_ruin", "west_top_ruin"}:
            self.concrete_box("Station ruin foundation", (x,y,.08),
                              (w*.465,d*.46,.08)).parent = group
            for side in (-1, 1):
                height = .97 if side < 0 else .65
                self.concrete_box("Station ruin fractured pier", (x+side*w*.355,y,height/2),
                                  (w*.105,d*.37,height/2),.052).parent = group
            self.concrete_box("Station ruin rear wall", (x,y+d*.365,.37),
                              (w*.34,d*.079,.37),.048).parent = group
            slab = self.concrete_box("Station ruin slipped slab", (x+w*.065,y-d*.125,.30),
                                     (w*.21,d*.218,.095),.036)
            slab.rotation_euler.y = -.23
            slab.parent = group
        elif self.city and ("ruin" in name or name == "ne_corner"):
            self.concrete_box(name+" rubble base", (x,y,.16), (w*.47,d*.46,.16)).parent = group
            for side in (-1,1):
                for index in range(3):
                    if self.ruined_downtown and index == 1:
                        continue
                    if self.flooded_square and index == 1 and side == (-1 if y > 0 else 1):
                        continue
                    if self.burned_market and side == (-1 if name.startswith("n") else 1):
                        if index == (0 if name.startswith(("nw", "sw")) else 1):
                            continue
                    height = .75+.22*((index+(side>0))%3)
                    self.concrete_box(name+" fractured facade", (x+(index-1)*w*.31,y+side*d*.41,height/2),
                        (w*.154,d*.075,height/2), .065).parent = group
            self.concrete_box(name+" end wall", (x-w*.405,y,.51), (w*.058,d*.36,.51), .065).parent = group
            if self.ruined_downtown:
                self.downtown_exposed_frame(group, name, x, y, w, d)
            elif self.burned_market:
                self.burned_market_ruin(group, name, x, y, w, d)
            elif self.flooded_square:
                self.flooded_square_ruin(group, x, y, w, d)
            elif self.cratered_waterfront:
                self.waterfront_warehouse_ruin(group, name, x, y, w, d)
        elif self.irradiated_basin and name in {"west_ruin", "east_ruin"}:
            self.concrete_box("Basin ruined foundation", (x,y,.062),
                              (w*.46,d*.46,.062)).parent = group
            bank = -1 if name == "west_ruin" else 1
            self.concrete_box("Basin surviving bank wall", (x+bank*w*.39,y,.38),
                              (w*.075,d*.46,.38)).parent = group
            for offset, height in ((-.30,.20),(.04,.13),(.28,.24)):
                block = self.concrete_box("Basin displaced bank coping",
                                           (x+bank*w*.38,y+offset*d,.74+height/2),
                                           (w*.064,d*.095,height/2), .028)
                block.rotation_euler.x = offset*.42
                block.parent = group
            for side, height in ((-1,.57),(1,.29)):
                self.concrete_box("Basin broken return wall", (x+bank*w*.14,y+side*d*.39,height*.5),
                                  (w*.29,d*.076,height*.5)).parent = group
            slab = self.concrete_box("Basin dislodged slab", (x-bank*w*.14,y,.22),
                                     (w*.15,d*.19,.084))
            slab.rotation_euler = (.24,0,bank*.18)
            slab.parent = group
        elif self.ruined_downtown and name.startswith(("wall_", "barrier_", "rubble_")):
            self.downtown_road_cover(group, name, x, y, length, breadth, yaw)
        elif any(part in name for part in ("ruin","rubble","wall","barrier")):
            for i in range(3):
                self.concrete_box(name,(x+w*(i-1)/3,y,.18+.11*i),
                    (w*.162,d*.48,.18+.11*i),.08).parent = group
        else:
            raise ValueError(f"No wasteland object model for {name}")

    def add_salt_flat_utility_poles(self):
        timber = make_material("Salt-stained utility timber", (.105,.061,.029,1), 0,.91)
        for px, py, height, lean in ((81,185,1.24,.07), (448,82,1.46,-.13),
                                     (842,135,1.23,.03), (595,353,1.31,-.09)):
            x,y = self.coordinates(px,py)
            bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=.046, radius2=.027,
                                            depth=height, location=(x+lean*height/2,y,height/2),
                                            rotation=(0,lean,0))
            pole = bpy.context.object
            pole.name = "Salt flat abandoned utility pole"
            pole.data.materials.append(timber)
            arm = box("Salt flat utility crossarm", (0,0,height*.40),
                      (.133,.023,.028),timber,.008)
            arm.parent = pole

    def salt_flat_fence(self, group, points, width):
        for index, (x, y) in enumerate(points):
            height = (.77, .57, .66)[index % 3]
            box("Salt flat fence post", (x,y,height/2), (width*.12,width*.12,height/2),
                self.dark,.012).parent = group
        for index, ((ax,ay),(bx,by)) in enumerate(zip(points,points[1:])):
            length = math.hypot(bx-ax,by-ay)
            yaw = math.atan2(by-ay,bx-ax)
            for elevation in (.22,.43):
                wire = bpy.data.curves.new("Salt flat sagging fence wire", "CURVE")
                wire.dimensions = "3D"
                wire.resolution_u = 6
                wire.bevel_depth = min(.016,width*.062)
                wire.bevel_resolution = 1
                wire.materials.append(self.steel)
                spline = wire.splines.new("BEZIER")
                spline.bezier_points.add(2)
                for point, coordinate in zip(spline.bezier_points, (
                    (ax,ay,elevation),
                    ((ax+bx)/2,(ay+by)/2,elevation-min(.11,length*.06)),
                    (bx,by,elevation),
                )):
                    point.co = coordinate
                    point.handle_left_type = point.handle_right_type = "AUTO"
                rail = bpy.data.objects.new("Salt flat fence rail", wire)
                bpy.context.collection.objects.link(rail)
                rail.parent = group
            if index == 0:
                brace = box("Salt flat leaning fence brace", (ax,ay,.43),
                            (.023,.024,.44), self.steel,.007)
                brace.rotation_euler = (0,.18,yaw)
                brace.parent = group

    def basin_drain(self, group, name, x, y, width, depth):
        segments = 20
        tank = name == "sw_tank"
        radius = min(width,depth)*(.23 if tank else .39 if name == "south_pipe" else .33)
        length = min(width,depth)*(.75 if tank else .55)
        rings = ((radius,0), (radius,length),
                 (radius*.76,length), (radius*.76,0))
        vertices = [(r*math.cos(math.tau*i/segments), r*math.sin(math.tau*i/segments), z)
                    for r,z in rings for i in range(segments)]
        faces = []
        for ring in range(len(rings)):
            start, following = ring*segments, ((ring+1)%len(rings))*segments
            for i in range(segments):
                j = (i+1)%segments
                faces.append((start+i,start+j,following+j,following+i))
        mesh = bpy.data.meshes.new("Hollow basin drain shell")
        mesh.from_pydata(vertices, [], faces)
        mesh.materials.append(self.steel if tank else self.aggregate)
        self.project_concrete_uv(mesh)
        drain = bpy.data.objects.new("Open corroded basin tank" if tank else "Hollow basin drain", mesh)
        bpy.context.collection.objects.link(drain)
        drain.parent = group
        if tank:
            angle = .60
            drain.location = (x-math.sin(angle)*length/2,y+math.cos(angle)*length/2,radius*.89)
            drain.rotation_euler = (math.pi/2,0,angle)
            for offset in (.16,.52,.86):
                bpy.ops.mesh.primitive_torus_add(major_segments=20, minor_segments=6,
                    major_radius=radius, minor_radius=.027, location=(0,0,length*offset))
                band = bpy.context.object
                band.name = "Corroded tank reinforcing band"
                band.data.materials.append(self.dark)
                band.parent = drain
            for offset in (.08,.92):
                flange = box("Torn tank mounting flange",
                             (radius*.84,0,length*offset),
                             (radius*.27,radius*.18,.048), self.steel,.012)
                flange.rotation_euler.z = math.pi/9
                flange.parent = drain
        elif name == "south_pipe":
            drain.location = (x,y,0)
        else:
            drain.location = (x,y,radius*.90)
            drain.rotation_euler = (math.pi/2,0,.40 if name == "west_pipe" else -.46)
        if not tank:
            # The dark joint at each lip makes the opening readable against
            # bright concrete while preserving the hollow center.
            for offset in (.09,.91):
                bpy.ops.mesh.primitive_torus_add(major_segments=20, minor_segments=6,
                    major_radius=radius*.97, minor_radius=radius*.075,
                    location=(0,0,length*offset))
                collar = bpy.context.object
                collar.name = "Basin drain socket collar"
                collar.data.materials.append(self.steel)
                collar.parent = drain

    def waterfront_warehouse_ruin(self, group, name, x, y, width, depth):
        level = 1.96 if name == "north_ruin" else 1.54
        for offset in (-.34, .08, .35):
            box("Waterfront warehouse steel post", (x+width*offset,y-depth*.30,level/2),
                (.065,.065,level/2), self.steel).parent = group
            box("Waterfront warehouse exposed joist", (x+width*offset,y,level),
                (.052,depth*.35,.070), self.steel).parent = group
        box("Waterfront warehouse gapped lintel", (x-width*.12,y-depth*.31,level-.12),
            (width*.24,.055,.065), self.dark).parent = group
        box("Waterfront warehouse facade remnant", (x+width*.30,y-depth*.486,.59),
            (width*.11,.022,.12), self.facade_blue,.013).parent = group
        fragment = self.concrete_box("Waterfront warehouse fallen deck",
                                     (x+width*.16,y+depth*.11,.58),
                                     (width*.23,depth*.21,.105))
        fragment.rotation_euler.y = -.24
        fragment.parent = group

    def waterfront_cargo(self, group, name, x, y, length, width, yaw):
        group.location = (x,y,0)
        group.rotation_euler.z = yaw
        box("Quay cargo skid", (0,0,.10),
            (length*.46,width*.43,.10), self.dark).parent = group
        if name == "cargo_e2":
            box("Quay tarped load", (0,0,.44),
                (length*.43,width*.40,.27), self.facade_blue,.085).parent = group
            for offset in (-.23,.18):
                box("Quay tarp lashing", (length*offset,0,.714),
                    (.022,width*.37,.016), self.dark,.006).parent = group
                for side in (-1, 1):
                    box("Quay tarp lashing drop", (length*offset,side*width*.397,.441),
                        (.022,width*.018,.247),self.dark,.006).parent = group
                    box("Quay tarp lashing buckle", (length*offset,side*width*.419,.27),
                        (.047,width*.014,.039),self.steel,.010).parent = group
        else:
            for offset, height in ((-.28,.27),(0,.34),(.28,.23)):
                box("Quay salvaged crate", (length*offset,0,.20+height),
                    (length*.133,width*.32,height), self.steel,.028).parent = group
                lid_height = .20+2*height
                box("Quay crate fitted lid", (length*offset,0,lid_height+.014),
                    (length*.135,width*.325,.023),self.dark,.012).parent = group
                for side in (-1, 1):
                    box("Quay crate lid batten", (length*(offset+side*.082),0,lid_height+.045),
                        (length*.017,width*.315,.018),self.steel,.006).parent = group
            for side in (-1,1):
                box("Quay cargo frame rail", (0,side*width*.39,.48),
                    (length*.44,.034,.041), self.dark,.012).parent = group

    def waterfront_quay_segment(self, group, name, ax, ay, bx, by, width):
        length = math.hypot(bx-ax,by-ay)
        yaw = math.atan2(by-ay,bx-ax)
        x, y = (ax+bx)/2, (ay+by)/2
        broken = name == "quay_crater_w"
        wall = self.concrete_box("Quay masonry footing", (x,y,.13),
                                 (length/2,width*.48,.15))
        wall.rotation_euler.z = yaw
        wall.parent = group
        if broken:
            for offset, tilt, elevation in ((-.30,.34,.32), (.03,-.26,.29), (.31,.49,.35)):
                slab = self.concrete_box("Slumped crater quay block",
                                         (x+(bx-ax)*offset,y+(by-ay)*offset,elevation),
                                         (length*.125,width*.38,.12))
                slab.rotation_euler = (0,tilt,yaw)
                slab.parent = group
        else:
            count = max(1, round(length/1.25))
            for index in range(count):
                offset = (index+.5)/count-.5
                pier = self.concrete_box("Quay retaining pier",
                    (x+(bx-ax)*offset,y+(by-ay)*offset,.205),
                    (min(.065,length*.11/count),width*.49,.205), .018)
                pier.rotation_euler.z = yaw
                pier.parent = group
                cap = self.concrete_box("Intact quay coping",
                                        (x+(bx-ax)*offset,y+(by-ay)*offset,.35),
                                        (length*.485/count,width*.48,.09))
                cap.rotation_euler.z = yaw
                cap.parent = group
            if length >= .85:
                radius = min(.069,width*.22)
                for label, size, elevation, height in (
                    ("Quay bollard stem", radius, .55, .22),
                    ("Quay bollard crown", radius*1.35, .669, .052),
                ):
                    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=size, depth=height,
                                                       location=(x,y,elevation))
                    bollard = bpy.context.object
                    bollard.name = label
                    bollard.data.materials.append(self.steel)
                    bollard.parent = group

    def transit_boundary(self, group, name, points, width):
        stairs = name.endswith("_stairs_guard")
        for (ax,ay),(bx,by) in zip(points, points[1:]):
            length = math.hypot(bx-ax,by-ay)
            yaw = math.atan2(by-ay,bx-ax)
            x, y = (ax+bx)/2, (ay+by)/2
            curb = self.concrete_box("Station boundary curb", (x,y,.09),
                                     (length/2,width*.46,.09))
            curb.rotation_euler.z = yaw
            curb.parent = group
            if stairs:
                rail = box("Station stair guard rail", (x,y,.52),
                           (length*.48,.034,.034), self.steel,.009)
                rail.rotation_euler.z = yaw
                rail.parent = group
                if length >= .85:
                    lower = box("Station stair lower rail", (x,y,.32),
                                (length*.44,.024,.024),self.steel,.007)
                    lower.rotation_euler.z = yaw
                    lower.parent = group
                    box("Station stair intermediate support", (x,y,.33),
                        (.041,.041,.21),self.steel,.012).parent = group
            else:
                cap = self.concrete_box("Station perimeter coping", (x,y,.25),
                                        (length*.49,width*.38,.072))
                cap.rotation_euler.z = yaw
                cap.parent = group
        if stairs:
            for x,y in points:
                box("Station stair guard post", (x,y,.33),
                    (.041,.041,.21), self.steel,.012).parent = group

    def transit_column(self, group, x, y, width, depth):
        self.concrete_box("Station column stepped footing", (x,y,.13),
                          (width*.46,depth*.46,.13)).parent = group
        self.concrete_box("Station column concrete core", (x,y,.91),
                          (width*.28,depth*.36,.68)).parent = group
        plaza_side = -1 if x > 0 else 1
        for offset, height in ((-.23,.32), (.02,.37), (.25,.26)):
            box("Station column blue panel", (x+plaza_side*width*.29,y+depth*offset,1.04),
                (.026,depth*.105,height), self.facade_blue,.014).parent = group
        for offset in (-.35,.35):
            box("Station column corroded frame", (x+plaza_side*width*.30,y+depth*offset,.92),
                (.036,.034,.64), self.steel,.010).parent = group

    def transit_platform(self, group, name, x, y, width, depth):
        rail_side = -1 if name == "west_platform" else 1
        self.concrete_box("Station platform deck", (x,y,.19),
                          (width*.48,depth*.49,.19)).parent = group
        self.concrete_box("Station platform track edge", (x+rail_side*width*.42,y,.37),
                          (width*.058,depth*.49,.08)).parent = group
        for bay in (-.39,-.25,-.11,.17,.31):
            box("Blue station cladding panel", (x-rail_side*width*.26,y+bay*depth,.418),
                (width*.18,depth*.062,.047), self.facade_blue,.018).parent = group
        for bay in (-.43,-.22,.02,.24,.43):
            box("Station platform trim", (x+rail_side*width*.42,y+bay*depth,.455),
                (width*.057,depth*.027,.018), self.steel,.008).parent = group
        for bay in (-.38,-.24,-.10,.04,.32):
            box("Surviving platform warning strip", (x+rail_side*width*.32,y+bay*depth,.393),
                (width*.026,depth*.064,.015),self.platform_warning,.006).parent = group
            for offset in (-.041,0,.041):
                box("Station tactile strip rib", (x+rail_side*width*.32,y+(bay+offset)*depth,.410),
                    (width*.022,depth*.005,.005),self.platform_warning,.003).parent = group

    def add_transit_south_carriage(self):
        # Follow the paired rails in the original south track bed. The sleepers
        # stay in the existing floor texture beneath the raised running surfaces.
        rail_rows = (468, 496)
        rail_top = .054
        for row in rail_rows:
            x, y = self.coordinates(480, row)
            box("South transit running rail", (x,y,rail_top/2),
                (self.gw/2,.026,rail_top/2),self.steel,.006)
        group = bpy.data.objects.new("South transit carriage", None)
        bpy.context.collection.objects.link(group)
        x, y = self.coordinates(480, sum(rail_rows)/2)
        half_gauge = (rail_rows[1]-rail_rows[0])*self.gh/(2*self.ch)
        self.transit_train(group, x, y, 266*self.gw/self.cw, 49*self.gh/self.ch, 0,
                           roofless=True, half_gauge=half_gauge, rail_top=rail_top)

    def transit_train(self, group, x, y, length, width, yaw, *, roofless=False,
                      half_gauge=None, rail_top=0.0):
        group.location = (x,y,0)
        group.rotation_euler.z = yaw
        wheel_offset = width*.33 if half_gauge is None else half_gauge
        box("Transit carriage underframe", (0,0,.37),
            (length*.48,width*.43,.14), self.dark).parent = group
        for end in (-1,1):
            box("Transit bogie", (end*length*.30,0,.19),
                (length*.085,width*.39,.16), self.dark).parent = group
            box("Transit carriage cab", (end*length*.401,0,.81),
                (length*.077,width*.42,.35), self.steel,.065).parent = group
            box("Transit cab broken glazing", (end*length*.476,0,.96),
                (.018,width*.32,.095), self.dark,.014).parent = group
            box("Transit carriage recessed coupler", (end*length*.479,0,.35),
                (length*.018,width*.12,.074),self.dark,.025).parent = group
            for side in (-1, 1):
                box("Transit carriage dead lamp", (end*length*.478,side*width*.27,.69),
                    (.020,width*.058,.037),self.facade_blue,.011).parent = group
            for offset in (-.043,.043):
                for side in (-1,1):
                    bpy.ops.mesh.primitive_cylinder_add(
                        vertices=12, radius=.16, depth=.085,
                        location=((end*.30+offset)*length,side*wheel_offset,.16+rail_top),
                        rotation=(math.pi/2,0,0))
                    wheel = bpy.context.object
                    wheel.name = "Transit carriage wheel"
                    wheel.data.materials.append(self.steel)
                    wheel.parent = group
        if roofless:
            for offset in (-.28,.06,.29):
                box("Exposed transit roof rib", (offset*length,0,1.13),
                    (.052,width*.425,.058), self.steel,.018).parent = group
            for side in (-1, 1):
                for offset in (-.235,.215):
                    box("Exposed transit seat pan", (offset*length,side*width*.285,.68),
                        (length*.085,width*.087,.038),self.facade_blue,.018).parent = group
                    box("Exposed transit seat back", (offset*length,side*width*.368,.817),
                        (length*.083,width*.024,.14),self.steel,.018).parent = group
        else:
            box("Transit carriage roof", (0,0,1.18),
                (length*.38,width*.425,.085), self.steel,.054).parent = group
        for side in (-1,1):
            box("Transit carriage side sill", (0,side*width*.413,.58),
                (length*.38,.055,.17), self.steel).parent = group
            for step in range(-3,4):
                box("Transit carriage window mullion", (step*length*.105,side*width*.413,.94),
                    (.041,.048,.18), self.steel).parent = group
        for offset in (() if roofless else (-.22,0,.22)):
            box("Transit roof vent", (length*offset,0,1.29),
                (length*.041,width*.24,.027), self.dark).parent = group

    def scavenger_perimeter_ruin(self, group, x, y, width, depth):
        # Put the broken outer wall away from the market lanes.
        outside = -1 if x < 0 else 1
        for offset, angle in ((-.25,.22),(.19,-.28)):
            slab = self.concrete_box("Scavenger fallen perimeter masonry",
                                     (x+outside*width*.18,y+depth*offset,.19),
                                     (width*.125,depth*.096,.11))
            slab.rotation_euler = (.16,0,angle)
            slab.parent = group
        for offset, height in ((-.31,1.42), (.02,2.04), (.32,1.67)):
            self.concrete_box("Scavenger broken perimeter pier",
                              (x+outside*width*.39,y+depth*offset,height/2),
                              (width*.07,depth*.09,height/2)).parent = group
        # Keep the fracture within the surveyed perimeter and leave the
        # inner side of the footprint open toward the stalls.
        profile = [(-.42,0), (.41,0), (.41,.92), (.26,1.12), (.12,.76),
                   (-.03,1.43), (-.19,1.04), (-.42,1.22)]
        vertices = [(x+outside*width*edge, y+depth*along, z)
                    for edge in (.35,.43) for along,z in profile]
        count = len(profile)
        faces = [tuple(reversed(range(count))), tuple(range(count,2*count))]
        for index in range(count):
            following = (index+1)%count
            faces.append((index,following,following+count,index+count))
        if outside < 0:
            faces = [face[::-1] for face in faces]
        mesh = bpy.data.meshes.new("Scavenger fractured perimeter wall")
        mesh.from_pydata(vertices, [], faces)
        self.project_concrete_uv(mesh)
        mesh.materials.append(self.aggregate)
        wall = bpy.data.objects.new(mesh.name, mesh)
        bpy.context.collection.objects.link(wall)
        wall.parent = group
        for offset, tilt in ((-.24,.22), (.19,-.37)):
            slab = self.concrete_box("Scavenger fallen floor panel",
                                     (x+outside*width*.08,y+depth*offset,.56),
                                     (width*.26,depth*.13,.085))
            slab.rotation_euler.y = outside*tilt
            slab.parent = group
        box("Scavenger exposed floor beam", (x+outside*width*.32,y,1.36),
            (.055,depth*.38,.073), self.steel,.02).parent = group

    def flooded_square_ruin(self, group, x, y, width, depth):
        street = -1 if y > 0 else 1
        for offset, panel_height in ((-.29,.20), (.02,.15), (.32,.09)):
            box("Flooded ruin blue plinth panel",
                (x+width*offset, y+street*depth*.487, .27),
                (width*.115, .023, panel_height), self.facade_blue,.012).parent = group
        for offset, height in ((-.32,1.61), (.29,1.36)):
            box("Flooded ruin exposed column",
                (x+width*offset, y+street*depth*.28, height/2),
                (.071,.071,height/2), self.steel).parent = group
        lintel = box("Flooded ruin tilted facade lintel",
                     (x-width*.015,y+street*depth*.28,1.485),
                     (width*.31,.067,.058), self.steel,.014)
        lintel.rotation_euler.y = math.atan2(.25,width*.61)
        lintel.parent = group
        fallen_column = self.concrete_box(
            "Flooded ruin fallen column", (x+width*.19,y-street*depth*.27,.43),
            (width*.22,min(.11,depth*.06),.12), .04,
        )
        fallen_column.rotation_euler.z = street*.28
        fallen_column.parent = group
        floor = self.concrete_box("Flooded ruin fallen upper floor",
                                  (x-width*.14, y-street*depth*.16, .63),
                                  (width*.23,depth*.20,.09))
        floor.rotation_euler.y = street*.28
        floor.parent = group
        for offset_x, offset_y, size, tilt in (
            (.18,.08,.11,.31), (.34,-.15,.075,-.24), (.06,.24,.065,-.42),
        ):
            fragment = self.concrete_box(
                "Flooded ruin interior rubble",
                (x+width*offset_x,y+street*depth*offset_y,.37),
                (width*size,depth*size*.75,.068), .021,
            )
            fragment.rotation_euler.y = tilt
            fragment.rotation_euler.z = street*tilt
            fragment.parent = group
        # Anchor exposed reinforcement to the tilted slab so it follows the
        # fracture rather than floating above the flooded ground.
        for offset, reach, bend in ((-.13,.16,-.17), (.02,.23,.09), (.14,.12,.22)):
            rod = box("Flooded ruin exposed slab reinforcement",
                      (width*.21+reach/2, depth*offset, .015),
                      (reach/2+.035,.013,.012), self.steel)
            rod.rotation_euler.z = bend
            rod.parent = floor

    def burned_market_ruin(self, group, name, x, y, width, depth):
        street = -1 if name.startswith("n") else 1
        level = 1.88 if name in {"nw_ruin", "ne_corner", "sw_ruin", "se_ruin"} else 1.48
        for side in (-1, 1):
            box("Exposed market roof joist", (x+side*width*.33, y, level),
                (.055, depth*.38, .065), self.steel).parent = group
            box("Burned market corner post",
                (x+side*width*.33, y-street*depth*.33, level/2),
                (.080, .080, level/2), self.dark).parent = group
        box("Surviving market crossbeam", (x, y-street*depth*.31, level),
            (width*.37, .060, .080), self.steel).parent = group
        canopy = box("Charred market roof remnant",
                     (x-width*.215,y-street*depth*.245,level+.09),
                     (width*.15,depth*.133,.026),self.dark,.012)
        canopy.rotation_euler.x = street*.19
        canopy.parent = group
        for index in range(4):
            rib = box("Charred market roof seam",
                      (width*(index-1.5)*.068,0,.037),
                      (.016,depth*.124,.014),self.steel,.005)
            rib.parent = canopy
        shutter = box("Buckled market storefront shutter",
                      (x-width*.16,y+street*depth*.25,.52),
                      (width*.13,.038,.42),self.blue_sheet,.018)
        shutter.rotation_euler.x = street*.24
        shutter.parent = group
        box("Charred market storefront jamb", (x-width*.31,y+street*depth*.25,.67),
            (.055,.055,.67),self.dark,.012).parent = group
        brace = box("Fallen market roof brace",
                    (x+width*.16,y+street*depth*.13,.78),
                    (.055,depth*.24,.055),self.steel,.014)
        brace.rotation_euler.x = street*.48
        brace.rotation_euler.z = -.19
        brace.parent = group
        for offset, height in ((-.25,.17), (.03,.28), (.30,.12)):
            piece = self.concrete_box("Fallen market floor fragment",
                                      (x+width*offset, y+street*depth*.08, .32+height),
                                      (width*.11, depth*.16, .065))
            piece.rotation_euler.y = offset
            piece.parent = group

    def scavenger_stall(self, group, name, x, y, length, width, yaw):
        group.location = (x,y,0)
        group.rotation_euler.z = yaw
        covers = {
            "market_nw": ("rust",), "market_n": ("sand","olive"),
            "market_ne": ("sand","blue"), "market_w": ("blue",),
            "market_sw": ("blue","rust"), "market_e": ("olive",),
            "market_south": ("sand","blue"), "market_sw2": ("rust","sand"),
            "market_se2": ("blue",),
        }
        box("Salvaged market counter", (0,0,.525), (length*.43,width*.27,.055),
            self.steel).parent = group
        for end in (-1,1):
            box("Scavenger counter trestle", (length*end*.33,0,.24),
                (min(.075,length*.04),width*.23,.24), self.dark).parent = group
        for offset in (-.32, 0, .30):
            box("Scavenger parts bin", (length*offset,0,.64),
                (length*.085,width*.15,.075), self.dark).parent = group
        for offset, cross, height in ((-.34,-.05,.05),(-.29,.065,.031),(.02,.045,.064),(.31,-.052,.045)):
            box("Scavenger recovered machine part", (length*offset,width*cross,.715+height),
                (length*.024,width*.041,height), self.steel,.011).parent = group
        if name in {"market_n", "market_w", "market_south", "market_se2"}:
            radius = min(.074,length*.034,width*.09)
            bpy.ops.mesh.primitive_torus_add(
                major_segments=16, minor_segments=8, major_radius=radius, minor_radius=radius*.24,
                location=(-length*.018,-width*.058,.715+radius*.40),
                rotation=(.18,0,.25),
            )
            bearing = bpy.context.object
            bearing.name = "Scavenger reclaimed bearing"
            bearing.data.materials.append(self.steel)
            bearing.parent = group
        else:
            coil = box("Scavenger used motor housing", (-length*.018,-width*.040,.766),
                       (length*.032,width*.050,.051),self.steel,.018)
            coil.rotation_euler.z = .31
            coil.parent = group
        fabrics = covers.get(name, ())
        for index, fabric in enumerate(fabrics):
            half = length*(.20 if len(fabrics) == 2 else .26)
            center = length*((index-.5)*.45 if len(fabrics) == 2 else .14)
            depth = width*.40
            for side in (-1,1):
                for end in (-1,1):
                    box("Salvaged canopy post", (center+end*half,side*depth,.58),
                        (.037,.037,.58), self.dark).parent = group
            mesh = bpy.data.meshes.new("Salvaged canvas")
            corners = [(center-half,-depth,1.14), (center+half,-depth,1.16),
                       (center+half,depth,1.12), (center-half,depth,1.15)]
            edge_midpoints = [(center,-depth,1.065), (center+half,0,1.08),
                              (center,depth,1.035), (center-half,0,1.075)]
            ridge = (center+half*.14,width*.06,1.30+index*.035)
            vertices = corners+edge_midpoints+[ridge]
            faces = [(i,4+i,8) for i in range(4)] + [(4+i,(i+1)%4,8) for i in range(4)]
            patch = faces.pop((len(name)+index)%len(faces))
            center_point = sum((Vector(vertices[i]) for i in patch), Vector((0,0,0)))/3
            vertices.extend(center_point.lerp(Vector(vertices[i]), .67) for i in patch)
            for edge in range(3):
                following = (edge+1)%3
                faces.append((patch[edge],patch[following],9+following,9+edge))
            faces.append((9,10,11))
            mesh.from_pydata(vertices, [], faces)
            mesh.materials.append(self.stall_fabric[fabric])
            repair_fabric = "sand" if fabric in {"blue", "rust"} else "olive" if fabric == "sand" else "rust"
            mesh.materials.append(self.stall_fabric[repair_fabric])
            mesh.polygons[-1].material_index = 1
            cloth = bpy.data.objects.new("Salvaged canopy "+fabric, mesh)
            bpy.context.collection.objects.link(cloth)
            cloth.parent = group

    def burned_market_stall(self, group, name, x, y, length, width, yaw):
        group.location = (x, y, 0)
        group.rotation_euler.z = yaw
        for side in (-1, 1):
            box("Charred stall counter", (0, side*width*.30, .40),
                (length*.44, width*.12, .12), self.dark).parent = group
            box("Charred canopy rail", (0, side*width*.35, 1.07),
                (length*.44, .038, .043), self.steel).parent = group
            for end in (-1, 1):
                box("Charred stall upright", (end*length*.39, side*width*.35, .54),
                    (.045, .045, .54), self.dark).parent = group
        if name in {"stall_w", "stall_ne", "stall_sw"}:
            # A remaining crossbar and short hanging fragments reveal the
            # collapsed roof without filling the open stall silhouette.
            crossbar_x = length*(.18 if name == "stall_ne" else -.24)
            crossbar = box("Surviving canopy crossbar", (crossbar_x,0,1.045),
                           (.034,width*.37,.028), self.steel)
            crossbar.rotation_euler.z = .16
            crossbar.parent = group
            rail_y = width*.35
            vertices = [(length*x, rail_y+y*width, z) for x,y,z in (
                (-.38,0,1.09), (.25,0,1.09), (.14,.07,.99),
                (-.04,.10,.85), (-.18,.07,.98), (-.33,.06,.91),
            )]
            scraps = bpy.data.meshes.new("Scorched market fabric")
            scraps.from_pydata(vertices, [], [(0,5,4), (0,4,1), (1,4,3), (1,3,2)])
            scraps.materials.append(self.scorched_canvas)
            fabric = bpy.data.objects.new("Hanging canopy remnants", scraps)
            bpy.context.collection.objects.link(fabric)
            fabric.parent = group
            for offset, angle in ((-.27,.23),(.19,-.32)):
                scrap = box("Collapsed charred stall plank", (offset*length,0,.14),
                            (length*.13,width*.075,.038),self.dark,.014)
                scrap.rotation_euler = (.18,0,angle)
                scrap.parent = group
            tray = box("Burned stall fallen stock tray", (length*.18,-width*.16,.083),
                       (length*.12,width*.12,.057),self.scorched_canvas,.021)
            tray.rotation_euler.z = -.19 if name == "stall_ne" else .28
            tray.parent = group
            for offset in (-1, 1):
                runner = box("Burned tray split slat", (0,offset*width*.079,.065),
                             (length*.107,width*.022,.014),self.steel,.006)
                runner.parent = tray
            return
        if name == "stall_se":
            box("Blue corrugated market cover", (0,0,1.105),
                (length*.31,width*.32,.031), self.blue_sheet).parent = group
            for rib in range(-4, 5):
                box("Corrugated cover rib", (rib*length*.065,0,1.144),
                    (.020,width*.32,.017), self.blue_sheet,.008).parent = group
            return
        vertices = [(-length*.39,-width*.35,1.08), (length*.39,-width*.35,1.08),
                    (length*.39,width*.35,1.08), (-length*.39,width*.35,1.08),
                    (length*.09,0,1.22)]
        faces = [(0,1,4), (2,3,4), (3,0,4)]
        mesh = bpy.data.meshes.new("Torn canvas")
        mesh.from_pydata(vertices, [], faces)
        mesh.materials.append(self.red_canvas if name in {"stall_n", "stall_e"} else self.scorched_canvas)
        canopy = bpy.data.objects.new("Torn market canvas", mesh)
        bpy.context.collection.objects.link(canopy)
        canopy.parent = group

    def stripped_car(self, group, x, y, length, width, yaw):
        group.location = (x, y, 0)
        group.rotation_euler.z = yaw
        box("Stripped car exposed floor", (0,0,.22),
            (length*.47,width*.43,.11), self.dark).parent = group
        for end in (-1,1):
            box("Stripped car crushed deck", (end*length*.34,0,.34),
                (length*.13,width*.43,.11), self.steel).parent = group
        for side in (-1,1):
            box("Stripped car torn sill", (0,side*width*.43,.32),
                (length*.33,width*.055,.12), self.steel).parent = group
            for offset in (-.24,.20):
                pillar = box("Stripped car window frame", (length*offset,side*width*.42,.49),
                             (length*.035,width*.042,.19), self.steel)
                pillar.rotation_euler.y = -offset
                pillar.parent = group

    def open_bus_wreck(self, group, x, y, length, width, yaw):
        group.location = (x, y, 0)
        group.rotation_euler.z = yaw
        box("Bus wreck floor", (0,0,.38), (length*.48,width*.46,.13), self.dark).parent = group
        box("Surviving bus roof", (-length*.31,0,1.18),
            (length*.155,width*.44,.052), self.steel).parent = group
        for side in (-1,1):
            box("Bus wreck side sill", (0,side*width*.43,.64),
                (length*.47,width*.055,.17), self.steel).parent = group
            for offset in (-.15,.02,.20,.39):
                box("Exposed bus window pillar", (length*offset,side*width*.43,.96),
                    (.042,.039,.20), self.dark).parent = group
            for offset in (-.32,.32):
                radius = min(.23,length*.078)
                bpy.ops.mesh.primitive_cylinder_add(
                    vertices=16, radius=radius, depth=width*.19,
                    location=(length*offset,side*width*.38,radius),
                    rotation=(math.pi/2,0,0),
                )
                wheel = bpy.context.object
                wheel.name = "Bus wreck grounded tire"
                wheel.data.materials.append(self.dark)
                wheel.parent = group
                box("Bus wreck hub", (length*offset,side*width*.48,radius),
                    (radius*.36,width*.016,radius*.36), self.steel,.023).parent = group

    def downtown_road_cover(self, group, name, x, y, length, width, yaw):
        group.location = (x,y,0)
        group.rotation_euler.z = yaw
        rubble = name.startswith("rubble_")
        for index, height in enumerate((.21,.33,.26) if rubble else (.44,.63,.51)):
            along = length*(index-1)*.31
            cross = width*(.08 if index == 1 else -.06)
            if rubble:
                slab = self.concrete_box("Downtown fallen masonry", (along,cross,height*.48),
                                        (length*.13,width*.32,height*.48), .045)
                slab.rotation_euler.z = (.16,-.22,.12)[index]
            else:
                slab = self.concrete_guardrail("Downtown fractured road barrier",
                                               length*.29,width*.80,height)
                slab.location = (along,cross,0)
            slab.parent = group
        if rubble:
            for along, cross, angle in ((-.38,.30,.44), (-.12,-.32,-.28),
                                         (.18,.31,.60), (.37,-.28,-.47)):
                chip = self.concrete_box("Downtown loose masonry fragment",
                                         (length*along,width*cross,.064),
                                         (length*.052,width*.095,.068),.028)
                chip.rotation_euler.z = angle
                chip.parent = group

    def downtown_exposed_frame(self, group, name, x, y, width, depth):
        street_side = -1 if name.startswith("n") else 1
        height = 2.35 if name in {"nw_ruin", "se_ruin"} else 1.75
        facade_y = y+street_side*depth*.486
        missing_bay = -1 if name.startswith(("nw", "se")) else 1
        box("Downtown exposed storefront lintel", (x,facade_y,1.29),
            (width*.24,.058,.071), self.steel,.018).parent = group
        for bay in (-1, 0, 1):
            if bay == missing_bay:
                continue
            for offset, panel_height in ((-.075,.12), (.075,.085)):
                box("Surviving blue facade panel", (x+(bay*.31+offset)*width, facade_y, .49),
                    (width*.065,.021,panel_height), self.facade_blue,.012).parent = group
            box("Corroded facade rail", (x+bay*.31*width, facade_y, .66),
                (width*.14,.032,.025), self.steel,.01).parent = group
        for side in (-1, 1):
            box("Exposed corner column", (x+side*width*.35, y+street_side*depth*.35, height/2),
                (.075, .075, height/2), self.steel).parent = group
            rear_height = height if side != missing_bay else height*.64
            box("Downtown rear column remnant",
                (x+side*width*.35,y-street_side*depth*.34,rear_height/2),
                (.075,.075,rear_height/2), self.steel).parent = group
            box("Surviving roof girder", (x+side*width*.35, y, height),
                (.055, depth*.37, .075), self.dark).parent = group
        for offset in (-.34, .08):
            box("Exposed transverse beam", (x, y+street_side*offset*depth, height),
                (width*.355, .055, .066), self.steel).parent = group
        self.concrete_box("Broken upper floor remnant",
                          (x-width*.22, y-street_side*depth*.18, height-.11),
                          (width*.125, depth*.20, .10)).parent = group
        # Leave the missing bays open while showing the collapse below them.
        for offset, distance, angle in ((-.17,.12,-.28),(.06,.25,.36),(.24,-.12,-.19)):
            fragment = self.concrete_box(
                "Downtown collapsed floor fragment",
                (x+offset*width,y+street_side*distance*depth,.39),
                (width*.085,depth*.088,.074),.028,
            )
            fragment.rotation_euler.x = angle
            fragment.rotation_euler.z = street_side*angle
            fragment.parent = group

    def overpass_ruin(self, group, name, x, y, width, depth):
        self.concrete_box("Ruined foundation", (x, y, .065),
                          (width*.47, depth*.45, .065)).parent = group
        front = 1 if name.startswith(("nw", "ne")) else -1
        side = -1 if name.startswith(("nw", "sw")) else 1
        # Keep fragment geometry inside the surveyed ruin footprint.
        fragments = ((-.31, -.15, .10, .22), (-.15, -.27, .14, -.31),
                     (.06, -.20, .08, .39), (.25, -.12, .13, -.19))
        for dx, dy, height, angle in fragments:
            fragment = self.concrete_box(
                "Scattered concrete fragment",
                (x+side*dx*width, y+front*dy*depth, .13+height*.52),
                (min(.35, width*.074), min(.26, depth*.085), height*.52), .035,
            )
            fragment.rotation_euler = (angle*.5, 0, side*angle)
            fragment.parent = group
        if "_inner_" in name:
            for offset, height in ((-.27, .72), (.17, .43)):
                self.concrete_box("Broken ramp-side retaining wall",
                                  (x+offset*width, y+front*depth*.28, height/2),
                                  (width*.17, depth*.095, height/2)).parent = group
            debris = self.concrete_box("Fallen retaining slab", (x, y-front*depth*.14, .31),
                                       (width*.29, depth*.13, .08))
            debris.rotation_euler.x = front*.25
            debris.parent = group
            beam = box("Buckled ramp-side steel support",
                       (x-side*width*.09, y-front*depth*.10, .49),
                       (width*.24,.056,.072), self.steel,.013)
            beam.rotation_euler = (0,side*.26,front*.31)
            beam.parent = group
        else:
            for offset, height in ((-.32, 1.48), (0, 1.08), (.30, .59)):
                self.concrete_box("Fractured exterior wall",
                                  (x+side*offset*width, y+front*depth*.39, height/2),
                                  (width*.13, depth*.07, height/2)).parent = group
            self.concrete_box("Surviving corner pier",
                              (x+side*width*.40, y-front*depth*.09, .66),
                              (width*.08, depth*.28, .66)).parent = group
            frame_y = y+front*depth*.25
            span = width*.48
            for end, height in ((-1,1.72),(1,1.32)):
                box("Exposed overpass ruin column", (x+end*span*.5,frame_y,height*.5),
                    (.050,.048,height*.5),self.steel,.008).parent = group
            box("Exposed overpass ruin lintel", (x,frame_y,1.26),
                (span*.52,.050,.049),self.steel,.008).parent = group
            brace = box("Exposed overpass ruin diagonal", (x,frame_y,.73),
                        (math.hypot(span,.92)*.5,.038,.036),self.steel,.008)
            brace.rotation_euler.y = side*math.atan2(.92,span)
            brace.parent = group

    def trainyard_workshop_ruin(self, group, name, x, y, width, depth):
        # The survey covers roofless workshops, with the surviving walls at
        # the back and an open, broken edge toward the north siding.
        slab = self.concrete_box("Workshop slab", (x, y, .035),
                                 (width*.49, depth*.48, .035))
        slab.parent = group
        if self.surveyed_surface is not None:
            mesh = slab.data
            mesh.materials.append(self.surveyed_surface)
            uv = mesh.uv_layers.active
            for face in mesh.polygons:
                if face.normal.z < .9:
                    continue
                face.material_index = 1
                for index in face.loop_indices:
                    point = mesh.vertices[mesh.loops[index].vertex_index].co
                    uv.data[index].uv = (.5+(x+point.x)/self.gw, .5+(y+point.y)/self.gh)
        self.concrete_box("Workshop rear wall", (x-width*.06, y+depth*.42, .38),
                          (width*.41, depth*.055, .38)).parent = group
        high_side = -1 if name == "northwest_ruin" else 1
        coping = self.concrete_box("Workshop broken rear wall crest",
                                   (x+high_side*width*.23,y+depth*.42,.845),
                                   (width*.16,depth*.048,.105),.040)
        coping.rotation_euler.y = high_side*.08
        coping.parent = group
        for side in (-1, 1):
            self.concrete_box("Workshop return wall",
                              (x+side*width*.44, y+depth*.14, .28),
                              (min(.18, width*.055), depth*.32, .28)).parent = group
        for offset in ((-.32, .04, .32) if name == "northwest_ruin" else (-.22, .23)):
            self.concrete_box("Broken workshop frontage",
                              (x+width*offset, y-depth*.43, .15),
                              (width*.10, depth*.05, .15)).parent = group
        for offset, angle in ((-.32,.24),(.30,-.19)):
            fragment = self.concrete_box("Fallen workshop masonry",
                                         (x+width*offset,y-depth*.30,.16),
                                         (width*.082,depth*.074,.10))
            fragment.rotation_euler.z = angle
            fragment.parent = group
        equipment = (
            ("Workshop service cabinet", "industrial_service267/model.glb", 130, 28, 43, 35, .65),
            ("Workshop parts crate", "cargo_crate274/model.glb", 201, 28, 29, 24, .43),
            ("Workshop fan assembly", "roof_twin_fan/optimized.glb", 301, 21, 44, 27, .30),
        ) if name == "northwest_ruin" else (
            ("Workshop service cabinet", "industrial_service267/model.glb", 615, 48, 36, 29, .65),
        )
        for label, asset, px, py, w, d, height in equipment:
            fixture_x, fixture_y = self.coordinates(px, py)
            parts = place(self.library / asset, group, (fixture_x, fixture_y, .07),
                          (w*self.gw/self.cw, d*self.gh/self.ch, height), merge=True)
            for part in parts:
                part.name = label

    def trainyard_turntable(self, x, y, yaw, wagon_width):
        bridge = bpy.data.objects.new("Trainyard turntable bridge", None)
        bpy.context.collection.objects.link(bridge)
        bridge.location = (x, y, 0)
        bridge.rotation_euler.z = yaw
        length = 2 * math.hypot(64*self.gw/self.cw, 52*self.gh/self.ch)
        radius = length / 2
        segments = 48
        profile = ((radius+.08, .018), (radius+.06, .074),
                   (radius-.06, .074), (radius-.08, .027))
        vertices = []
        faces = []
        for segment in range(segments):
            angle = math.tau*segment/segments
            vertices.extend((r*math.cos(angle), r*math.sin(angle), z)
                            for r, z in profile)
            current = segment*len(profile)
            following = ((segment+1) % segments)*len(profile)
            for edge in range(len(profile)-1):
                faces.append((current+edge, following+edge,
                              following+edge+1, current+edge+1))
        mesh = bpy.data.meshes.new("Turntable rim profile")
        mesh.from_pydata(vertices, [], faces)
        mesh.materials.append(self.steel)
        mesh.materials.append(self.dark)
        for face in mesh.polygons:
            face.material_index = 0 if face.index % (len(profile)-1) == 1 else 1
        rim = bpy.data.objects.new("Turntable circular rim", mesh)
        bpy.context.collection.objects.link(rim)
        rim.parent = bridge

        gauge = wagon_width * .63
        box("Turntable bridge deck", (0,0,.023),
            (length*.486,gauge*.79,.023),self.dark,.009).parent = bridge
        for index in range(-7, 8):
            sleeper = box("Turntable sleeper", (index*length/16, 0, .052),
                          (length/48, gauge*.75, .030), self.dark, .008)
            sleeper.parent = bridge
        for side in (-1, 1):
            box("Turntable bridge edge beam", (0,side*gauge*.78,.041),
                (length*.482,.024,.024),self.steel,.007).parent = bridge
            rail = box("Turntable bridge rail", (0, side*gauge/2, .095),
                       (length/2, .026, .024), self.steel, .008)
            rail.parent = bridge

    def trainyard_wagon(self, group, name, x, y, length, width, yaw):
        group.location = (x,y,0)
        group.rotation_euler.z = yaw

        def part(label, along, across, z, dimensions, material):
            box(label, (along,across,z), dimensions, material,.019).parent = group

        part("Wagon underframe", 0,0,.30, (length*.47,width*.43,.13), self.dark)
        part("Wagon coupling", 0,0,.36, (length*.49,width*.105,.049), self.dark)
        for end in (-1,1):
            part("Wagon bogie", end*length*.29,0,.18, (length*.098,width*.43,.15), self.dark)
        if name in {"wagon_sw", "wagon_s", "north_tank"}:
            radius = min(width*.37,.54)
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=length*.84,
                location=(0,0,.46+radius), rotation=(0,math.pi/2,0))
            tank = bpy.context.object
            tank.name = "Rail tanker cylinder"
            tank.data.materials.append(self.steel)
            tank.parent = group
            for offset in (-.31,0,.31):
                bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=6,
                    major_radius=radius, minor_radius=.019,
                    location=(offset*length,0,.46+radius), rotation=(0,math.pi/2,0))
                brace = bpy.context.object
                brace.name = "Rail tanker brace"
                brace.data.materials.append(self.dark)
                brace.parent = group
        elif name in {"wagon_n3", "wagon_mid"}:
            part("Open wagon recessed floor", 0,0,.465, (length*.44,width*.39,.055), self.dark)
            for side in (-1,1):
                part("Open wagon side", 0,side*width*.398,.69, (length*.45,width*.048,.24), self.steel)
                part("Open wagon end", side*length*.431,0,.69, (length*.036,width*.40,.24), self.steel)
            for section in (-.29,0,.29):
                part("Open wagon cargo rib", section*length,0,.536,
                     (length*.022,width*.34,.03), self.steel)
            for along, across, angle in ((-.28,-.12,.31),(-.08,.10,-.34),(.13,-.08,.39),(.31,.10,-.23)):
                scrap = box("Open wagon salvaged plate", (along*length,across*width,.59),
                            (length*.089,width*.105,.043), self.steel,.012)
                scrap.rotation_euler.z = angle
                scrap.parent = group
            part("Open wagon bent crossmember", .16,.02,.66,
                 (length*.18,width*.028,.025), self.dark)
        else:
            part("Covered wagon body", 0,0,.81, (length*.443,width*.416,.405), self.steel)
            part("Covered wagon roof", 0,0,1.245, (length*.461,width*.439,.066), self.steel)
            for seam in (-.34, -.17, 0, .17, .34):
                part("Covered wagon roof seam", seam*length,0,1.315,
                     (.018,width*.425,.013), self.dark)
            part("Covered wagon replacement roof sheet", length*.24,width*.08,1.318,
                 (length*.067,width*.27,.014), self.dark)
            for side in (-1,1):
                part("Wagon sliding door", 0,side*width*.423,.803,
                     (length*.164,width*.025,.307), self.dark)
                for elevation in (.49, 1.13):
                    part("Wagon sliding door runner", length*.065,side*width*.455,elevation,
                         (length*.238,.018,.026),self.steel)
                part("Wagon sliding door pull", -length*.115,side*width*.457,.79,
                     (.027,.024,.072),self.steel)
                for bay in (-.35,-.22,.22,.35):
                    part("Wagon cladding rib", bay*length,side*width*.434,.82,
                         (.024,.018,.357), self.steel)

    def convoy_vehicle(self, group, name, x, y, length, width, yaw):
        group.location = (x,y,0)
        group.rotation_euler.z = yaw + (0 if name == "convoy_e" else math.pi)

        cab_sources = {"convoy_w": (55,243,92,270), "convoy_mw": (269,239,304,274),
                       "convoy_me": (468,242,500,274), "convoy_e": (711,241,731,271),
                       "convoy_far_e": (773,242,810,270)}
        tarp_sources = {"convoy_w": (101,233,168,274), "convoy_e": (641,231,706,271),
                        "convoy_far_e": (822,235,874,273)}

        def project_art(obj, source, min_up=.9):
            if not self.convoy_crossing or source is None:
                return
            mesh = obj.data
            mesh.materials.append(self.surveyed_surface)
            uv = mesh.uv_layers.active
            transform = group.matrix_basis @ obj.matrix_basis
            points = [transform @ vertex.co for vertex in mesh.vertices]
            x0, x1 = min(p.x for p in points), max(p.x for p in points)
            y0, y1 = min(p.y for p in points), max(p.y for p in points)
            left, top, right, bottom = source
            for face in mesh.polygons:
                if (transform.to_3x3() @ face.normal).normalized().z < min_up:
                    continue
                face.material_index = 1
                for index in face.loop_indices:
                    point = points[mesh.loops[index].vertex_index]
                    u = left+(right-left)*(point.x-x0)/(x1-x0)
                    v = bottom-(bottom-top)*(point.y-y0)/(y1-y0)
                    uv.data[index].uv = (u/self.cw,1-v/self.ch)

        def part(label, position, scale, material, bevel=.035, *, source=None):
            obj = box(label, position, scale, material, bevel)
            obj.parent = group
            project_art(obj, source)

        def shaped_body(label, sections, material, source, min_up):
            vertices = []
            for rear, front, half_width, z in sections:
                vertices.extend(((rear,-half_width,z), (front,-half_width,z),
                                 (front,half_width,z), (rear,half_width,z)))
            faces = [(3,2,1,0)]
            for lower in range(0,len(vertices)-4,4):
                for edge in range(4):
                    first, second = lower+edge, lower+(edge+1)%4
                    faces.append((first,second,second+4,first+4))
            faces.append(tuple(range(len(vertices)-4,len(vertices))))
            mesh = bpy.data.meshes.new(label)
            mesh.from_pydata(vertices, [], faces)
            mesh.materials.append(material)
            mesh.uv_layers.new()
            for face in mesh.polygons:
                for index in face.loop_indices:
                    point = mesh.vertices[mesh.loops[index].vertex_index].co
                    mesh.uv_layers.active.data[index].uv = (point.x+point.y,point.z)
            obj = bpy.data.objects.new(label, mesh)
            bpy.context.collection.objects.link(obj)
            obj.parent = group
            bevel = obj.modifiers.new("Folded body edges", "BEVEL")
            bevel.width = .038
            bevel.segments = 2
            project_art(obj, source, min_up)

        stripped_flatbed = self.convoy_crossing and name.startswith("wreck_")
        chassis_width = .285 if self.convoy_crossing else .40
        chassis_center, chassis_span = (.345,.134) if stripped_flatbed else (0,.48)
        part("Convoy chassis", (length*chassis_center,0,.44),
             (length*chassis_span,width*chassis_width,.13), self.dark)
        body_steel = self.convoy_steel if self.convoy_crossing else self.steel
        if self.convoy_crossing:
            shaped_body("Convoy cab", (
                (length*.22,length*.46,width*.32,.53),
                (length*.21,length*.477,width*.393,.79),
                (length*.215,length*.463,width*.365,1.21),
                (length*.24,length*.412,width*.318,1.40),
            ), body_steel, cab_sources.get(name), .9)
            glass = box("Convoy windshield", (length*.439,0,1.315),
                        (.019,width*.312,.101),self.convoy_glass,.012)
            glass.rotation_euler.y = -math.atan2(length*.051,.19)
            glass.parent = group
            for side in (-1,1):
                part("Convoy door glazing", (length*.334,side*width*.381,1.14),
                     (length*.089,.027,.112),self.convoy_glass,.020)
                part("Convoy front mudguard", (length*.35,side*width*.424,.688),
                     (length*.078,width*.064,.052),body_steel,.038)
        else:
            part("Convoy cab", (length*.345,0,.80), (length*.139,width*.40,.34), body_steel)
            part("Convoy windshield", (length*.481,0,.924), (.016,width*.33,.111), self.dark)
        if (self.salt_flat or self.dust_road or self.wrecked_highway
                or self.scavenger_plaza or self.ruined_downtown):
            for side in (-1, 1):
                part("Wreck side window", (length*.35,side*width*.405,.94),
                     (length*.085,.012,.102), self.dark,.012)
                part("Wreck cab sill", (length*.35,side*width*.412,.58),
                     (length*.12,.024,.033), self.dark,.011)
        if (self.salt_flat or self.dust_road or self.wrecked_highway or self.convoy_crossing
                or self.scavenger_plaza or self.ruined_downtown):
            part("Wreck front bumper", (length*.484,0,.45),
                 (.013,width*.42,.052), self.dark,.012)
        if self.convoy_crossing:
            part("Convoy radiator grille", (length*.485,0,.702),
                 (.014,width*.227,.071), self.dark,.011)
            for elevation in (.668,.700,.732):
                part("Convoy grille louver", (length*.488,0,elevation),
                     (.008,width*.204,.006), self.steel,.004)
            for side in (-1,1):
                part("Convoy headlamp housing", (length*.485,side*width*.324,.701),
                     (.013,width*.057,.042), self.dark,.010)
                part("Convoy headlamp lens", (length*.489,side*width*.324,.701),
                     (.009,width*.041,.023), self.steel,.006)
                part("Convoy cab access step", (length*.32,side*width*.449,.491),
                     (length*.093,.036,.025), self.dark,.009)
        if stripped_flatbed:
            for side in (-1, 1):
                part("Wreck exposed frame rail", (-length*.143,side*width*.235,.56),
                     (length*.325,width*.045,.059),body_steel,.016)
                part("Wreck rear mudflap", (-length*.408,side*width*.405,.36),
                     (.021,width*.10,.166),self.convoy_rubber,.012)
            part("Wreck rear underride beam", (-length*.462,0,.41),
                 (.031,width*.43,.043),body_steel,.016)
        elif self.convoy_crossing and name == "convoy_mw":
            part("Convoy tanker cradle beam", (-length*.143,0,.59),
                 (length*.315,width*.245,.089),body_steel,.027)
            for side in (-1,1):
                part("Convoy tanker rear fender", (-length*.27,side*width*.415,.756),
                     (length*.143,width*.075,.045),body_steel,.037)
            part("Convoy tanker rear bumper", (-length*.459,0,.397),
                 (.036,width*.408,.058),body_steel,.017)
        else:
            part("Convoy cargo bed", (-length*.143,0,.60), (length*.325,width*.415,.055), self.steel)
        # Keep the wheel tops above the chassis underside at .31 m.
        wheel_radius = min(.38,max(.23,width*.23)) if self.convoy_crossing else min(.30,max(.17,width*.19))
        for side in (-1,1):
            for offset in (-.35,-.19,.35):
                bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=wheel_radius,
                    depth=width*.14, location=(length*offset,side*width*.41,wheel_radius),
                    rotation=(math.pi/2,0,0))
                wheel = bpy.context.object
                wheel.name = "Convoy wheel"
                wheel.data.materials.append(self.convoy_rubber if self.convoy_crossing else self.dark)
                wheel.parent = group
                if self.convoy_crossing:
                    for face in wheel.data.polygons:
                        face.use_smooth = len(face.vertices) == 4
                    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=wheel_radius*.52,
                        depth=.04, location=(length*offset,side*width*.48,wheel_radius),
                        rotation=(math.pi/2,0,0))
                    hub = bpy.context.object
                    hub.name = "Convoy axle hub"
                    hub.data.materials.append(body_steel)
                    hub.parent = group
        if name == "convoy_mw":
            radius = min(.43,width*.33)
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius,
                depth=length*.59, location=(-length*.13,0,1.04), rotation=(0,math.pi/2,0))
            tank = bpy.context.object
            tank.name = "Convoy tanker vessel"
            tank.data.materials.append(body_steel)
            tank.parent = group
            if group.name == "Occludable_convoy_mw":
                project_art(tank, (316,238,419,273), min_up=.30)
            for face in tank.data.polygons:
                face.use_smooth = len(face.vertices) == 4
            if self.convoy_crossing or self.salt_flat or self.dust_road or self.wrecked_highway:
                for end in (-.425,.165):
                    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12,
                        radius=radius, location=(length*end,0,1.04))
                    cap = bpy.context.object
                    cap.name = "Convoy tanker dished end"
                    cap.scale.x = min(.10,length*.025)/radius
                    for face in cap.data.polygons:
                        face.use_smooth = True
                    cap.data.materials.append(body_steel)
                    cap.parent = group
                bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius*.42,
                    depth=.072, location=(-length*.13,0,1.06+radius))
                hatch = bpy.context.object
                hatch.name = "Convoy tanker inspection hatch"
                hatch.data.materials.append(self.dark)
                hatch.parent = group
            for offset in (-.31,.03):
                bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=6,
                    major_radius=radius, minor_radius=.023,
                    location=(length*offset,0,1.04), rotation=(0,math.pi/2,0))
                band = bpy.context.object
                band.name = "Convoy tank band"
                band.data.materials.append(self.dark)
                band.parent = group
                if self.convoy_crossing:
                    for side in (-1, 1):
                        part("Convoy tanker saddle bracket",
                             (length*offset,side*radius*.66,.725),
                             (length*.023,radius*.27,.105), self.dark,.018)
        elif name == "convoy_me":
            # Sample the four main crate lids and the smaller crate at the tail.
            crate_lids = {
                (-1, 1): (518,238,531,249), (1, 1): (520,252,533,262),
                (-1, 0): (541,236,552,247), (1, 0): (542,251,553,261),
                (-1,-1): (576,251,586,257), (1,-1): (576,251,586,257),
            }
            for row in (-1,1):
                for slot in (-1,0,1):
                    crate_x, crate_y = (-.147+slot*.19)*length, row*width*.205
                    part("Convoy strapped crate", (crate_x,crate_y,.83),
                         (length*.079,width*.155,.18),self.canvas,
                         source=crate_lids[row,slot])
                    if self.convoy_crossing:
                        for offset in (-.047,.047):
                            part("Convoy crate lid batten", (crate_x+length*offset,crate_y,1.02),
                                 (length*.006,width*.15,.013),self.dark,.006)
        elif name.startswith("wreck_"):
            for side in (-1,1):
                part("Wreck flatbed side rail", (-length*.135,side*width*.365,.75),
                     (length*.291,.036,.081),self.steel,.012)
            crossmember_offsets = (-.40,-.14,.107) if stripped_flatbed else tuple(
                -.395+slot*.085 for slot in range(7)
            )
            for offset in crossmember_offsets:
                part("Wreck flatbed crossmember", (offset*length,0,.668),
                     (length*.021,width*.348,.028),self.dark,.009)
            if stripped_flatbed:
                for offset in (-.35,-.19):
                    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.052,
                        depth=width*.72, location=(length*offset,0,wheel_radius),
                        rotation=(math.pi/2,0,0))
                    axle = bpy.context.object
                    axle.name = "Wreck exposed rear axle"
                    axle.data.materials.append(body_steel)
                    axle.parent = group
                bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.047,
                    depth=length*.49, location=(-length*.079,0,wheel_radius+.018),
                    rotation=(0,math.pi/2,0))
                shaft = bpy.context.object
                shaft.name = "Wreck exposed drive shaft"
                shaft.data.materials.append(body_steel)
                shaft.parent = group
        else:
            tarp = self.canvas
            if self.convoy_crossing:
                tarp = self.convoy_tarps["tan" if name == "convoy_e" else "olive"]
            if self.convoy_crossing:
                shaped_body("Convoy tarpaulin load", (
                    (-length*.45,length*.156,width*.383,.66),
                    (-length*.45,length*.156,width*.386,1.08),
                    (-length*.43,length*.137,width*.319,1.28),
                    (-length*.415,length*.122,width*.192,1.37),
                ), tarp, tarp_sources.get(name), .45)
            else:
                part("Convoy tarpaulin load", (-length*.147,0,.94),
                     (length*.303,width*.386,.286),tarp,.112)
            if not self.convoy_crossing:
                for offset in (-.34,-.18,-.02):
                    part("Convoy tarp strap", (length*offset,0,1.23),
                         (.024,width*.36,.018),self.dark,.007)

    def vehicle(self, group, name, x,y,w,d):
        vertical = d>w
        length, width = (d,w) if vertical else (w,d)
        group.location = (x,y,0)
        group.rotation_euler.z = math.pi/2 if vertical else 0
        bus = name.startswith("bus_")
        box(name+" chassis", (0,0,.42), (length*.47,width*.44,.26), self.dark).parent = group
        box(name+" body", (-length*.04,0,.83), (length*(.43 if bus else .27),width*.43,.38),
            self.steel).parent = group
        box(name+" cab", (length*.28,0,.80), (length*.16,width*.41,.34), self.steel).parent = group
        for side in (-1,1):
            for offset in (-.29,.29):
                box(name+" wheel", (length*offset,width*side*.40,.21),
                    (length*.082,width*.09,.21), self.dark, .065).parent = group
            for i in range(4 if bus else 1):
                box(name+" window", (length*(.28-i*.20),width*side*.44,.98),
                    (length*.075,.021,.103), self.dark).parent = group
