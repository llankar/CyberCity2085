"""Northwest service plant: original roof layout and interpreted concrete utility walls."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase243';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase241/environment.blend'))
root=bpy.data.objects['Occludable_nw_building'];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
vertices_before=[tuple(v.co) for v in body.data.vertices];faces_before=[tuple(p.vertices) for p in body.data.polygons]
points=[body.matrix_world@Vector(p) for p in body.bound_box];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
w=hi.x-lo.x;d=hi.y-lo.y;z=hi.z+.035;added=[];removed=[]
for assembly in [o for o in root.children_recursive if o.name.startswith(('Authored_old_military_compressor','Authored_modular_electric_cables'))]:
 for child in list(assembly.children_recursive):removed.append(child.name);bpy.data.objects.remove(child,do_unlink=True)
 removed.append(assembly.name);bpy.data.objects.remove(assembly,do_unlink=True)
for obj in list(root.children_recursive):
 if obj.name.startswith(('AuthoredFacade_','Facade206','District208','AuthoredGarageBay184','AuthoredGarageShutter184','AuthoredRoofVent','AuthoredRoofWalkway184','Roof199')):
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
concrete=make_material('Plant243 worn concrete',(.2,.22,.24,1),.02,.9);shader=concrete.node_tree.nodes['Principled BSDF']
for filename,socket in [('diff.jpg','Base Color'),('rough.jpg','Roughness'),('nor_gl.jpg','Normal')]:
 tex=concrete.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(LAB/'sources/environment169/concrete_wall_001'/filename),check_existing=True)
 if socket!='Base Color':tex.image.colorspace_settings.name='Non-Color'
 if socket=='Normal':
  normal=concrete.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.38;concrete.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);concrete.node_tree.links.new(normal.outputs['Normal'],shader.inputs[socket])
 else:concrete.node_tree.links.new(tex.outputs['Color'],shader.inputs[socket])
# Keep real concrete detail but bring its white photographic albedo into night lighting.
base=shader.inputs['Base Color'];source_color=base.links[0].from_socket
tone=concrete.node_tree.nodes.new('ShaderNodeMix');tone.data_type='RGBA';tone.blend_type='MULTIPLY';tone.inputs[0].default_value=1;tone.inputs[7].default_value=(.32,.34,.38,1)
concrete.node_tree.links.new(source_color,tone.inputs[6]);concrete.node_tree.links.new(tone.outputs[2],base)
body.data=body.data.copy();slot=len(body.data.materials);body.data.materials.append(concrete);uv=body.data.uv_layers.active or body.data.uv_layers.new();normal_matrix=body.matrix_world.to_3x3().inverted().transposed()
for poly in body.data.polygons:
 normal=(normal_matrix@poly.normal).normalized()
 if abs(normal.z)>.2:continue
 poly.material_index=slot
 for loop in poly.loop_indices:
  co=body.matrix_world@body.data.vertices[body.data.loops[loop].vertex_index].co;uv.data[loop].uv=((co.y if abs(normal.x)>.5 else co.x)/2,co.z/2)
def template(pack,name):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(LAB/'sources/environment169'/pack/(pack+'_1k.gltf')));imported=set(bpy.data.objects)-before
 obj=next(o for o in imported if o.type=='MESH' and o.name==name);mesh=obj.data.copy();mesh.transform(obj.matrix_world)
 low=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);high=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)]);dims=high-low;mesh.transform(Matrix.Translation(-(low+high)/2))
 if dims.x<dims.y:mesh.transform(Matrix.Rotation(math.pi/2,4,'Z'));dims.x,dims.y=dims.y,dims.x
 for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
 return mesh,dims
vent,vd=template('modular_airduct_rectangular_01','modular_airduct_rectangular_01_vent_01')
door,dd=template('modular_factory_facade','door_recessed_large_01')
trim=bpy.data.materials['Original229 weathered roof reinforcement'];paint=bpy.data.materials['Original229 dark roof panels'];black=bpy.data.materials['Service230 recessed joints']
def at(u,v,h=0):return Vector((lo.x+u*w,hi.y-v*d,z+h))
def attach(obj):
 world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world;added.append(obj.name);return obj
def part(name,position,half,material):return attach(box('Plant243 '+name,position,half,material,.009))
def module(name,mesh,position,scale,rotation):
 obj=bpy.data.objects.new('Plant243 acquired '+name,mesh);bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Translation(Vector(position))@rotation@Matrix.Diagonal(Vector((*scale,1)));return attach(obj)
front=lo.y-.12
module('service door',door,(lo.x+w*.27,front,1.23),(1.28/dd.x,min(1,.2/dd.y),2.24/dd.z),Matrix.Identity(4))
for fraction in [.59,.82]:module('wall ventilation',vent,(lo.x+w*fraction,front,1.65),(1.05/vd.x,min(1,.18/vd.y),.75/vd.z),Matrix.Identity(4))
for fraction in [.20,.65]:module('side ventilation',vent,(hi.x+.10,lo.y+d*fraction,1.8),(1.20/vd.x,min(1,.18/vd.y),.8/vd.z),Matrix.Rotation(math.pi/2,4,'Z'))
for fraction in [.03,.44,.97]:part('front column',(lo.x+w*fraction,front+.04,1.48),(.06,.05,1.45),trim)
magenta=make_material('Plant243 source magenta strip',(.62,.015,.18,1),.1,.5,2.1)
part('light housing',(lo.x+w*.27,front-.03,2.55),(.81,.05,.07),black);part('source accent',(lo.x+w*.27,front-.09,2.55),(.72,.014,.018),magenta)
# Original shows a central plant row and a large isolated extractor on the right.
nx=max(2,round(w/.9));ny=max(2,round(d/.85))
for i in range(nx):
 for j in range(ny):part('roof plate',at((i+.5)/nx,(j+.5)/ny),(w/nx/2-.012,d/ny/2-.012,.018),paint)
for u in [.025,.975]:part('roof rim',at(u,.5,.055),(.04,d*.47,.04),trim)
for v in [.025,.975]:part('roof rim',at(.5,v,.055),(w*.47,.04,.04),trim)
for v in [.14,.35,.56,.77]:
 part('plant row base',at(.43,v,.13),(.66,.43,.11),trim)
 module('roof service grille',vent,at(.43,v,.29),(1.20/vd.x,min(1,.16/vd.y),.74/vd.z),Matrix.Rotation(-math.pi/2,4,'X'))
source_root=bpy.data.objects['Occludable_ne_building'];fans=[o for o in source_root.children_recursive if o.name.startswith('Original236 reused extractor ') and abs(o.matrix_world.to_scale().x-1.85)<.001];assert len(fans)==10
part('extractor base',at(.77,.56,.10),(.49,.47,.085),trim)
for old in fans:
 obj=bpy.data.objects.new('Plant243 reused '+old.data.name,old.data);bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Translation(at(.77,.56,.19))@Matrix.Scale(1.6,4);attach(obj)
pipe=next(o.data for o in source_root.children_recursive if o.name.startswith('Original236 acquired pipe run'))
low=Vector([min(v.co[i] for v in pipe.vertices) for i in range(3)]);high=Vector([max(v.co[i] for v in pipe.vertices) for i in range(3)]);dims=high-low;k=max(range(3),key=lambda i:dims[i]);axis=Vector(tuple(1 if i==k else 0 for i in range(3)));cross=max(dims[i] for i in range(3) if i!=k)
for a,b in [(at(.27,.08,.16),at(.27,.88,.16)),(at(.59,.08,.16),at(.59,.88,.16))]:
 delta=b-a;scale=[.18/cross]*3;scale[k]=delta.length/dims[k]
 module('source pipe run',pipe,(a+b)/2,scale,axis.rotation_difference(delta.normalized()).to_matrix().to_4x4())
assert vertices_before==[tuple(v.co) for v in body.data.vertices] and faces_before==[tuple(p.vertices) for p in body.data.polygons]
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'plant.json').write_text(json.dumps({'source_object':'nw_building','source_context':'environment-library/references/city_exterior_neon_market_alley__nw_building.png','added':added,'removed':removed,'base_geometry_preserved':True,'acquired':'PBR concrete, duct grilles and recessed factory door; existing extractor/pipe meshes','limits':'Genuine single roof context; row arrangement follows source, depths and concrete service facade interpreted','tactical_changes':False},indent=2))
print('NORTHWEST243_EXPORTED',len(added),list(vd))
