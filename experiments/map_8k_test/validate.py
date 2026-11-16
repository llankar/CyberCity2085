import json, hashlib
from pathlib import Path
from PIL import Image
from game.map_geometry import load_map_geometry
src=Path('assets/maps/city_exterior_neon_market_alley.png')
out=Path('experiments/map_8k_test/city_exterior_neon_market_alley_8k_test.png')
g=load_map_geometry(src)
assert g
new=json.loads(json.dumps(g))
new.update(image=out.name,image_size=[7680,4320],image_sha256=hashlib.sha256(out.read_bytes()).hexdigest())
out.with_suffix('.walls.json').write_text(json.dumps(new,indent=2)+'\n')
restored=load_map_geometry(out)
assert Image.open(out).size==(7680,4320)
assert restored['walls']==g['walls']
assert restored['grid']==g['grid']
assert hashlib.sha256(src.read_bytes()).hexdigest()==g['image_sha256']
report={'source':str(src),'source_size':[1920,1080],'restoration_native_size':[1672,941],'output_size':[7680,4320],'method':'Image restoration followed by Lanczos resize; NOT native 8K detail','wall_count':len(g['walls']),'geometry_unchanged':True,'original_hash_unchanged':True,'visual_collision_alignment':'Pending manual inspection; generated contours not guaranteed pixel-identical','production_enabled':False}
Path('experiments/map_8k_test/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
