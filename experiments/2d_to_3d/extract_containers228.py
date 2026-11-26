"""Isolate the original paneled pair; retain tactical ID without asserting object type."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
ROOT=Path('E:/CyberCity2085-3d-lab/environment-library')
catalog=json.loads((ROOT/'library.json').read_text(encoding='utf8'))
parent=next(r for r in catalog['records'] if r['source_object_id']=='east_bins')
source=Path(parent['context_crop']);raw=source.read_bytes()
out=ROOT/'assets/purple_paneled_pair';out.mkdir(parents=True,exist_ok=True)
if not (out/'source.json').exists():
 with Image.open(source) as original:
  image=original.convert('RGBA');mask=Image.new('L',image.size,0)
  polygons=[[(25,4),(139,4),(142,250),(20,250)],[(145,4),(245,4),(268,51),(254,250),(145,250)]]
  for polygon in polygons:ImageDraw.Draw(mask).polygon(polygon,fill=255)
  image.putalpha(mask);image.save(out/'reference.png');mask.save(out/'mask.png')
 bounds=parent['crop_pixels'];cx=(bounds[0]+bounds[2])/2/7680*40-20;cz=(bounds[1]+bounds[3])/2/4320*28-14
 data={'id':'purple_paneled_pair','family':'Industrial','source_image':parent['source_image'],
  'source_sha256':parent['source_sha256'],'context_sha256':hashlib.sha256(raw).hexdigest(),
  'source_object_id':'east_bins','isolated_reference':str(out/'reference.png'),'mask':str(out/'mask.png'),
  'polygon_context_pixels':polygons,'authentic_views':1,'generated_views':0,
  'reference_status':'MANUAL_MASK_REVIEW_PENDING','artistic_status':'NOT_RECONSTRUCTED',
  'dimensions':[1.56,1.6,.85],'dimension_status':'Source footprint estimate; height and hidden sides inferred',
  'anchor':'bottom_center','models':{},'license':'Project source illustration / Blender reconstruction',
  'map_associations':[{'map':parent['source_map'],'position':[cx,0,cz],'rotation':0,'scale':[1,1,1],
    'occlusion_parent':'east_bins','replaces':['*'],'tactical_effect':'decorative only; source cells retained'}],
  'ground_art_status':'Original source floor retained; duplicate-art visibility requires native review'}
 (out/'source.json').write_text(json.dumps(data,indent=2))
else:data=json.loads((out/'source.json').read_text())
assert source.read_bytes()==raw
assets={a['id']:a for a in catalog['assets']};assets.setdefault(data['id'],data)
catalog['assets']=list(assets.values());(ROOT/'library.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False),encoding='utf8')
print('CONTAINER_REFERENCE_READY',out)
