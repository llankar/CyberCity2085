"""Register the reusable rigid pod bank, preserving all existing library work."""
import json
from pathlib import Path
from environment_library import LAB,OUT,digest

def main():
    folder=LAB/'generated/phase2/lab247'
    info=json.loads((folder/'pod_bank.json').read_text())
    path=OUT/'library.json';library=json.loads(path.read_text(encoding='utf8'))
    record=next(r for r in library['records'] if r['id']=='city_interior_research_lab__north_pods')
    asset={'id':info['id'],'family':'Laboratory','source_image':record['context_crop'],
        'source_map':info['source_map'],'source_sha256':digest(Path(record['context_crop'])),
        'models':{'blend':str(folder/'environment.blend'),'glb':str(folder/'pod_bank.glb')},
        'source_root':info['source_root'],'glb_sha256':digest(folder/'pod_bank.glb'),
        'dimensions':info['dimensions_godot'],'orientation':info['orientation'],
        'anchor':info['anchor_godot'],'footprint_cells':record['footprint_cells'],
        'textures':[],'materials':info['materials'],'variants':[],
        'provenance':info['method'],'artistic_status':info['artistic_status'],
        'map_associations':[]}
    library['assets']=[a for a in library.get('assets',[]) if a['id']!=asset['id']]+[asset]
    path.write_text(json.dumps(library,indent=2,ensure_ascii=False),encoding='utf8')
    rejected=folder/'pod_shape/artistic_review.json'
    rejected.write_text(json.dumps({'status':'REJECTED','reason':'Neutral source and optimized renders show a box-like housing, not the illustrated cylindrical pod. Texture run stopped before inference.','fallback':asset['id']},indent=2))
    print('LAB247_POD_BANK_REGISTERED',asset['dimensions'])

if __name__=='__main__':main()
