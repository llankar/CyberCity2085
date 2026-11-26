"""Southwest framed housing, curved service pipes and extractors from one source view."""
from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase245';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase243/environment.blend'))
root=bpy.data.objects['Occludable_sw_building'];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
before_v=[tuple(v.co) for v in body.data.vertices];before_f=[tuple(p.vertices) for p in body.data.polygons]
points=[body.matrix_world@Vector(p) for p in body.bound_box];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
w=hi.x-lo.x;d=hi.y-lo.y;z=hi.z+.035;added=[];removed=[]
for assembly in [o for o in root.children_recursive if o.name.startswith(('Authored_old_military_compressor','Authored_modular_electric_cables'))]:
 for child in list(assembly.children_recursive):removed.append(child.name);bpy.data.objects.remove(child,do_unlink=True)
 removed.append(assembly.name);bpy.data.objects.remove(assembly,do_unlink=True)
for obj in list(root.children_recursive):
 if obj.name.startswith(('AuthoredRoofVent','Roof199','AuthoredRoofWalkway184','AuthoredFacade_','Facade206','District208','AuthoredGarageBay184','AuthoredGarageShutter184')):
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
paint=bpy.data.materials['Original229 dark roof panels'];trim=bpy.data.materials['Original229 weathered roof reinforcement'];black=bpy.data.materials['Service230 recessed joints']
concrete=bpy.data.materials['Plant243 worn concrete'];pipe_paint=bpy.data.materials['Service232 acquired worn plate PBR']
def at(u,v,h=0):return Vector((lo.x+u*w,hi.y-v*d,z+h))
def attach(obj):
 world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world;added.append(obj.name);return obj
def part(name,point,half,material):return attach(box('Southwest245 '+name,point,half,material,.012))
body.data=body.data.copy();slot=len(body.data.materials);body.data.materials.append(concrete);uv=body.data.uv_layers.active or body.data.uv_layers.new();normal_matrix=body.matrix_world.to_3x3().inverted().transposed()
for poly in body.data.polygons:
 normal=(normal_matrix@poly.normal).normalized()
 if abs(normal.z)>.2:continue
 poly.material_index=slot
 for loop in poly.loop_indices:
  co=body.matrix_world@body.data.vertices[body.data.loops[loop].vertex_index].co;uv.data[loop].uv=((co.y if abs(normal.x)>.5 else co.x)/2,co.z/2)
nx=max(2,round(w/.9));ny=max(2,round(d/.85))
for i in range(nx):
 for j in range(ny):part('roof plate',at((i+.5)/nx,(j+.5)/ny),(w/nx/2-.012,d/ny/2-.012,.018),paint)
for u in [.025,.975]:part('roof edge',at(u,.5,.055),(.04,d*.47,.04),trim)
for v in [.025,.975]:part('roof edge',at(.5,v,.055),(w*.47,.04,.04),trim)
# Blue-topped framed service unit. Do not assert a function absent from source data.
c=at(.30,.23);hw=w*.235;hd=d*.075
part('service housing',(c.x,c.y,z+.32),(hw,hd,.29),trim)
part('housing recessed top',(c.x,c.y,z+.62),(hw-.09,hd-.09,.018),black)
panel=make_material('Southwest245 genuine blue inset',(1,1,1,1),.3,.48);shader=panel.node_tree.nodes['Principled BSDF'];tex=panel.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(LAB/'environment-library/assets/sw_service_housing/blue_panel.png'));panel.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
obj=part('original blue inset',(c.x,c.y,z+.646),(hw-.16,hd-.14,.012),panel)
uv=obj.data.uv_layers.active or obj.data.uv_layers.new()
for poly in obj.data.polygons:
 for loop in poly.loop_indices:
  co=obj.data.vertices[obj.data.loops[loop].vertex_index].co;uv.data[loop].uv=(co.x/(2*(hw-.16))+.5,co.y/(2*(hd-.14))+.5)
