"""Add the source-specific cylindrical power-machine family to the retained detail stage."""
from pathlib import Path
import bpy,json,sys
sys.path.insert(0,str(Path(__file__).parent))
from library_placement import place
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3];OUT=LAB/'generated/phase2/factory260';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/factory257/environment.blend'));bpy.context.preferences.filepaths.save_version=0
survey=json.loads((ROOT/'assets/maps/city_industrial_factory_floor.wall-traces.json').read_text());cw,ch=survey['canvas_size'];instances=[]
for item in survey['walls']:
 if item['id'] not in ['reactor_north','reactor_middle']:continue
 x1,y1,x2,y2=item['rect'];w=(x2-x1)*40/cw;d=(y2-y1)*28/ch;x=(x1+x2)/2*40/cw-20;y=14-(y1+y2)/2*28/ch
 parent=bpy.data.objects.new('Occludable_'+item['id'],None);bpy.context.collection.objects.link(parent)
 place(LAB/'environment-library/assets/cylindrical_machine259/model.glb',parent,(x,y,0),(w,d,1.65),preserve_anchor=True)
 instances.append({'asset':'cylindrical_machine259','parent':item['id'],'position_blender':[x,y,0],'fitting_envelope':[w,d,1.65]})
# Remove the visibly artificial platform in this derivative only; old prototypes
# remain intact. The earlier generator mesh still needs an artistic upgrade.
platform=bpy.data.objects.get('west_generator mounting platform')
if platform:bpy.data.objects.remove(platform,do_unlink=True)
floor=bpy.data.materials['Retained factory floor'];next(n for n in floor.node_tree.nodes if n.type=='TEX_IMAGE').image=bpy.data.images.load(str(OUT/'floor.png'))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
(OUT/'placements.json').write_text(json.dumps({'source':'factory257','new_instances':instances,'meaningful_new_instances_total':13,'tactical_mutation':False,'artistic_status':'NEEDS_NATIVE_REVIEW','remaining':'Four corner machines, electrical/pipe infrastructure, generator upgrade, walls and platforms remain open'},indent=2))
print('FACTORY260_CYLINDRICAL_MACHINES_EXPORTED',len(instances))
