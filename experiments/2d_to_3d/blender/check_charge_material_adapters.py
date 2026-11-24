"""Native preflight gate: supported source interfaces and explicit glass refusal."""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from charge_pbr import channels

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/security_geometry01')
bpy.ops.wm.open_mainfile(filepath=str(folder/'security_geometry.blend'),use_scripts=False)
used={slot.material for obj in bpy.context.scene.objects if obj.type=='MESH' for slot in obj.material_slots}
report={'supported':[],'refused':[]}
for material in sorted(used,key=lambda m:m.name):
    try:
        result=channels(material)
    except ValueError:
        report['refused'].append(material.name)
    else:
        assert set(result)=={'BaseColor','Roughness','Metallic','Alpha','Emission'}
        report['supported'].append(material.name)
assert len(used)==9
assert len(report['supported'])==8
assert report['refused']==['robot_glass']
(folder/'material_adapter_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CHARGE_ADAPTER_TEST_OK supported=8 refused_glass=1')
