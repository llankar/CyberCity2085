"""Actual export/source coverage checks; not artistic or combat acceptance."""
import hashlib,json,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];LAB=Path('E:/CyberCity2085-3d-lab/generated/phase2')

def exported_names(path):
 data=path.read_bytes();length,kind=struct.unpack_from('<II',data,12)
 if kind!=0x4e4f534a:raise ValueError('Missing GLB JSON')
 return {n.get('name','') for n in json.loads(data[20:20+length])['nodes']}

class OutdoorCoverage(unittest.TestCase):
 def check_source(self,name):
  source=ROOT/f'assets/maps/{name}.png';walls=json.loads(source.with_suffix('.walls.json').read_text())
  self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),walls['image_sha256'])
  return json.loads(source.with_suffix('.wall-traces.json').read_text())['walls']
 def test_residential_exports_surveyed_buildings(self):
  survey=self.check_source('city_district_apartment_block')
  expected={'Occludable_'+r['id'] for r in survey if any(k in r['id'] for k in ['building','tower','extension'])}
  actual={n for n in exported_names(LAB/'residential253/environment.glb') if n.startswith('Occludable_')}
  self.assertEqual(actual,expected)
 def test_ruins_preserve_wrecks_as_2d(self):
  survey=self.check_source('wasteland_outdoor_02_ashfield_ruins')
  expected={'Occludable_'+r['id'] for r in survey if 'wreck' not in r['id']}
  actual={n for n in exported_names(LAB/'wasteland254/environment.glb') if n.startswith('Occludable_')}
  self.assertEqual(actual,expected)

if __name__=='__main__':unittest.main()
