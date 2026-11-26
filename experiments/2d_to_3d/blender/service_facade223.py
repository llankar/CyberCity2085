"""Fit acquired service-access meshes to existing industrial facade bays."""
from pathlib import Path
import bpy,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab')
OUT=LAB/'generated/phase2/showcase223';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase219/environment.blend'))
def template(pack,name):
 before=set(bpy.data.objects)
 bpy.ops.import_scene.gltf(filepath=str(LAB/'sources/environment169'/pack/(pack+'_1k.gltf')))
 imported=set(bpy.data.objects)-before
 source=next(o for o in imported if o.type=='MESH' and (o.name==name or o.name.startswith(name+'.')))
 mesh=source.data.copy();mesh.transform(source.matrix_world)
 lo=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)])
 hi=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)])
 mesh.transform(Matrix.Translation(-(lo+hi)/2))
 for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
 print('SERVICE223_SOURCE',name,list(hi-lo))
 return mesh,hi-lo
deck=template('modular_fire_escape','modular_fire_escape_platform_middle')
rail=template('modular_fire_escape','modular_fire_escape_platform_railing')
ladder=template('modular_fire_escape','modular_fire_escape_ladder_bottom')
box=template('modular_electric_cables','cable_box_double')
vent=template('modular_airduct_rectangular_01','modular_airduct_rectangular_01_vent_01')
records=[]
for name in ['se_building','sw_building']:
 root=bpy.data.objects['Occludable_'+name]
 body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
 center_body=sum([body.matrix_world@Vector(p) for p in body.bound_box],Vector())/8
 windows=[o for o in root.children_recursive if o.type=='MESH' and o.name.startswith(('AuthoredFacade_window','Facade206 urban window'))]
 def surface(obj):
  center=sum([obj.matrix_world@Vector(p) for p in obj.bound_box],Vector())/8
  normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
  vertical=[p for p in obj.data.polygons if abs((normal_matrix@p.normal).normalized().z)<.5]
  normal=normal_matrix@max(vertical,key=lambda p:p.area).normal
  normal.z=0;normal.normalize()
  if normal.dot(center-center_body)<0:normal=-normal
  return center,normal
 window=max(windows,key=lambda o:surface(o)[1].dot(Vector((0,-1,0))))
 center,normal=surface(window);center.z=1.8
 rotation=(-normal).to_track_quat('Y','Z').to_matrix()
 def place(source,label,u,depth,z,length):
  mesh,dims=source;obj=bpy.data.objects.new('Service223 '+label,mesh)
  bpy.context.collection.objects.link(obj);obj.parent=root
  obj.matrix_world=Matrix.Translation(center+rotation@Vector((u,-depth,z)))@rotation.to_4x4()@Matrix.Scale(length/max(dims),4)
  return obj
 place(deck,'maintenance deck',0,.48,.15,2.6)
 place(rail,'safety rail',0,.48,.64,2.6)
 place(ladder,'access ladder',1.05,.7,-.35,2.2)
 place(box,'power distribution',-.82,.22,-.55,.45)
 place(vent,'industrial intake',0,.18,-.55,.95)
 records.append({'building':name,'bay':window.name,'center':list(center),'normal':list(normal)})
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'services.json').write_text(json.dumps(records,indent=2))

