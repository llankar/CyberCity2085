"""Register two material variants of the shared wall family with actual GLB bounds."""
import json,struct,hashlib
from environment_library import LAB

def main():
 path=LAB/'environment-library/library.json';library=json.loads(path.read_text(encoding='utf8'));assets={a['id']:a for a in library['assets']}
 for variant in ['factory','metro']:
  folder=LAB/'environment-library/assets'/('service_wall269_'+variant)
  asset=json.loads((folder/'asset.json').read_text());raw=(folder/'model.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];model=json.loads(raw[20:20+length]);bounds=[]
  for node in model['nodes']:
   if 'mesh' not in node:continue
   shift=node.get('translation',[0,0,0])
   for primitive in model['meshes'][node['mesh']]['primitives']:
    a=model['accessors'][primitive['attributes']['POSITION']]
    bounds.extend([[a['min'][i]+shift[i] for i in range(3)],[a['max'][i]+shift[i] for i in range(3)]])
  asset['dimensions']=[max(p[i] for p in bounds)-min(p[i] for p in bounds) for i in range(3)]
  asset['glb_sha256']=hashlib.sha256(raw).hexdigest();asset['artistic_status']='NATIVE_REVIEWED_PROTOTYPE'
  asset['source_wall_groups']=json.loads((LAB/'generated/phase2'/(variant+'270')/'walls.json').read_text())['walls']
  asset['reconstruction_note']='Shared dimensioned family; individual source walls assembled at exact surveyed lengths, not stretched from a two-metre static model'
  assets[asset['id']]=asset
 library['assets']=list(assets.values());path.write_text(json.dumps(library,indent=2,ensure_ascii=False),encoding='utf8')
 print('WALL269_REGISTERED two material variants, nine source wall groups, one shared geometric family')

if __name__=='__main__':main()
