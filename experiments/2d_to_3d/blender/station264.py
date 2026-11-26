"""Source-guided station column service housings, retained rails and original layout."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/metro264';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/metro263/environment.blend'));bpy.context.preferences.filepaths.save_version=0
steel=bpy.data.materials['Subway worn dark steel'];chrome=bpy.data.materials['Brushed stair nosing'];black=bpy.data.materials['Rubber and recessed joints'];cyan=bpy.data.materials['Platform service lighting']
bronze=make_material('Station weathered brass service trim',(.18,.115,.05,1),.75,.6)
cache={};groups={}
def part(name,p,s,mat,root):
 key=(tuple(s),mat.name)
 if key not in cache:
  x,y,z=s;data=bpy.data.meshes.new(name)
  data.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
  data.materials.append(mat);uv=data.uv_layers.new(name='UVMap')
  for face in data.polygons:
   for i,loop in enumerate(face.loop_indices):uv.data[loop].uv=[(0,0),(1,0),(1,1),(0,1)][i]
  cache[key]=data
 o=bpy.data.objects.new(name,cache[key]);bpy.context.collection.objects.link(o);o.location=p;o.parent=root
 bevel=o.modifiers.new('Machined edge','BEVEL');bevel.width=.012;bevel.segments=2
 groups.setdefault(root,[]).append(o);return o
roots=[o for o in bpy.data.objects if o.name.startswith('Occludable_column')]
for root in roots:
 core=next(o for o in root.children if 'structural core' in o.name)
 x,y,z=core.location;wx,dy,h=core.dimensions
 # The core dimensions are already the surveyed footprint. Faces and conduits
 # remain within the original footing; no new blockers are generated.
 for side in [-1,1]:
  fy=y+side*(dy/2+.025)
  part('Station264 maintenance recess',(x,fy,1.1),(wx*.36,.018,.62),black,root)
  for k in range(9):part('Station264 louver',(x,fy+side*.025,.65+k*.065),(wx*.30,.035,.012),steel,root)
  part('Station264 inspection door',(x,fy+side*.02,1.48),(wx*.31,.028,.15),steel,root)
  part('Station264 access latch',(x+wx*.22,fy+side*.055,1.48),(.025,.018,.055),chrome,root)
  part('Station264 service strip',(x-wx*.26,fy+side*.06,1.49),(.012,.012,.10),cyan,root)
 for sx in [-1,1]:
  px=x+sx*(wx/2+.025)
  for yy in [-1,1]:part('Station264 corner guard',(px,y+yy*dy*.42,1.3),(.045,.045,1.15),bronze,root)
 for height in [.27,2.28]:part('Station264 collar',(x,y,height),(wx*.56,dy*.56,.065),steel,root)
 # Side conduits: real round pipe section and socket bands, shared geometry.
 for sx in [-1,1]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.04,depth=1.75,location=(x+sx*(wx/2+.085),y,1.22))
  pipe=bpy.context.object;pipe.name='Station264 service conduit';pipe.data.materials.append(chrome);pipe.parent=root;groups[root].append(pipe)
  for height in [.40,1.20,2.03]:part('Station264 conduit clamp',(pipe.location.x,y,height),(.06,.065,.025),steel,root)
# Bake/join per source root, retaining source cutaway grouping. Existing display,
# bench and stair meshes are not deleted or modified.
for root,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:
  o.select_set(True);bpy.context.view_layer.objects.active=o
  if o.modifiers and o.data.users>1:o.data=o.data.copy()
  for modifier in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name='Station264Service_'+root.name
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_') or o.name=='Track263VisualOnly')
bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
root=roots[0];children=list(root.children_recursive)
points=[o.matrix_world@Vector(c) for o in children if o.type=='MESH' for c in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
root.location=(-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z)
for o in bpy.context.scene.objects:o.select_set(o==root or o in children)
bpy.ops.export_scene.gltf(filepath=str(OUT/'service_column.glb'),export_format='GLB',use_selection=True,export_apply=True)
root.location=(0,0,0)
(OUT/'service_column.json').write_text(json.dumps({'id':'station_service_column264','dimensions':[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],'anchor':'center_ground_normalized','source_root':root.name,'models':{'blend':str(OUT/'environment.blend'),'glb':str(OUT/'service_column.glb')},'source_map':'city_transit_subway_platform','provenance':'Original source placement; inferred side service construction; retained source display and metal PBR'},indent=2))
(OUT/'detail.json').write_text(json.dumps({'column_groups':len(roots),'source':'metro263','geometry':'Maintenance panels, louvers, collars, corner guards and round conduits','status':'NEEDS_NATIVE_REVIEW','tactical_change':False},indent=2))
print('STATION264_SERVICE_EXPORTED',len(roots),'source column groups')
