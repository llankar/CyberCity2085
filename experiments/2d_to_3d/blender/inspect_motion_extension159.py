import bpy,json
from pathlib import Path
p=Path('E:/CyberCity2085-3d-lab/sources/quaternius_ual_standard/animation_library.blend')
with bpy.data.libraries.load(str(p),link=False) as (data,_):names=list(data.actions)
out=Path('E:/CyberCity2085-3d-lab/generated/phase2/motion_extension159');out.mkdir(exist_ok=True)
(out/'source_actions.json').write_text(json.dumps(names,indent=2));print('UAL159_AVAILABLE',json.dumps(names))
