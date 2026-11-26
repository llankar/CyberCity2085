"""Finish the production lot in sequence; defer all artistic renders to map review."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
LAB=Path('E:/CyberCity2085-3d-lab');SCRIPTS=Path(__file__).parent

def windows(path):
 if not path.startswith('/mnt/e/CyberCity2085-3d-lab/'):raise ValueError('Batch paths must stay on E: lab')
 return Path('E:/'+path[len('/mnt/e/'):])

def main():
 parser=argparse.ArgumentParser();parser.add_argument('manifest',type=Path);parser.add_argument('--refresh-materials',action='store_true');args=parser.parse_args()
 if not args.manifest.resolve().is_relative_to(LAB.resolve()):raise ValueError('Manifest must stay on E:')
 entries=json.loads(args.manifest.read_text())['assets']
 for entry in entries:
  paint=windows(entry['paint']);meta=entry['finish'];out=LAB/'environment-library/assets'/meta['id']
  report=json.loads((paint/'result.json').read_text());assert report['status']=='PASS'
  digest=hashlib.sha256((paint/'mesh.glb').read_bytes()).hexdigest()
  recipe=hashlib.sha256(json.dumps(meta,sort_keys=True).encode()).hexdigest()
  if (out/'asset.json').exists():
   old=json.loads((out/'asset.json').read_text())
   if old.get('finish_input_sha256')==digest and old.get('finish_recipe_sha256')==recipe and (out/'model.glb').exists():
    print('BATCH_FINISH_REUSED',meta['id']);continue
   if not args.refresh_materials or old.get('finish_input_sha256')!=digest:raise RuntimeError('Preserve existing output before changed rebuild: '+str(out))
  subprocess.run([sys.executable,str(SCRIPTS/'prepare_arm_material256.py'),'--source',str(paint/'colour.png'),'--output',str(out),'--surface',meta['surface'],'--keep-colour','--palette',meta.get('palette','none')],check=True)
  command=['powershell.exe','-NoProfile','-File',str(SCRIPTS/'run_blender.ps1'),'-Script','blender/finish_arm256.py','--source',str(paint/'mesh.glb'),'--output',str(out),'--asset-id',meta['id'],'--source-map',meta['map'],'--source-object',meta['object'],'--family',meta['family'],'--height',str(meta['height']),'--high-definition',str(windows(entry['shape'])/'mesh.glb'),'--reference-kind',meta['reference_kind'],'--anchor-kind','base']
  subprocess.run(command,check=True)
  data=json.loads((out/'asset.json').read_text());data['finish_input_sha256']=digest
  data['finish_recipe_sha256']=recipe
  data['original_or_inferred_reference']=str(windows(entry['reference']))
  (out/'asset.json').write_text(json.dumps(data,indent=2))
  print('BATCH_FINISH_EXPORTED',meta['id'],flush=True)

if __name__=='__main__':main()
