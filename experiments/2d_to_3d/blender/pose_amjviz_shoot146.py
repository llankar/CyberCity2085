"""Retarget one licensed shooting pose through actual FK controls, not deform bones."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from game_materials import restore

sys.path.insert(0,str(Path(__file__).parent))
from amjviz_fk import load,solve
c=load();root=c.root;base=c.base;scene=c.scene;game=c.game;mapping=c.mapping;scale=c.scale
out=root/'generated/phase2/amjviz_combat146';out.mkdir(exist_ok=True)
action=c.clips['Pistol_Shoot'];first,last=action.frame_range;frame=(first+last)/2
transfer=solve(c,'Pistol_Shoot',frame)
notice=(base/'CREDITS.txt').read_text(encoding='utf8')+'\n'+(root/'sources/quaternius_ual_standard/License.txt').read_text(encoding='utf8')+'\n146 single FK shooting-pose diagnostic using licensed UAL Pistol_Shoot. No gun/contact or full clip accepted.\n'
bpy.data.texts.new('SHOOTING_POSE_SOURCE_LICENSES').write(notice)
for obj in scene.objects:obj.select_set(obj==game or (obj.type=='MESH' and any(m.type=='ARMATURE' and m.object==game for m in obj.modifiers)))
bpy.context.view_layer.objects.active=game
bpy.ops.wm.save_as_mainfile(filepath=str(out/'shoot_pose.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'shoot_pose_raw.glb'),export_format='GLB',use_selection=True,
                        export_animations=False,export_current_frame=True,export_rest_position_armature=False,
                        export_all_influences=True,export_copyright=notice)
compiled=Glb(out/'shoot_pose_raw.glb');material_report=restore(compiled,Glb(base/'human.glb'));compiled.save(out/'shoot_pose.glb')
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'pose_report.json').write_text(json.dumps({'source_clip':'Pistol_Shoot','source_frame':frame,'control_mapping':mapping,
    'maximum_game_bone_head_transfer_error_m':transfer,'source_pelvis_scale':scale,'material_restoration':material_report,
    'glb_sha256':hashlib.sha256((out/'shoot_pose.glb').read_bytes()).hexdigest(),
    'scope':'Single static diagnostic, not a full shooting clip or final art'},indent=2))
print('AMJVIZ_FK_SHOOT_POSE_READY',transfer,flush=True)
