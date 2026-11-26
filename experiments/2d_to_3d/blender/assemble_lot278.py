"""Assemble the whole prepared object lot before any map review/captures."""
from pathlib import Path
import bpy,json,sys,math,argparse
sys.path.insert(0,str(Path(__file__).parent))
from library_placement import place,reset_library_cache
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3]
ASSETS=LAB/'environment-library/assets';cargo=ASSETS/'cargo_crate274/model.glb';wreck=ASSETS/'derelict_suv275/model.glb'
parser=argparse.ArgumentParser();parser.add_argument('--maps',default='factory,residential,wasteland');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
selected=set(args.maps.split(','));assert selected<={'factory','residential','wasteland'}
assert cargo.is_file() and wreck.is_file(),'Finish the entire production lot before map assembly'
tasks=[('factory273','factory278','city_industrial_factory_floor','Retained factory floor'),('residential253','residential278','city_district_apartment_block','Residential original street floor'),('wasteland254','wasteland278','wasteland_outdoor_02_ashfield_ruins','Original ashfield ground')]
for source,folder,name,ground in tasks:
 if folder.removesuffix('278') not in selected:continue
 out=LAB/'generated/phase2'/folder;out.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2'/source/'environment.blend'));reset_library_cache();bpy.context.preferences.filepaths.save_version=0
 survey=json.loads((ROOT/f'assets/maps/{name}.wall-traces.json').read_text());cw,ch=survey['canvas_size'];instances=[]
 ids=['north_crates_w','north_crates_m','north_crates_e','south_crates_w','south_crates_e'] if folder=='factory278' else ['west_street_crates'] if folder=='residential278' else ['wreck_e']
 for item in survey['walls']:
  if item['id'] not in ids:continue
  x1,y1,x2,y2=item['rect'];w=(x2-x1)*40/cw;d=(y2-y1)*28/ch;x=(x1+x2)/2*40/cw-20;y=14-(y1+y2)/2*28/ch
  root=bpy.data.objects.get('Occludable_'+item['id'])
  if root:
   for o in list(root.children_recursive):bpy.data.objects.remove(o,do_unlink=True)
  else:root=bpy.data.objects.new('Occludable_'+item['id'],None);bpy.context.collection.objects.link(root)
  if folder!='wasteland278':
   nx=max(1,round(w/1.5));ny=max(1,round(d/1.3))
   for ix in range(nx):
    for iy in range(ny):
     center=(x-w/2+(ix+.5)*w/nx,y-d/2+(iy+.5)*d/ny,0)
     place(cargo,root,center,(w/nx*.9,d/ny*.9,1.05),preserve_anchor=True,yaw=math.pi if iy%2 else 0)
     instances.append({'asset':'cargo_crate274','parent':item['id'],'position_blender':list(center)})
  else:
   meta=json.loads((ASSETS/'derelict_suv275/asset.json').read_text());dx,h,dy=meta['dimensions'];yaw=-math.pi/4
   rotated=(abs(math.cos(yaw))*dx+abs(math.sin(yaw))*dy,abs(math.sin(yaw))*dx+abs(math.cos(yaw))*dy)
   factor=min(w/rotated[0],d/rotated[1],1.7/h)
   place(wreck,root,(x,y,0),(dx*factor,dy*factor,h*factor),preserve_anchor=True,yaw=yaw)
   instances.append({'asset':'derelict_suv275','parent':item['id'],'position_blender':[x,y,0],'uniform_scale':factor,'actual_height':h*factor,'source_fit_note':'Source wreck footprint is unusually small; artistic scale acceptance pending ensemble review'})
 material=bpy.data.materials[ground];next(n for n in material.node_tree.nodes if n.type=='TEX_IMAGE').image=bpy.data.images.load(str(out/'floor.png'))
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'environment.blend'))
 for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' or o.type=='LIGHT' and o.name.startswith('Wall270') or o.name.startswith('Occludable_'))
 bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
 bpy.ops.export_scene.gltf(filepath=str(out/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_lights=True)
 (out/'placements.json').write_text(json.dumps({'source':source,'map':name,'instances':instances,'removed_artificial_plinths':folder=='factory278','tactical_mutation':False,'artistic_status':'NEEDS_ENSEMBLE_REVIEW'},indent=2))
 print('PRODUCTION278_ASSEMBLED',folder,len(instances),'new-family instances',flush=True)
