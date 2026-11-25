"""Fit real licensed hair cards to the existing intact head; no primitive hairstyle."""
import bpy,sys,hashlib,json
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from game_materials import restore
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=root/'hair_cards157';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'face_review156/human_face035.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST';bpy.context.view_layer.update()
body=max((o for o in scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
protected=hashlib.sha256(repr([(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in body.data.vertices]).encode()).hexdigest()
old=bpy.data.objects.get('ActualCopperQuiff148');assert old and len(old.data.polygons)==1702
bpy.data.objects.remove(old,do_unlink=True)
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath='E:/CyberCity2085-3d-lab/sources/blenderkit_hair157/source_godot.glb')
bpy.context.view_layer.update();meshes=[o for o in scene.objects if o not in before and o.type=='MESH'];assert len(meshes)==2
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=Vector([min(p[k] for p in points) for k in range(3)]);hi=Vector([max(p[k] for p in points) for k in range(3)])
# Explicit first fitting bounds, NOT a claimed final scalp/contact acceptance.
target_lo=Vector((-.098,-.065,1.692));target_hi=Vector((.098,.135,1.838))
for index,obj in enumerate(meshes):
 world=obj.matrix_world.copy();obj.data=obj.data.copy()
 for v in obj.data.vertices:
  p=world@v.co
  v.co=rig.matrix_world.inverted()@Vector([target_lo[k]+(p[k]-lo[k])/(hi[k]-lo[k])*(target_hi[k]-target_lo[k]) for k in range(3)])
 obj.parent=rig;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4);obj.name='AuthoredHairCards157_'+str(index)
 for group in list(obj.vertex_groups):obj.vertex_groups.remove(group)
 obj.vertex_groups.new(name='DEF-spine.006').add(list(range(len(obj.data.vertices))),1.,'REPLACE')
 obj.modifiers.new('ExistingHeadRig','ARMATURE').object=rig
 for mat in obj.data.materials:mat.name='LicensedHairCards157_'+str(index)
assert protected==hashlib.sha256(repr([(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in body.data.vertices]).encode()).hexdigest()
rig.data.pose_position='POSE'
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Hard stand'
rig.animation_data.action=None;scene.frame_set(0);bpy.context.view_layer.update()
notice=(root/'face_review156/CREDITS.txt').read_text()+'\nHair cards: Salman Ramezani, Short hair card, Blendkit4793aff4-5e46-4902-a329-314731ebde09 version0a91297d-d3c1-43a6-9d38-d1f00c352f00, Royalty Free NOT CC0; private derivative only, no raw redistribution. Actual author meshes/UV/alpha retained, bounding fit and head weights changed. First fit NOT final Rook.\n'
(out/'CREDITS.txt').write_text(notice);bpy.data.texts.new('HAIR157_SOURCE_AND_CHANGES').write(notice)
for obj in scene.objects:obj.select_set(obj==rig or obj.type=='MESH')
bpy.context.view_layer.objects.active=rig;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_raw.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,export_rest_position_armature=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_optimize_animation_keep_anim_object=True,export_all_influences=True)
glb=Glb(out/'human_raw.glb');restore(glb,Glb(root/'face_review156/human_face035.glb'));glb.save(out/'human.glb')
(out/'fit.json').write_text(json.dumps({'protected_body_vertices_weights_sha256':protected,'body_vertex_weights_exact':True,'removed_quiff_faces':1702,'hair_meshes':len(meshes),'source_bounds':[list(lo),list(hi)],'target_bounds':[list(target_lo),list(target_hi)],'scope':'First real authored hair-card fit, silhouette/contact/animation/art not accepted'},indent=2))
print('AUTHORED_HAIR157_FIT_EXPORTED')
