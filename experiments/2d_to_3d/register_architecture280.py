"""Register the two reused facade parts with shared source, not duplicated scenes."""
import hashlib,json,struct
from environment_library import LAB,OUT

def main():
 folder=OUT/'assets/urban_facade280';source=folder/'source.blend';path=OUT/'library.json'
 data=json.loads(path.read_text(encoding='utf8'));assets={a['id']:a for a in data['assets']}
 for kind,filename in [('window','window.glb'),('door','entrance.glb')]:
  model=folder/filename;raw=model.read_bytes();size=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+size]);bounds=[]
  for mesh in gltf['meshes']:
   for primitive in mesh['primitives']:
    accessor=gltf['accessors'][primitive['attributes']['POSITION']];bounds.extend([accessor['min'],accessor['max']])
  identifier='urban_'+kind+'280'
  assets[identifier]={'id':identifier,'family':'Architecture','models':{'blend':str(source),'glb':str(model)},'dimensions':[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(3)],'anchor':'center_ground_normalized','orientation':'glTF Y up; facade width X','glb_sha256':hashlib.sha256(raw).hexdigest(),'source_model':str(LAB/'sources/environment169/modular_urban_apartments_facade/modular_urban_apartments_facade_1k.gltf'),'provenance':'Previously acquired genuine facade mesh, retained geometry with night-palette material variant; no IA generation','used_in':[{'map':'city_district_apartment_block','scene':str(LAB/'generated/phase2/residential280/environment.glb')}],'artistic_status':'ENSEMBLE_REVIEWED_PROTOTYPE','rights_note':'Retained acquisition source; no new distribution clearance asserted'}
 data['assets']=list(assets.values());path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
 print('ARCHITECTURE280_LIBRARY_REGISTERED two retained-geometry variants')

if __name__=='__main__':main()
