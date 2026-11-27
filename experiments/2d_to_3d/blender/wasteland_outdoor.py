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


class WastelandOutdoors:
    def __init__(self, library, grid, canvas, *, city=False, overpass=False, wrecked_highway=False, trainyard=False):
        self.library = library
        self.gw, self.gh = grid
        self.cw, self.ch = canvas
        self.city = city
        self.overpass = overpass
        self.wrecked_highway = wrecked_highway
        self.trainyard = trainyard
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
        pixels.reshape(-1, 4)[:, :3] *= (.40, .40, .38) if overpass else (.62, .58, .54)
        diffuse.image = bpy.data.images.new("Weathered Wasteland concrete", *source.size)
        diffuse.image.pixels.foreach_set(pixels)
        diffuse.image.pack()
        links.new(diffuse.outputs["Color"], shader.inputs["Base Color"])
        roughness = nodes.new("ShaderNodeTexImage")
        roughness.image = bpy.data.images.load(str(concrete_path / "rough.jpg"), check_existing=True)
        roughness.image.colorspace_settings.name = "Non-Color"
        links.new(roughness.outputs["Color"], shader.inputs["Roughness"])
        self.seam = make_material("Dark fractured concrete edge", (.095,.073,.052,1), .04,.95)
        self.steel = make_material("Corroded steel", (.13,.073,.042,1), .62,.69)
        self.dark = make_material("Weathered undercarriage", (.046,.039,.032,1), .4,.82)
        self.canvas = make_material("Weathered sandbags", (.21,.17,.11,1), 0,.94)

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
            for i, ((ax,ay),(bx,by)) in enumerate(zip(points, points[1:])):
                height = .56 + .15*(i % 3)
                length = math.hypot(bx-ax,by-ay)
                if self.overpass:
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
            vertices = [(x,y,0) for x,y in points]
            vertices.extend((x,y,crest[i]*(.64+.08*(i%3))) for i,(x,y) in enumerate(points))
            vertices.extend((x,y,crest[i]) for i,(x,y) in enumerate(points))
            faces = [tuple(reversed(range(n))), tuple(range(2*n,3*n))]
            for layer in (0, n):
                for i in range(n):
                    j = (i+1)%n
                    faces.append((layer+i,layer+j,layer+j+n,layer+i+n))
            broken_deck = self.overpass and ("span" in name or "ramp" in name)
            if broken_deck:
                # A dark intact substrate separates the lifted fragments.
                # Each inset face stays inside the original surveyed outline.
                for index, triangle in enumerate(tessellate_polygon([[Vector(point) for point in points]])):
                    corners = [vertices[2*n+corner] for corner in triangle]
                    center = tuple(sum(axis)/3 for axis in zip(*corners))
                    start = len(vertices)
                    for x,y,z in corners:
                        distance = math.hypot(center[0]-x,center[1]-y)
                        inset = min(.095,.052/max(distance,.01))
                        vertices.append((x+(center[0]-x)*inset,y+(center[1]-y)*inset,
                                         z+(center[2]-z)*inset+.032+(index%3)*.022))
                    faces.append((start,start+1,start+2))
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(vertices, [], faces)
            self.project_concrete_uv(mesh)
            for material in (self.stone, self.aggregate, self.seam):
                mesh.materials.append(material)
            mesh.polygons[1].material_index = 2 if broken_deck else 1
            if broken_deck:
                for face in mesh.polygons[2+2*n:]:
                    face.material_index = 1
            for i in range(n):
                mesh.polygons[2+n+i].material_index = 2 if i%3 == 0 else 1
            fragment = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(fragment)
            fragment.parent = group
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
        wreck_yaws = {"wreck_mid_w": -.16, "wreck_mid_e": -.34,
                     "wreck_far_e": -.09, "wreck_middle5": -.12}
        if self.trainyard and ("wagon" in name or name == "north_tank"):
            if name == "wagon_turntable":
                yaw = math.atan2(54*self.gh/self.ch, 66*self.gw/self.cw)
                length, breadth = w, d*.40
                c, s = math.cos(yaw), math.sin(yaw)
                fit = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
                length, breadth = length*fit, breadth*fit
                self.trainyard_turntable(x, y, yaw, breadth)
            self.trainyard_wagon(group, name, x, y, length, breadth, yaw)
        elif self.wrecked_highway and name in wreck_yaws:
            angle = -wreck_yaws[name]
            c,s = abs(math.cos(angle)),abs(math.sin(angle))
            scale = min(w/(length*c+breadth*s), d/(length*s+breadth*c))
            self.convoy_vehicle(group, name, x, y, length*scale, breadth*scale, angle)
        elif name.startswith("convoy_"):
            self.convoy_vehicle(group, name, x, y, length, breadth, yaw)
        elif self.city and name.startswith(("bus_", "truck_")):
            self.vehicle(group, name, x,y,w,d)
        elif name.startswith(("wreck_", "truck_", "convoy_", "car_")):
            place(self.library / "derelict_suv275/model.glb", group, (x,y,0),
                  (length*.97,breadth*.97,1.55), yaw=yaw + (math.pi if x<0 else 0))
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
            build_crane(group,x,y,w,d,self.dark,self.steel,height=3.4,outreach=min(length,2.5))
        elif any(part in name for part in ("pipe","tank","shelf")):
            place(self.library / "industrial_service267/model.glb", group, (x,y,0),
                  (length*.97,breadth*.97,1.42), yaw=yaw)
        elif "stall" in name or name.startswith("market_"):
            place(self.library / "market_southeast_display/shop.glb", group, (x,y,0),
                  (length*.96,breadth*.96,1.6), yaw=yaw, merge=True)
        elif "crate" in name:
            place(self.library / "cargo_crate274/model.glb", group, (x,y,0),
                  (length*.94,breadth*.94,.8), yaw=yaw)
        elif name.startswith("stairs_"):
            for step in range(6):
                height = (step+1)*.12
                box(name, (x,y+d*((step+.5)/6-.5),height/2),
                    (w*.48,d/12,height/2), self.stone).parent = group
        elif "column" in name or name == "monument":
            box(name+" footing", (x,y,.16), (w*.47,d*.47,.16), self.stone).parent = group
            box(name, (x,y,1.15), (w*.25,d*.25,1.0), self.stone).parent = group
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
        elif "sandbag" in name:
            for layer in range(2):
                for offset in (-.31,0,.31):
                    box(name, (x+(0 if vertical else offset*w),y+(offset*d if vertical else 0),.12+.19*layer),
                        (w*(.41 if vertical else .146),d*(.146 if vertical else .41),.11),
                        self.canvas, .08).parent = group
        elif self.trainyard and name in {"northwest_ruin", "northeast_ruin"}:
            self.trainyard_workshop_ruin(group, name, x, y, w, d)
        elif self.city and ("ruin" in name or name == "ne_corner"):
            self.concrete_box(name+" rubble base", (x,y,.16), (w*.47,d*.46,.16)).parent = group
            for side in (-1,1):
                for index in range(3):
                    height = .75+.22*((index+(side>0))%3)
                    self.concrete_box(name+" fractured facade", (x+(index-1)*w*.31,y+side*d*.41,height/2),
                        (w*.154,d*.075,height/2), .065).parent = group
            self.concrete_box(name+" end wall", (x-w*.405,y,.51), (w*.058,d*.36,.51), .065).parent = group
        elif any(part in name for part in ("ruin","rubble","wall","barrier")):
            for i in range(3):
                self.concrete_box(name,(x+w*(i-1)/3,y,.18+.11*i),
                    (w*.162,d*.48,.18+.11*i),.08).parent = group
        else:
            raise ValueError(f"No wasteland object model for {name}")

    def trainyard_workshop_ruin(self, group, name, x, y, width, depth):
        # The survey covers roofless workshops, with the surviving walls at
        # the back and an open, broken edge toward the north siding.
        self.concrete_box("Workshop slab", (x, y, .035),
                          (width*.49, depth*.48, .035)).parent = group
        self.concrete_box("Workshop rear wall", (x-width*.06, y+depth*.42, .38),
                          (width*.41, depth*.055, .38)).parent = group
        for side in (-1, 1):
            self.concrete_box("Workshop return wall",
                              (x+side*width*.44, y+depth*.14, .28),
                              (min(.18, width*.055), depth*.32, .28)).parent = group
        for offset in ((-.32, .04, .32) if name == "northwest_ruin" else (-.22, .23)):
            self.concrete_box("Broken workshop frontage",
                              (x+width*offset, y-depth*.43, .15),
                              (width*.10, depth*.05, .15)).parent = group
        place(self.library / "industrial_service267/model.glb", group,
              (x-width*.23, y+depth*.15, .07), (min(width*.26, 2.2), depth*.34, .58))

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
        for index in range(-7, 8):
            sleeper = box("Turntable sleeper", (index*length/16, 0, .052),
                          (length/48, gauge*.75, .030), self.dark, .008)
            sleeper.parent = bridge
        for side in (-1, 1):
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
        else:
            part("Covered wagon body", 0,0,.81, (length*.443,width*.416,.405), self.steel)
            part("Covered wagon roof", 0,0,1.245, (length*.461,width*.439,.066), self.dark)
            for side in (-1,1):
                part("Wagon sliding door", 0,side*width*.423,.803,
                     (length*.164,width*.025,.307), self.dark)
                for bay in (-.35,-.22,.22,.35):
                    part("Wagon cladding rib", bay*length,side*width*.434,.82,
                         (.024,.018,.357), self.steel)

    def convoy_vehicle(self, group, name, x, y, length, width, yaw):
        group.location = (x,y,0)
        group.rotation_euler.z = yaw + (0 if name == "convoy_e" else math.pi)

        def part(label, position, scale, material, bevel=.035):
            box(label, position, scale, material, bevel).parent = group

        part("Convoy chassis", (0,0,.44), (length*.48,width*.40,.13), self.dark)
        part("Convoy cab", (length*.345,0,.80), (length*.139,width*.40,.34), self.steel)
        part("Convoy windshield", (length*.481,0,.924), (.016,width*.33,.111), self.dark)
        part("Convoy cargo bed", (-length*.143,0,.60), (length*.325,width*.415,.055), self.steel)
        for side in (-1,1):
            for offset in (-.35,-.19,.35):
                bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=min(.30,width*.19),
                    depth=width*.14, location=(length*offset,side*width*.41,.30),
                    rotation=(math.pi/2,0,0))
                wheel = bpy.context.object
                wheel.name = "Convoy wheel"
                wheel.data.materials.append(self.dark)
                wheel.parent = group
        if name == "convoy_mw":
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=min(.43,width*.33),
                depth=length*.59, location=(-length*.13,0,1.04), rotation=(0,math.pi/2,0))
            tank = bpy.context.object
            tank.name = "Convoy tanker vessel"
            tank.data.materials.append(self.steel)
            tank.parent = group
            for offset in (-.31,.03):
                bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=6,
                    major_radius=min(.43,width*.33), minor_radius=.023,
                    location=(length*offset,0,1.04), rotation=(0,math.pi/2,0))
                band = bpy.context.object
                band.name = "Convoy tank band"
                band.data.materials.append(self.dark)
                band.parent = group
        elif name == "convoy_me":
            for row in (-1,1):
                for slot in (-1,0,1):
                    part("Convoy strapped crate", ((-.147+slot*.19)*length,row*width*.205,.83),
                         (length*.079,width*.155,.18),self.canvas)
        elif name.startswith("wreck_"):
            for side in (-1,1):
                part("Wreck flatbed side rail", (-length*.135,side*width*.365,.75),
                     (length*.291,.036,.081),self.steel,.012)
            for slot in range(7):
                part("Wreck flatbed crossmember", ((-.395+slot*.085)*length,0,.668),
                     (length*.021,width*.348,.028),self.dark,.009)
        else:
            part("Convoy tarpaulin load", (-length*.147,0,.94),
                 (length*.303,width*.386,.286),self.canvas,.112)
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
