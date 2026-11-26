"""Replace three original assembly lines with reusable real arms and roller conveyors."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from library_placement import place
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3];OUT=LAB/'generated/phase2/factory257';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/factory249/environment.blend'));bpy.context.preferences.filepaths.save_version=0
survey=json.loads((ROOT/'assets/maps/city_industrial_factory_floor.wall-traces.json').read_text());cw,ch=survey['canvas_size'];gw,gh=40,28
arm=LAB/'environment-library/assets/industrial_arm256/model.glb';conveyor=LAB/'environment-library/assets/roller_conveyor256/model.glb'
placements=[]
for item in survey['walls']:
 if item['id'] not in ['west_assembly','east_assembly_north','east_assembly_south']:continue
 identifier=item['id'];x1,y1,x2,y2=item['rect'];w=(x2-x1)*gw/cw;d=(y2-y1)*gh/ch;x=(x1+x2)/2*gw/cw-gw/2;y=gh/2-(y1+y2)/2*gh/ch
 root=bpy.data.objects.new('Occludable_'+identifier,None);bpy.context.collection.objects.link(root)
 for side in [-1,1]:
  position=(x+side*w*.30,y,0)
  place(arm,root,position,(2.7,2.7,2.1),preserve_anchor=True,yaw=-side*math.pi/2)
  placements.append({'asset':'industrial_arm256','parent':identifier,'position_blender':position,'yaw':-side*math.pi/2})
 count=2 if w>9 else 1
 for i in range(count):
  position=(x+(i-(count-1)/2)*3.7,y+d*.13,0)
  place(conveyor,root,position,(4.2,1.65,.95),preserve_anchor=True)
  placements.append({'asset':'roller_conveyor256','parent':identifier,'position_blender':position})
floor=bpy.data.materials['Retained factory floor'];next(n for n in floor.node_tree.nodes if n.type=='TEX_IMAGE').image=bpy.data.images.load(str(OUT/'floor.png'))
scene=bpy.context.scene;scene.render.filepath=str(OUT/'overview.png');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=next(o for o in scene.objects if o.type=='MESH');bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
(OUT/'placements.json').write_text(json.dumps({'source_map':'city_industrial_factory_floor','new_asset_families':2,'new_robot_arms':6,'new_conveyor_modules':len(placements)-6,'instances':placements,'tactical_mutation':False,'artistic_status':'NEEDS_NATIVE_REVIEW'},indent=2))
print('FACTORY257_ASSEMBLY_EXPORTED',len(placements),'new meaningful instances')
