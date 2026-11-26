"""Place selected authored facade modules; preserve the underlying map volumes."""
import math
import bpy
from mathutils import Vector,Matrix

class FacadeModules:
    def __init__(self,source,detailed=False):
        self.detailed=detailed
        self.templates={};self.centres={};self.placements=0
        wanted={
            'modular_factory_facade':['wall_window_centered_medium_01','window_centered_medium_01','wall_door_centered_large_01','door_centered_large_01','cornice02_standard_standard_01'],
            'modular_urban_apartments_facade':['wall_door_centered_large_01','door_centered_large_01','cornice_standard_standard_01'],
            'modular_airduct_rectangular_01':['modular_airduct_rectangular_01_single_01','modular_airduct_rectangular_01_vent_01'],
        }
        if detailed:
            wanted['modular_urban_apartments_facade'] += [prefix+name for name in ['window_centered_double_01','window_centered_large_03','window_offset_small_01'] for prefix in ['', 'wall_']]
        for pack,names in wanted.items():
            before=set(bpy.data.objects)
            bpy.ops.import_scene.gltf(filepath=str(source/pack/(pack+'_1k.gltf')))
            imported=set(bpy.data.objects)-before
            for name in names:
                original=next(o for o in imported if o.type=='MESH' and o.name==name)
                mesh=original.data.copy();mesh.transform(original.matrix_world)
                points=[v.co for v in mesh.vertices]
                low=Vector([min(p[i] for p in points) for i in range(3)])
                high=Vector([max(p[i] for p in points) for i in range(3)])
                self.centres[(pack,name)]=(low+high)/2
                mesh.transform(Matrix.Translation(-(low+high)/2))
                dimensions=high-low
                # Imported modules are Z-up; make their thin axis localY.
                if dimensions.x<dimensions.y:
                    mesh.transform(Matrix.Rotation(math.pi/2,4,'Z'))
                    dimensions.x,dimensions.y=dimensions.y,dimensions.x
                self.templates[(pack,name)]=(mesh,dimensions.copy())
                print('FACADE_COMPONENT',pack,name,list(dimensions),flush=True)
            for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)

    def place(self,key,center,normal,width,height,parent):
        mesh,dims=self.templates[key]
        obj=bpy.data.objects.new('AuthoredFacade_'+key[1],mesh)
        bpy.context.collection.objects.link(obj);obj.parent=parent
        obj.scale=(width/max(.001,dims.x),min(1,.24/max(.001,dims.y)),height/max(.001,dims.z))
        obj.rotation_euler=(-normal).to_track_quat('Y','Z').to_euler()
        obj.location=center+normal*.07
        self.placements+=1

    def decorate(self,parent,parts,index,world):
        groups={}
        for kind,cell,points in parts:
            if kind!='wall':continue
            vertices=[world(p) for p in points]
            normal=-(vertices[1]-vertices[0]).cross(vertices[2]-vertices[0]).normalized()
            center=sum(vertices,Vector())/4
            key=(round(normal.x),round(normal.y),round(center.dot(normal),3))
            groups.setdefault(key,[]).append((center,normal))
        for key,values in groups.items():
            axis=0 if abs(key[1]) else 1
            values.sort(key=lambda row:row[0][axis])
            for start in range(0,len(values)-2,3):
                chunk=values[start:start+3]
                if abs(chunk[-1][0][axis]-chunk[0][0][axis]-2)>.01:continue
                center=sum((row[0] for row in chunk),Vector())/3;normal=chunk[0][1]
                window=('modular_factory_facade','wall_window_centered_medium_01')
                door=('modular_urban_apartments_facade','wall_door_centered_large_01')
                panel=door if (index+start)%5==0 else window
                if self.detailed and index%2==0 and panel!=door:
                    style=['window_centered_double_01','window_centered_large_03','window_offset_small_01'][(index+start//3)%3]
                    panel=('modular_urban_apartments_facade','wall_'+style)
                self.place(panel,center,normal,2.98,2.98,parent)
                insert=(panel[0],panel[1].removeprefix('wall_'))
                scale=2.98/self.templates[panel][1].x
                offset=self.centres[insert]-self.centres[panel]
                offset=(-normal).to_track_quat('Y','Z')@(offset*scale)
                dims=self.templates[insert][1]
                self.place(insert,center+offset,normal,dims.x*scale,dims.z*scale,parent)
                cornice=('modular_factory_facade','cornice02_standard_standard_01') if index%2 else ('modular_urban_apartments_facade','cornice_standard_standard_01')
                self.place(cornice,Vector((center.x,center.y,3)),normal,2.99,.22,parent)

    def roof(self,point,parent,index):
        key=('modular_airduct_rectangular_01','modular_airduct_rectangular_01_vent_01' if index%2 else 'modular_airduct_rectangular_01_single_01')
        mesh,dims=self.templates[key]
        obj=bpy.data.objects.new('AuthoredRoofVent',mesh);bpy.context.collection.objects.link(obj);obj.parent=parent
        scale=1.5/max(dims);obj.scale=(scale,)*3
        obj.location=point+Vector((-.5,0,dims.z*scale/2))
