"""Original source crops for the southeast covered display counter."""
from pathlib import Path
from PIL import Image
import hashlib,json
root=Path('E:/CyberCity2085-3d-lab/environment-library');out=root/'assets/market_southeast_display';out.mkdir(exist_ok=True)
source=root/'references/city_exterior_neon_market_alley__market_se.png'
bounds={'cloth':[95,80,515,294],'tray0':[125,425,186,491],'tray1':[205,425,269,492],'tray2':[293,425,363,492],'tray3':[393,425,456,492]}
with Image.open(source) as image:
 for name,box in bounds.items():
  crop=image.crop(box);crop.save(out/(name+'.png'))
  with Image.open(out/(name+'.png')) as check:assert check.tobytes()==crop.tobytes()
(out/'source.json').write_text(json.dumps({'context':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'original_rgb_crops':bounds,'authentic_views':1,'generated_views':0,'baked_light_retained':True},indent=2))
print('SOUTHEAST_ORIGINAL_CROPS_VERIFIED',len(bounds))
