"""Angular street lighting and a service facade, within the retained showcase."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase211';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase208/environment.blend'))
steel=bpy.data.materials['Kiosk207_WeatheredSteel'];rubber=bpy.data.materials['Kiosk207_CableRubber'];cyan=bpy.data.materials['Kiosk207_Cyan']
def attach(obj,root):
 bpy.context.view_layer.update();world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world;return obj
def box(name,point,size,mat,root):
 bpy.ops.mesh.primitive_cube_add(size=1,location=point);obj=bpy.context.object;obj.name=name;obj.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat)
 bevel=obj.modifiers.new('Manufactured edge','BEVEL');bevel.width=.025;bevel.segments=3
 return attach(obj,root)
def beam(name,start,end,width,depth,mat,root):
 middle=(Vector(start)+Vector(end))/2;direction=Vector(end)-Vector(start)
 obj=box(name,middle,(width,depth,direction.length),mat,root)
 obj.rotation_euler=direction.to_track_quat('Z','Y').to_euler();return obj
lamps=[]
for index,old in enumerate([o for o in list(bpy.data.objects) if o.type=='MESH' and o.name.startswith('street_lamp_01')]):
 points=[old.matrix_world@v.co for v in old.data.vertices];z=min(p.z for p in points)
 bottom=[p for p in points if p.z<z+.05];base=sum(bottom,Vector())/len(bottom);x,y=base.x,base.y
 root=bpy.data.objects.new('Street211_LightAssembly',None);bpy.context.collection.objects.link(root)
 box('Lamp211_ServiceBase',(x,y,z+.16),(.38,.36,.32),steel,root)
 beam('Lamp211_Column',(x,y,z+.22),(x+.16,y,z+2.72),.14,.18,steel,root)
 beam('Lamp211_Cantilever',(x+.16,y,z+2.72),(x+.87,y,z+3.04),.16,.2,steel,root)
 box('Lamp211_LightHousing',(x+.95,y,z+3.04),(1.0,.4,.14),steel,root)
 box('Lamp211_Emitter',(x+.95,y,z+2.955),(.82,.29,.025),cyan,root)
 box('Lamp211_Status',(x-.079,y-.095,z+1.25),(.035,.02,.55),cyan,root)
 box('Lamp211_AccessPanel',(x,y-.19,z+.3),(.23,.035,.24),rubber,root)
 lamps.append(list(base));bpy.data.objects.remove(old,do_unlink=True)
assert len(lamps)==2,lamps
# Replace one tall repeated glazed bay with an industrial service module.
root=bpy.data.objects['Occludable_east_building']
windows=[o for o in root.children_recursive if o.type=='MESH' and o.name.startswith('AuthoredFacade_window')]
assert windows
old=windows[0];points=[old.matrix_world@Vector(p) for p in old.bound_box];center=sum(points,Vector())/8
normal=old.matrix_world.to_3x3().inverted().transposed()@max(old.data.polygons,key=lambda p:p.area).normal;normal.z=0;normal.normalize()
body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'));bp=[body.matrix_world@Vector(p) for p in body.bound_box];bc=sum(bp,Vector())/8
if normal.dot(center-bc)<0:normal=-normal
rotation=(-normal).to_track_quat('Y','Z').to_matrix();right=rotation@Vector((1,0,0))
plate=box('Service211_ArmorPanel',center+normal*.17,(2.45,.12,2.65),steel,root)
plate.matrix_world=Matrix.Translation(center+normal*.17)@rotation.to_4x4()
# Use a retained professional vent mesh, keeping its detailed PBR material.
source=next(o for o in bpy.data.objects if o.name.startswith('Kiosk207_AuthoredServicePart') and o.type=='MESH')
vent=bpy.data.objects.new('Service211_AuthoredVent',source.data.copy());bpy.context.collection.objects.link(vent)
pts=[v.co for v in vent.data.vertices];lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)])
vent.data.transform(Matrix.Translation(-(lo+hi)/2));dims=hi-lo
vent.parent=root;vent.matrix_world=Matrix.Translation(center+normal*.30)@rotation.to_4x4()@Matrix.Scale(1.6/max(dims),4)
for dx in [-1.06,1.06]:
 light=box('Service211_EdgeLight',center+right*dx+normal*.26,(.045,.04,2.2),cyan,root)
 light.matrix_world=Matrix.Translation(center+right*dx+normal*.26)@rotation.to_4x4()
bpy.data.objects.remove(old,do_unlink=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'street.json').write_text(json.dumps({'lamp_bases':lamps,'service_facade':'east_building','scope':'two cosmetic lamp replacements and one facade bay; existing tactical map retained'},indent=2))
print('STREET211_READY',len(lamps),flush=True)
