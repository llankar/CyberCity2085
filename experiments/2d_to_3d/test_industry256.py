"""Actual generated GLB and source-preservation checks, not global art acceptance."""
import hashlib,json,struct,unittest
from pathlib import Path
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[2]
def glb(path):
 data=path.read_bytes();length,kind=struct.unpack_from('<II',data,12)
 if kind!=0x4e4f534a:raise ValueError('Missing GLB JSON')
 return json.loads(data[20:20+length])

class IndustrialResources(unittest.TestCase):
 def test_arm_is_volumetric_and_textured_pbr(self):
  folder=LAB/'environment-library/assets/industrial_arm256'
  asset=json.loads((folder/'asset.json').read_text());self.assertTrue(all(v>.5 for v in asset['dimensions']))
  model=glb(folder/'model.glb')
  material=model['materials'][0]['pbrMetallicRoughness']
  self.assertIn('baseColorTexture',material);self.assertIn('metallicRoughnessTexture',material)
  self.assertTrue(all('bufferView' in image for image in model['images']))
  self.assertTrue(Path(asset['models']['high_definition']).is_file())
 def test_conveyor_and_source_replacement(self):
  model=glb(LAB/'environment-library/assets/roller_conveyor256/model.glb')
  self.assertEqual(sum(n.get('name','').startswith('Transverse roller') for n in model['nodes']),22)
  folder=LAB/'generated/phase2/factory257';placements=json.loads((folder/'placements.json').read_text())
  self.assertEqual(sum(i['asset']=='industrial_arm256' for i in placements['instances']),6)
  self.assertEqual(sum(i['asset']=='roller_conveyor256' for i in placements['instances']),5)
  source=ROOT/'assets/maps/city_industrial_factory_floor.png'
  self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),json.loads((folder/'floor.json').read_text())['source_sha256'])

if __name__=='__main__':unittest.main()
