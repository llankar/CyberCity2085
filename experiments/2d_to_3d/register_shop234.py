"""Register the reusable original-derived shop without duplicating source Blender files."""
from pathlib import Path
import json
root=Path('E:/CyberCity2085-3d-lab/environment-library');out=root/'assets/market_three_canopies'
model=json.loads((out/'model.json').read_text());source=json.loads((out/'source.json').read_text())
catalog=json.loads((root/'library.json').read_text(encoding='utf8'))
asset={'id':'market_three_canopies','family':'Shops','source_object_id':'market_nw','authentic_views':1,'generated_views':0,
 'anchor':'bottom_center','models':{'glb':str(out/'shop.glb'),'blender':model['blender_source']},
 'blender_source_root':model['source_root'],'isolated_reference':str(out/'sage.png'),
 'source_sha256':source['sha256'],'artistic_status':'PARTIAL_SOURCE_DERIVED_NOT_FINAL',
 'license':'Project cloth crops; inherited acquired machinery from existing showcase sources; see environment169 provenance',
 'map_associations':[{'map':'city_exterior_neon_market_alley','position':model['map_position'],'rotation':0,'scale':[1,1,1],
 'occlusion_parent':'market_nw','replaces':['*'],'tactical_effect':'cosmetic only; existing cells retained'}],
 'remaining':['Baked illumination remains','Lower counter/machinery interpreted, not source-recovered','Review native placement and occlusion']}
assets={a['id']:a for a in catalog.get('assets',[])};assets[asset['id']]=asset;catalog['assets']=list(assets.values())
record=next(r for r in catalog['records'] if r['source_object_id']=='market_nw');record['artistic_status']='PARTIAL_SOURCE_DERIVED_NOT_FINAL';record['models']=asset['models'];record['remaining']=asset['remaining']
(root/'library.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False),encoding='utf8')
print('REGISTERED',asset['id'],model['map_position'])
