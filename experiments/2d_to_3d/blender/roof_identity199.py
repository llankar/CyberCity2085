"""Differentiate clinic, utility and repair roofs within existing footprints."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase199';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase198/environment.blend'))
def mat(name,color,metal=.4,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=.55;s.inputs['Metallic'].default_value=metal
 if emit:s.inputs['Emission Color'].default_value=(*color,1);s.inputs['Emission Strength'].default_value=emit
 return m
steel=mat('Roof199 steel',(.045,.065,.075),.7);tankmat=mat('Roof199 oxidized reservoir',(.08,.15,.14),.5);solar=mat('Roof199 photovoltaic',(.012,.035,.09),.45);cyan=mat('Roof199 clinic light',(.015,.6,.55),.1,2)
records=[]
def parent(o,root):
 world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
 if root.name.startswith("Roof199 solar assembly"):o.rotation_euler=(0,0,0)
 return o
def box(name,loc,size,m,root):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);b=o.modifiers.new('Fabricated edge','BEVEL');b.width=.018;b.segments=3;return parent(o,root)
def cylinder(name,loc,radius,depth,m,root):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(m);b=o.modifiers.new('Rolled seam edge','BEVEL');b.width=.025;b.segments=3
 for f in o.data.polygons:f.use_smooth=abs(f.normal.z)<.5
 return parent(o,root)
def anchor(name):
 root=bpy.data.objects['Occludable_'+name];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'));pts=[body.matrix_world@Vector(c) for c in body.bound_box];z=max(p.z for p in pts)
 roof=[body.matrix_world@p.center for p in body.data.polygons if p.normal.z>.5]
 occupied=[o.matrix_world.translation for o in root.children_recursive if o.type=='MESH' and not o.name.startswith(('PBR_Facade_','AuthoredFacade_')) and o.matrix_world.translation.z>2.8]
 candidates=[p for p in roof if all(any((q-Vector((p.x+dx,p.y+dy,p.z))).length<.1 for q in roof) for dx in [-1,0,1] for dy in [-1,0,1])]
 assert candidates,name
 chosen=max(candidates,key=lambda p:min([(p-q).length for q in occupied] or [10]));return root,chosen.x,chosen.y,z
# Utility building: a real cylindrical reservoir, metal bands, lid and mounts.
root,x,y,z=anchor('nw_building')
for dx in [-.45,.45]:box('Roof199 reservoir mount',(x+dx,y,z+.18),(.18,1.35,.36),steel,root)
cylinder('Roof199 reservoir shell',(x,y,z+.95),.68,1.35,tankmat,root)
for dz in [.35,.65,1.28,1.6]:cylinder('Roof199 reservoir band',(x,y,z+dz),.704,.055,steel,root)
cylinder('Roof199 service cap',(x,y,z+1.69),.24,.14,steel,root)
records.append({'building':root.name,'type':'utility reservoir'})
# Repair shop: low, tilted photovoltaic array with actual cell grid and frame.
root,x,y,z=anchor('south_building_w')
for row in [-.5,.5]:
 for col in [-.55,.55]:
  assembly=bpy.data.objects.new('Roof199 solar assembly',None);bpy.context.collection.objects.link(assembly);assembly.parent=root;assembly.location=(x+col,y+row,z+.22);assembly.rotation_euler.x=math.radians(12)
  frame=box('Roof199 solar frame',(0,0,0),(1.02,.88,.055),steel,assembly);frame.location=(0,0,0)
  panel=box('Roof199 solar cells',(0,0,.035),(.94,.8,.018),solar,assembly);panel.location=(0,0,.035)
  for dx in [-.3,0,.3]:
   strip=box('Roof199 solar bus',(dx,0,.048),(.009,.79,.004),steel,assembly);strip.location=(dx,0,.048)
  for dy in [-.26,0,.26]:
   strip=box('Roof199 solar row',(0,dy,.048),(.93,.008,.004),steel,assembly);strip.location=(0,dy,.048)
records.append({'building':root.name,'type':'repair photovoltaic array'})
# Clinic: a restrained roof-mounted sign with supports, not another blank box.
root,x,y,z=anchor('south_building_e')
for dx in [-1.1,1.1]:box('Roof199 sign support',(x+dx,y,z+.38),(.09,.12,.76),steel,root)
box('Roof199 clinic sign housing',(x,y,z+1.0),(2.8,.16,.85),steel,root)
curve=bpy.data.curves.new('Roof199 clinic sign type','FONT');curve.body='CLINIC // 24H';curve.align_x='CENTER';curve.align_y='CENTER';curve.size=.26;curve.extrude=.003
sign=bpy.data.objects.new('Roof199 clinic lettering',curve);bpy.context.collection.objects.link(sign);sign.parent=root;sign.location=(x,y-.095,z+1);sign.rotation_euler=(math.pi/2,0,0);sign.data.materials.append(cyan)
for dx in [-1.34,1.34]:box('Roof199 sign edge',(x+dx,y-.1,z+1),(.025,.025,.7),cyan,root)
records.append({'building':root.name,'type':'clinic rooftop sign'})
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'roofs.json').write_text(json.dumps({'assemblies':records,'scope':'cosmetic roofs; original tactical map retained'},indent=2));print('ROOF199_READY',len(records),flush=True)
