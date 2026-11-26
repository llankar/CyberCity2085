"""Verify actual four corner placements share one mesh and retain source inputs."""
import hashlib,json,unittest
from pathlib import Path
from test_industry256 import LAB,ROOT,glb

class CornerIntegration(unittest.TestCase):
 def test_four_source_groups_share_one_actual_exported_mesh(self):
  model=glb(LAB/'generated/phase2/factory273/environment.glb');indices=[]
  for name in ['nw_machine','ne_machine','sw_machine','se_machine']:
   root=next(n for n in model['nodes'] if n.get('name')=='Occludable_'+name)
   self.assertEqual(len(root['children']),1)
   indices.append(model['nodes'][root['children'][0]]['mesh'])
  self.assertEqual(len(set(indices)),1)
  old=glb(LAB/'generated/phase2/factory270/environment.glb')
  roots=lambda d:{n['name'] for n in d['nodes'] if n.get('name','').startswith('Occludable_') and n.get('children')}
  self.assertTrue(roots(old)<=roots(model))
 def test_original_source_and_generated_reference_are_traceable(self):
  folder=LAB/'generated/phase2/factory273';meta=json.loads((folder/'floor.json').read_text())
  self.assertEqual(meta['source_sha256'],hashlib.sha256((ROOT/'assets/maps/city_industrial_factory_floor.png').read_bytes()).hexdigest())
  self.assertEqual(len(json.loads((folder/'placements.json').read_text())['new_instances']),4)
  self.assertEqual(len(meta['replaced_objects']),15)
  provenance=json.loads((LAB/'sources/corner267/provenance.json').read_text())
  self.assertEqual(provenance['source_sha256'],hashlib.sha256(Path(provenance['source']).read_bytes()).hexdigest())

if __name__=='__main__':unittest.main()
