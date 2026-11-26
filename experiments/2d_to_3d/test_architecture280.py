"""Grouped scene regression: actual west-wall UV area and retained source groups."""
import json,struct,unittest
import numpy as np
from test_industry256 import LAB,glb

class ArchitectureLot(unittest.TestCase):
 def test_west_facade_uvs_are_not_collapsed_to_a_line(self):
  raw=(LAB/'generated/phase2/residential280/environment.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0];data=json.loads(raw[20:20+size])
  def array(index,columns):
   a=data['accessors'][index];view=data['bufferViews'][a['bufferView']];dtype=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']])
   return np.ndarray((a['count'],columns),dtype=dtype,buffer=raw,offset=28+size+view.get('byteOffset',0)+a.get('byteOffset',0),strides=(view.get('byteStride',columns*dtype.itemsize),dtype.itemsize))
  node=next(n for n in data['nodes'] if n.get('name')=='northwest_building shell')
  primitive=next(p for p in data['meshes'][node['mesh']]['primitives'] if data['materials'][p['material']]['name']=='Residential weathered concrete')
  self.assertIn('normalTexture',data['materials'][primitive['material']])
  triangles=array(primitive['indices'],1).reshape((-1,3));normals=array(primitive['attributes']['NORMAL'],3)
  west=np.abs(normals[triangles,0].mean(axis=1))>.9;self.assertTrue(west.any())
  uv=array(primitive['attributes']['TEXCOORD_0'],2)[triangles[west]];a=uv[:,1]-uv[:,0];b=uv[:,2]-uv[:,0]
  self.assertTrue(np.all(np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])>1e-6))
 def test_existing_cutaway_groups_and_original_roof_material_are_retained(self):
  roots=lambda d:{n['name'] for n in d['nodes'] if n.get('name','').startswith('Occludable_') and n.get('children')}
  for current,old in [('residential280','residential278'),('wasteland280','wasteland254')]:
   new=glb(LAB/'generated/phase2'/current/'environment.glb');previous=glb(LAB/'generated/phase2'/old/'environment.glb');self.assertEqual(roots(new),roots(previous))
  self.assertTrue(any(m['name']=='Original residential roof artwork' for m in glb(LAB/'generated/phase2/residential280/environment.glb')['materials']))

if __name__=='__main__':unittest.main()
