"""Apply missing base-location channels without repeating the expensive FK bake."""
import json,sys
from pathlib import Path
import bpy
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).parent))
from amjviz_fk import stabilize_original_locations

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/amjviz_actions146')
report=json.loads((folder/'bake_report.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(folder/'animated_unarmed.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
actions={s.action.name:s.action for t in rig.animation_data.nla_tracks for s in t.strips if s.action.name in report['preserved_source_action_names']}
added=stabilize_original_locations(rig,actions,Matrix(report['base_game_world']))
rig.animation_data.action=None;rig.matrix_world=Matrix(report['base_game_world'])
for track in rig.animation_data.nla_tracks:track.mute=track.name!='T_pose'
bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'animated_unarmed.blend'))
report['added_source_base_location_tracks']=sorted(set(report.get('added_source_base_location_tracks',[]))|set(added))
(folder/'bake_report.json').write_text(json.dumps(report,indent=2))
print('AMJVIZ_SOURCE_BASE_LOCATIONS_STABILIZED',added,flush=True)
