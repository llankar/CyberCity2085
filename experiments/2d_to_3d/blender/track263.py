"""Real rail profiles, sleepers and fasteners aligned to original subway track art."""
from pathlib import Path
import bpy,json,sys
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/metro263'
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/metro250/environment.blend'))
bpy.context.preferences.filepaths.save_version=0
rail=make_material('Track263 worn rail steel',(.14,.17,.18,1),.9,.32)
rust=make_material('Track263 oxidized rail web',(.12,.065,.035,1),.65,.77)
concrete=make_material('Track263 weathered concrete ties',(.12,.13,.12,1),.05,.9)
black=make_material('Track263 resilient fastening pads',(.015,.02,.021,1),.15,.86)
root=bpy.data.objects.new('Track263VisualOnly',None);bpy.context.collection.objects.link(root)
cache={};objects=[]
def part(name,p,half,mat):
 key=(tuple(half),mat.name)
 if key not in cache:
  x,y,z=half;mesh=bpy.data.meshes.new(name)
  mesh.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
  mesh.materials.append(mat);cache[key]=mesh
 o=bpy.data.objects.new(name,cache[key]);bpy.context.collection.objects.link(o);o.location=p;o.parent=root;objects.append(o);return o
# Position follows the two original rail centerlines in the 960x540 canvas.
start=22*40/960-20;end=936*40/960-20
centers=[14-p*28/540 for p in (252,284)];middle=sum(centers)/2
# Keep ground-level contact/routing. A lowered track trench requires separate
# actor-height integration and is deliberately not faked in this visual asset.
count=96
for i in range(count):
 x=start+(i+.5)*(end-start)/count
 part('Track263 concrete sleeper',(x,middle,.035),(.10,1.24,.045),concrete)
 for y in centers:
  part('Track263 fastening pad',(x,y,.095),(.14,.16,.018),black)
  for side in [-1,1]:part('Track263 rail clip',(x,y+side*.115,.13),(.065,.025,.025),rust)
segments=12
for i in range(segments):
 x=start+(i+.5)*(end-start)/segments;half=(end-start)/segments/2-.008
 for y in centers:
  part('Track263 rail foot',(x,y,.135),(half,.105,.018),rust)
  part('Track263 rail web',(x,y,.20),(half,.025,.05),rust)
  part('Track263 rail running head',(x,y,.265),(half,.065,.022),rail)
  for side in [-1,1]:part('Track263 joint fishplate',(x-half+.10,y+side*.035,.20),(.10,.012,.038),rail)
# Consolidate by material while retaining a few shared source meshes in the BLEND.
for mat in [rail,rust,concrete,black]:
 selected=[o for o in root.children if o.type=='MESH' and o.data.materials[0]==mat]
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();selected[0].name='Track263 '+mat.name
floor=bpy.data.materials['Original subway floor with recessed stair openings']
next(n for n in floor.node_tree.nodes if n.type=='TEX_IMAGE').image=bpy.data.images.load(str(OUT/'floor.png'))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_') or o==root)
bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
for o in bpy.context.scene.objects:o.select_set(o==root or o.parent==root)
bpy.ops.export_scene.gltf(filepath=str(OUT/'track.glb'),export_format='GLB',use_selection=True,export_apply=True)
(OUT/'track.json').write_text(json.dumps({'sleepers':count,'rails':2,'rail_segments':segments,'visual_only':True,'source_canvas_rail_y':[252,284],'anchor':'Original map coordinates; ground level','provenance':'Source-guided rigid construction; unseen rail cross section and ballast inferred','artistic_status':'NEEDS_NATIVE_REVIEW'},indent=2))
print('METRO263_TRACK_EXPORTED',count,'sleepers;2 real-profile rails')
