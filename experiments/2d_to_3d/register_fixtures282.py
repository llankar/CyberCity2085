"""Register shared acquired fixture parts and actual per-map instance reuse."""
import hashlib,json
from pathlib import Path
from environment_library import LAB,OUT

def main():
 folder=OUT/'assets/wall_fixtures282';parts=json.loads((folder/'parts.json').read_text());path=OUT/'library.json';library=json.loads(path.read_text(encoding='utf8'));assets={a['id']:a for a in library['assets']}
 for part in parts:
  identifier=part['id']+'282';usage=[]
  for name in ['lab282','metro282']:
   placement=LAB/'generated/phase2'/name/'fixtures.json';data=json.loads(placement.read_text());instances=[r for r in data['instances'] if r['asset']==identifier]
   usage.append({'map':data['map'],'placements':str(placement),'instances':len(instances)})
  dx,dy,dz=part['dimensions_blender']
  assets[identifier]={'id':identifier,'family':'WallFixtures','models':{'blend':str(folder/'source.blend'),'glb':part['model']},'dimensions':[dx,dz,dy],'anchor':part['anchor'],'orientation':'glTF Y up; straight-part length X, vent face normal Y','source_model':part['source'],'source_node':part['source_node'],'glb_sha256':hashlib.sha256(Path(part['model']).read_bytes()).hexdigest(),'provenance':part['provenance'],'used_in':usage,'artistic_status':'ENSEMBLE_REVIEWED_PROTOTYPE','rights_note':'Existing acquisition source retained; no new distribution clearance asserted'}
 library['assets']=list(assets.values());path.write_text(json.dumps(library,indent=2,ensure_ascii=False),encoding='utf8')
 print('FIXTURES282_LIBRARY_REGISTERED three reused fixture parts, two map associations each')

if __name__=='__main__':main()
