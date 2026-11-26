"""Actual export check for the recessed stairs and prepared floor openings."""
import json,struct,unittest
from pathlib import Path
from PIL import Image

class MetroAssembly(unittest.TestCase):
 def test_recessed_stairs_and_floor_openings(self):
  folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/metro250')
  data=(folder/'environment.glb').read_bytes();length,kind=struct.unpack_from('<II',data,12)
  self.assertEqual(kind,0x4e4f534a);gltf=json.loads(data[20:20+length])
  names=[n.get('name','') for n in gltf['nodes']]
  self.assertEqual(sum(name.startswith('Occludable_stair_') for name in names),4)
  self.assertEqual(sum(' tread' in name and 'lip' not in name for name in names),112)
  image=Image.open(folder/'floor.png')
  self.assertEqual(image.mode,'RGBA');self.assertEqual(image.getchannel('A').getextrema(),(0,255))
  self.assertEqual(image.getpixel((image.width//2,image.height//2))[3],255)

if __name__=='__main__':unittest.main()
