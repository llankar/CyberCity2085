import copy,tempfile,unittest
from pathlib import Path
from build_library_scene import compile_bindings

class PlacementContract(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir='E:/CyberCity2085-3d-lab/tmp',prefix='bindings-test-')
  self.lab=Path(self.temp.name);self.model=self.lab/'existing.glb';self.model.write_bytes(b'existing-mesh-placeholder-for-metadata-test')
  self.data={'records':[{'source_map':'alley','source_object_id':'roof'}],
   'assets':[{'id':'fan','anchor':'bottom_center','models':{'glb':str(self.model)},'map_associations':[
    {'map':'alley','position':[1,3,2],'scale':[1,1,1],'rotation':0,'occlusion_parent':'roof'}]}]}
 def tearDown(self):self.temp.cleanup()
 def test_compiles_without_mutating_source_or_tactical_data(self):
  before=copy.deepcopy(self.data);blob=self.model.read_bytes()
  output=compile_bindings(self.data,'alley',self.lab)
  self.assertFalse(output['tactical_mutation']);self.assertEqual(output['instances'][0]['position'],[1,3,2])
  self.assertEqual(output['instances'][0]['parent'],'roof')
  self.assertEqual(self.data,before);self.assertEqual(self.model.read_bytes(),blob)
 def test_rejects_unknown_parent(self):
  self.data['assets'][0]['map_associations'][0]['occlusion_parent']='invented'
  with self.assertRaisesRegex(ValueError,'Unknown surveyed parent'):compile_bindings(self.data,'alley',self.lab)
 def test_rejects_invalid_scale(self):
  self.data['assets'][0]['map_associations'][0]['scale']=[1,-1,1]
  with self.assertRaisesRegex(ValueError,'Invalid scale'):compile_bindings(self.data,'alley',self.lab)
 def test_other_maps_do_not_spawn(self):
  self.assertEqual(compile_bindings(self.data,'different',self.lab)['instances'],[])

if __name__=='__main__':unittest.main()
