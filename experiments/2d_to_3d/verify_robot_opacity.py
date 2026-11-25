"""Verify alpha-only GLB derivative and real native five-action captures."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from compact_glb import unpack

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'security_opaque137'
report=json.loads((folder/'opacity_report.json').read_text())
paths=[root/'security_compact134/robot_actions.glb',folder/'robot_actions.glb']
raw=[p.read_bytes() for p in paths]
assert [hashlib.sha256(r).hexdigest() for r in raw]==[report['source_glb_sha256'],report['output_glb_sha256']]
before,binary=unpack(raw[0]);after,retained=unpack(raw[1]);assert binary==retained
changed=set(report['changed_materials']);assert len(changed)==122
for material in after['materials']:
    if material['name'] in changed:
        assert material['alphaMode']=='OPAQUE';material['alphaMode']='BLEND'
assert after==before
assert len(report['retained_blend_materials'])==2
proofs=[]
for clip in ('Idle','Walk','Melee','Hit','Death'):
    log_bytes=(folder/(clip+'.log')).read_bytes()
    log=log_bytes.decode('utf-16' if log_bytes.startswith(b'\xff\xfe') else 'utf-8-sig')
    assert f'CYBERCITY_IMPORTED_CLIP_SAMPLED {clip}' in log and 'CYBERCITY_CAPTURE_RESULT 0' in log
    assert 'CYBERCITY_GODOT_GLTF_OK '+paths[1].as_posix() in log
    a=root/'security_compact134'/('compact_'+clip+'.png');b=folder/(clip+'.png')
    first=np.asarray(Image.open(a).convert('RGB'));second=np.asarray(Image.open(b).convert('RGB'))
    assert first.shape==second.shape
    difference=np.abs(first.astype(int)-second.astype(int))
    proofs.append({'clip':clip,'fraction':.5,'changed_pixels':int(np.any(difference,axis=2).sum()),
                   'maximum_channel_difference':int(difference.max()),
                   'capture_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),
                   'baseline_capture_sha256':hashlib.sha256(a.read_bytes()).hexdigest()})
proof={'glb_sha256':report['output_glb_sha256'],'binary_and_non_alpha_json_exact':True,'native_samples':proofs,
       'scope':'Five actual midpoint captures; intended material change, not artistic or full-animation acceptance'}
(folder/'native_opacity_validation.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
print('SOURCE_OPACITY_NATIVE_VERIFIED',[(p['clip'],p['changed_pixels']) for p in proofs])
