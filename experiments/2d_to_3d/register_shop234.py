"""Register the reusable original-derived shop without duplicating source Blender files."""
from pathlib import Path
import json,argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--asset',choices=['market_three_canopies','market_southeast_display'],default='market_three_canopies')
args=parser.parse_args()
root=Path('E:/CyberCity2085-3d-lab/environment-library');out=root/'assets'/args.asset
model=json.loads((out/'model.json').read_text());source=json.loads((out/'source.json').read_text())
catalog=json.loads((root/'library.json').read_text(encoding='utf8'))
parent=model['source_object']
assert parent in {r['source_object_id'] for r in catalog['records']}
preview=next(iter(source['original_rgb_crops']))+'.png'
asset={'id':args.asset,'family':'Shops','source_object_id':parent,'authentic_views':1,'generated_views':0,
 'anchor':'bottom_center','models':{'glb':str(out/'shop.glb'),'blender':model['blender_source']},
 'blender_source_root':model['source_root'],'isolated_reference':str(out/preview),
 'source_sha256':source['sha256'],'artistic_status':'PARTIAL_SOURCE_DERIVED_NOT_FINAL',
 'license':'Project cloth crops; inherited acquired machinery from existing showcase sources; see environment169 provenance',
 'map_associations':[{'map':'city_exterior_neon_market_alley','position':model['map_position'],'rotation':0,'scale':[1,1,1],
 'occlusion_parent':parent,'replaces':['*'],'tactical_effect':'cosmetic only; existing cells retained'}],
 'remaining':['Baked illumination remains','Lower counter/machinery interpreted, not source-recovered','Review native placement and occlusion']}
assets={a['id']:a for a in catalog.get('assets',[])};assets[asset['id']]=asset;catalog['assets']=list(assets.values())
record=next(r for r in catalog['records'] if r['source_object_id']==parent);record['artistic_status']='PARTIAL_SOURCE_DERIVED_NOT_FINAL';record['models']=asset['models'];record['remaining']=asset['remaining']
(root/'library.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False),encoding='utf8')
print('REGISTERED',asset['id'],model['map_position'])
