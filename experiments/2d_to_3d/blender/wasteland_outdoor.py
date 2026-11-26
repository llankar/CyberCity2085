"""Build the surveyed props shared by the original outdoor wasteland maps."""
import math

import bpy

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
        self.steel = make_material("Corroded steel", (.13,.073,.042,1), .62,.69)
        self.dark = make_material("Weathered undercarriage", (.046,.039,.032,1), .4,.82)
        self.canvas = make_material("Weathered sandbags", (.21,.17,.11,1), 0,.94)

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
                segment = box(name, ((ax+bx)/2,(ay+by)/2,height/2),
                              (math.hypot(bx-ax,by-ay)/2,width/2,height/2), self.stone, .055)
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
            vertices = [(x,y,0) for x,y in points] + [(x,y,height+.19*(i%4)) for i,(x,y) in enumerate(points)]
            faces = [tuple(reversed(range(n))), tuple(range(n,2*n))]
            faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(vertices, [], faces)
            mesh.materials.append(self.stone)
            fragment = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(fragment)
            fragment.parent = group
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
                  (length*.96,breadth*.96,1.6), yaw=yaw)
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
            box(name+" rubble base", (x,y,.16), (w*.47,d*.46,.16), self.stone).parent = group
            for side in (-1,1):
                for index in range(3):
                    height = .75+.22*((index+(side>0))%3)
                    box(name+" fractured facade", (x+(index-1)*w*.31,y+side*d*.41,height/2),
                        (w*.154,d*.075,height/2), self.stone, .065).parent = group
            box(name+" end wall", (x-w*.405,y,.51), (w*.058,d*.36,.51), self.stone, .065).parent = group
        elif any(part in name for part in ("ruin","rubble","wall","barrier")):
            for i in range(3):
                box(name,(x+w*(i-1)/3,y,.18+.11*i),
                    (w*.162,d*.48,.18+.11*i),self.stone,.08).parent = group
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
