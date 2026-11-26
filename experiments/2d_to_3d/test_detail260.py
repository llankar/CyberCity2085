"""Checks actual new detail exports; no campaign or global artistic acceptance."""
import json,unittest
from pathlib import Path
from test_industry256 import glb,LAB

class NewDetailExports(unittest.TestCase):
 def test_cylindrical_machine_has_textures_and_two_actual_instances(self):
  folder=LAB/'environment-library/assets/cylindrical_machine259'
  data=glb(folder/'model.glb');material=data['materials'][0]['pbrMetallicRoughness']
  self.assertIn('baseColorTexture',material);self.assertIn('metallicRoughnessTexture',material)
  meta=json.loads((folder/'asset.json').read_text());self.assertTrue(all(v>.5 for v in meta['dimensions']))
  scene=glb(LAB/'generated/phase2/factory260/environment.glb')
  for name in ['reactor_north','reactor_middle']:
   self.assertTrue(any(n.get('name')=='Occludable_'+name and n.get('children') for n in scene['nodes']))
 def test_lab_retains_source_object_groups_and_punctual_lights(self):
  old=glb(LAB/'generated/phase2/lab248/environment.glb');new=glb(LAB/'generated/phase2/lab261/environment.glb')
  groups=lambda data:{n.get('name') for n in data['nodes'] if n.get('name','').startswith('Occludable_')}
  self.assertEqual(groups(old),groups(new))
  self.assertEqual(len(new['extensions']['KHR_lights_punctual']['lights']),3)
  self.assertTrue(any(n.get('name','').startswith('Lab261ServiceSkin_') for n in new['nodes']))

if __name__=='__main__':unittest.main()
