"""Reproducible manual polygon isolation from an unchanged surveyed map crop."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=LAB/'environment-library'
parent='city_exterior_neon_market_alley__south_building_w'
source=ROOT/'references'/(parent+'.png')
out=ROOT/'assets/roof_twin_fan';out.mkdir(parents=True,exist_ok=True)
raw=source.read_bytes();before=hashlib.sha256(raw).hexdigest()
polygon=[(45,258),(286,258),(294,411),(57,427)]
if (out/'source.json').exists():
 existing=json.loads((out/'source.json').read_text())
 if existing['context_sha256']!=before or existing['polygon_context_pixels']!=[list(p) for p in polygon]:
  raise RuntimeError('Preserve prior extraction; use a new revision for changed input/mask')
 if (out/'reference.png').exists() and (out/'mask.png').exists():
  print('REUSED_ROOF_EXTRACTION; existing reconstruction metadata preserved')
  raise SystemExit(0)
with Image.open(source) as image:
 image=image.convert('RGBA');mask=Image.new('L',image.size,0)
 ImageDraw.Draw(mask).polygon(polygon,fill=255)
 image.putalpha(mask);bounds=mask.getbbox()
 image.crop(bounds).save(out/'reference.png');mask.crop(bounds).save(out/'mask.png')
assert source.read_bytes()==raw
library=json.loads((ROOT/'library.json').read_text(encoding='utf8'))
record=next(r for r in library['records'] if r['id']==parent)
origin=record['crop_pixels'];source_bounds=[origin[0]+bounds[0],origin[1]+bounds[1],origin[0]+bounds[2],origin[1]+bounds[3]]
metadata={'id':'roof_twin_fan','family':'Rooftops','parent_record':parent,
 'source_image':record['source_image'],'source_sha256':record['source_sha256'],
 'context_sha256':before,'source_bounds_pixels':source_bounds,
 'isolation_method':'Manual polygon on actual context crop; no invented source views',
 'polygon_context_pixels':polygon,'isolated_reference':str(out/'reference.png'),
 'mask':str(out/'mask.png'),'authentic_views':1,'generated_views':0,
 'dimensions':[(source_bounds[2]-source_bounds[0])/192,(source_bounds[3]-source_bounds[1])/(4320/28),.4],
 'dimension_status':'XY from surveyed source pixels/grid; height estimated',
 'anchor':'bottom_center','reference_status':'MANUAL_MASK_REVIEW_PENDING',
 'models':{},'artistic_status':'NOT_RECONSTRUCTED',
 'license':'Project original illustration; Blender reconstruction pending',
 'map_associations':[{'map':record['source_map'],'position':[(source_bounds[0]+source_bounds[2])/2/192-20,3,(source_bounds[1]+source_bounds[3])/2/(4320/28)-14],
 'height_status':'3m roof provisional; calibrate to existing roof geometry','rotation':0,'scale':[1,1,1],
 'tactical_effect':'decorative only; retain source walls/cells','occlusion_parent':'south_building_w'}]}
(out/'source.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
assets={r['id']:r for r in library.get('assets',[])}
assets.setdefault(metadata['id'],metadata);library['assets']=list(assets.values())
(ROOT/'library.json').write_text(json.dumps(library,indent=2,ensure_ascii=False),encoding='utf8')
print('ROOF_REFERENCE_EXTRACTED',source_bounds,out)
