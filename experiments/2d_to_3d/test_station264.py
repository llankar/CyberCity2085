"""Check exported detailed columns keep inherited source groups and rail meshes."""
import unittest
from test_industry256 import glb,LAB

class StationDetail(unittest.TestCase):
 def test_source_groups_retained_with_eight_service_meshes(self):
  old=glb(LAB/'generated/phase2/metro263/environment.glb')
  new=glb(LAB/'generated/phase2/metro264/environment.glb')
  groups=lambda d:{n['name'] for n in d['nodes'] if n.get('name','').startswith('Occludable_')}
  self.assertEqual(groups(old),groups(new))
  skins=[n for n in new['nodes'] if n.get('name','').startswith('Station264Service_')]
  self.assertEqual(len(skins),8)
  for skin in skins:
   primitives=new['meshes'][skin['mesh']]['primitives']
   self.assertGreater(sum(new['accessors'][p['indices']]['count'] for p in primitives),1000)
  self.assertTrue(any(n.get('name')=='Track263VisualOnly' for n in new['nodes']))

if __name__=='__main__':unittest.main()
