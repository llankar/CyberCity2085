"""Small data-contract checks; no campaign or model generation."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import environment_library as library

class LibraryContract(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir='E:/CyberCity2085-3d-lab/tmp',prefix='library-test-')
  self.root=Path(self.temp.name)
  self.lab=self.root/'lab';self.out=self.lab/'environment-library'
  self.source=self.lab/'sources/tactical_map/test_map.png'
  self.source.parent.mkdir(parents=True)
  Image.new('RGB',(100,50),'blue').save(self.source)
  self.maps=self.root/'repo/assets/maps';self.maps.mkdir(parents=True)
  self.walls={'image_sha256':hashlib.sha256(self.source.read_bytes()).hexdigest(),'grid':[10,5],
   'walls':[{'id':'bench','kind':'cover','blocks_sight':False,'cells':[[2,1],[3,1]]}]}
  (self.maps/'test_map.walls.json').write_text(json.dumps(self.walls))
  (self.maps/'test_map.wall-traces.json').write_text(json.dumps({'canvas_size':[100,50],'walls':[{'id':'bench','rect':[20,10,40,20]}]}))
  self.patch=patch.multiple(library,ROOT=self.root/'repo',LAB=self.lab,OUT=self.out,MAP='test_map')
  self.patch.start()
 def tearDown(self):
  self.patch.stop();self.temp.cleanup()
 def test_source_and_tactical_data_unchanged(self):
  before=self.source.read_bytes();walls=(self.maps/'test_map.walls.json').read_bytes()
  library.initialize()
  record=json.loads((self.out/'library.json').read_text(encoding='utf8'))['records'][0]
  self.assertEqual(self.source.read_bytes(),before)
  self.assertEqual((self.maps/'test_map.walls.json').read_bytes(),walls)
  self.assertEqual(record['footprint_cells'],[[2,1],[3,1]])
  self.assertEqual(record['placement']['position'],[-2.0,0,-1.0])
  self.assertIsNone(record['isolated_reference'])
  self.assertEqual(record['authentic_views'],1)
 def test_reimport_preserves_work_without_duplicate_ids(self):
  library.initialize();path=self.out/'library.json'
  data=json.loads(path.read_text(encoding='utf8'));data['records'][0]['artistic_status']='REVIEW_PENDING'
  data['assets']=[{'id':'retained-model','models':{'glb':'existing.glb'}}]
  path.write_text(json.dumps(data),encoding='utf8');library.initialize()
  records=json.loads(path.read_text(encoding='utf8'))['records']
  self.assertEqual(len(records),1);self.assertEqual(records[0]['artistic_status'],'REVIEW_PENDING')
  self.assertEqual(json.loads(path.read_text(encoding='utf8'))['assets'][0]['id'],'retained-model')
 def test_rejects_changed_source(self):
  Image.new('RGB',(100,50),'red').save(self.source)
  with self.assertRaisesRegex(ValueError,'differs'):library.initialize()

if __name__=='__main__':unittest.main()
