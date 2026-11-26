"""Reuse existing industrial roof components in the northern source-specific layout."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase239';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase238/environment.blend'))
root=bpy.data.objects['Occludable_north_building'];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
points=[body.matrix_world@Vector(p) for p in body.bound_box];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
w=hi.x-lo.x;d=hi.y-lo.y;z=hi.z+.035;added=[];removed=[]
for assembly in [o for o in root.children_recursive if o.name.startswith('Authored_old_military_compressor')]:
 if assembly.name.startswith('Authored_old_military_compressor'):
  for child in list(assembly.children_recursive):
   removed.append(child.name);bpy.data.objects.remove(child,do_unlink=True)
  removed.append(assembly.name);bpy.data.objects.remove(assembly,do_unlink=True)
for obj in list(root.children_recursive):
 if obj.name.startswith(('AuthoredRoofVent','Roof199')):removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
paint=bpy.data.materials['Original229 dark roof panels'];trim=bpy.data.materials['Original229 weathered roof reinforcement'];black=bpy.data.materials['Service230 recessed joints']
def at(u,v,h=0):return Vector((lo.x+u*w,hi.y-v*d,z+h))
def attach(obj):
 world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world;added.append(obj.name);return obj
def part(name,location,half,material):return attach(box('Original239 '+name,location,half,material,.009))
nx=max(2,round(w/.9));ny=max(2,round(d/.85))
for x in range(nx):
 for y in range(ny):part('roof plate',at((x+.5)/nx,(y+.5)/ny),(w/nx/2-.012,d/ny/2-.012,.018),paint)
for u in [.025,.975]:part('roof perimeter',at(u,.5,.055),(.04,d*.47,.04),trim)
for v in [.025,.975]:part('roof perimeter',at(.5,v,.055),(w*.47,.04,.04),trim)
# Source clusters machinery to the left, leaving a broad right-side panel.
source_root=bpy.data.objects['Occludable_ne_building']
fans=[o for o in source_root.children_recursive if o.name.startswith('Original236 reused extractor ') and abs(o.matrix_world.to_scale().x-1.85)<.001]
assert len(fans)==10
part('extractor base',at(.29,.31,.10),(.48,.46,.085),trim)
for old in fans:
 obj=bpy.data.objects.new('Original239 reused '+old.data.name,old.data);bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Translation(at(.29,.31,.19))@Matrix.Scale(1.5,4);attach(obj)
part('broad raised panel',at(.76,.18,.10),(w*.17,d*.16,.08),trim)
part('broad inset lid',at(.76,.18,.19),(w*.157,d*.147,.025),paint)
part('service equipment base',at(.53,.47,.18),(.32,d*.19,.16),trim)
part('service equipment inset',at(.53,.47,.35),(.27,d*.17,.025),black)
for v in [.34,.44,.54,.64]:part('service louvre',at(.53,v,.39),(.28,.025,.02),trim)
source_pipe=next(o for o in source_root.children_recursive if o.name.startswith('Original236 acquired pipe run'))
mesh=source_pipe.data
low=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);high=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)]);dims=high-low
longitudinal=max(range(3),key=lambda i:dims[i]);axis=Vector(tuple(1 if i==longitudinal else 0 for i in range(3)));cross=max(dims[i] for i in range(3) if i!=longitudinal)
for a,b in [(at(.10,.06,.16),at(.10,.78,.16)),(at(.10,.78,.16),at(.45,.78,.16)),(at(.44,.08,.16),at(.44,.70,.16))]:
 delta=b-a;scales=[.22/cross]*3;scales[longitudinal]=delta.length/dims[longitudinal]
 obj=bpy.data.objects.new('Original239 reused acquired pipe',mesh);bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Translation((a+b)/2)@axis.rotation_difference(delta.normalized()).to_matrix().to_4x4()@Matrix.Diagonal(Vector((*scales,1)));attach(obj)
assert len(added)>40
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'roof.json').write_text(json.dumps({'building':root.name,'source_context':'environment-library/references/city_exterior_neon_market_alley__north_building.png','added':added,'removed':removed,'reused_fan_parts':10,'pipe_diameter_m':.22,'limits':'One genuine roof view; machinery depth, connections and unseen shape inferred; right panel preserved as broad service area','tactical_changes':False},indent=2))
print('NORTHERN239_EXPORTED',len(added))
