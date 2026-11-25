"""Synchronize retained skin and attached head weights in a separate study."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from head_skinning import smooth_neck_skull_weights
from reviewed_selection import face_selection

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_neck_uv128';out=root/'rook_neck_weights129';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
body=bpy.data.objects['char1'];head=bpy.data.objects['MIT_HeadFitStudy']
report=json.loads((source/'neck_report.json').read_text())
selected=face_selection({'source_glb_sha256':report['glb_sha256'],'selected':report['assigned_faces']},hashlib.sha256((source/'human.glb').read_bytes()).hexdigest(),len(body.data.polygons))
body_vertices={i for face in selected for i in body.data.polygons[face].vertices}
original={obj.name:[tuple(v.co) for v in obj.data.vertices] for obj in (body,head)}
changed={}
for obj,indices in ((body,body_vertices),(head,range(len(head.data.vertices)))):
    count=0
    for index in indices:
        v=obj.data.vertices[index];z=(obj.matrix_world@v.co).z
        factor=max(0.,min(1.,(z-1.48)/.025)) if obj==body else 1.
        if not factor:continue
        previous={g.group:g.weight for g in v.groups}
        neck,skull=smooth_neck_skull_weights(z)
        desired={obj.vertex_groups['neck'].index:neck,obj.vertex_groups['Head'].index:skull}
        for group in list(obj.vertex_groups):
            value=previous.get(group.index,0)*(1-factor)+desired.get(group.index,0)*factor
            if value:group.add([index],value,'REPLACE')
            elif group.index in previous:group.remove([index])
        assert abs(sum(g.weight for g in v.groups)-1)<1e-5
        count+=1
    changed[obj.name]=count
    assert original[obj.name]==[tuple(v.co) for v in obj.data.vertices]
rig.data.pose_position='POSE'
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\nNeck129: smooth neck/Head weights synchronized on actual retained skin and original head; lower shirt boundary blended to original weights. Geometry/UV unchanged; deformation/contact/art review required.\n'
credits=bpy.data.texts.new('NECK_WEIGHT_STUDY');credits.write(notice);credits.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'weights_report.json').write_text(json.dumps({'weighted_vertices':changed,'geometry_uv_unchanged':True,'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'scope':'Skin weights only; not neck seam/contact or artistic acceptance'},indent=2))
print('SYNCHRONIZED_NECK_WEIGHTS_EXPORTED',changed,flush=True)
