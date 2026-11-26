from pathlib import Path
from PIL import Image
import json,hashlib
root=Path('E:/CyberCity2085-3d-lab/environment-library');out=root/'assets/market_three_canopies';out.mkdir(exist_ok=True)
source=root/'references/city_exterior_neon_market_alley__market_nw.png'
bounds={'sage':[318,174,718,375],'plum':[785,155,1127,411],'green':[305,3,682,112]}
with Image.open(source) as image:
 for name,box in bounds.items():
  crop=image.crop(box);crop.save(out/(name+'.png'))
  with Image.open(out/(name+'.png')) as check:assert check.tobytes()==crop.tobytes()
(out/'source.json').write_text(json.dumps({'context':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'original_rgb_crops':bounds,'authentic_views':1,'generated_views':0,'baked_light_retained':True},indent=2))
print('THREE_ORIGINAL_RGB_CROPS_VERIFIED')
