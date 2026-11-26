"""Export checks for the actual wall family and preservation of source cutaway roots."""
import unittest
from test_industry256 import LAB,glb

class WallFamily(unittest.TestCase):
 def test_both_maps_keep_their_existing_cutaway_roots(self):
  for new,old in [('factory270','factory266'),('metro270','metro264')]:
   roots=lambda d:{n['name'] for n in d['nodes'] if n.get('name','').startswith('Occludable_') and n.get('children')}
   self.assertEqual(roots(glb(LAB/'generated/phase2'/new/'environment.glb')),roots(glb(LAB/'generated/phase2'/old/'environment.glb')))
 def test_standalone_variants_are_textured_and_volumetric(self):
  for variant in ['factory','metro']:
   model=glb(LAB/'environment-library/assets'/('service_wall269_'+variant)/'model.glb')
   accessors=[model['accessors'][p['attributes']['POSITION']] for mesh in model['meshes'] for p in mesh['primitives']]
   extents=[max(a['max'][i] for a in accessors)-min(a['min'][i] for a in accessors) for i in range(3)]
   self.assertGreater(extents[0],2);self.assertGreater(extents[1],1.6);self.assertGreater(extents[2],.4)
   self.assertTrue(any('baseColorTexture' in m.get('pbrMetallicRoughness',{}) for m in model['materials']))

if __name__=='__main__':unittest.main()
