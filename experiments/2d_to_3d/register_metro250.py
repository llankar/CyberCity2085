"""Register standalone transit modules without overwriting other library work."""
import json
from pathlib import Path
from environment_library import LAB,OUT,digest

def main():
 folder=LAB/'generated/phase2/metro250';path=OUT/'library.json'
 library=json.loads(path.read_text(encoding='utf8'));assets={a['id']:a for a in library.get('assets',[])}
 for asset in json.loads((folder/'assets.json').read_text()):
  record=next(r for r in library['records'] if r['id']=='city_transit_subway_platform__'+asset['source_object_id'])
  asset.update(source_map=record['source_map'],source_image=record['context_crop'],source_sha256=digest(Path(record['context_crop'])),
   footprint_cells=record['footprint_cells'],glb_sha256=digest(Path(asset['models']['glb'])),
   variants=[],provenance='Source-guided procedural rigid transit module; existing PBR maps; no AI generation',
   textures=[str(LAB/'sources/environment169/blue_metal_plate/diff.jpg'),str(LAB/'sources/environment169/blue_metal_plate/rough.jpg'),str(folder/'source_display.png')],map_associations=[])
  assets[asset['id']]=asset
 library['assets']=list(assets.values());path.write_text(json.dumps(library,indent=2,ensure_ascii=False),encoding='utf8')
 print('TRANSIT_MODULES_REGISTERED',4)

if __name__=='__main__':main()
