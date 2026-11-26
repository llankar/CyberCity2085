"""Build the surveyed props shared by the original outdoor wasteland maps."""
import math

import bpy
import numpy as np

from create_hardsurface_crate import box, make_material
from library_placement import place
from loading_crane import build_crane
from shipping_container import build_container


class WastelandOutdoors:
    def __init__(self, library, grid, canvas, *, city=False):
        self.library = library
        self.gw, self.gh = grid
        self.cw, self.ch = canvas
        self.city = city
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
        pixels.reshape(-1, 4)[:, :3] *= (.62, .58, .54)
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
                segment = self.concrete_box(name, ((ax+bx)/2,(ay+by)/2,height/2),
                              (math.hypot(bx-ax,by-ay)/2,width/2,height/2), .055)
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
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(vertices, [], faces)
            self.project_concrete_uv(mesh)
            for material in (self.stone, self.aggregate, self.seam):
                mesh.materials.append(material)
            mesh.polygons[1].material_index = 1
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
        if self.city and name.startswith(("bus_", "truck_")):
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
