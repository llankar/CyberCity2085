"""Record actual lot reuse and the rejected wreck fit without claiming map completion."""
import json,subprocess,sys
from pathlib import Path
from environment_library import LAB,OUT

def main():
 script=Path(__file__).parent/'register_industry256.py'
 subprocess.run([sys.executable,str(script),'--asset-id','cargo_crate274','--placements',str(LAB/'generated/phase2/factory278/placements.json'),'--original-reference',str(LAB/'sources/crate.png')],check=True)
 subprocess.run([sys.executable,str(script),'--asset-id','derelict_suv275','--placements',str(LAB/'generated/phase2/wasteland278/placements.json'),'--inferred-folder',str(LAB/'sources/wreck275')],check=True)
 path=OUT/'library.json';library=json.loads(path.read_text(encoding='utf8'));usage=[]
 for folder in ['factory278','residential278','wasteland278']:
  placement=LAB/'generated/phase2'/folder/'placements.json';data=json.loads(placement.read_text())
  usage.append({'map':data['map'],'placements':str(placement),'instances':len(data['instances']),'asset':data['instances'][0]['asset'],'fit':'SCALE_REJECTED' if folder=='wasteland278' else 'ENSEMBLE_REVIEWED_PROTOTYPE'})
 for asset in library['assets']:
  if asset['id']=='cargo_crate274':asset.update(used_in=[u for u in usage if u['asset']==asset['id']],artistic_status='ENSEMBLE_REVIEWED_PROTOTYPE')
  if asset['id']=='derelict_suv275':asset.update(used_in=[u for u in usage if u['asset']==asset['id']],artistic_status='NEEDS_COMPATIBLE_FOOTPRINT',map_fit_note='Retained reusable full-size mesh; original wreck_e footprint makes it implausibly small. Do not promote that map placement.')
 path.write_text(json.dumps(library,indent=2,ensure_ascii=False),encoding='utf8')
 print('PRODUCTION278_LIBRARY_USAGE',json.dumps(usage))

if __name__=='__main__':main()
