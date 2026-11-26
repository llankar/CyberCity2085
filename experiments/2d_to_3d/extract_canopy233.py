"""Extract the genuine green cloth panel from the original market context (no synthesis)."""
from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path('E:/CyberCity2085-3d-lab/environment-library')
source=ROOT/'references/city_exterior_neon_market_alley__market_nw.png'
out=ROOT/'assets/market_green_canopy';out.mkdir(exist_ok=True)
# Interior cloth only: poles, neighboring shops and floor excluded.
bounds=(318,174,718,375)
with Image.open(source) as image:image.crop(bounds).save(out/'source_cloth.png')
with Image.open(source) as original, Image.open(out/'source_cloth.png') as extracted:
 assert original.crop(bounds).tobytes()==extracted.tobytes()
(out/'source.json').write_text(json.dumps({'source':str(source),'context_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'crop_context_pixels':bounds,'authentic_views':1,'generated_views':0,'operation':'Crop original RGB only; baked source illumination retained; hidden cloth shape inferred'},indent=2))
catalog=json.loads((ROOT/'library.json').read_text(encoding='utf8'))
record=next(r for r in catalog['records'] if r['source_object_id']=='market_nw')
record['isolated_reference']=str(out/'source_cloth.png')
record['reference_status']='PARTIAL_CLOTH_RGB_CROP_REVIEWED'
record['artistic_status']='PARTIAL_CLOTH_RECONSTRUCTION'
record['remaining']=['Isolate remaining shop structures','Improve source baked lighting and texture proportions','Export reusable complete shop assembly']
(ROOT/'library.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False),encoding='utf8')
print('SOURCE_CLOTH_READY',out)
