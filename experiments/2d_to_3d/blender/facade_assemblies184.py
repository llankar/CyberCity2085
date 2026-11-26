"""Replace selected repetitive bays with authored garage assemblies and roof walkways."""
from pathlib import Path
import bpy,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase184';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase183/environment.blend'))
selected={
'modular_factory_facade':['wall_door_garage_double_01','door_garage_double_01'],
'modular_fire_escape':['modular_fire_escape_platform_railing','modular_fire_escape_platform_middle']}
templates={}
for pack,names in selected.items():
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(LAB/'sources/environment169'/pack/(pack+'_1k.gltf')))
 imported=set(bpy.data.objects)-before
 for name in names:
  obj=next(o for o in imported if o.type=='MESH' and o.name==name)
  mesh=obj.data.copy();mesh.transform(obj.matrix_world)
  low=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)])
  high=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)])
  center=(low+high)/2;mesh.transform(Matrix.Translation(-center));dims=high-low
  if pack=='modular_factory_facade' and dims.x<dims.y:
   mesh.transform(Matrix.Rotation(1.57079632679,4,'Z'));dims.x,dims.y=dims.y,dims.x
  templates[name]=(mesh,dims)
  print('BAY184_TEMPLATE',name,list(dims),flush=True)
 for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
roots=sorted([o for o in bpy.data.objects if o.name.startswith('Occludable_')],key=lambda o:o.name)
replaced=0;walkways=0
for index,root in enumerate(roots):
 bays=sorted([o for o in root.children if o.name.startswith('AuthoredFacade_wall_window')],key=lambda o:o.name)
 if index%2==0 and bays:
  bay=bays[len(bays)//2];old=bay.location.copy()
  # Remove only its nearby window insert; leave neighboring bays untouched.
  for obj in list(root.children):
   if obj.name.startswith('AuthoredFacade_window') and (obj.location-old).length<1.3:bpy.data.objects.remove(obj,do_unlink=True)
  mesh,dims=templates['wall_door_garage_double_01'];bay.data=mesh;bay.scale=(2.98/dims.x,min(1,.24/dims.y),2.98/dims.z)
  bay.name='AuthoredGarageBay184'
  mesh,dims=templates['door_garage_double_01'];insert=bpy.data.objects.new('AuthoredGarageShutter184',mesh);bpy.context.collection.objects.link(insert)
  insert.parent=root;insert.location=old;insert.rotation_euler=bay.rotation_euler
  insert.scale=(2.5/dims.x,min(1,.20/dims.y),2.5/dims.z);replaced+=1
 if index%3==1:
  body=next((o for o in root.children if o.name.startswith('PBR_Facade_')),None)
  if body:
   pts=[body.matrix_world@Vector(c) for c in body.bound_box];x=sum(p.x for p in pts)/8;y=sum(p.y for p in pts)/8;z=max(p.z for p in pts)
   if z>2:
    roof=[body.matrix_world@poly.center for poly in body.data.polygons if poly.normal.z>.5]
    occupied=[o.matrix_world.translation for o in root.children_recursive if o.type=='MESH' and not o.name.startswith(('PBR_Facade_','AuthoredFacade_')) and o.matrix_world.translation.z>2.8]
    candidates=[p for p in roof if all(any((q-Vector((p.x+dx,p.y+dy,p.z))).length<.1 for q in roof) for dx in [-1,0,1] for dy in [-1,0,1])]
    if not candidates:continue
    best=max(candidates,key=lambda p:min([(p-q).length for q in occupied] or [10]))
    if occupied and min((best-q).length for q in occupied)<2:continue
    x,y=best.x,best.y
    for name,dz in [('modular_fire_escape_platform_middle',.08),('modular_fire_escape_platform_railing',.55)]:
     mesh,dims=templates[name];obj=bpy.data.objects.new('AuthoredRoofWalkway184_'+name,mesh);bpy.context.collection.objects.link(obj);obj.parent=root
     factor=2.5/max(dims);obj.scale=(factor,)*3;obj.location=(x,y,z+dz);walkways+=1
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'assemblies.json').write_text(json.dumps({'garage_bays':replaced,'roof_walkway_parts':walkways,'scope':'authored local meshes, same map walls'},indent=2))
print('BAY184_READY',replaced,walkways,flush=True)
