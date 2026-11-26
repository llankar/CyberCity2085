"""Replace four remaining flat service machines using one source-guided AI family."""
from pathlib import Path
import bpy,json,sys
sys.path.insert(0,str(Path(__file__).parent))
from library_placement import place
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3]
OUT=LAB/'generated/phase2/factory273';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/factory270/environment.blend'));bpy.context.preferences.filepaths.save_version=0
survey=json.loads((ROOT/'assets/maps/city_industrial_factory_floor.wall-traces.json').read_text());cw,ch=survey['canvas_size'];instances=[]
for item in survey['walls']:
 if item['id'] not in ['nw_machine','ne_machine','sw_machine','se_machine']:continue
 x1,y1,x2,y2=item['rect'];w=(x2-x1)*40/cw;d=(y2-y1)*28/ch;x=(x1+x2)/2*40/cw-20;y=14-(y1+y2)/2*28/ch
 assert bpy.data.objects.get('Occludable_'+item['id']) is None,'Do not silently duplicate a pre-existing volume'
 root=bpy.data.objects.new('Occludable_'+item['id'],None);bpy.context.collection.objects.link(root)
 objects=place(LAB/'environment-library/assets/industrial_service267/model.glb',root,(x,y,0),(w,d,2.4),preserve_anchor=True)
 instances.append({'asset':'industrial_service267','parent':item['id'],'position_blender':[x,y,0],'fitting_envelope':[w,d,2.4],'policy':'Uniform fit; original source envelope includes service clearance, no anisotropic stretching','mesh_instances':len(objects)})
floor=bpy.data.materials['Retained factory floor'];next(n for n in floor.node_tree.nodes if n.type=='TEX_IMAGE').image=bpy.data.images.load(str(OUT/'floor.png'))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' or o.type=='LIGHT' and o.name.startswith('Wall270') or o.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_lights=True)
(OUT/'placements.json').write_text(json.dumps({'source':'factory270','new_instances':instances,'meaningful_industrial_instances_total':18,'industrial_types_total':5,'replaced_flat_source_groups':4,'tactical_mutation':False,'artistic_status':'NEEDS_NATIVE_REVIEW'},indent=2))
print('FACTORY273_CORNER_MACHINES_EXPORTED',len(instances))
