"""Reproducible local inventory of the reviewed, private AmJViZ source GLB."""
import hashlib,json
from pathlib import Path
import numpy as np
from glb_document import Glb

folder=Path('E:/CyberCity2085-3d-lab/sources/blenderkit_cyberpunk143')
metadata=json.loads((folder/'metadata.json').read_text(encoding='utf-8-sig'))
assert metadata['id']=='3faea5ca-a58d-46c5-adc3-5ed1ef39dc44'
assert metadata['isFree'] and metadata['license']=='royalty_free'
path=folder/'source_godot.glb';glb=Glb(path);doc=glb.doc
kinds={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}
used=set();rows=[];maximum_weight_error=0.
for mesh in doc['meshes']:
    for primitive in mesh['primitives']:
        attributes=primitive['attributes'];position=doc['accessors'][attributes['POSITION']]
        assert {'NORMAL','TEXCOORD_0','JOINTS_0','WEIGHTS_0'}<=set(attributes)
        total=np.zeros(position['count'])
        for suffix in ('0','1'):
            if 'JOINTS_'+suffix not in attributes:continue
            joint=doc['accessors'][attributes['JOINTS_'+suffix]]
            weight=doc['accessors'][attributes['WEIGHTS_'+suffix]]
            js=np.frombuffer(glb.values(attributes['JOINTS_'+suffix]),dtype=kinds[joint['componentType']]).reshape(-1,4)
            ws=np.frombuffer(glb.values(attributes['WEIGHTS_'+suffix]),dtype=kinds[weight['componentType']]).reshape(-1,4)
            assert weight['componentType']==5126,'Review integer normalization explicitly'
            assert np.isfinite(ws).all() and (ws>=0).all()
            assert (js<len(doc['skins'][0]['joints'])).all()
            total+=ws.sum(axis=1);used.update(int(i) for i in js[ws>0])
        maximum_weight_error=max(maximum_weight_error,float(abs(total-1).max()))
        rows.append({'vertices':position['count'],'min':position.get('min'),'max':position.get('max')})
assert maximum_weight_error<1e-5
report={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,
        'source_joint_count':len(doc['skins'][0]['joints']),'weighted_joint_count':len(used),
        'vertices_across_primitives':sum(row['vertices'] for row in rows),'primitives':rows,
        'maximum_weight_sum_error':maximum_weight_error,
        'clips':[a.get('name') for a in doc.get('animations',[])],
        'images':len(doc.get('images',[])),'materials':len(doc.get('materials',[])),
        'scope':'Source inventory and numeric skin validity only; not artistic/animation acceptance'}
(folder/'verified_inventory.json').write_text(json.dumps(report,indent=2))
notice='''CyberPunk Rigged character — AmJViZ (Amir Jafari)
Asset base: ebd01e7e-ebd8-4c74-88f0-6c0e3ccc0806
Asset version: 3faea5ca-a58d-46c5-adc3-5ed1ef39dc44
https://www.blendkit.com/asset-gallery-detail/ebd01e7e-ebd8-4c74-88f0-6c0e3ccc0806/
License: Blendkit Royalty Free. NOT CC0, NOT a freely redistributable asset pack.
https://www.blendkit.com/docs/licenses/
https://www.blendkit.com/docs/licenses/licensing-faq/
Commercial higher-level derivative works and games allowed; game assets must not
be directly/easily extractable in distribution. Raw 3D resale is prohibited.
Private experimental files only. Do not push source BLEND/GLB/textures or publish
a downloadable raw scene. Sprite-render distribution is a separate allowed route.
Retrieved 2026-11-25 via public API, free asset download with scene_uuid parameter.
Initial 403 stated missing scene_uuid; no authentication bypass or token used.
Original author attribution retained voluntarily. No current final Rook adoption,
no claim that source costume/markings are final CyberCity identity.
'''
(folder/'CREDITS.txt').write_text(notice,encoding='utf8')
print('AMJVIZ_SOURCE_INVENTORY_OK',json.dumps({k:v for k,v in report.items() if k!='primitives'}))
