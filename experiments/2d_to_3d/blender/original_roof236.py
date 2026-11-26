"""One source-layout industrial roof; reuse acquired duct and existing extractor meshes."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase236';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase235/environment.blend'))
root=bpy.data.objects['Occludable_ne_building'];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
pts=[body.matrix_world@Vector(p) for p in body.bound_box];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
w=hi.x-lo.x;d=hi.y-lo.y;z=hi.z+.035;removed=[];added=[]
for obj in list(root.children_recursive):
 if obj.name.startswith(('AuthoredRoofVent','Roof199')):
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
paint=bpy.data.materials['Original229 dark roof panels'];trim=bpy.data.materials['Original229 weathered roof reinforcement'];black=bpy.data.materials['Service230 recessed joints']
def at(u,v,height=0):return Vector((lo.x+u*w,hi.y-v*d,z+height))
def attach(obj):
 world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world;added.append(obj.name);return obj
def part(name,position,half,mat):return attach(box('Original236 '+name,position,half,mat,.009))
nx=max(2,round(w/.9));ny=max(2,round(d/.85))
for i in range(nx):
 for j in range(ny):part('dark roof plate',at((i+.5)/nx,(j+.5)/ny),(w/nx/2-.012,d/ny/2-.012,.018),paint)
for u in [.025,.975]:part('long roof perimeter',at(u,.5,.055),(.045,d*.47,.045),trim)
for v in [.025,.975]:part('short roof perimeter',at(.5,v,.055),(w*.47,.045,.045),trim)
# Genuine source has a large stepped service hatch in the upper right.
part('hatch plinth',at(.68,.21,.17),(w*.135,d*.17,.14),trim)
part('hatch dark gasket',at(.68,.21,.32),(w*.124,d*.157,.025),black)
part('hatch raised lid',at(.68,.21,.38),(w*.111,d*.14,.045),paint)
for u in [.59,.77]:part('hatch stiffener',at(u,.21,.445),(.03,d*.135,.025),trim)
# Reuse the actual swept extractor blades/rings from the retained library master.
with bpy.data.libraries.load(str(LAB/'environment-library/assets/roof_twin_fan/source.blend'),link=False) as (source,target):
 target.objects=[n for n in source.objects if n.startswith(('Recess beneath fan','Rolled fan surround','Fan motor','Extractor blade'))]
for loaded in target.objects:
 if loaded is not None:bpy.context.collection.objects.link(loaded)
bpy.context.view_layer.update()
fan_parts=[]
for obj in target.objects:
 if obj is None:continue
 points=[obj.matrix_world@Vector(p) for p in obj.bound_box]
 if sum(p.x for p in points)/len(points)<-.05:
  mesh=obj.data.copy();mesh.transform(Matrix.Translation(Vector((.31,0,-.30)))@obj.matrix_world);fan_parts.append(mesh)
 # Loaded library objects are not linked into this scene.
 bpy.data.objects.remove(obj,do_unlink=True)
assert len(fan_parts)==10, len(fan_parts)
for u,v,scale in [(.28,.37,1.85),(.20,.66,1.35)]:
 center=at(u,v,.18)
 part('extractor base',at(u,v,.095),(.30*scale,.29*scale,.08),trim)
 for mesh in fan_parts:
  obj=bpy.data.objects.new('Original236 reused extractor '+mesh.name,mesh);bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Translation(center)@Matrix.Scale(scale,4);attach(obj)
def template(pack,name):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(LAB/'sources/environment169'/pack/(pack+'_1k.gltf')))
 imported=set(bpy.data.objects)-before;source=next(o for o in imported if o.type=='MESH' and o.name==name)
 mesh=source.data.copy();mesh.transform(source.matrix_world)
 low=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);high=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)]);dims=high-low;mesh.transform(Matrix.Translation(-(low+high)/2))
 for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
 return mesh,dims
pipe,dims=template('modular_industrial_pipes_01','modular_industrial_pipes_01_pipe01')
axis=Vector((1,0,0)) if dims.x==max(dims) else Vector((0,1,0)) if dims.y==max(dims) else Vector((0,0,1))
def run(a,b):
 a=Vector(a);b=Vector(b);delta=b-a;obj=bpy.data.objects.new('Original236 acquired pipe run',pipe);bpy.context.collection.objects.link(obj)
 # Length must not inflate pipe diameter into a roof-sized sewer main.
 longitudinal=max(range(3),key=lambda i:dims[i]);cross=max(dims[i] for i in range(3) if i!=longitudinal)
 scaling=[.22/cross]*3;scaling[longitudinal]=delta.length/dims[longitudinal]
 obj.matrix_world=Matrix.Translation((a+b)/2)@axis.rotation_difference(delta.normalized()).to_matrix().to_4x4()@Matrix.Diagonal(Vector((*scaling,1)));attach(obj)
# Source-visible perimeter/service routing; hidden exact connections are interpreted.
for a,b in [(at(.13,.84,.15),at(.88,.84,.15)),(at(.88,.84,.15),at(.88,.35,.15)),(at(.40,.04,.16),at(.40,.52,.16))]:run(a,b)
assert len(added)>40
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'roof.json').write_text(json.dumps({'building':root.name,'source_context':'environment-library/references/city_exterior_neon_market_alley__ne_building.png','added':added,'removed':removed,'reused_fan_meshes':len(fan_parts),'source_layout':'Two unequal extractors, upper-right raised hatch, lower/right pipe routing','limits':'Single source view; vertical depths, service connections and materials interpreted','tactical_changes':False},indent=2))
print('INDUSTRIAL_ROOF236_EXPORTED',len(added))
