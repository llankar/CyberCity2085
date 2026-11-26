"""Replace only the experimental track band; preserve stair alpha and original files."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from environment_library import LAB,ROOT

def prepare():
 source=ROOT/'assets/maps/city_transit_subway_platform.png'
 out=LAB/'generated/phase2/metro263';out.mkdir(parents=True,exist_ok=True)
 old=Image.open(LAB/'generated/phase2/metro250/floor.png').convert('RGBA')
 pixels=np.array(old);h,w=pixels.shape[:2]
 # Source canvas coordinates; inferred bed under the drawn rails, not recovered art.
 bounds=(round(22*w/960),round(236*h/540),round(936*w/960),round(304*h/540))
 x1,y1,x2,y2=bounds;rng=np.random.default_rng(263)
 noise=rng.normal(0,5,(y2-y1,x2-x1,1))
 bed=np.clip(np.array([30,34,35])[None,None,:]+noise,0,255).astype('uint8')
 pixels[y1:y2,x1:x2,:3]=bed
 Image.fromarray(pixels).save(out/'floor.png')
 mask=np.zeros((h,w),dtype=bool);mask[y1:y2,x1:x2]=True
 assert np.array_equal(pixels[~mask],np.array(old)[~mask])
 assert np.array_equal(pixels[:,:,3],np.array(old)[:,:,3])
 (out/'floor.json').write_text(json.dumps({'bounds_pixels':bounds,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'outside_band_identical':True,'stair_alpha_preserved':True,'bed':'Inferred dark ballast; no tactical elevation or collision change'},indent=2))
 print('TRACK263_FLOOR_PREPARED',bounds)

if __name__=='__main__':prepare()
