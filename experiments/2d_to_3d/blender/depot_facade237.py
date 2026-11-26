"""Adapt acquired industrial doors to one interpreted facade, retaining source roof."""
from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase237';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase236/environment.blend'))
root=bpy.data.objects['Occludable_ne_building'];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
pts=[body.matrix_world@Vector(p) for p in body.bound_box];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
removed=[]
for obj in list(root.children_recursive):
 if obj.name.startswith(('AuthoredFacade_','Facade206','District208')):
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
# Reuse an acquired worn metallic PBR material; body vertices/collision never change.
cladding=bpy.data.materials['Service232 acquired worn plate PBR'].copy();cladding.name='Depot237 worn industrial cladding'
body.data=body.data.copy();slot=len(body.data.materials);body.data.materials.append(cladding)
uv=body.data.uv_layers.active or body.data.uv_layers.new();normal_matrix=body.matrix_world.to_3x3().inverted().transposed();faces=0
for poly in body.data.polygons:
 normal=(normal_matrix@poly.normal).normalized()
 if abs(normal.z)>.2:continue
 poly.material_index=slot;faces+=1
 for loop in poly.loop_indices:
  co=body.matrix_world@body.data.vertices[body.data.loops[loop].vertex_index].co
  uv.data[loop].uv=((co.y if abs(normal.x)>.5 else co.x)/2,co.z/2)
pack=LAB/'sources/environment169/modular_factory_facade/modular_factory_facade_1k.gltf'
before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(pack));imported=set(bpy.data.objects)-before
wanted=['door_garage_double_01','door_centered_small_01','window_centered_medium_01'];templates={}
for name in wanted:
 source=next(o for o in imported if o.type=='MESH' and o.name==name)
 mesh=source.data.copy();mesh.transform(source.matrix_world)
 low=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);high=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)]);dims=high-low
 mesh.transform(Matrix.Translation(-(low+high)/2))
 if dims.x<dims.y:mesh.transform(Matrix.Rotation(math.pi/2,4,'Z'));dims.x,dims.y=dims.y,dims.x
 templates[name]=(mesh,dims);print('DEPOT237_MODULE',name,list(dims))
for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
added=[]
def attach(obj):
 world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world;added.append(obj.name);return obj
def part(name,point,half,material):return attach(box('Depot237 '+name,point,half,material,.009))
def module(name,point,width,height,angle=0):
 mesh,dims=templates[name];obj=bpy.data.objects.new('Depot237 acquired '+name,mesh);bpy.context.collection.objects.link(obj)
 scale=Vector((width/dims.x,min(1,.20/max(dims.y,.001)),height/dims.z))
 obj.matrix_world=Matrix.Translation(Vector(point))@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal((*scale,1));return attach(obj)
trim=bpy.data.materials['Original229 weathered roof reinforcement'];black=bpy.data.materials['Service230 recessed joints']
magenta=make_material('Depot237 source magenta light',(.65,.018,.18,1),.15,.5,2.2)
width=hi.x-lo.x;depth=hi.y-lo.y
front=lo.y-.10
# Closed maintenance door is cosmetic: the tactical wall remains solid.
module('door_garage_double_01',(lo.x+width*.40,front,1.30),3.35,2.42)
module('door_centered_small_01',(hi.x-.95,front,1.20),.94,2.20)
for x in [lo.x+.12,lo.x+width*.72,hi.x-.12]:part('structural upright',(x,front+.035,1.48),(.065,.075,1.45),trim)
part('light recessed housing',(lo.x+width*.40,front-.035,2.69),(1.37,.055,.085),black)
part('magenta service strip',(lo.x+width*.40,front-.095,2.69),(1.27,.014,.023),magenta)
# Side gets two narrow high industrial windows instead of repeated brick bays.
for y in [lo.y+depth*.31,lo.y+depth*.68]:module('window_centered_medium_01',(hi.x+.11,y,2.03),1.25,.72,math.pi/2)
for y in [lo.y+.12,hi.y-.12]:part('side corner upright',(hi.x+.065,y,1.48),(.075,.065,1.45),trim)
for height in [.20,2.89]:
 part('front panel rail',((lo.x+hi.x)/2,front+.04,height),(width/2-.12,.04,.04),trim)
 part('side panel rail',(hi.x+.06,(lo.y+hi.y)/2,height),(.04,depth/2-.12,.04),trim)
assert faces>0 and len(templates)==3
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'facade.json').write_text(json.dumps({'building':root.name,'removed':removed,'added':added,'source_pack':str(pack),'reused_modules':wanted,'clad_body_faces':faces,'source_identity':'Roof layout retained, source magenta accent retained; vertical factory facade interpreted, not recovered original view','tactical_changes':False},indent=2))
print('DEPOT237_EXPORTED',len(added))
