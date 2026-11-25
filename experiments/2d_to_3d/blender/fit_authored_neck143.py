"""Diagnostic integration of genuine CC0 Diesel anatomical neck geometry."""
import json,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from garment_alignment import axial_segment_transform
from neck_boundary_fit import neck_weights

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=root/'rook_anatomy143';out.mkdir(exist_ok=True)
src=root/'diesel_candidate01/human.blend'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST';bpy.context.view_layer.update()
body=bpy.data.objects['retopo_body.002'];points=[body.matrix_world@v.co for v in body.data.vertices]
head_weights=[sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.removeprefix('mixamorig:')=='Head') for v in body.data.vertices]
old={b.name.removeprefix('mixamorig:'):rig.matrix_world@b.head_local for b in rig.data.bones}
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_diesel_replacement141/human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST';bpy.context.view_layer.update()
target={b.name:rig.matrix_world@b.head_local for b in rig.data.bones}
radial=(target['LeftArm']-target['RightArm']).length/(old['LeftArm']-old['RightArm']).length
mapping=Matrix(axial_segment_transform(old['Neck'],old['Head'],target['neck'],target['Head'],radial))
with bpy.data.libraries.load(str(src),link=False) as (available,loaded):loaded.objects=['retopo_body.002']
patch=loaded.objects[0];scene.collection.objects.link(patch);patch.parent=None;patch.matrix_world=Matrix.Identity(4)
for modifier in list(patch.modifiers):patch.modifiers.remove(modifier)
for group in list(patch.vertex_groups):patch.vertex_groups.remove(group)
for v,p in zip(patch.data.vertices,points):v.co=mapping@p
bm=bmesh.new();bm.from_mesh(patch.data)
bm.verts.ensure_lookup_table()
remove=[f for f in bm.faces if not all(1.425<v.co.z<1.56 and abs(v.co.x)<.085 and head_weights[v.index]<.25 for v in f.verts)]
bmesh.ops.delete(bm,geom=remove,context='FACES')
unused=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=unused,context='VERTS')
bm.to_mesh(patch.data);bm.free();assert len(patch.data.polygons)>20
patch.name='AuthoredAnatomicalNeckStudy'
for v in patch.data.vertices:
    for name,weight in neck_weights(v.co.z).items():
        if weight>0:
            group=patch.vertex_groups.get(name) or patch.vertex_groups.new(name=name);group.add([v.index],weight,'REPLACE')
patch.parent=rig;patch.matrix_world=Matrix.Identity(4)
mod=patch.modifiers.new('ExistingSkeleton','ARMATURE');mod.object=rig
rig.data.pose_position='POSE'
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update();helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(root/'rook_diesel_replacement141/CREDITS.txt').read_text(encoding='utf8')+'\n143 diagnostic: real CC0 Diesel retopo_body neck excerpt, original source UV/material, existing skeleton. Separate patch, seams/art not accepted.\n'
bpy.data.texts.new('ANATOMICAL143_CREDITS').write(notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,
    export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_all_influences=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,
    export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'patch_report.json').write_text(json.dumps({'vertices':len(patch.data.vertices),'faces':len(patch.data.polygons),
    'source_neck':list(old['Neck']),'source_head':list(old['Head']),
    'target_neck':list(target['neck']),'target_head':list(target['Head']),
    'status':'Diagnostic; no seam, art or animation acceptance'},indent=2))
print('AUTHORED_NECK143_EXPORTED',len(patch.data.polygons),flush=True)
