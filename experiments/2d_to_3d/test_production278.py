"""One grouped check of the assembled production lot, not per-asset art gates."""
import hashlib,json,unittest
from test_industry256 import LAB,ROOT,glb

class ProductionLot(unittest.TestCase):
 def test_cargo_reuse_and_removal_of_old_display_plinths(self):
  factory=glb(LAB/'generated/phase2/factory278/environment.glb');meshes=[]
  for node in factory['nodes']:
   if node.get('name') in {'Occludable_'+s for s in ['north_crates_w','north_crates_m','north_crates_e','south_crates_w','south_crates_e']}:
    meshes.extend(factory['nodes'][i]['mesh'] for i in node['children'])
  self.assertGreater(len(meshes),5);self.assertEqual(len(set(meshes)),1)
  self.assertFalse(any('mounting platform' in node.get('name','') for node in factory['nodes']))
  residential=glb(LAB/'generated/phase2/residential278/environment.glb')
  self.assertTrue(any(n.get('name')=='Occludable_west_street_crates' and n.get('children') for n in residential['nodes']))
 def test_three_original_map_images_still_match_canonical_tactical_hashes(self):
  names=['city_industrial_factory_floor','city_district_apartment_block','wasteland_outdoor_02_ashfield_ruins']
  for name in names:
   source=ROOT/f'assets/maps/{name}.png';walls=json.loads(source.with_suffix('.walls.json').read_text())
   self.assertEqual(walls['image_sha256'],hashlib.sha256(source.read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
