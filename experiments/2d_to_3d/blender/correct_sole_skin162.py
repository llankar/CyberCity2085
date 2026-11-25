"""Isolated minimal source-sole skin correction, retaining all authored geometry/clips."""
import bpy,json,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent))
from sole_skin_weights162 import redistribute
from glb_document import Glb
from game_materials import restore
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');source=root/'foot_contact161';out=root/'sole_skin162';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');body=max((o for o in scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
def geometry_hash():return hashlib.sha256(repr(([tuple(v.co) for v in body.data.vertices],[tuple(p.vertices) for p in body.data.polygons],[tuple(u.uv) for u in body.data.uv_layers.active.data])).encode()).hexdigest()
before_geometry=geometry_hash();before_weights={v.index:{g.group:g.weight for g in v.groups} for v in body.data.vertices}
selected=set();changes=[]
for side in ('L','R'):
 foot={g.index for g in body.vertex_groups if g.name in ('DEF-foot.'+side,'DEF-toe.'+side)}
 shin={g.index for g in body.vertex_groups if g.name.startswith('DEF-shin.'+side)}
 ids=[v.index for v in body.data.vertices if sum(before_weights[v.index].get(g,0.) for g in foot)>.5]
 floor=min((body.matrix_world@body.data.vertices[i].co).z for i in ids)
 ids=[i for i in ids if (body.matrix_world@body.data.vertices[i].co).z<floor+.012]
 for index in ids:
  old=before_weights[index];new=redistribute(old,foot,shin)
  for group,value in new.items():body.vertex_groups[group].add([index],value,'REPLACE')
  selected.add(index)
 changes.append({'side':side,'selected_vertices':len(ids),'shin_retention':.7})
assert geometry_hash()==before_geometry
for v in body.data.vertices:
 if v.index not in selected:assert before_weights[v.index]=={g.group:g.weight for g in v.groups}
 else:assert abs(sum(g.weight for g in v.groups)-sum(before_weights[v.index].values()))<1e-6
notice=(source/'CREDITS.txt').read_text()+'\n162: sole-only skin study,30percent of existing shin weights redistributed to existing foot/toe influences within bottom12mm. Geometry/UV/all other weights and all clip channels retained; full sole and native regression pending.\n'
(out/'CREDITS.txt').write_text(notice);bpy.data.texts.new('SOLE162_CHANGES').write(notice)
for o in scene.objects:o.select_set(o==rig or o.type=='MESH')
bpy.context.view_layer.objects.active=rig;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_raw.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,export_rest_position_armature=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_optimize_animation_keep_anim_object=True,export_all_influences=True)
g=Glb(out/'human_raw.glb');restore(g,Glb(source/'human.glb'));g.save(out/'human.glb')
(out/'skin_changes.json').write_text(json.dumps({'selections':changes,'selected_total':len(selected),'geometry_uv_sha256':before_geometry,'other_weights_exact':True,'weight_sums_preserved':True,'variant_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest()},indent=2));print('SOLE_SKIN162_EXPORTED',len(selected))
