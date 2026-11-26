"""Continue both existing real-profile rails through the visual station exits."""
import bpy

def extend_track_ends():
 root=bpy.data.objects['Track263VisualOnly'];parts=[]
 rail=bpy.data.materials['Track263 worn rail steel'];rust=bpy.data.materials['Track263 oxidized rail web'];concrete=bpy.data.materials['Track263 weathered concrete ties']
 def part(name,p,half,mat):
  x,y,z=half;data=bpy.data.meshes.new(name)
  data.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);data.materials.append(mat)
  o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=p;o.parent=root;parts.append(o)
 centers=[14-p*28/540 for p in [252,284]]
 for start,end in [(-20,22*40/960-20),(936*40/960-20,20)]:
  middle=(start+end)/2;half=(end-start)/2
  for y in centers:
   for z,width,height,mat in [(.135,.105,.018,rust),(.20,.025,.05,rust),(.265,.065,.022,rail)]:part('Track272 continuous exit rail',(middle,y,z),(half,width,height),mat)
  for i in range(3):part('Track272 exit sleeper',(start+(i+.5)*(end-start)/3,sum(centers)/2,.035),(.10,1.24,.045),concrete)
 # Keep just the original material batches, without introducing a solid portal.
 for mat in [rail,rust,concrete]:
  objects=[o for o in root.children if o.type=='MESH' and o.data.materials[0]==mat]
  bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
 print('TRACK272_EXITS_EXTENDED_TO_MAP_EDGES')
