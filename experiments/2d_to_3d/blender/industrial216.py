"""Replace repeated merchandise with acquired repair machinery and rooftop ducts."""
from pathlib import Path
import bpy,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase216';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase214/environment.blend'))
def bounds(obj):
 pts=[obj.matrix_world@Vector(p) for p in obj.bound_box]
 return Vector([min(p[i] for p in pts) for i in range(3)]),Vector([max(p[i] for p in pts) for i in range(3)])
def template(pack,name=None):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(LAB/'sources/environment169'/pack/(pack+'_1k.gltf')))
 imported=set(bpy.data.objects)-before
 source=next(o for o in imported if o.type=='MESH' and (name is None or o.name==name))
 mesh=source.data.copy();mesh.transform(source.matrix_world)
 lo=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);hi=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)])
 mesh.transform(Matrix.Translation(-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))))
 for o in imported:bpy.data.objects.remove(o,do_unlink=True)
 return mesh,hi-lo
def part(source,name,position,length,root):
 mesh,dims=source;obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.parent=root
 obj.matrix_world=Matrix.Translation(Vector(position))@Matrix.Scale(length/max(dims),4)
 return obj
compressor=template('old_military_compressor')
elbow=template('modular_industrial_pipes_01','modular_industrial_pipes_01_pipe04')
valve=template('modular_industrial_pipes_01','modular_industrial_pipes_01_pipe08')
duct=template('modular_airduct_rectangular_01','modular_airduct_rectangular_01_corner_01')
removed=0;shops=[];roofs=[]
for name,kind in [('market_nw','repair'),('market_se','pipe salvage')]:
 root=bpy.data.objects['Occludable_'+name];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
 lo,hi=bounds(body);cx=(lo.x+hi.x)/2;cy=(lo.y+hi.y)/2;depth=min(hi.y-lo.y-.3,3.4);front=cy-depth/2
 for o in list(root.children_recursive):
  if o.name.startswith(('Store197 sealed components','Store197 rear stock','Store197 medical stock')):
   bpy.data.objects.remove(o,do_unlink=True);removed+=1
 if kind=='repair':
  part(compressor,'Industry216 repair compressor',(cx-.6,front+.4,.78),1.42,root)
  part(valve,'Industry216 service valve',(cx+.7,front+.4,.78),.55,root)
 else:
  for dx,length in [(-.8,.65),(0,.48),(.65,.7)]:
   part(elbow,'Industry216 salvaged elbow',(cx+dx,front+.4,.78),length,root)
  part(valve,'Industry216 salvaged valve',(cx,front+1.0,.78),.65,root)
 for o in root.children_recursive:
  if o.type=='FONT' and o.name.startswith('Store197 shop identifier'):
   o.data=o.data.copy();o.data.body='REPAIR / PUMPS' if kind=='repair' else 'PIPE / RECLAIM'
 shops.append(name)
for name in ['south_building_w','south_building_e']:
 root=bpy.data.objects['Occludable_'+name]
 old=next(o for o in root.children_recursive if o.type=='MESH' and o.name.startswith('AuthoredRoofVent'))
 lo,hi=bounds(old);position=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 bpy.data.objects.remove(old,do_unlink=True)
 obj=part(duct,'Industry216 roof exhaust',position,1.65,root)
 roofs.append({'building':name,'base':list(position)})
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'industry.json').write_text(json.dumps({'diversified_shops':shops,'removed_repeated_parts':removed,'rooftop_exhausts':roofs,'scope':'retained authored PBR meshes inside existing shop/roof footprints; no tactical rule changes'},indent=2))
print('INDUSTRY216_READY',shops,removed,flush=True)
