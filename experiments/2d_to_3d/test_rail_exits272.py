"""Inspect actual exported triangles: neither station exit may close the rails."""
import json,struct,unittest,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from test_industry256 import LAB,ROOT

class RailwayExits(unittest.TestCase):
 def read_export(self, folder):
  self.raw=(folder/'environment.glb').read_bytes()
  self.json_size=struct.unpack_from('<I',self.raw,12)[0]
  self.data=json.loads(self.raw[20:20+self.json_size])
 def array(self,index,columns):
  accessor=self.data['accessors'][index];view=self.data['bufferViews'][accessor['bufferView']]
  dtype=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2'}[accessor['componentType']])
  offset=28+self.json_size+view.get('byteOffset',0)+accessor.get('byteOffset',0)
  return np.ndarray((accessor['count'],columns),dtype=dtype,buffer=self.raw,offset=offset,strides=(view.get('byteStride',dtype.itemsize*columns),dtype.itemsize))
 def test_no_wall_triangle_crosses_either_rail_exit(self):
  godot = Path(__file__).with_name("godot")
  catalogue = json.loads((godot / "preproduction_catalog.json").read_text())
  entry = next(row for row in catalogue if row["map"] == "city_transit_subway_platform")
  scene = godot / entry["scene"].removeprefix("res://")
  folder = next(line.split('"')[1] for line in scene.read_text().splitlines()
                if line.startswith("review_folder = "))
  for export in (LAB / "generated/phase2/metro270", Path(folder)):
   with self.subTest(export=export):
    self.read_export(export)
    self.check_opening()
    self.check_track_extent()

 def check_opening(self):
  for name in ['Occludable_west_wall','Occludable_east_wall']:
   root=next(n for n in self.data['nodes'] if n.get('name')==name)
   checked=0
   for child in root['children']:
    node=self.data['nodes'][child]
    if 'mesh' not in node:continue
    self.assertNotIn('rotation',node);self.assertNotIn('scale',node);self.assertNotIn('matrix',node)
    for primitive in self.data['meshes'][node['mesh']]['primitives']:
     positions=self.array(primitive['attributes']['POSITION'],3)
     indices=self.array(primitive['indices'],1).reshape(-1,3)
     z=positions[indices,2]+node.get('translation',[0,0,0])[2]
     # Blender Y -> glTF -Z; original railway band is symmetric around zero.
     limit=14-236*28/540
     self.assertFalse(np.any((z.min(axis=1)<limit)&(z.max(axis=1)>-limit)),name)
     checked+=len(indices)
   self.assertGreater(checked,100)
 def check_track_extent(self):
  root=next(n for n in self.data['nodes'] if n.get('name')=='Track263VisualOnly');extents=[]
  for child in root['children']:
   node=self.data['nodes'][child]
   if 'mesh' not in node:continue
   for primitive in self.data['meshes'][node['mesh']]['primitives']:
    a=self.data['accessors'][primitive['attributes']['POSITION']];tx=node.get('translation',[0,0,0])[0]
    extents.extend([a['min'][0]+tx,a['max'][0]+tx])
  self.assertLessEqual(min(extents),-19.999);self.assertGreaterEqual(max(extents),19.999)

 def test_source_png_stays_unchanged(self):
  meta=json.loads((LAB/'generated/phase2/metro270/rail_exit_floor.json').read_text())
  self.assertEqual(meta['source_sha256'],hashlib.sha256((ROOT/'assets/maps/city_transit_subway_platform.png').read_bytes()).hexdigest())

if __name__=='__main__':unittest.main()
