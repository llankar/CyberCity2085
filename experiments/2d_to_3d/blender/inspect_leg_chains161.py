import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/cover_transitions160/human.blend',use_scripts=False)
r=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
report=[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'children':[c.name for c in b.children]} for b in r.data.bones if any(s in b.name for s in ('thigh','shin','foot','toe'))]
Path('E:/CyberCity2085-3d-lab/generated/phase2/foot_contact161/leg_chains.json').write_text(json.dumps(report,indent=2));print('LEG_CHAINS161',json.dumps([(b['name'],b['parent']) for b in report]))
