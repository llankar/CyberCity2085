"""Separate actual replaced objects from the experimental floor, retaining outside pixels."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from prepare_floor248 import prepare,ROOT,LAB

def main():
 source=ROOT/'assets/maps/city_industrial_factory_floor.png';raw=source.read_bytes()
 survey=json.loads(source.with_suffix('.wall-traces.json').read_text())
 old={'west_generator','north_crates_w','north_crates_m','north_crates_e','south_crates_w','south_crates_e'}
 lines={'west_assembly','east_assembly_north','east_assembly_south'}
 selected=dict(survey,walls=[r for r in survey['walls'] if r['id'] in old|lines])
 original=Image.open(source).convert('RGB');floor,mask=prepare(original,selected)
 sx=original.width/survey['canvas_size'][0];sy=original.height/survey['canvas_size'][1]
 # Reviewed clean original floor sample; no new schematic/pedestal artwork.
 sample=(350,164,374,183);tile=original.crop(tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(sample)))
 double=Image.new('RGB',(tile.width*2,tile.height*2));double.paste(tile,(0,0));double.paste(ImageOps.mirror(tile),(tile.width,0));double.paste(ImageOps.flip(tile),(0,tile.height));double.paste(ImageOps.flip(ImageOps.mirror(tile)),(tile.width,tile.height))
 for item in selected['walls']:
  if item['id'] not in lines:continue
  x1,y1,x2,y2=[round(v*(sx if i%2==0 else sy)) for i,v in enumerate(item['rect'])]
  patch=Image.new('RGB',(x2-x1,y2-y1))
  for y in range(0,patch.height,double.height):
   for x in range(0,patch.width,double.width):patch.paste(double,(x,y))
  floor.paste(patch,(x1,y1))
 result=np.asarray(floor);pixels=np.asarray(original)
 assert np.array_equal(result[mask==0],pixels[mask==0])
 assert source.read_bytes()==raw
 out=LAB/'generated/phase2/factory257';out.mkdir(parents=True,exist_ok=True)
 floor.save(out/'floor.png');Image.fromarray(mask).save(out/'replacement_mask.png')
 (out/'floor.json').write_text(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),'replaced_objects':sorted(old|lines),'local_floor_sample_canvas':sample,'method':'Original clean-floor sample mirrored under assembly replacements; inferred hidden floor, unchanged outside surveyed masks','outside_mask_pixel_identity':True},indent=2))
 print('FACTORY257_FLOOR_SEPARATED',len(old|lines),'source objects; outside mask pixels identical')

if __name__=='__main__':main()
