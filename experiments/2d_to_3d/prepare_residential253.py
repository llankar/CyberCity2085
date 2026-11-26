"""Original street copy plus explicitly toned PBR albedo for glTF portability."""
import json
from PIL import Image,ImageChops
from prepare_floor248 import ROOT,LAB,prepare

def main():
 name='city_district_apartment_block';source=ROOT/f'assets/maps/{name}.png'
 survey=json.loads(source.with_suffix('.wall-traces.json').read_text())
 survey['walls']=[r for r in survey['walls'] if any(k in r['id'] for k in ['building','tower','extension'])]
 out=LAB/'generated/phase2/residential253';out.mkdir(parents=True,exist_ok=True)
 image,mask=prepare(Image.open(source),survey);image.save(out/'floor.png')
 albedo=Image.open(LAB/'sources/environment169/concrete_wall_001/diff.jpg').convert('RGB')
 ImageChops.multiply(albedo,Image.new('RGB',albedo.size,(78,90,102))).save(out/'concrete_diff.jpg',quality=95)
 print('RESIDENTIAL253_SOURCE_PREPARED')

if __name__=='__main__':main()
