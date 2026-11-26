"""Dress seven existing stalls with real local merchandise and metal counters."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase197';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase195/environment.blend'))
def mat(name,color,metal=.2,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=.67;s.inputs['Metallic'].default_value=metal
 if emission:s.inputs['Emission Color'].default_value=(*color,1);s.inputs['Emission Strength'].default_value=emission
 return m
steel=mat('Store197 brushed charcoal',(.035,.045,.055),.65)
cyan=mat('Store197 mint display',(.025,.32,.35),.1,1.2)
amber=mat('Store197 amber display',(.35,.12,.015),.1,1.2)
paint=[mat('Store197 paint'+str(i),c,.35) for i,c in enumerate([(.025,.075,.075),(.08,.045,.02),(.065,.025,.055)])]
def box(name,loc,size,material,root):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 world=o.matrix_world.copy();o.parent=root;o.matrix_world=world;o.data.materials.append(material);b=o.modifiers.new('Folded metal edges','BEVEL');b.width=.012;b.segments=2
 return o
def template(path):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));objects=set(bpy.data.objects)-before
 meshes=[o for o in objects if o.type=='MESH'];parts=[]
 for o in meshes:
  mesh=o.data.copy();mesh.transform(o.matrix_world);parts.append(mesh)
 for o in objects:bpy.data.objects.remove(o,do_unlink=True)
 points=[v.co for mesh in parts for v in mesh.vertices];lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
 return parts,lo,hi
def goods(source,loc,length,root,label):
 parts,lo,hi=source;scale=length/max(hi-lo);center=(lo+hi)*.5;center.z=lo.z
 for mesh in parts:
  o=bpy.data.objects.new(label,mesh);bpy.context.collection.objects.link(o);o.parent=root;o.scale=Vector((scale,scale,scale));o.location=Vector(loc)-center*scale
crate=template(LAB/'generated/phase2/crate_procedural/crate_procedural.glb')
medical=template(LAB/'sources/environment169/medical_box/medical_box_1k.gltf')
records=[]
for idx,name in enumerate(['market_nmid','market_nw','market_ne','market_sw','market_smid','market_se','market_east']):
 root=bpy.data.objects['Occludable_'+name];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
 pts=[body.matrix_world@Vector(c) for c in body.bound_box];lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)])
 cx=(lo.x+hi.x)/2;cy=(lo.y+hi.y)/2;width=min(hi.x-lo.x-.3,5.5);depth=min(hi.y-lo.y-.3,3.4);front=cy-depth/2
 # Fit merchandise on the actual 70cm counter, entirely inside its footprint.
 box('Store197 counter fascia',(cx,front-.012,.45),(width-.14,.055,.42),paint[idx%3],root)
 box('Store197 steel worktop',(cx,front+.33,.735),(width-.12,.8,.055),steel,root)
 for dx in [-.32,.0,.32]:
  box('Store197 ventilation slit',(cx+width*dx,front-.047,.45),(.14,.014,.20),steel,root)
 for j in range(4):
  x=cx+(j-1.5)*min(.65,width/4.5)
  goods(medical if idx%3==0 else crate,(x,front+.35,.77),.42 if idx%3==0 else .46,root,'Store197 medical stock' if idx%3==0 else 'Store197 sealed components')
 # A short backboard sits inside the existing footprint, not across a path.
 box('Store197 stock backboard',(cx,front+1.15,1.13),(width-.2,.06,.7),steel,root)
 for j in range(3):
  goods(crate,(cx+(j-1)*min(.7,width/3.5),front+1.0,.77),.35,root,'Store197 rear stock')
 box('Store197 terminal housing',(cx+width*.32,front+.33,1.13),(.32,.18,.4),steel,root)
 box('Store197 terminal screen',(cx+width*.32,front+.23,1.15),(.25,.015,.23),cyan,root)
 for j in range(3):box('Store197 screen readout',(cx+width*.32,front+.216,1.09+j*.055),(.16,.008,.008),amber,root)
 # Actual emissive 3D type, not a pre-rendered screenshot of fake UI.
 curve=bpy.data.curves.new('Store197 shop sign','FONT');curve.body=['MED / SUPPLY','CELL / EXCHANGE','SALVAGE'][idx%3];curve.align_x='CENTER';curve.size=.17;curve.extrude=.001
 sign=bpy.data.objects.new('Store197 shop identifier',curve);bpy.context.collection.objects.link(sign);sign.parent=root;sign.location=(cx,front-.045,1.95);sign.rotation_euler=(math.pi/2,0,0);sign.data.materials.append(cyan if idx%3==0 else amber)
 records.append(name)
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'storefronts.json').write_text(json.dumps({'stalls':records,'sources':['local authored crate','local medical_box PBR'],'scope':'cosmetic merchandise within existing obstacle footprints; no tactical rule change'},indent=2))
print('STOREFRONT197_READY',len(records),flush=True)
