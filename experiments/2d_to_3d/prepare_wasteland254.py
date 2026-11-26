"""Prepare an experimental ashfield floor copy and weathered material variant."""
import json
from PIL import Image,ImageChops
from prepare_floor248 import ROOT,LAB,prepare

def main():
 name='wasteland_outdoor_02_ashfield_ruins';source=ROOT/f'assets/maps/{name}.png'
 survey=json.loads(source.with_suffix('.wall-traces.json').read_text())
 survey['walls']=[r for r in survey['walls'] if 'wreck' not in r['id']]
 out=LAB/'generated/phase2/wasteland254';out.mkdir(parents=True,exist_ok=True)
 image,mask=prepare(Image.open(source),survey);image.save(out/'floor.png')
 albedo=Image.open(LAB/'sources/environment169/concrete_wall_001/diff.jpg').convert('RGB')
 ImageChops.multiply(albedo,Image.new('RGB',albedo.size,(110,95,80))).save(out/'concrete_diff.jpg',quality=95)
 print('WASTELAND254_SOURCE_PREPARED')

if __name__=='__main__':main()
