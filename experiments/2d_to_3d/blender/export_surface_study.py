"""Re-export a saved surface study with its explicit single action name."""
import json
import sys
from pathlib import Path
import bpy

clip=next(arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--ual='))
assert clip and all(c.isalnum() or c=='_' for c in clip)
folder=Path('E:/CyberCity2085-3d-lab/generated/phase2')/f'einar_ual_{clip}01_surfaces'
report=json.loads((folder/'rig_report.json').read_text())
assert report['clip']==clip and report['surface_corrections']
bpy.ops.wm.open_mainfile(filepath=str(folder/'human_rig.blend'),use_scripts=False)
bpy.context.scene.name=clip
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human_rig.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human_rig.glb'),export_format='GLB',
    use_selection=True,use_active_scene=True,export_animations=True,
    export_animation_mode='SCENE',export_anim_scene_split_object=False,
    export_anim_single_armature=False,export_all_influences=True,export_anim_slide_to_zero=True)
print('SURFACE_STUDY_REEXPORTED',clip,flush=True)
