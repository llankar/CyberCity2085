"""Grouped fixture reuse and the owner's open railway-exit invariant."""
import hashlib,json,struct,unittest
import numpy as np
from test_industry256 import LAB,glb

def exported_arrays(path):
 raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];data=json.loads(raw[20:20+size])
 def array(index,columns):
  a=data['accessors'][index];v=data['bufferViews'][a['bufferView']];dtype=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']])
  return np.ndarray((a['count'],columns),dtype=dtype,buffer=raw,offset=28+size+v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',columns*dtype.itemsize),dtype.itemsize))
 return data,array

class FixtureLot(unittest.TestCase):
 def test_all_three_parts_are_reused_in_both_assembled_maps(self):
  for folder in ['lab282','metro282']:
   model=glb(LAB/'generated/phase2'/folder/'environment.glb')
   for kind in ['duct','vent','cable']:
    matches=[n['mesh'] for n in model['nodes'] if 'Fixture282 '+kind in n.get('name','') and 'mesh' in n]
    self.assertGreaterEqual(len(matches),2);self.assertEqual(len(set(matches)),1)
 def test_fixtures_do_not_change_either_open_rail_end_wall(self):
  def geometry(folder):
   model,array=exported_arrays(LAB/'generated/phase2'/folder/'environment.glb');result={}
   for name in ['Occludable_west_wall','Occludable_east_wall']:
    root=next(n for n in model['nodes'] if n.get('name')==name);parts=[]
    for index in root['children']:
     node=model['nodes'][index]
     if 'mesh' not in node:continue
     for p in model['meshes'][node['mesh']]['primitives']:
      parts.append(hashlib.sha256(array(p['attributes']['POSITION'],3).tobytes()+array(p['indices'],1).tobytes()).hexdigest())
    result[name]=sorted(parts)
   return result
  self.assertEqual(geometry('metro270'),geometry('metro282'))

if __name__=='__main__':unittest.main()
