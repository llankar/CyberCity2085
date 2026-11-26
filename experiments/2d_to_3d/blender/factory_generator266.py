"""Replace the coarse west generator only, preserving the detailed factory260."""
from pathlib import Path
import bpy,json,sys
sys.path.insert(0,str(Path(__file__).parent))
from library_placement import place
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3]
OUT=LAB/'generated/phase2/factory266';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/factory260/environment.blend'));bpy.context.preferences.filepaths.save_version=0
survey=json.loads((ROOT/'assets/maps/city_industrial_factory_floor.wall-traces.json').read_text())
item=next(r for r in survey['walls'] if r['id']=='west_generator');cw,ch=survey['canvas_size']
x1,y1,x2,y2=item['rect'];w=(x2-x1)*40/cw;d=(y2-y1)*28/ch;x=(x1+x2)/2*40/cw-20;y=14-(y1+y2)/2*28/ch
root=bpy.data.objects['Occludable_west_generator']
for child in list(root.children_recursive):bpy.data.objects.remove(child,do_unlink=True)
place(LAB/'environment-library/assets/industrial_generator265/model.glb',root,(x,y,0),(w,d,1.35),preserve_anchor=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
(OUT/'placements.json').write_text(json.dumps({'source':'factory260','new_instances':[{'asset':'industrial_generator265','parent':'west_generator','position_blender':[x,y,0],'fitting_envelope':[w,d,1.35]}],'meaningful_new_instances_total':14,'new_asset_types_total':4,'tactical_mutation':False,'artistic_status':'NEEDS_NATIVE_REVIEW'},indent=2))
print('FACTORY266_GENERATOR_EXPORTED')
