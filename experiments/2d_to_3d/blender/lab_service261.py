"""Dark source-compatible scientific wall service skins; no tactical geometry changes."""
from pathlib import Path
import bpy,sys,math,json
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/lab261';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/lab248/environment.blend'));bpy.context.preferences.filepaths.save_version=0
steel=bpy.data.materials['Lab brushed steel'];dark=bpy.data.materials['Lab recessed service panels'];cyan=bpy.data.materials['Lab cyan instrumentation']
fastener=make_material('Scientific steel fasteners',(.16,.19,.21,1),.85,.4)
walls=[o for o in bpy.data.objects if o.type=='MESH' and o.dimensions.z>1 and any(m and m.name.startswith('Lab clinical ceramic') for m in o.data.materials)]
decor={};panels=0
bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.023,depth=.025)
bolt_mesh=bpy.context.object.data.copy();bpy.data.objects.remove(bpy.context.object,do_unlink=True)
bolt_mesh.materials.append(fastener)
def part(name,p,size,mat,angle,root):
 x,y,z=size
 vertices=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
 data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],[[0,3,2,1],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]]);data.materials.append(mat)
 uv=data.uv_layers.new(name='UVMap')
 for face in data.polygons:
  for index,loop in enumerate(face.loop_indices):uv.data[loop].uv=[(0,0),(1,0),(1,1),(0,1)][index]
 o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=p;o.rotation_euler.z=angle;o.parent=root
 bevel=o.modifiers.new('Service panel machined edges','BEVEL');bevel.width=.008;bevel.segments=2
 decor.setdefault(root,[]).append(o);return o
for wall in walls:
 for i,m in enumerate(wall.data.materials):
  if m and m.name.startswith('Lab clinical ceramic'):wall.data.materials[i]=steel
 coords=[v.co for v in wall.data.vertices]
 ext=Vector([max(v[i] for v in coords)-min(v[i] for v in coords) for i in range(3)])
 angle=wall.rotation_euler.z+(math.pi/2 if ext.y>ext.x else 0);length=max(ext.x,ext.y);thickness=min(ext.x,ext.y)
 tangent=Vector((math.cos(angle),math.sin(angle),0));normal=Vector((-math.sin(angle),math.cos(angle),0));root=wall.parent
 count=max(1,int(length/2.5));width=min(2.3,length/count-.12)
 for index in range(count):
  middle=Vector((wall.location.x,wall.location.y,0))+tangent*((index+.5)*length/count-length/2)
  for side in [-1,1]:
   p=middle+normal*side*(thickness/2+.025)
   part('Lab261 panel rim',tuple(p+Vector((0,0,1.0))),(width/2,.025,.72),steel,angle,root)
   front=p+normal*side*.033
   part('Lab261 recessed equipment panel',tuple(front+Vector((0,0,1.04))),(width*.46,.012,.64),dark,angle,root)
   for j in range(7):
    vent=front+normal*side*.018+Vector((0,0,.45+j*.055))
    part('Lab261 ventilation slat',tuple(vent),(width*.36,.015,.012),steel,angle,root)
   light=front+normal*side*.02+tangent*(width*.39)+Vector((0,0,1.34))
   part('Lab261 service indicator',tuple(light),(.018,.014,.16),cyan,angle,root)
   for x in [-1,1]:
    for z in [.39,1.62]:
     location=p+tangent*x*(width*.45)+normal*side*.05+Vector((0,0,z))
     o=bpy.data.objects.new('Lab261 panel bolt',bolt_mesh);bpy.context.collection.objects.link(o);o.location=location;o.rotation_euler=(math.pi/2,0,angle);o.parent=root;decor[root].append(o)
   panels+=1
# Merge each wall's new skin only; source parents/cutaway groups remain intact.
for root,objects in decor.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Lab261ServiceSkin_'+root.name
for i,p in enumerate([(-.5,11.5,2.4),(14,-4,2.4),(0,-2,2.4)]):
 bpy.ops.object.light_add(type='POINT',location=p);o=bpy.context.object;o.name='Lab261LocalLight'+str(i);o.data.energy=3.5;o.data.color=(.08,.65,1);o.data.use_custom_distance=True;o.data.cutoff_distance=4
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' or o.name.startswith(('Occludable_','Lab261LocalLight')))
bpy.context.view_layer.objects.active=walls[0];bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_lights=True)
(OUT/'detail.json').write_text(json.dumps({'source':'lab248','wall_segments':len(walls),'service_panels':panels,'local_lights':3,'tactical_mutation':False,'artistic_status':'NEEDS_NATIVE_REVIEW','remaining':'Doors, advanced scientific instruments, servers and medical equipment remain open'},indent=2))
print('LAB261_SERVICE_SKINS_EXPORTED',panels,'panels',len(walls),'source wall segments')
