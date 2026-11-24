"""Verify that derived robot clips share scale, anchor and facing metadata."""
import json
from pathlib import Path

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
baseline=None
for action in ['Idle','Walk','Shoot','HitRecieve_1','Death']:
    path=root/f'robot_unified_{action}'/f'robot_{action.lower()}_atlas.json'
    data=json.loads(path.read_text())
    assert data['facing_to_orbit_view']==[4,5,6,7,0,1,2,3]
    assert data['animations'][action.lower()]['loop']==(action in ['Idle','Walk'])
    for anchor in data['anchors_by_orbit_view']:
        assert max(abs(a-b) for a,b in zip(anchor,data['anchor_uv']))<1e-6
    values=[*data['anchor_uv'],data['reference_height_uv'],data['orthographic_scale'],*data['camera_target']]
    if baseline is None:
        baseline=values
    assert max(abs(a-b) for a,b in zip(values,baseline))<1e-6,action
report={'clips':5,'shared_anchor_uv':baseline[:2], 'reference_height_uv':baseline[2],
        'scale_and_anchor_tolerance':1e-6,'projected_facing_mapping':[4,5,6,7,0,1,2,3],
        'visual_facing_acceptance':'NOT VERIFIED'}
(root/'robot_unified_alignment.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ROBOT_CLIP_ALIGNMENT_VERIFIED',json.dumps(report))
