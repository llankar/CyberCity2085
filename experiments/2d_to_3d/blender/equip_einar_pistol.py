"""Attach the licensed fictional prop to the actual game wrist skin joint.

Placement is a reviewable fitting hypothesis, never automatic grip acceptance.
"""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
surfaces='--surface-corrections' in sys.argv
folder=root/('einar_pistol_fit01_surfaces' if surfaces else 'einar_pistol_fit01'); folder.mkdir(parents=True,exist_ok=True)
character=root/('einar_ual_Pistol_Shoot01_surfaces' if surfaces else 'einar_ual_Pistol_Shoot01')
report=json.loads((character/'rig_report.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(character/'human_rig.blend'),use_scripts=False)
scene=bpy.context.scene; rig=bpy.data.objects['EinarGameRig']
existing=[obj for obj in scene.objects if obj.type=='MESH']
wrist_name=next(b['joint'] for b in report['joints_map'] if b['source']==['RIG-einar','DEF-Wrist.R'])
thumb_name=next(b['joint'] for b in report['joints_map'] if b['source']==['RIG-einar','DEF-Finger_Thumb1.R'])
wrist=rig.data.bones[wrist_name].matrix_local
thumb=rig.data.bones[thumb_name].head_local
forward=(wrist.to_3x3() @ Vector((0,1,0))).normalized()
up=thumb-wrist.translation; up=(up-forward*up.dot(forward)).normalized()
right=(-forward).cross(up).normalized(); up=right.cross(-forward).normalized()
rotation=Matrix((right,-forward,up)).transposed().to_4x4()
anchor=Vector((0,-.012,.052))
grip=wrist.translation+forward*.065
placement=Matrix.Translation(grip) @ rotation @ Matrix.Translation(-anchor)
source_blend=root/'firewarden_pistol01/pistol.blend'
with bpy.data.libraries.load(str(source_blend),link=False) as (available,loaded):
    loaded.objects=[name for name in available.objects if name in {'Pistol','trigger','barrel','hammer','magazine (loaded)','9mm.001','9mm','slide','night sights'}]
originals=list(loaded.objects)
for obj in originals: scene.collection.objects.link(obj)
bpy.context.view_layer.update(); graph=bpy.context.evaluated_depsgraph_get()
equipped=[]
for original in originals:
    mesh=bpy.data.meshes.new_from_object(original.evaluated_get(graph),preserve_all_data_layers=True,depsgraph=graph)
    mesh.transform(placement @ original.matrix_world)
    obj=bpy.data.objects.new('EquippedPistol_'+original.name,mesh)
    scene.collection.objects.link(obj); obj.parent=rig
    group=obj.vertex_groups.new(name=wrist_name); group.add(list(range(len(mesh.vertices))),1,'REPLACE')
    modifier=obj.modifiers.new('WristAttachment','ARMATURE'); modifier.object=rig
    equipped.append(obj)
for original in originals: scene.collection.objects.unlink(original)
bpy.ops.object.select_all(action='DESELECT')
for obj in [*existing,*equipped,rig]: obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human_pistol.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human_pistol.glb'),export_format='GLB',
                        use_selection=True,use_active_scene=True,export_animations=True,
                        export_animation_mode='SCENE' if surfaces else 'ACTIONS',export_anim_scene_split_object=False,
                        export_anim_single_armature=False,
                        export_all_influences=True,export_anim_slide_to_zero=True)
metadata={'character_meshes':len(existing),'weapon_parts':len(equipped),'joint':wrist_name,
          'rest_grip_world':list(grip),'weapon_source_grip_anchor':list(anchor),
          'weapon_forward_rest':list(forward),'weapon_up_rest':list(up),
          'sources':[{'author':'Blender Foundation','asset':'Einar','license':'CC BY4.0'},
                     {'author':'Quaternius','asset':'Universal Animation Library Standard','license':'CC0'},
                     {'author':'FireWarden','asset':'Lowpoly Pistol','license':'CC0',
                      'url':'https://opengameart.org/content/lowpoly-pistol'}],
          'limitations':['Primary grip hypothesis needs visual/contact review',
                         'Oversized mechanical support hand still needs adaptation',
                         'Low-poly prop/materials are not final artistic acceptance']}
(folder/'fit_report.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
print('EINAR_PISTOL_ATTACHMENT_EXPORTED',len(equipped),flush=True)
