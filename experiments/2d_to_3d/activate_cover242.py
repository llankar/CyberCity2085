"""Activate the source-derived cover association; bounds checked by the native loader."""
from pathlib import Path
import json
root=Path('E:/CyberCity2085-3d-lab/environment-library');p=root/'assets/east_blue_cover/source.json';asset=json.loads(p.read_text())
asset['map_associations']=[{'map':'city_exterior_neon_market_alley','position':asset['map_anchor'],'rotation':0,'scale':[1,1,1],'occlusion_parent':'east_building','replaces':['East241 blue covering*','East241 cover tension post*','East241 cover edge rail*'],'match_replaced_bounds':True}]
asset['artistic_status']='PARTIAL_SOURCE_DERIVED_STANDALONE_PLACEMENT_REVIEW_PENDING'
asset['remaining']=['Baked source highlights remain','Review native replacement after activation/regeneration']
p.write_text(json.dumps(asset,indent=2))
catalog=root/'library.json';data=json.loads(catalog.read_text(encoding='utf8'));data['assets']=[asset if a['id']==asset['id'] else a for a in data['assets']];catalog.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
print('COVER242_ASSOCIATION_ACTIVATED')
