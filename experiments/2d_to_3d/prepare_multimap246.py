"""Prepare six-map production queue from original art; never change tactical data."""
import json
from pathlib import Path
from environment_library import ROOT, LAB, OUT, digest, initialize

SELECTION = [
 ('city_exterior_neon_market_alley','showcase','Existing reconstructed reference; preserve its assets and encounter.'),
 ('city_district_apartment_block','residential','Dense rooftops, residential entrances and narrow inter-building streets.'),
 ('city_interior_research_lab','laboratory','Clinical partitions, scientific pods and central laboratory workstations.'),
 ('city_industrial_factory_floor','industrial','Heavy machinery, production aisles and industrial service equipment.'),
 ('city_transit_subway_platform','metro','Parallel railway tracks, platforms and constrained underground routes.'),
 ('wasteland_outdoor_02_ashfield_ruins','wasteland','Open ash terrain, ruined structures and irregular rubble cover.'),
]

def main():
    maps=ROOT/'assets/maps'
    inventory=[]
    for source in sorted(maps.glob('*.png')):
        walls=source.with_suffix('.walls.json');survey=source.with_suffix('.wall-traces.json')
        inventory.append({'id':source.stem,'image':str(source),'walls':walls.is_file(),'survey':survey.is_file()})
    for name,_,_ in SELECTION[1:]:initialize(name)
    library=json.loads((OUT/'library.json').read_text(encoding='utf8'))
    assets=library.get('assets',[])
    selected=[]
    for name,family,reason in SELECTION:
        source=maps/(name+'.png');walls=maps/(name+'.walls.json');survey=maps/(name+'.wall-traces.json')
        tactical=json.loads(walls.read_text(encoding='utf8'))
        records=[r for r in library['records'] if r['source_map']==name]
        associated={a['occlusion_parent']:asset['id'] for asset in assets for a in asset.get('map_associations',[]) if a['map']==name}
        missing=[{'id':r['source_object_id'],'reference':r['context_crop'],
                  'footprint':r['footprint_cells'],'position':r['placement']['position'],
                  'reason':'Needs visual asset match or new reconstruction; context crop is not segmented'}
                 for r in records if r['source_object_id'] not in associated]
        selected.append({'id':name,'family':family,'reason':reason,'source_image':str(source),
            'source_sha256':digest(source),'walls_sha256':digest(walls),'survey_sha256':digest(survey),
            'grid':tactical['grid'],'survey_objects':len(records),'explicit_library_matches':associated,
            'unmatched_survey_objects':missing,'artistic_status':'EXISTING_SHOWCASE_IN_PROGRESS' if family=='showcase' else 'NOT_RECONSTRUCTED',
            'metrics':{'conversion_seconds':None,'art_correction_seconds':None,'memory_mb':None,'live_fps':None},
            'tactical_mutation':False})
    output=LAB/'generated/phase2/multimap246';output.mkdir(parents=True,exist_ok=True)
    (output/'production_queue.json').write_text(json.dumps({'inventory':inventory,'selected':selected,
        'scope':'Six experimental environments only; no automatic artistic approval',
        'reuse_candidates':[{'id':a['id'],'family':a.get('family'),'models':a.get('models',{})} for a in assets]},indent=2),encoding='utf8')
    print('MULTIMAP_QUEUE',len(inventory),'images;',len(selected),'selected;',sum(x['survey_objects'] for x in selected[1:]),'new-map survey objects')

if __name__=='__main__':main()
