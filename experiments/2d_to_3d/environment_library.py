"""Reuse the showcase's existing art survey; keep all generated library data on E:."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
LAB=Path('E:/CyberCity2085-3d-lab')
OUT=LAB/'environment-library'
MAP='city_exterior_neon_market_alley'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def initialize():
    traces=ROOT/'assets/maps'/f'{MAP}.wall-traces.json'
    walls_path=ROOT/'assets/maps'/f'{MAP}.walls.json'
    walls=json.loads(walls_path.read_text())
    survey=json.loads(traces.read_text())
    source=LAB/'sources/tactical_map'/f'{MAP}.png'
    source_hash=digest(source)
    if source_hash!=walls['image_sha256']:
        raise ValueError('Source image differs from the surveyed production original')
    OUT.mkdir(exist_ok=True)
    crops=OUT/'references';crops.mkdir(exist_ok=True)
    cells={w['id']:w for w in walls['walls']}
    records=[]
    with Image.open(source) as image:
        width,height=image.size
        sx=width/survey['canvas_size'][0];sy=height/survey['canvas_size'][1]
        for item in survey['walls']:
            identifier=item['id'];wall=cells[identifier]
            rect=item['rect'];bounds=[round(rect[0]*sx),round(rect[1]*sy),round(rect[2]*sx),round(rect[3]*sy)]
            target=crops/f'{MAP}__{identifier}.png'
            if not target.exists():image.crop(bounds).save(target)
            occupied=wall['cells'];xs=[c[0] for c in occupied];ys=[c[1] for c in occupied]
            category='Buildings' if 'building' in identifier else 'Shops' if any(s in identifier for s in ['market','stall','awning']) else 'Street Furniture'
            record={'id':f'{MAP}__{identifier}','family':category,'source_map':MAP,
                'source_image':str(source),'source_sha256':source_hash,'survey_file':str(traces),
                'source_object_id':identifier,'context_crop':str(target),'crop_pixels':bounds,
                'isolated_reference':None,'reference_status':'CONTEXT_CROP_NOT_SEGMENTED',
                'authentic_views':1,'generated_views':0,'tactical_kind':wall['kind'],
                'blocks_sight':wall['blocks_sight'],'footprint_cells':occupied,
                'estimated_dimensions_cells':[max(xs)-min(xs)+1,max(ys)-min(ys)+1],
                'placement':{'position':[(min(xs)+max(xs))/2+.5-walls["grid"][0]/2,0,(min(ys)+max(ys))/2+.5-walls["grid"][1]/2],
                             'rotation':None,'scale':None,'anchor':'footprint_center_ground','occlusion':'building_cutaway' if category=='Buildings' else 'prop'},
                'models':{},'materials':[],'license':'Project original; no new third-party model',
                'artistic_status':'NOT_RECONSTRUCTED','remaining':['Isolate source object','Review reference','Select existing mesh or generation method']}
            records.append(record)
    manifest={'schema_version':1,'name':'CYBERCITY 2085 — ENVIRONMENT ASSET LIBRARY',
              'scope':'One showcase map; source survey reused without tactical changes',
              'source_walls_sha256':digest(walls_path),'records':records}
    target=OUT/'library.json'
    if target.exists():
        old=json.loads(target.read_text(encoding='utf8'))
        manifest['assets']=old.get('assets',[])
        existing={r['id']:r for r in old['records']}
        # Preserve later reconstruction/segmentation decisions on repeated import.
        manifest['records']=[existing.get(r['id'],r) for r in records]
    target.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
    cards=[]
    for r in manifest['records']:
        relative=Path(r['context_crop']).relative_to(OUT).as_posix()
        cards.append(f'<article><h2>{html.escape(r["source_object_id"])}</h2><img src="{relative}"><p>{r["family"]} · context crop, not isolated · one authentic view</p></article>')
    for asset in manifest.get('assets',[]):
        links=[]
        for kind,path in asset.get('models',{}).items():
            relative=os.path.relpath(OUT/Path(path),OUT).replace('\\','/')
            links.append(f'<a href="{html.escape(relative)}">{html.escape(kind)}</a>')
        preview=asset.get('isolated_reference') or asset.get('source_image')
        picture=''
        if preview:
            relative=os.path.relpath(OUT/Path(preview),OUT).replace('\\','/')
            picture=f'<img src="{html.escape(relative)}">'
        cards.append(f'<article><h2>{html.escape(asset["id"])}</h2>{picture}<p>{html.escape(asset.get("artistic_status","NOT_VERIFIED"))} ? '+ ' / '.join(links)+'</p></article>')
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>CyberCity Environment Library</title><style>body{background:#08141b;color:#d8edef;font:16px system-ui;margin:30px}main{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}img{max-width:100%;max-height:320px}article{border:1px solid #24636b;padding:15px}</style><h1>CyberCity 2085 — original map references</h1><p>Existing survey reused. Crops include surrounding image content; segmentation and reconstruction remain open.</p><main>'+''.join(cards)+'</main>',encoding='utf8')
    assert digest(source)==source_hash
    print('LIBRARY_IMPORTED',len(records),target)

def register_selected():
    path=OUT/'library.json'
    data=json.loads(path.read_text(encoding='utf8'))
    assets={r['id']:r for r in data.get('assets',[])}
    candidates=[('cargo_crate','Cover','crate.png','crate_procedural/crate_procedural','Project procedural mesh; source reference provenance retained'),
                ('industrial_generator','Industrial','industrial_machine.png','generator01/generator','Project procedural mesh; source reference provenance retained'),
                ('stealth_vtol','Vehicles','vtol220/reference.png','vtol222/vtol_actions','Prior Hunyuan experiment: territorial permission unresolved; no production integration')]
    for identifier,family,reference,model,license_note in candidates:
        base=LAB/'generated/phase2'/model
        paths={'blend':str(base.with_suffix('.blend')),'glb':str(base.with_suffix('.glb'))}
        if not all(Path(p).is_file() for p in paths.values()):raise FileNotFoundError(paths)
        source=LAB/'sources'/reference
        assets.setdefault(identifier,{'id':identifier,'family':family,'source_image':str(source),
            'source_sha256':digest(source),'models':paths,'glb_sha256':digest(Path(paths['glb'])),
            'dimensions':None,'anchor':'NATIVE_NOT_YET_CALIBRATED','orientation':None,
            'authentic_views':1,'reference_status':'EXISTING_SOURCE_REFERENCE',
            'artistic_status':'EXISTING_EXPERIMENT_NOT_FINAL','license':license_note,
            'map_associations':[]})
    data['assets']=list(assets.values())
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
    print('EXISTING_ASSETS_INDEXED',len(assets),'No mesh copied or regenerated')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--init',action='store_true');parser.add_argument('--find')
    parser.add_argument('--register-selected',action='store_true')
    args=parser.parse_args()
    if args.init:initialize()
    if args.register_selected:register_selected()
    if args.find:
        data=json.loads((OUT/'library.json').read_text(encoding='utf8'))
        records=data['records']+data.get('assets',[])
        found=[{k:r[k] for k in ['id','family','reference_status','models','artistic_status']} for r in records if args.find.lower() in (r['id']+' '+r['family']).lower()]
        print(json.dumps(found,indent=2))

if __name__=='__main__':main()
