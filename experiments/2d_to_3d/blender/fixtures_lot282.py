"""Prepare three acquired fixture parts, then assemble both maps before review."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from library_placement import place,reset_library_cache
LAB=Path('E:/CyberCity2085-3d-lab');LIB=LAB/'environment-library/assets/wall_fixtures282';LIB.mkdir(parents=True,exist_ok=True)
SOURCES=LAB/'sources/environment169'
parts=[('duct','modular_airduct_rectangular_01','modular_airduct_rectangular_01_single_01'),('vent','modular_airduct_rectangular_01','modular_airduct_rectangular_01_vent_01'),('cable','modular_electric_cables','cable_straight_long')]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
catalog=[];prototypes=[]
for identifier,kit,node_name in parts:
 source=next((SOURCES/kit).glob('*.gltf'));before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(source));imported=set(bpy.data.objects)-before
 original=next(o for o in imported if o.type=='MESH' and o.name==node_name);data=original.data.copy();data.transform(original.matrix_world)
 def bounds():
  lo=Vector([min(v.co[i] for v in data.vertices) for i in range(3)]);hi=Vector([max(v.co[i] for v in data.vertices) for i in range(3)]);return lo,hi
 lo,hi=bounds();extent=hi-lo
 if identifier=='vent':
  axis=min(range(3),key=lambda i:extent[i])
  if axis==2:data.transform(Matrix.Rotation(math.pi/2,4,'X'))
  if axis==0:data.transform(Matrix.Rotation(math.pi/2,4,'Z'))
 else:
  axis=max(range(3),key=lambda i:extent[i])
  if axis==1:data.transform(Matrix.Rotation(math.pi/2,4,'Z'))
  if axis==2:data.transform(Matrix.Rotation(math.pi/2,4,'Y'))
 lo,hi=bounds();data.transform(Matrix.Translation(Vector((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z))))
 for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
 obj=bpy.data.objects.new('Fixture282 '+identifier,data);bpy.context.collection.objects.link(obj);prototypes.append(obj)
 for other in bpy.context.scene.objects:other.select_set(other==obj)
 bpy.context.view_layer.objects.active=obj;bpy.ops.export_scene.gltf(filepath=str(LIB/(identifier+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
 catalog.append({'id':identifier,'model':str(LIB/(identifier+'.glb')),'source':str(source),'source_node':node_name,'dimensions_blender':list(hi-lo),'anchor':'center_ground_normalized','provenance':'Retained acquired real mesh; canonical orientation only, original proportions/materials retained'})
 obj.location.x=len(prototypes)*3
bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(LIB/'source.blend'))
(LIB/'parts.json').write_text(json.dumps(catalog,indent=2))
dimensions={r['id']:r['dimensions_blender'] for r in catalog}

for source,folder,map_name in [('lab261','lab282','city_interior_research_lab'),('metro270','metro282','city_transit_subway_platform')]:
 out=LAB/'generated/phase2'/folder;out.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2'/source/'environment.blend'));reset_library_cache();bpy.context.preferences.filepaths.save_version=0
 walls=[];instances=[]
 if folder=='lab282':
  for obj in list(bpy.data.objects):
   if obj.type!='MESH' or not obj.parent or not obj.parent.name.startswith('Occludable_') or obj.name.startswith('Lab261'):continue
   if obj.dimensions.z<1.8 or not any(m and m.name=='Lab brushed steel' for m in obj.data.materials):continue
   vertices=[v.co for v in obj.data.vertices];extent=Vector([max(v[i] for v in vertices)-min(v[i] for v in vertices) for i in range(3)])
   length=max(extent.x,extent.y);depth=min(extent.x,extent.y)
   if length<1.8:continue
   angle=obj.rotation_euler.z+(math.pi/2 if extent.y>extent.x else 0)
   walls.append((obj.parent,Vector((obj.location.x,obj.location.y,0)),length,depth,angle))
 else:
  wall_records=json.loads((LAB/'generated/phase2/metro270/walls.json').read_text())['walls']
  for record in wall_records:
   # Never put any fixture/beam across the east or west rail exits.
   if record['root'] not in ['Occludable_north_wall','Occludable_south_wall']:continue
   lo,hi=[Vector(v) for v in record['source_bounds']];size=hi-lo
   walls.append((bpy.data.objects[record['root']],Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,0)),size.x,size.y,0))
 for root,center,length,depth,angle in walls:
  normal=Vector((-math.sin(angle),math.cos(angle),0));side=-1 if normal.dot(center)>0 else 1
  face=center+normal*side*(depth/2+.045);yaw=angle+(math.pi if side<0 else 0)
  rows=[('vent',(.65,.18,.45),1.30),('duct',(.95,.32,.25),1.84 if folder=='lab282' else 1.56),('cable',(min(length*.65,1.8),.10,.08),.34)]
  if folder=='metro282':rows[0]=('vent',(.65,.18,.32),1.25);rows[1]=('duct',(.95,.32,.18),1.56)
  for identifier,envelope,height in rows:
   dims=dimensions[identifier];factor=min(envelope[i]/dims[i] for i in range(3));p=face.copy();p.z=height-dims[2]*factor/2
   place(LIB/(identifier+'.glb'),root,tuple(p),envelope,preserve_anchor=True,yaw=yaw)
   instances.append({'asset':identifier+'282','parent':root.name,'position_blender':list(p),'yaw':yaw})
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'environment.blend'))
 for obj in bpy.context.scene.objects:obj.select_set(obj.type=='MESH' or obj.type=='LIGHT' and obj.data.type=='POINT' or obj.name.startswith('Occludable_') or obj.name=='Track263VisualOnly')
 bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
 bpy.ops.export_scene.gltf(filepath=str(out/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_lights=True)
 (out/'fixtures.json').write_text(json.dumps({'source':source,'map':map_name,'instances':instances,'upgraded_wall_groups':sorted({r['parent'] for r in instances}),'tactical_mutation':False,'artistic_status':'NEEDS_ENSEMBLE_REVIEW'},indent=2))
 print('FIXTURES282_BATCH_ASSEMBLED',folder,len(instances),'placements in',len({r['parent'] for r in instances}),'existing wall groups',flush=True)
