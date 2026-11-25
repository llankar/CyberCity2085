"""Read-only rig/animation/export prerequisites for the complete authored human."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab');folder=root/'generated/phase2/amjviz_runtime144';folder.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'sources/blenderkit_cyberpunk143/source.blend'),use_scripts=False)
rig=bpy.data.objects['rig'];body=bpy.data.objects['Character']
strips=[{'track':t.name,'action':s.action.name,'start':s.frame_start,'end':s.frame_end,
         'action_start':s.action_frame_start,'action_end':s.action_frame_end,'scale':s.scale,
         'repeat':s.repeat,'influence':s.influence,'blend':s.blend_type,'muted':t.mute}
        for t in rig.animation_data.nla_tracks for s in t.strips]
report={'fps':bpy.context.scene.render.fps,'fps_base':bpy.context.scene.render.fps_base,
        'strips':strips,'active_action':rig.animation_data.action.name if rig.animation_data.action else None,
        'modifiers':[{'name':m.name,'type':m.type,'enabled':m.show_viewport,'render':m.show_render,
                      'target':m.object.name if m.type=='ARMATURE' and m.object else None,
                      'preserve_volume':m.use_deform_preserve_volume if m.type=='ARMATURE' else None} for m in body.modifiers],
        'shape_keys':[k.name for k in body.data.shape_keys.key_blocks] if body.data.shape_keys else [],
        'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'deform':b.use_deform,
                  'bbone_segments':b.bbone_segments,'inherit_scale':b.inherit_scale,
                  'head_world':list(rig.matrix_world@b.head_local),'tail_world':list(rig.matrix_world@b.tail_local)} for b in rig.data.bones],
        'maximum_weight_influences':max(sum(g.weight>0 for g in v.groups) for v in body.data.vertices)}
(folder/'source_rig_audit.json').write_text(json.dumps(report,indent=2))
print('AMJVIZ_RIG_AUDIT',json.dumps({k:v for k,v in report.items() if k!='bones'}),flush=True)
