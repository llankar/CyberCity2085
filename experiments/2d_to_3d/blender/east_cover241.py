"""Source-context blue covering and maintenance roof, no tactical body edits."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase241';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase240/environment.blend'))
root=bpy.data.objects['Occludable_east_building'];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
original_vertices=[tuple(v.co) for v in body.data.vertices];original_faces=[tuple(p.vertices) for p in body.data.polygons]
points=[body.matrix_world@Vector(p) for p in body.bound_box];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
w=hi.x-lo.x;d=hi.y-lo.y;z=hi.z+.035;added=[];removed=[]
for old in list(root.children_recursive):
 if old.name.startswith(('AuthoredRoofVent','Roof199','AuthoredRoofWalkway184','AuthoredFacade_wall','Facade206 urban wall','AuthoredGarageBay184')):
  removed.append(old.name);bpy.data.objects.remove(old,do_unlink=True)
paint=bpy.data.materials['Original229 dark roof panels'];trim=bpy.data.materials['Original229 weathered roof reinforcement']
def at(u,v,h=0):return Vector((lo.x+u*w,hi.y-v*d,z+h))
def attach(obj):
 world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world;added.append(obj.name);return obj
def part(name,point,half,material):return attach(box('East241 '+name,point,half,material,.008))
# Actual worn cladding, preserving original texture pixels via glTF color factors.
wall=bpy.data.materials['Service232 acquired worn plate PBR'].copy();wall.name='East241 blue technical cladding'
shader=wall.node_tree.nodes['Principled BSDF'];socket=shader.inputs['Base Color'];old_color=socket.links[0].from_socket
mix=wall.node_tree.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[7].default_value=(.4,.7,1,1)
wall.node_tree.links.new(old_color,mix.inputs[6]);wall.node_tree.links.new(mix.outputs[2],socket)
body.data=body.data.copy();index=len(body.data.materials);body.data.materials.append(wall);uv=body.data.uv_layers.active or body.data.uv_layers.new();normal_matrix=body.matrix_world.to_3x3().inverted().transposed()
for poly in body.data.polygons:
 normal=(normal_matrix@poly.normal).normalized()
 if abs(normal.z)>.2:continue
 poly.material_index=index
 for loop in poly.loop_indices:
  co=body.matrix_world@body.data.vertices[body.data.loops[loop].vertex_index].co;uv.data[loop].uv=((co.y if abs(normal.x)>.5 else co.x)/2,co.z/2)
nx=max(2,round(w/.9));ny=max(2,round(d/.85))
for i in range(nx):
 for j in range(ny):part('roof plate',at((i+.5)/nx,(j+.5)/ny),(w/nx/2-.012,d/ny/2-.012,.018),paint)
for u in [.025,.975]:part('edge reinforcement',at(u,.5,.05),(.04,d*.47,.04),trim)
for v in [.025,.975]:part('edge reinforcement',at(.5,v,.05),(w*.47,.04,.04),trim)
source_root=bpy.data.objects['Occludable_ne_building'];fans=[o for o in source_root.children_recursive if o.name.startswith('Original236 reused extractor ') and abs(o.matrix_world.to_scale().x-1.85)<.001]
assert len(fans)==10
part('service extractor base',at(.56,.41,.09),(.32,.31,.075),trim)
for old in fans:
 obj=bpy.data.objects.new('East241 reused '+old.data.name,old.data);bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Translation(at(.56,.41,.18))@Matrix.Scale(1.05,4);attach(obj)
# Tensioned three-dimensional cloth, raised above the retained solid roof.
material=bpy.data.materials.new('East241 genuine blue covering');material.use_nodes=True;shader=material.node_tree.nodes['Principled BSDF'];shader.inputs['Roughness'].default_value=.96
tex=material.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(LAB/'environment-library/assets/east_blue_cover/cloth.png'));material.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
u0,u1,v0,v1=.23,.86,.55,.83;center=at((u0+u1)/2,(v0+v1)/2);cw=(u1-u0)*w;cd=(v1-v0)*d;nx=32;ny=24;vertices=[];faces=[]
for i in range(nx+1):
 u=i/nx
 for j in range(ny+1):
  v=j/ny;h=.57-.22*math.sin(math.pi*u)*math.sin(math.pi*v)+.018*math.sin(u*math.pi*11)*math.sin(math.pi*v)
  vertices.append((center.x+(u-.5)*cw,center.y+(v-.5)*cd,z+h))
for i in range(nx):
 for j in range(ny):
  a=i*(ny+1)+j;faces.append((a,a+ny+1,a+ny+2,a+1))
mesh=bpy.data.meshes.new('East241 draped cloth');mesh.from_pydata(vertices,[],faces);mesh.materials.append(material);uv=mesh.uv_layers.new()
for poly in mesh.polygons:
 poly.use_smooth=True
 for loop in poly.loop_indices:
  idx=mesh.loops[loop].vertex_index;uv.data[loop].uv=(idx//(ny+1)/nx,idx%(ny+1)/ny)
obj=bpy.data.objects.new('East241 blue covering',mesh);bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Identity(4);attach(obj);solid=obj.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.012
for x in [center.x-cw/2,center.x+cw/2]:
 for y in [center.y-cd/2,center.y+cd/2]:part('cover tension post',(x,y,z+.29),(.025,.025,.29),trim)
for y in [center.y-cd/2,center.y+cd/2]:part('cover edge rail',(center.x,y,z+.56),(cw/2,.025,.025),trim)
assert len(faces)==768 and original_vertices==[tuple(v.co) for v in body.data.vertices] and original_faces==[tuple(p.vertices) for p in body.data.polygons]
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'roof.json').write_text(json.dumps({'source_object':'east_building','source_context':'environment-library/references/city_exterior_neon_market_alley__east_building.png','cloth_quads':768,'added':added,'removed':removed,'base_geometry_preserved':True,'limits':'Single context view; covered area translated onto retained solid roof, not a newly walkable courtyard; hidden vertical design interpreted','tactical_changes':False},indent=2))
print('EAST241_EXPORTED',len(added))
