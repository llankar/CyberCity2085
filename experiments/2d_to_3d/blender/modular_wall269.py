"""Dimensioned service-wall family, shared by industrial and subway architecture."""
import bpy,math
from mathutils import Vector

def build_wall(root,center,length,depth,height,angle,materials):
 """Retain source footprint/height and cutaway parent; add genuine service depth."""
 metal,dark,trim,lamp=materials
 tangent=Vector((math.cos(angle),math.sin(angle),0));normal=Vector((-math.sin(angle),math.cos(angle),0));origin=Vector(center)
 objects=[]
 def part(name,local,half,material):
  x,y,z=half;coords=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
  p=origin+tangent*local[0]+normal*local[1]+Vector((0,0,local[2]))
  data=bpy.data.meshes.new(name);data.from_pydata([tuple(p+tangent*v[0]+normal*v[1]+Vector((0,0,v[2]))) for v in coords],[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);data.materials.append(material)
  uv=data.uv_layers.new(name='UVMap')
  for face in data.polygons:
   points=[data.vertices[data.loops[i].vertex_index].co for i in face.loop_indices]
   w=(points[1]-points[0]).length/1.5;h=(points[2]-points[1]).length/1.5
   for loop,value in zip(face.loop_indices,[(0,0),(w,0),(w,h),(0,h)]):uv.data[loop].uv=value
  o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.parent=root;objects.append(o)
  return o
 def pipe(side,z):
  vertices=[];faces=[];radius=.035
  for end in [-1,1]:
   p=origin+tangent*end*(length/2-.06)+normal*side*(depth/2+.09)+Vector((0,0,z))
   for j in range(12):
    a=j*math.tau/12;vertices.append(tuple(p+normal*math.cos(a)*radius+Vector((0,0,math.sin(a)*radius))))
  for j in range(12):faces.append((j,(j+1)%12,(j+1)%12+12,j+12))
  faces.extend([tuple(reversed(range(12))),tuple(range(12,24))])
  data=bpy.data.meshes.new('Wall269 round conduit');data.from_pydata(vertices,[],faces);data.materials.append(trim)
  o=bpy.data.objects.new('Wall269 round conduit',data);bpy.context.collection.objects.link(o);o.parent=root;objects.append(o)
 part('Wall269 structural backing',(0,0,height/2),(length/2,depth/2,height/2),dark)
 count=max(1,math.ceil(length/2));bay=length/count
 for i in range(count):
  x=-length/2+(i+.5)*bay
  for side in [-1,1]:
   y=side*(depth/2+.018)
   part('Wall269 framed panel',(x,y,height*.53),(bay*.47,.025,height*.39),metal)
   part('Wall269 inset service channel',(x-bay*.28,y+side*.03,height*.52),(bay*.14,.018,height*.29),dark)
   for j in range(7):part('Wall269 ventilation blade',(x-bay*.28,y+side*.06,height*(.31+j*.045)),(bay*.115,.02,.012),trim)
   part('Wall269 upper lamp housing',(x+bay*.16,y+side*.04,height*.84),(bay*.17,.04,.045),dark)
   part('Wall269 recessed lamp',(x+bay*.16,y+side*.083,height*.84),(bay*.14,.005,.015),lamp)
   part('Wall269 panel latch',(x+bay*.32,y+side*.05,height*.50),(.025,.018,.065),trim)
   part('Wall269 panel seam',(x-bay*.48,y,height*.50),(.026,.05,height*.47),trim)
 for side in [-1,1]:
  for z in [height*.10,height*.19]:pipe(side,z)
  for i in range(count+1):
   x=-length/2+i*bay
   part('Wall269 conduit clamp',(x,side*(depth/2+.09),height*.145),(.035,.05,height*.075),metal)
 for z in [.055,height-.055]:part('Wall269 edge beam',(0,0,z),(length/2,depth/2+.075,.055),metal)
 # Material batches preserve the original source root used by cutaway code.
 result=[]
 for material in materials:
  selected=[o for o in objects if o.name in bpy.data.objects and o.data.materials[0]==material]
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();result.append(selected[0])
  objects=[o for o in root.children if o.type=='MESH']
 return result
