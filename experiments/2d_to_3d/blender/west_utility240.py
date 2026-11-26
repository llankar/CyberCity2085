"""One western utility frontage, interpreted below the genuine dark tiled roof."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase240';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase239/environment.blend'))
root=bpy.data.objects['Occludable_west_building'];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
original_vertices=[tuple(v.co) for v in body.data.vertices];original_faces=[tuple(p.vertices) for p in body.data.polygons]
points=[body.matrix_world@Vector(p) for p in body.bound_box];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
w=hi.x-lo.x;d=hi.y-lo.y;removed=[];added=[]
for assembly in [o for o in root.children_recursive if o.name.startswith('Authored_old_military_compressor')]:
 for child in list(assembly.children_recursive):removed.append(child.name);bpy.data.objects.remove(child,do_unlink=True)
 removed.append(assembly.name);bpy.data.objects.remove(assembly,do_unlink=True)
for obj in list(root.children_recursive):
 if obj.name.startswith(('AuthoredFacade_','Facade206','District208','AuthoredRoofVent','Roof199','AuthoredGarageBay184','AuthoredGarageShutter184','AuthoredRoofWalkway184')):
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
# Preserve actual PBR wear while making this frontage darker than the depot.
wall=bpy.data.materials['Service232 acquired worn plate PBR'].copy();wall.name='Utility240 dark worn facade'
shader=wall.node_tree.nodes['Principled BSDF'];socket=shader.inputs['Base Color'];color_source=socket.links[0].from_socket
mix=wall.node_tree.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[7].default_value=(.45,.55,.65,1)
wall.node_tree.links.new(color_source,mix.inputs[6]);wall.node_tree.links.new(mix.outputs[2],socket)
body.data=body.data.copy();index=len(body.data.materials);body.data.materials.append(wall);uv=body.data.uv_layers.active or body.data.uv_layers.new();normal_matrix=body.matrix_world.to_3x3().inverted().transposed()
for poly in body.data.polygons:
 normal=(normal_matrix@poly.normal).normalized()
 if abs(normal.z)>.2:continue
 poly.material_index=index
 for loop in poly.loop_indices:
  co=body.matrix_world@body.data.vertices[body.data.loops[loop].vertex_index].co;uv.data[loop].uv=((co.y if abs(normal.x)>.5 else co.x)/2,co.z/2)
pack=LAB/'sources/environment169/modular_urban_apartments_facade/modular_urban_apartments_facade_1k.gltf'
before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(pack));imported=set(bpy.data.objects)-before
wanted=['window_centered_large_03','door_window_small_05'];templates={}
for name in wanted:
 source=next(o for o in imported if o.type=='MESH' and o.name==name);mesh=source.data.copy();mesh.transform(source.matrix_world)
 low=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);high=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)]);dims=high-low;mesh.transform(Matrix.Translation(-(low+high)/2))
 if dims.x<dims.y:mesh.transform(Matrix.Rotation(math.pi/2,4,'Z'));dims.x,dims.y=dims.y,dims.x
 templates[name]=(mesh,dims)
for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
def attach(obj):
 world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world;added.append(obj.name);return obj
def part(name,location,half,material):return attach(box('Utility240 '+name,location,half,material,.008))
def module(name,location,width,height,angle):
 mesh,dims=templates[name];obj=bpy.data.objects.new('Utility240 acquired '+name,mesh);bpy.context.collection.objects.link(obj)
 scale=(width/dims.x,min(1,.18/max(.001,dims.y)),height/dims.z)
 obj.matrix_world=Matrix.Translation(Vector(location))@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal((*scale,1));return attach(obj)
trim=bpy.data.materials['Original229 weathered roof reinforcement'];paint=bpy.data.materials['Original229 dark roof panels'];black=bpy.data.materials['Service230 recessed joints']
magenta=make_material('Utility240 original accent',(.58,.012,.16,1),.15,.5,2)
# Long east-facing frontage: two tall bays and a service entry, not another garage.
side=hi.x+.11
for fraction in [.24,.73]:module('window_centered_large_03',(side,lo.y+d*fraction,1.82),1.30,1.52,math.pi/2)
module('door_window_small_05',(side,lo.y+d*.48,1.18),1.05,2.15,math.pi/2)
for fraction in [.025,.38,.60,.975]:part('side structural rib',(side-.025,lo.y+d*fraction,1.48),(.065,.045,1.45),trim)
for z in [.20,2.86]:part('long wall rail',(side-.025,(lo.y+hi.y)/2,z),(.04,d*.47,.04),trim)
part('magenta housing',(side+.01,lo.y+d*.48,2.54),(.055,.68,.075),black)
part('magenta service light',(side+.07,lo.y+d*.48,2.54),(.014,.57,.018),magenta)
# Authentic roof is segmented and carries an edge conduit, without invented fans.
nx=max(2,round(w/.85));ny=max(2,round(d/.85));z=hi.z+.035
for i in range(nx):
 for j in range(ny):part('roof plate',(lo.x+(i+.5)*w/nx,lo.y+(j+.5)*d/ny,z),(w/nx/2-.012,d/ny/2-.012,.018),paint)
for x in [lo.x+.07,hi.x-.07]:part('roof perimeter',(x,(lo.y+hi.y)/2,z+.045),(.035,d*.48,.035),trim)
for y in [lo.y+.07,hi.y-.07]:part('roof perimeter',((lo.x+hi.x)/2,y,z+.045),(w*.46,.035,.035),trim)
# Reuse the established acquired pipe mesh, keeping transverse diameter fixed.
source=next(o for o in bpy.data.objects['Occludable_ne_building'].children_recursive if o.name.startswith('Original236 acquired pipe run'));mesh=source.data
low=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);high=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)]);dims=high-low;k=max(range(3),key=lambda i:dims[i]);axis=Vector(tuple(1 if i==k else 0 for i in range(3)));cross=max(dims[i] for i in range(3) if i!=k)
a=Vector((hi.x-.25,lo.y+d*.2,z+.15));b=Vector((hi.x-.25,lo.y+d*.77,z+.15));delta=b-a;scale=[.18/cross]*3;scale[k]=delta.length/dims[k]
obj=bpy.data.objects.new('Utility240 source edge conduit',mesh);bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Translation((a+b)/2)@axis.rotation_difference(delta.normalized()).to_matrix().to_4x4()@Matrix.Diagonal(Vector((*scale,1)));attach(obj)
assert original_vertices==[tuple(v.co) for v in body.data.vertices]
assert original_faces==[tuple(p.vertices) for p in body.data.polygons]
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'facade.json').write_text(json.dumps({'source_object':'west_building','source_context':'environment-library/references/city_exterior_neon_market_alley__west_building.png','removed':removed,'added':added,'acquired_modules':wanted,'base_geometry_preserved':True,'limits':'Original segmented roof/conduit and magenta palette; vertical window/door layout interpreted, not recovered original views','tactical_changes':False},indent=2))
print('UTILITY240_EXPORTED',len(added))
