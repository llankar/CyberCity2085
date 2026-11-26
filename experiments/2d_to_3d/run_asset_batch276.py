"""WSL production lot: keep one local IA pipeline loaded, review assembled maps later."""
import argparse,hashlib,json,sys
from pathlib import Path

LAB=Path('/mnt/e/CyberCity2085-3d-lab')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['shape','paint']);parser.add_argument('manifest',type=Path);args=parser.parse_args()
 if not args.manifest.resolve().is_relative_to(LAB):raise ValueError('Batch manifest must stay on E:')
 entries=json.loads(args.manifest.read_text())['assets']
 for entry in entries:
  for field in ['reference','shape','optimized','paint']:
   if not Path(entry[field]).resolve().is_relative_to(LAB):raise ValueError('Batch paths must stay on E:')
  for field in (['reference','optimized'] if args.stage=='paint' else ['reference']):
   if not Path(entry[field]).is_file():raise FileNotFoundError(entry[field])
 if args.stage=='shape':import run_hunyuan_shape as worker
 else:import run_hunyuan_paint168 as worker
 for entry in entries:
  print('ASSET_BATCH_START',args.stage,entry['id'],flush=True)
  if args.stage=='shape':
   sys.argv=['run_hunyuan_shape.py',entry.get('subject','industrial_machine'),'--reference',entry['reference'],'--output',entry['shape']]
  else:
   result=Path(entry['paint'])/'result.json'
   if result.exists():
    data=json.loads(result.read_text());model=Path(entry['paint'])/'mesh.glb'
    if data.get('status')=='PASS' and model.is_file() and data.get('glb_sha256')==hashlib.sha256(model.read_bytes()).hexdigest() and data.get('source_sha256')==hashlib.sha256(Path(entry['optimized']).read_bytes()).hexdigest() and data.get('reference_sha256')==hashlib.sha256(Path(entry['reference']).read_bytes()).hexdigest():
     print('ASSET_BATCH_REUSED_EXISTING',entry['id'],flush=True);continue
    raise RuntimeError('Preserve and diagnose previous result for '+entry['id'])
   sys.argv=['run_hunyuan_paint168.py','--local-only','--mesh',entry['optimized'],'--reference',entry['reference'],'--output',entry['paint'],'--label',entry['id']]
  worker.main()
  print('ASSET_BATCH_DONE',args.stage,entry['id'],flush=True)

if __name__=='__main__':main()
