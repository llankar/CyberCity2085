"""Prepare one genuine alternative prop in the already calibrated weapon space."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from game_materials import restore

root=Path('E:/CyberCity2085-3d-lab');generated=root/'generated/phase2';out=generated/'amjviz_modules153';out.mkdir(exist_ok=True)
hero=generated/'amjviz_wardrobe150';source=root/'sources/blenderkit_p320153'
bpy.ops.wm.open_mainfile(filepath=str(hero/'human_actions.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=track.name!='ShootStudy'
rig.animation_data.action=None;bpy.context.scene.frame_set(38);bpy.context.view_layer.update()
relative=Matrix(json.loads((generated/'amjviz_actions146/weapon_fit_pad.json').read_text())['relative_matrix'])
placement=rig.matrix_world@rig.pose.bones['DEF-hand.R'].matrix@relative
yup=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
placement_yup=yup@placement@yup.inverted()

bpy.ops.wm.open_mainfile(filepath=str(source/'source.blend'),use_scripts=False)
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
audit=json.loads((generated/'amjviz_components153/p320_component_audit.json').read_text())
assert audit['source_blend_sha256']==hashlib.sha256((source/'source.blend').read_bytes()).hexdigest()
trigger_component=next(c for c in audit['components'] if c['first_face']==1390)
assert trigger_component['face_count']==84
ids={i for face in trigger_component['faces'] for i in obj.data.polygons[face].vertices}
trigger_center=sum((obj.matrix_world@obj.data.vertices[i].co for i in ids),Vector())/len(ids)
with bpy.data.libraries.load(str(generated/'firewarden_pistol01/pistol.blend'),link=False) as (_,data):data.objects=['trigger']
old_trigger=data.objects[0]
bpy.context.scene.collection.objects.link(old_trigger);bpy.context.view_layer.update()
old_center=old_trigger.matrix_world@(sum((v.co for v in old_trigger.data.vertices),Vector())/len(old_trigger.data.vertices))
assert old_center.z>.05,'Reference trigger transform was not evaluated'
bpy.data.objects.remove(old_trigger,do_unlink=True)
# Source lies in XY: +Y muzzle, +X top, +Z thickness. Rotate into existing
# canonical pistol space(+X thickness, -Y muzzle, +Z top), then uniform scale.
normalization=Matrix(((0,0,.8,0),(0,-.8,0,0),(.8,0,0,0),(0,0,0,1)))
normalization.translation=old_center-normalization@trigger_center
obj.data=obj.data.copy();obj.data.transform(normalization@obj.matrix_world)
obj.parent=None;obj.matrix_world=Matrix.Identity(4);obj.name='P320_Module'
for o in bpy.context.scene.objects:o.select_set(o==obj)
bpy.context.view_layer.objects.active=obj
notice=(source/'CREDITS.txt').read_text(encoding='utf-8-sig')+'\n153 derivative: uniform.8scale/axis normalization and trigger-component centroid alignment to the existing canonical prop. No human meshes modified. Trigger identification and contact fit require visual/native inspection.\n'
bpy.data.texts.new('PRIVATE_PROP_SOURCE_LICENSE').write(notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'p320.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'p320_raw.glb'),export_format='GLB',use_selection=True,export_animations=False,export_copyright=notice)
compiled=Glb(out/'p320_raw.glb');restore(compiled,Glb(source/'source_godot.glb'));compiled.save(out/'p320.glb')
credits=notice+'\nBaseline FireWarden Lowpoly Pistol: CC0, https://opengameart.org/content/lowpoly-pistol . Existing calibrated prop preserved.\n'
(out/'CREDITS.txt').write_text(credits)
variants={
    'firewarden':{'file':str(generated/'firewarden_pistol01/pistol.glb'),'game_item_id':'shock_pistol','mapping_status':'Approximate sidearm mesh study, not canonical production art'},
    'p320':{'file':str(out/'p320.glb'),'game_item_id':None,'mapping_status':'Unassigned licensed alternative prop; no invented game item'}}
for variant in variants.values():variant['sha256']=hashlib.sha256(Path(variant['file']).read_bytes()).hexdigest()
report={'bone':'DEF-hand.R','reference_clip':'ShootStudy','reference_time_s':38/120,
    'body_glb_sha256':hashlib.sha256((hero/'human_actions.glb').read_bytes()).hexdigest(),
    'world_placement_yup':[list(row) for row in placement_yup],
    'p320_source_normalization':[list(row) for row in normalization],
    'p320_trigger_component_first_face':1390,'variants':variants,
    'reference_trigger_canonical':list(old_center),'p320_trigger_source_centroid':list(trigger_center),
    'scope':'Constant bone-socket prop swap; body/rig/animations unchanged. Hand/contact/native equivalence checks pending.'}
(out/'modules.json').write_text(json.dumps(report,indent=2))
print('REAL_WEAPON_MODULES_PREPARED',flush=True)
