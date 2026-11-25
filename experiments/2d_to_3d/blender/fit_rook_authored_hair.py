"""Reuse actual quiff mesh/UV from licensed outfit; never a primitive hair cap."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
import bmesh
import numpy as np
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent.parent))
from rook_material_regions import region
from quiff_fit import fit_point

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'rook_hair127';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_head_fit126/human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
target=bpy.data.objects['char1']
with bpy.data.libraries.load(str(root/'cyborg_actions01/human.blend'),link=False) as (available,loaded):loaded.objects=['char1']
source=loaded.objects[0]
shader=next(n for n in source.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
image=shader.inputs['Base Color'].links[0].from_node.image
width,height=image.size;pixels=np.empty(width*height*4,dtype=np.float32)
image.pixels.foreach_get(pixels);pixels=pixels.reshape(height,width,4)
selected=set()
for face in source.data.polygons:
    point=sum((target.matrix_world@source.data.vertices[i].co for i in face.vertices),Vector())/len(face.vertices)
    uv=sum((source.data.uv_layers.active.data[i].uv for i in face.loop_indices),Vector((0,0)))/len(face.loop_indices)
    color=pixels[int(uv.y*height)%height,int(uv.x*width)%width,:3]
    if region(point,color)==1:selected.add(face.index)
assert len(selected)==2077,len(selected)
data=source.data.copy();bm=bmesh.new();bm.from_mesh(data);bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index not in selected],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
for face in bm.faces:face.material_index=0
bm.to_mesh(data);bm.free();data.transform(target.matrix_world)
maximum_fit=0.
for vertex in data.vertices:
    old=vertex.co.copy();vertex.co=fit_point(old)
    maximum_fit=max(maximum_fit,(vertex.co-old).length)
data.materials.clear();data.materials.append(target.data.materials[0])
hair=bpy.data.objects.new('ActualCopperQuiff',data);scene.collection.objects.link(hair)
hair.parent=rig;hair.matrix_world=Matrix.Identity(4)
group=hair.vertex_groups.new(name='Head');group.add(list(range(len(data.vertices))),1,'REPLACE')
modifier=hair.modifiers.new('ExistingSkeleton','ARMATURE');modifier.object=rig
bpy.data.objects.remove(source,do_unlink=True)
rig.data.pose_position='POSE'
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(root/'rook_head_fit126/CREDITS.txt').read_text()+'\nHair127: original2077quiff faces from licensed CC0 cyberpunk source, existing copper material/UV, rigid Head binding. Fit and hairline require artistic inspection.\n'
credits=bpy.data.texts.new('ACTUAL_QUIFF_CREDITS');credits.write(notice);credits.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'hair_report.json').write_text(json.dumps({'source_faces':len(selected),'vertices':len(data.vertices),'maximum_fit_displacement_m':maximum_fit,'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'limitations':['Source scalp shape differs from new head','Hairline, neck seam and final Rook art not accepted']},indent=2))
print('ACTUAL_ROOK_QUIFF_EXPORTED',flush=True)
