"""Compile inferred floor support strictly inside existing occupied tactical cells."""
from pathlib import Path
import json,hashlib
LAB=Path('E:/CyberCity2085-3d-lab')
def compile_plan(data):
 grid=data['grid'];assert len(grid)==2 and all(type(n) is int and n>0 for n in grid)
 cells=set()
 for wall in data['walls']:
  for cell in wall['cells']:
   if len(cell)!=2 or any(type(n) is not int for n in cell) or not (0<=cell[0]<grid[0] and 0<=cell[1]<grid[1]):raise ValueError('Invalid occupied cell')
   cells.add(tuple(cell))
 return {'grid':grid.copy(),'cells':[list(c) for c in sorted(cells)],'scope':'Inferred floor only inside existing occupied cells; no tactical mutation'}
if __name__=='__main__':
 source=LAB/'sources/tactical_map/city_exterior_neon_market_alley.walls.json';raw=source.read_bytes();plan=compile_plan(json.loads(raw))
 plan['walls_sha256']=hashlib.sha256(raw).hexdigest();plan['original_png_sha256']=hashlib.sha256((source.parent/'city_exterior_neon_market_alley.png').read_bytes()).hexdigest()
 out=LAB/'generated/phase2/floor244';out.mkdir(exist_ok=True);(out/'plan.json').write_text(json.dumps(plan,indent=2));assert source.read_bytes()==raw
 print('VOLUME_FLOOR_PLAN',len(plan['cells']))
