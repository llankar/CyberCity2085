"""Isolate the genuine blue covering interior; retain source RGB and provenance."""
from pathlib import Path
from PIL import Image
import json,hashlib
root=Path('E:/CyberCity2085-3d-lab/environment-library');out=root/'assets/east_blue_cover';out.mkdir(exist_ok=True)
source=root/'references/city_exterior_neon_market_alley__east_building.png';bounds=(298,956,792,1265)
with Image.open(source) as image:
 crop=image.crop(bounds);crop.save(out/'cloth.png')
 with Image.open(out/'cloth.png') as check:assert check.tobytes()==crop.tobytes()
(out/'source.json').write_text(json.dumps({'context':str(source),'context_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'crop_pixels':bounds,'authentic_views':1,'generated_views':0,'limits':'Genuine blue cloth RGB, baked original illumination retained; hidden covering depth inferred'},indent=2))
print('EAST_CLOTH241_RGB_VERIFIED')
