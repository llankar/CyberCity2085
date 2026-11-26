"""Prepare only changed floor masks for the three-map production lot."""
import hashlib,json,subprocess,sys
import numpy as np
from PIL import Image
from prepare_floor248 import LAB,ROOT,prepare

def patch(name,base,folder,identifier):
 source=ROOT/f'assets/maps/{name}.png';survey=json.loads(source.with_suffix('.wall-traces.json').read_text())
 selected=dict(survey,walls=[r for r in survey['walls'] if r['id']==identifier])
 assert len(selected['walls'])==1
 repaired,mask=prepare(Image.open(source),selected)
 original=np.asarray(Image.open(LAB/'generated/phase2'/base/'floor.png').convert('RGB'))
 result=original.copy();result[mask>0]=np.asarray(repaired.convert('RGB'))[mask>0]
 out=LAB/'generated/phase2'/folder;out.mkdir(parents=True,exist_ok=True)
 Image.fromarray(result).save(out/'floor.png')
 (out/'floor.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'base':base,'changed_source_groups':[identifier],'outside_new_mask_identical':bool(np.array_equal(result[mask==0],original[mask==0]))},indent=2))

def main():
 script=ROOT/'experiments/2d_to_3d/prepare_factory257.py'
 extras='reactor_north,reactor_middle,west_generator,nw_machine,ne_machine,sw_machine,se_machine,north_crates_w,north_crates_m,north_crates_e,south_crates_w,south_crates_e'
 subprocess.run([sys.executable,str(script),'--output',str(LAB/'generated/phase2/factory278'),'--extra-objects',extras],check=True)
 patch('city_district_apartment_block','residential253','residential278','west_street_crates')
 patch('wasteland_outdoor_02_ashfield_ruins','wasteland254','wasteland278','wreck_e')
 print('PRODUCTION278_FLOORS_READY three experimental maps')

if __name__=='__main__':main()
