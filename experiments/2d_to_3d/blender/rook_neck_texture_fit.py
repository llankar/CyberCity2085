"""Transfer real head skin UVs onto retained neck geometry; no geometry masking."""
import hashlib
import json
import shutil
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_head_fit126';out=root/'rook_neck127';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
body=bpy.data.objects['char1'];head=bpy.data.objects['MIT_HeadFitStudy']
positions=[tuple(v.co) for v in body.data.vertices]
image=next(n.image for n in body.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.name.startswith('RookBodyBaseColor'))
width,height=image.size;pixels=np.empty(width*height*4,dtype=np.float32)
image.pixels.foreach_get(pixels);pixels=pixels.reshape(height,width,4)
head.data.calc_loop_triangles()
triangles=[t for t in head.data.loop_triangles if max((head.matrix_world@head.data.vertices[i].co).z for i in t.vertices)<1.565]
points=[head.matrix_world@v.co for v in head.data.vertices]
tree=BVHTree.FromPolygons(points,[tuple(t.vertices) for t in triangles],all_triangles=True)
body.data.materials.append(head.data.materials[0]);skin_index=len(body.data.materials)-1
source_uv=head.data.uv_layers.active.data;target_uv=body.data.uv_layers.active.data
selected=[];distances=[];rejected=[]
for face in body.data.polygons:
    coords=[body.matrix_world@body.data.vertices[i].co for i in face.vertices]
    if not all(1.465<p.z<1.57 and abs(p.x)<.09 for p in coords):continue
    uv=sum((target_uv[i].uv for i in face.loop_indices),Vector((0,0)))/len(face.loop_indices)
    r,g,b=pixels[int(uv.y*height)%height,int(uv.x*width)%width,:3]
    if not(r>.3 and g>.12 and b>.07 and r>g*1.15 and b<r*.9):continue
    matches=[tree.find_nearest(position) for position in coords]
    if any(index is None or distance>=.07 for closest,normal,index,distance in matches):
        rejected.append(face.index);continue
    for loop_index,(closest,normal,index,distance) in zip(face.loop_indices,matches):
        tri=triangles[index];xyz=[points[i] for i in tri.vertices]
        uv3=[Vector((*source_uv[i].uv,0)) for i in tri.loops]
        projected=barycentric_transform(closest,*xyz,*uv3)
        target_uv[loop_index].uv=projected.xy;distances.append(distance)
    face.material_index=skin_index;selected.append(face.index)
assert selected and positions==[tuple(v.co) for v in body.data.vertices]
rig.data.pose_position='POSE'
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\nNeck127: real head photograph UV transferred to retained neck faces via nearest head-neck triangle. Geometry unchanged, no hidden cutouts; projection/transition requires artistic review.\n'
credits=bpy.data.texts.new('NECK_UV_TRANSFER');credits.write(notice);credits.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
shutil.copyfile(source/'native_reference.json',out/'native_reference.json')
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'neck_report.json').write_text(json.dumps({'assigned_faces':selected,'rejected_distant_faces':rejected,'maximum_uv_projection_distance_m':max(distances),'geometry_unchanged':True,'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'scope':'UV projection only; no neck contact or final art acceptance'},indent=2))
print('ROOK_NECK_TEXTURE_TRANSFER_EXPORTED',len(selected),max(distances),flush=True)
