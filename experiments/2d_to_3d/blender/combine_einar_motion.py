"""Bundle verified compatible source-baked studies without duplicating meshes."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'einar_motion01'; folder.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'einar_idle01/human_rig.blend'),use_scripts=False)
rig=bpy.data.objects['EinarGameRig']
idle=rig.animation_data.action
assert idle.name=='Idle'
with bpy.data.libraries.load(str(root/'einar_walk01/human_rig.blend'),link=False) as (source,target):
    assert 'Walk' in source.actions
    target.actions=['Walk']
walk=target.actions[0]
track=rig.animation_data.nla_tracks.new(); track.name='IdleStudy'
track.strips.new('Idle',1,idle)
rig.animation_data.action=walk
scene=bpy.context.scene; scene.frame_start=1; scene.frame_end=49; scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
for obj in scene.objects:
    if obj.type in {'MESH','ARMATURE'}: obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human_motion.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human_motion.glb'),export_format='GLB',
                        use_selection=True,use_active_scene=True,export_animations=True,
                        export_animation_mode='ACTIONS',export_anim_single_armature=False,
                        export_all_influences=True,export_anim_slide_to_zero=True)
(folder/'motion_report.json').write_text(json.dumps({
    'clips':['Idle','Walk'],'joints':len(rig.data.bones),
    'source_reports':['einar_idle01/rig_report.json','einar_walk01/rig_report.json'],
    'credit':'Einar Rig (CC-BY) Blender Foundation | studio.blender.org',
    'license':'https://creativecommons.org/licenses/by/4.0/',
    'limitations':['Prototype Idle/Walk only; no full action or artistic acceptance',
                    'Walk is in place; intended virtual root travel0.7m/cycle']},indent=2),encoding='utf-8')
print('EINAR_MOTION_BUNDLED',flush=True)
