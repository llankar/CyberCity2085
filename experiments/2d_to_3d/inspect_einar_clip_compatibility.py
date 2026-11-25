"""Check actual primitive/bind compatibility before attempting a shared bundle."""
import hashlib
import json
from pathlib import Path
from glb_document import Glb

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
paths=['einar_idle01','einar_walk01','einar_ual_Pistol_Shoot01_surfaces',
       'einar_ual_Punch_Cross01_surfaces','einar_ual_Death0101_surfaces']
documents=[Glb(root/name/'human_rig.glb') for name in paths]
base=documents[0]
def meshes(glb): return {m['name']:m for m in glb.doc['meshes']}
reference=meshes(base); report={}
for name,glb in zip(paths,documents):
    mismatches=[]
    for mesh_name,mesh in meshes(glb).items():
        for index,primitive in enumerate(mesh['primitives']):
            expected=reference[mesh_name]['primitives'][index]
            for key,accessor in primitive['attributes'].items():
                if key not in expected['attributes'] or glb.values(accessor)!=base.values(expected['attributes'][key]):
                    mismatches.append({'mesh':mesh_name,'primitive':index,'attribute':key,
                        'count':glb.doc['accessors'][accessor]['count'],
                        'base_count':base.doc['accessors'][expected['attributes'][key]]['count'] if key in expected['attributes'] else None})
            if glb.values(primitive['indices'])!=base.values(expected['indices']):
                mismatches.append({'mesh':mesh_name,'primitive':index,'attribute':'indices'})
    report[name]={'sha256':hashlib.sha256((root/name/'human_rig.glb').read_bytes()).hexdigest(),
                  'mismatches':mismatches,'animations':[a['name'] for a in glb.doc['animations']]}
folder=root/'einar_bundle02'; folder.mkdir(exist_ok=True)
(folder/'compatibility.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_CLIP_COMPATIBILITY',json.dumps({name:len(data['mismatches']) for name,data in report.items()}))
