"""Two rejected topology-based restyling studies of real author cards; not final hair."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from game_materials import restore
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');reverse='--reverse-style' in sys.argv
out=root/('hair_reverse158' if reverse else 'hair_sweep158_cards');out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'hair_cards157/human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST';bpy.context.view_layer.update()
body=max((o for o in scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
body_before=hashlib.sha256(repr([(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in body.data.vertices]).encode()).hexdigest()
hairs=[o for o in scene.objects if o.name.startswith('AuthoredHairCards157_')];assert len(hairs)==2
count=0;root_count=0;maximum=0.;uv_hashes={}
def uv_hash(o):return hashlib.sha256(repr([tuple(v.uv) for v in o.data.uv_layers.active.data]).encode()).hexdigest()
def smooth(x):x=max(0.,min(1.,x));return x*x*(3-2*x)
for o in hairs:
 uv_hashes[o.name]=uv_hash(o)
 if reverse:
  center=Vector((0,.035,1.75))
  rotation=__import__('mathutils').Matrix.Rotation(math.pi,3,'Z')
  for v in o.data.vertices:
   p=o.matrix_world@v.co;candidate=center+rotation@(p-center)
   v.co=o.matrix_world.inverted()@candidate;maximum=max(maximum,(candidate-p).length);count+=1
  assert uv_hash(o)==uv_hashes[o.name]
  continue
 parent=list(range(len(o.data.vertices)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for edge in o.data.edges:
  a,b=map(find,edge.vertices);parent[a]=b
 groups={}
 for i in range(len(parent)):groups.setdefault(find(i),[]).append(i)
 for indices in groups.values():
  world=[o.matrix_world@o.data.vertices[i].co for i in indices]
  center=sum(world,Vector())/len(world)
  if center.y>.055 or min(p.y for p in world)>.005:
   root_count+=len(indices);continue
  top=max(p.z for p in world)
  roots=[p for p in world if p.z>=top-.004]
  anchor=sum(roots,Vector())/len(roots)
  # Entire connected authored sheet rotates as one, retaining all UVs/triangles.
  weight=smooth((.055-center.y)/.075)
  angle=math.radians(-145*weight)
  rotation=__import__('mathutils').Matrix.Rotation(angle,3,'X')
  for i,p in zip(indices,world):
   candidate=anchor+rotation@((p-anchor)*(1-.4*weight))
   offset=(candidate-p).length
   o.data.vertices[i].co=o.matrix_world.inverted()@candidate
   count+=int(offset>1e-6);maximum=max(maximum,offset)
 assert uv_hash(o)==uv_hashes[o.name]
assert body_before==hashlib.sha256(repr([(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in body.data.vertices]).encode()).hexdigest()
rig.data.pose_position='POSE'
for t in rig.animation_data.nla_tracks:t.mute=t.name!='Hard stand'
rig.animation_data.action=None;scene.frame_set(0);bpy.context.view_layer.update()
notice=(root/'hair_cards157/CREDITS.txt').read_text()+'\n158: actual author sheets restyled by '+('whole-style reversal' if reverse else 'upper-sheet-anchor rotation')+'; UV topology preserved. Diagnostic, not final Rook art.\n'
(out/'CREDITS.txt').write_text(notice);bpy.data.texts.new('HAIR158_CHANGES').write(notice)
for o in scene.objects:o.select_set(o==rig or o.type=='MESH')
bpy.context.view_layer.objects.active=rig;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_raw.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,export_rest_position_armature=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_optimize_animation_keep_anim_object=True,export_all_influences=True)
g=Glb(out/'human_raw.glb');restore(g,Glb(root/'hair_cards157/human.glb'));g.save(out/'human.glb')
(out/'fit.json').write_text(json.dumps({'moved_card_vertices':count,'unchanged_nonfront_vertices':root_count,'maximum_vertex_offset_m':maximum,'method':'whole_style_rotation' if reverse else 'connected_sheet_rotation','body_vertices_weights_exact':True,'uv_hashes':uv_hashes,'scope':'Actual card restyling; neutral/contact/animation review required'},indent=2))
print('AUTHORED_CARD_SWEEP158_READY',count,root_count,maximum)
