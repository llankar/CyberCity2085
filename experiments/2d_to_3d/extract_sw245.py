"""Extract genuine blue housing inset from the southwest source context."""
from pathlib import Path
from PIL import Image
import json,hashlib
root=Path('E:/CyberCity2085-3d-lab/environment-library');out=root/'assets/sw_service_housing';out.mkdir(exist_ok=True)
source=root/'references/city_exterior_neon_market_alley__sw_building.png';bounds=(61,278,506,475)
with Image.open(source) as image:
 crop=image.crop(bounds);crop.save(out/'blue_panel.png')
 with Image.open(out/'blue_panel.png') as check:assert check.tobytes()==crop.tobytes()
(out/'source.json').write_text(json.dumps({'context':str(source),'context_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'crop_pixels':bounds,'authentic_views':1,'generated_views':0,'limits':'Original blue inset RGB; unknown exact device function; hidden housing geometry inferred'},indent=2))
print('SW245_SOURCE_RGB_VERIFIED')
