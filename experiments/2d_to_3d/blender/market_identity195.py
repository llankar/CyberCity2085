"""Dress actual low market counters, preserving all tactical footprints."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase195';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase186/environment.blend'))
def material(name,color,rough=.8,metal=0,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal
 if emission:s.inputs['Emission Color'].default_value=(*color,1);s.inputs['Emission Strength'].default_value=emission
 return m
frame=material('Market195 anodized steel',(.035,.05,.06),.6,.65)
normal=bpy.data.images.load(str(OUT/'canvas_normal.png'));normal.colorspace_settings.name='Non-Color'

cloth=[]
for name,color in [('Teal',(.008,.035,.04)),('Ochre',(.06,.035,.012)),('Plum',(.045,.012,.03)),('Pale',(.045,.05,.048))]:
 m=material('Market195 canvas '+name,color,.95)
 nodes=m.node_tree.nodes;links=m.node_tree.links;tex=nodes.new('ShaderNodeTexImage');tex.image=normal
 n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.25;links.new(tex.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal']);cloth.append(m)
cyan=material('Clinic195 medical cyan',(.02,.8,.8),.6,0,2)
white=material('Clinic195 ceramic',(.35,.4,.4),.8)
def cube(name,point,size,mat,parent):
 bpy.ops.mesh.primitive_cube_add(size=1,location=point);o=bpy.context.object;o.name=name;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world;o.data.materials.append(mat)
 bevel=o.modifiers.new('Manufactured edges','BEVEL');bevel.width=.008;bevel.segments=2;return o
made=[]
for idx,name in enumerate(['market_nmid','market_nw','market_ne','market_sw','market_smid','market_se','market_east']):
 root=bpy.data.objects['Occludable_'+name];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
 pts=[body.matrix_world@Vector(c) for c in body.bound_box];lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)])
 # Use a smaller canopy over a central bay on broad counters; leave edges open.
 width=min(hi.x-lo.x-.3,5.5);depth=min(hi.y-lo.y-.3,3.4);cx=(hi.x+lo.x)/2;cy=(hi.y+lo.y)/2
 x0=cx-width/2;x1=cx+width/2;y0=cy-depth/2;y1=cy+depth/2
 for x in [x0,x1]:
  for y in [y0,y1]:cube('Market195 frame post',(x,y,1.5),(.045,.045,1.6),frame,root)
 for y in [y0,y1]:cube('Market195 longitudinal frame',(cx,y,2.29),(width,.055,.055),frame,root)
 for x in [x0,x1]:cube('Market195 cross frame',(x,cy,2.29),(.055,depth,.055),frame,root)
 cube('Market195 illuminated valance',(cx,y0,2.22),(width*.8,.025,.025),cyan,root)
 vertices=[];faces=[];steps=max(8,int(width*4))
 for ix in range(steps+1):
  x=x0+width*ix/steps
  for iy in range(5):
   f=iy/4;y=y0+depth*f;z=2.26+.20*math.sin(math.pi*f)-.025*math.sin(math.pi*ix/steps)
   vertices.append((x,y,z))
 for ix in range(steps):
  for iy in range(4):a=ix*5+iy;faces.append((a,a+5,a+6,a+1))
 mesh=bpy.data.meshes.new('Tensioned canopy195');mesh.from_pydata(vertices,[],faces);mesh.update()
 obj=bpy.data.objects.new('Market195 striped canopy '+name,mesh);bpy.context.collection.objects.link(obj);obj.parent=root
 mesh.materials.append(cloth[idx%3]);mesh.materials.append(cloth[3])
 uv=mesh.uv_layers.new(name='CanvasUV')
 for poly in mesh.polygons:
  poly.material_index=int((poly.index//4)%3==0)
  for li in poly.loop_indices:
   p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((p.x-x0)/1.5,(p.y-y0)/1.5)
 solid=obj.modifiers.new('Canvas thickness','SOLIDIFY');solid.thickness=.012
 made.append(name)
# A diegetic medical sign distinguishes the foreground clinic.
clinic=bpy.data.objects['Occludable_south_building_e']
cube('Clinic195 sign housing',(-.75,-14.15,2.15),(.7,.12,.85),frame,clinic)
cube('Clinic195 cross vertical',(-.75,-14.23,2.15),(.13,.025,.57),cyan,clinic)
cube('Clinic195 cross horizontal',(-.75,-14.24,2.15),(.49,.025,.13),cyan,clinic)
for x in [-1.65,1.25]:cube('Clinic195 entrance light',(x,-14.12,1.1),(.045,.045,1.8),cyan,clinic)
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'market.json').write_text(json.dumps({'market_stalls':made,'canopy_height_m':2.46,'supports_within_existing_counter_footprints':True,'functional_wall_cells':'unchanged','scope':'single-map cosmetic market dressing, not new tactical collisions'},indent=2))
print('MARKET195_READY',len(made),flush=True)