for x in [c.x-hw+.055,c.x+hw-.055]:part('housing edge frame',(x,c.y,z+.68),(.035,hd,.045),trim)
for y in [c.y-hd+.055,c.y+hd-.055]:part('housing edge frame',(c.x,y,z+.68),(hw,.035,.045),trim)
part('housing crossbar',(c.x,c.y,z+.70),(hw,.025,.025),trim)
# Two differently shaped extractor stations follow the visible source composition.
ne=bpy.data.objects['Occludable_ne_building'];fans=[o for o in ne.children_recursive if o.name.startswith('Original236 reused extractor ') and abs(o.matrix_world.to_scale().x-1.85)<.001];assert len(fans)==10
for u,v,scale in [(.21,.80,1.85),(.76,.67,1.6)]:
 part('extractor station',at(u,v,.14),(.57,.55,.12),trim)
 for old in fans:
  copy=bpy.data.objects.new('Southwest245 reused '+old.data.name,old.data);bpy.context.collection.objects.link(copy);copy.matrix_world=Matrix.Translation(at(u,v,.27))@Matrix.Scale(scale,4);attach(copy)
part('left service lid',at(.43,.80,.18),(.55,.48,.15),paint)
for v in [.80,.91]:part('right service lid',at(.76,v,.17),(.55,.44,.14),paint)
# Continuous rounded service runs, real tube geometry, with explicit source-layout bends.
for index,path in enumerate([[(.27,.305),(.27,.42),(.36,.50),(.39,.59),(.57,.63),(.66,.67)],[(.20,.305),(.20,.43),(.24,.55),(.25,.65),(.31,.73),(.20,.77)]]):
 curve=bpy.data.curves.new('Southwest245 curved service route','CURVE');curve.dimensions='3D';curve.bevel_depth=.14;curve.bevel_resolution=4;curve.resolution_u=10
 spline=curve.splines.new('BEZIER');spline.bezier_points.add(len(path)-1)
 for point,(u,v) in zip(spline.bezier_points,path):point.co=at(u,v,.30);point.handle_left_type=point.handle_right_type='AUTO'
 curve.materials.append(pipe_paint);obj=bpy.data.objects.new('Southwest245 source curved pipe '+str(index),curve);bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Identity(4);attach(obj)
# Reuse a real acquired factory access door and grille mesh on the unseen service face.
source_door=next(o for o in bpy.data.objects['Occludable_nw_building'].children_recursive if o.name.startswith('Plant243 acquired service door'))
source_vent=next(o for o in bpy.data.objects['Occludable_nw_building'].children_recursive if o.name.startswith('Plant243 acquired wall ventilation'))
for old,point in [(source_door,Vector((hi.x+.11,lo.y+d*.28,1.23))),(source_vent,Vector((hi.x+.11,lo.y+d*.65,1.75)))]:
 copy=old.copy();copy.parent=None;bpy.context.collection.objects.link(copy);copy.name='Southwest245 acquired service facade';copy.matrix_world=Matrix.Translation(point)@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Diagonal(Vector((*old.matrix_world.to_scale(),1)));attach(copy)
for fraction in [.50,.83]:
 copy=source_vent.copy();copy.parent=None;bpy.context.collection.objects.link(copy);copy.name='Southwest245 additional wall grille';copy.matrix_world=Matrix.Translation(Vector((hi.x+.11,lo.y+d*fraction,1.75)))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Diagonal(Vector((*source_vent.matrix_world.to_scale(),1)));attach(copy)
for fraction in [.025,.43,.74,.975]:part('wall structural rib',(hi.x+.07,lo.y+d*fraction,1.48),(.065,.045,1.45),trim)
for x in [lo.x+.12,hi.x-.12]:part('front corner reinforcement',(x,lo.y-.07,1.48),(.045,.065,1.45),trim)
assert before_v==[tuple(v.co) for v in body.data.vertices] and before_f==[tuple(p.vertices) for p in body.data.polygons]
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'service.json').write_text(json.dumps({'source_object':'sw_building','source_context':'environment-library/references/city_exterior_neon_market_alley__sw_building.png','added':added,'removed':removed,'base_geometry_preserved':True,'limits':'Single genuine roof view; unknown blue-housing function; curved pipe depths and concrete service facade inferred','tactical_changes':False},indent=2))
print('SOUTHWEST245_EXPORTED',len(added))
