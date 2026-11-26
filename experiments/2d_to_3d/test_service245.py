"""Generated-asset contract: curved routes must export as real volumetric triangle meshes."""
from pathlib import Path
import json,struct,unittest
MODEL=Path('E:/CyberCity2085-3d-lab/generated/phase2/showcase245/environment.glb')
@unittest.skipUnless(MODEL.is_file(),'Generate southwest_service245.py first')
class CurvedServiceExport(unittest.TestCase):
 def test_two_nonplanar_triangle_routes(self):
  with MODEL.open('rb') as stream:
   stream.seek(12);length,kind=struct.unpack('<II',stream.read(8));self.assertEqual(kind,0x4E4F534A);data=json.loads(stream.read(length))
  routes=[n for n in data['nodes'] if n.get('name','').startswith('Southwest245 source curved pipe')]
  self.assertEqual(len(routes),2)
  for route in routes:
   for primitive in data['meshes'][route['mesh']]['primitives']:
    self.assertEqual(primitive.get('mode',4),4)
    positions=data['accessors'][primitive['attributes']['POSITION']]
    self.assertGreater(positions['count'],100)
    self.assertTrue(all(positions['max'][i]-positions['min'][i]>.2 for i in range(3)))
if __name__=='__main__':unittest.main()
