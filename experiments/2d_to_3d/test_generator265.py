"""Actual coloured AI generator and inherited factory-source group checks."""
import hashlib,json,unittest
from test_industry256 import glb,LAB

class GeneratorDetail(unittest.TestCase):
 def test_original_illustration_and_textured_volume(self):
  asset=LAB/'environment-library/assets/industrial_generator265'
  meta=json.loads((asset/'asset.json').read_text());self.assertEqual(meta['generated_views'],0)
  self.assertTrue(all(d>.5 for d in meta['dimensions']))
  model=glb(asset/'model.glb')
  for m in model['materials']:
   self.assertIn('baseColorTexture',m['pbrMetallicRoughness'])
   self.assertIn('metallicRoughnessTexture',m['pbrMetallicRoughness'])
  shape=json.loads((LAB/'generated/phase2/generator265/shape/result.json').read_text())
  self.assertEqual(shape['source_sha256'],hashlib.sha256((LAB/'sources/industrial_machine.png').read_bytes()).hexdigest())
 def test_factory_retains_groups_and_replaces_coarse_generator(self):
  old=glb(LAB/'generated/phase2/factory260/environment.glb');new=glb(LAB/'generated/phase2/factory266/environment.glb')
  groups=lambda data:{n['name'] for n in data['nodes'] if n.get('name','').startswith('Occludable_') and 'mesh' not in n}
  self.assertEqual(groups(old),groups(new))
  root=next(n for n in new['nodes'] if n.get('name')=='Occludable_west_generator')
  self.assertEqual(len(root['children']),1)
  mesh=new['meshes'][new['nodes'][root['children'][0]]['mesh']]
  self.assertGreater(sum(new['accessors'][p['indices']]['count'] for p in mesh['primitives']),100000)

if __name__=='__main__':unittest.main()
