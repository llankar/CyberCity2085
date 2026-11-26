"""Crisp inferred subfloor under source buildings; preserve all street pixels."""
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from environment_library import LAB,ROOT

def main():
 out=LAB/'generated/phase2/residential284';out.mkdir(parents=True,exist_ok=True)
 source=ROOT/'assets/maps/city_district_apartment_block.png'
 survey=json.loads(source.with_suffix('.wall-traces.json').read_text());cw,ch=survey['canvas_size']
 base=Image.open(LAB/'generated/phase2/residential278/floor.png').convert('RGB');w,h=base.size
 mask=Image.new('L',base.size);draw=ImageDraw.Draw(mask);groups=[]
 for item in survey['walls']:
  if not any(tag in item['id'] for tag in ['building','tower','extension']):continue
  polygon=item.get('polygon')
  if polygon is None:
   x1,y1,x2,y2=item['rect'];polygon=[(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
  draw.polygon([(round(x*w/cw),round(y*h/ch)) for x,y in polygon],fill=255);groups.append(item['id'])
 sample=LAB/'sources/environment169/concrete_wall_001/diff.jpg'
 tile=Image.open(sample).convert('RGB').resize((round(w/40*1.5),round(h/28*1.5)),Image.Resampling.LANCZOS)
 tile=Image.fromarray(np.clip(np.asarray(tile)*np.array([.38,.42,.46]),0,255).astype('uint8'))
 seamless=Image.new('RGB',(tile.width*2,tile.height*2));seamless.paste(tile,(0,0));seamless.paste(ImageOps.mirror(tile),(tile.width,0));seamless.paste(ImageOps.flip(tile),(0,tile.height));seamless.paste(ImageOps.flip(ImageOps.mirror(tile)),(tile.width,tile.height))
 fill=Image.new('RGB',base.size)
 for y in range(0,h,seamless.height):
  for x in range(0,w,seamless.width):fill.paste(seamless,(x,y))
 result=Image.composite(fill,base,mask);result.save(out/'floor.png');mask.save(out/'subfloor_mask.png')
 assert np.array_equal(np.asarray(base)[np.asarray(mask)==0],np.asarray(result)[np.asarray(mask)==0])
 (out/'subfloor.json').write_text(json.dumps({'base':'residential278','building_groups':groups,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'material_reference':str(sample),'outside_building_masks_identical':True,'provenance':'Inferred neutral subfloor, not recovered authentic room interiors; replaces blurred inpaint only beneath reconstructed buildings'},indent=2))
 print('CLEAR_SUBFLOOR284_PREPARED',len(groups),'building masks; streets unchanged')

if __name__=='__main__':main()
