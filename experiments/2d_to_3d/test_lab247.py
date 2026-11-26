"""Check the actual exported curved pod geometry, not artistic acceptance."""
import json,struct,unittest
from pathlib import Path

class PodExport(unittest.TestCase):
 def test_pod_bank_has_three_round_chambers_and_materials(self):
  p=Path('E:/CyberCity2085-3d-lab/generated/phase2/lab247/pod_bank.glb')
  self.assertTrue(p.is_file(),'Build laboratory247 before this explicit asset check')
  data=p.read_bytes();length,kind=struct.unpack_from('<II',data,12)
  self.assertEqual(kind,0x4e4f534a)
  gltf=json.loads(data[20:20+length])
  chambers=[n for n in gltf['nodes'] if 'chamber' in n.get('name','')]
  self.assertEqual(len(chambers),3)
  for node in chambers:
   primitive=gltf['meshes'][node['mesh']]['primitives'][0]
   self.assertGreater(gltf['accessors'][primitive['attributes']['POSITION']]['count'],32)
  self.assertTrue(any('blue glass' in m.get('name','') for m in gltf['materials']))

if __name__=='__main__':unittest.main()
