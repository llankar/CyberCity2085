"""Camera-facing clinic service facade, using retained authored industrial meshes."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase214';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase211/environment.blend'))
root=bpy.data.objects['Occludable_south_building_e']
body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
bc=sum([body.matrix_world@Vector(p) for p in body.bound_box],Vector())/8
def surface(obj):
 points=[obj.matrix_world@Vector(p) for p in obj.bound_box];center=sum(points,Vector())/8
 normal=obj.matrix_world.to_3x3().inverted().transposed()@max(obj.data.polygons,key=lambda p:p.area).normal
 normal.z=0;normal.normalize()
 if normal.dot(center-bc)<0:normal=-normal
 return center,normal
windows=[o for o in root.children_recursive if o.type=='MESH' and o.name.startswith('AuthoredFacade_window')]
assert windows
view=Vector((0,-1,0))
old=max(windows,key=lambda o:round(surface(o)[1].dot(view),3)*100-abs(surface(o)[0].x)*.05)
center,normal=surface(old);center.z=1.5;rotation=(-normal).to_track_quat('Y','Z').to_matrix()
steel=bpy.data.materials['Kiosk207_WeatheredSteel'];dark=bpy.data.materials['Kiosk207_CableRubber'];cyan=bpy.data.materials['Kiosk207_Cyan'];amber=bpy.data.materials['Kiosk207_Amber']
def place(obj,u,depth,z):
 bpy.context.collection.objects.link(obj);obj.parent=root
 obj.matrix_world=Matrix.Translation(center+rotation@Vector((u,-depth,z)))@rotation.to_4x4()
 return obj
def box(name,u,depth,z,size,mat):
 bpy.ops.mesh.primitive_cube_add(size=1);obj=bpy.context.object;obj.name=name;obj.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat)
 bevel=obj.modifiers.new('Manufactured edges','BEVEL');bevel.width=.025;bevel.segments=3
 obj.parent=root;obj.matrix_world=Matrix.Translation(center+rotation@Vector((u,-depth,z)))@rotation.to_4x4()
 return obj
def template(pack,name):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(LAB/'sources/environment169'/pack/(pack+'_1k.gltf')))
 imported=set(bpy.data.objects)-before;source=next(o for o in imported if o.type=='MESH' and o.name==name)
 mesh=source.data.copy();mesh.transform(source.matrix_world)
 lo=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);hi=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)])
 mesh.transform(Matrix.Translation(-(lo+hi)/2))
 for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
 return mesh,hi-lo
vent,dims=template('modular_airduct_rectangular_01','modular_airduct_rectangular_01_vent_01')
box('Clinic214 service backing',0,.19,0,(2.5,.12,2.75),steel)
for u in [-1.1,1.1]:box('Clinic214 armored pilaster',u,.30,0,(.17,.20,2.6),dark)
mesh=vent.copy();mesh.transform(Matrix.Scale(1.12/max(dims),4));place(bpy.data.objects.new('Clinic214 authored air intake',mesh),-.58,.33,.25)
# A medical scanner display reuses the existing game illustration and texture.
mesh=bpy.data.meshes.new('Clinic214 scanner display');mesh.from_pydata([(.2,0,-.5),(.98,0,-.5),(.98,0,1.05),(.2,0,1.05)],[],[(0,1,2,3)])
uv=mesh.uv_layers.new()
for i,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
mesh.materials.append(bpy.data.materials['District208 clinic advertising'])
place(bpy.data.objects.new('Clinic214 medical scanner',mesh),0,.35,0)
box('Clinic214 scanner top',.59,.32,1.08,(.87,.1,.055),cyan)
box('Clinic214 scanner bottom',.59,.32,-.54,(.87,.1,.055),cyan)
for u in [-.91,-.73]:
 curve=bpy.data.curves.new('Clinic214 conduit','CURVE');curve.dimensions='3D';curve.bevel_depth=.035;curve.bevel_resolution=4
 spline=curve.splines.new('BEZIER');spline.bezier_points.add(3)
 for p,co in zip(spline.bezier_points,[(u,-.32,-1.2),(u,-.37,-.5),(u,-.37,.6),(u+.1,-.32,1.1)]):p.co=co;p.handle_left_type=p.handle_right_type='AUTO'
 curve.materials.append(steel);place(bpy.data.objects.new('Clinic214 external coolant',curve),0,0,0)
box('Clinic214 dispenser drawer',-.12,.37,-.96,(1.5,.32,.38),dark)
for u in [-.5,-.15,.2]:box('Clinic214 dispenser indicator',u,.55,-.95,(.13,.025,.05),cyan)
curve=bpy.data.curves.new('Clinic214 clinic signage','FONT');curve.body='TRAUMA // 24H';curve.align_x='CENTER';curve.size=.21;curve.extrude=.002
curve.materials.append(amber);obj=place(bpy.data.objects.new('Kiosk207_Sign_Hero214',curve),0,.36,1.23)
obj.matrix_world=obj.matrix_world@Matrix.Rotation(math.pi/2,4,'X')
selected=old.name;bpy.data.objects.remove(old,do_unlink=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'clinic.json').write_text(json.dumps({'building':root.name,'replaced_window':selected,'center':list(center),'outward':list(normal),'vent_source_dimensions':list(dims),'scope':'one camera-facing cosmetic service facade; existing tactical volumes and paths retained'},indent=2))
print('CLINIC214_READY',selected,list(center),list(normal),flush=True)
