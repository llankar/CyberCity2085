"""Interpret unseen walls beneath the original dark machine-roof as a service building."""
from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase230';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase229/environment.blend'))
root=bpy.data.objects['Occludable_south_building_w']
body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
points=[body.matrix_world@Vector(p) for p in body.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
removed=[]
for old in list(root.children_recursive):
 if old.name.startswith(('AuthoredFacade','Facade206','District208','Kiosk207_')):
  removed.append(old.name);bpy.data.objects.remove(old,do_unlink=True)
paint=bpy.data.materials['Original229 dark roof panels']
trim=bpy.data.materials['Original229 weathered roof reinforcement']
black=make_material('Service230 recessed joints',(.009,.015,.02,1),.4,.72)
glass=make_material('Service230 blue smoked glazing',(.015,.055,.065,1),.35,.22)
amber=make_material('Service230 power indicators',(.55,.23,.025,1),.2,.4,1.6)
added=[]
def panel(name,center,right,normal,width,height,thickness,material,cut=.07):
 center=Vector(center);right=Vector(right);normal=Vector(normal)
 w=width/2;h=height/2;c=min(cut,w/2,h/2)
 outline=[(-w+c,-h),(w-c,-h),(w,-h+c),(w,h-c),(w-c,h),(-w+c,h),(-w,h-c),(-w,-h+c)]
 vertices=[center+right*u+normal*d+Vector((0,0,z)) for d in [-thickness/2,thickness/2] for u,z in outline]
 faces=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.materials.append(material)
 # Metric UVs keep retained roughness/normal detail from stretching across bays.
 uv=mesh.uv_layers.new()
 for poly in mesh.polygons:
  for loop in poly.loop_indices:
   co=mesh.vertices[mesh.loops[loop].vertex_index].co
   uv.data[loop].uv=(co.dot(right),co.z)
 obj=bpy.data.objects.new('Service230 '+name,mesh);bpy.context.collection.objects.link(obj);obj.parent=root;obj.matrix_world=Matrix.Identity(4)
 bevel=obj.modifiers.new('Manufactured edge radius','BEVEL');bevel.width=.009;bevel.segments=2
 added.append(obj.name)
 return obj
for normal,right,center,width in [((0,-1,0),(1,0,0),((lo.x+hi.x)/2,lo.y-.07,1.5),hi.x-lo.x),((1,0,0),(0,1,0),(hi.x+.07,(lo.y+hi.y)/2,1.5),hi.y-lo.y)]:
 center=Vector(center);right=Vector(right);normal=Vector(normal)
 def at(u,z,depth=0):return center+right*u+normal*depth+Vector((0,0,z-1.5))
 panel('backing shell',center,right,normal,width-.04,2.95,.09,black)
 for u in [-width/2+.12,width/2-.12]:panel('structural column',at(u,1.5,.06),right,normal,.18,2.9,.18,trim)
 for z in [.18,2.83]:panel('perimeter beam',at(0,z,.06),right,normal,width-.25,.16,.18,trim)
 panel('inset access frame',at(-width*.2,1.24,.07),right,normal,1.15,2.35,.13,trim)
 panel('split service door',at(-width*.2,1.24,.15),right,normal,.96,2.14,.08,paint)
 panel('door joint',at(-width*.2,1.24,.195),right,normal,.024,2.0,.012,black,.005)
 panel('door access light',at(-width*.2+.4,1.2,.205),right,normal,.045,.18,.025,amber,.01)
 panel('window surround',at(width*.22,2.1,.07),right,normal,1.0,.75,.13,trim)
 panel('recessed glazing',at(width*.22,2.1,.145),right,normal,.85,.60,.025,glass)
 for u in [-.25,.0,.25]:panel('glazing mullion',at(width*.22+u,2.1,.17),right,normal,.025,.64,.025,black,.005)
 panel('lower utility surround',at(width*.22,.92,.08),right,normal,1.0,1.18,.14,trim)
 panel('lower utility cover',at(width*.22,.92,.16),right,normal,.85,1.0,.04,paint)
 for z in [.6,.77,.94,1.11]:panel('angled ventilation slit',at(width*.22,z,.19),right,normal,.68,.055,.035,black,.01)
 for z in [.44,2.58]:panel('panel seam',at(0,z,.11),right,normal,width-.40,.025,.018,black,.005)
 # Power conduit follows a manufactured curved path up the visible facade.
 curve=bpy.data.curves.new('Service230 exposed supply','CURVE');curve.dimensions='3D';curve.bevel_depth=.025;curve.bevel_resolution=3
 spline=curve.splines.new('BEZIER');spline.bezier_points.add(3)
 for point,(u,z) in zip(spline.bezier_points,[(width*.42,.3),(width*.42,1.5),(width*.40,2.5),(width*.32,2.8)]):
  point.co=at(u,z,.2);point.handle_left_type=point.handle_right_type='AUTO'
 curve.materials.append(trim);obj=bpy.data.objects.new('Service230 power conduit',curve);bpy.context.collection.objects.link(obj);obj.parent=root;obj.matrix_world=Matrix.Identity(4);added.append(obj.name)
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'facade.json').write_text(json.dumps({'building':root.name,'removed':removed,'added':added,'source_scope':'Original roof/colors govern identity. Unseen vertical facade, doors and glazing are interpreted, not authentic recovered views.','tactical_changes':False},indent=2))
print('SERVICE230_FACADE_EXPORTED',len(added))
