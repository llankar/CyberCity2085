"""Register the new industrial family with traceable original/inferred references."""
import json,argparse
from pathlib import Path
from environment_library import LAB,OUT,digest

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--asset-id',action='append')
 parser.add_argument('--placements',type=Path,default=LAB/'generated/phase2/factory257/placements.json')
 parser.add_argument('--inferred-folder',type=Path)
 args=parser.parse_args()
 path=OUT/'library.json';library=json.loads(path.read_text(encoding='utf8'))
 assets={a['id']:a for a in library.get('assets',[])}
 identifiers=args.asset_id or ['industrial_arm256','roller_conveyor256']
 for identifier in identifiers:
  folder=OUT/'assets'/identifier;asset=json.loads((folder/'asset.json').read_text())
  reference=next(r for r in library['records'] if r['id']==asset['source_map']+'__'+asset['source_object_id'])
  asset.update(original_reference=reference['context_crop'],source_reference_sha256=digest(Path(reference['context_crop'])),
   glb_sha256=digest(Path(asset['models']['glb'])),
   tactical_footprint={'policy':'Decorative geometry; canonical source map remains authoritative','source_group_cells':reference['footprint_cells']},
   variants=[],map_associations=[],used_in=[{'map':asset['source_map'],'placements':str(args.placements)}],
   artistic_status='NATIVE_REVIEWED_PROTOTYPE')
  if identifier=='industrial_arm256':
   asset['inferred_reference']=str(LAB/'sources/arm256/reference.png')
   asset['provenance_file']=str(LAB/'sources/arm256/provenance.json')
   asset['textures']=[str(folder/n) for n in ['albedo.png','roughness.png','metallic.png']]
  elif identifier=='roller_conveyor256':asset['textures']=[str(LAB/'sources/environment169/blue_metal_plate'/n) for n in ['diff.jpg','rough.jpg']]
  if args.inferred_folder:
   asset['inferred_reference']=str(args.inferred_folder/'reference.png')
   asset['provenance_file']=str(args.inferred_folder/'provenance.json')
  assets[identifier]=asset
 library['assets']=list(assets.values());path.write_text(json.dumps(library,indent=2,ensure_ascii=False),encoding='utf8')
 print('INDUSTRIAL_FAMILY_REGISTERED',len(identifiers),'reusable resources')

if __name__=='__main__':main()
