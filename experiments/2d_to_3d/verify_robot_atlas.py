"""Verify rendered atlas packing, alpha margins and distinct action samples."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image, ImageChops

folder=Path(sys.argv[1]).resolve()
if folder.drive.upper() != 'E:':
    raise ValueError('Use the external experimental atlas folder')
manifest=json.loads((folder/'robot_walk_atlas.json').read_text())
sheet=Image.open(folder/manifest['texture']).convert('RGBA')
assert sheet.size==(1024,512)
checked=0
for direction,indices in enumerate(manifest['animations']['walk']['rows']):
    hashes=set()
    for sample,index in enumerate(indices):
        image=Image.open(folder/f'walk_d{direction}_f{sample}.png').convert('RGBA')
        bounds=image.getchannel('A').getbbox()
        assert bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<128 and bounds[3]<128
        hashes.add(hashlib.sha256(image.tobytes()).hexdigest())
        x,y=index%8,index//8
        packed=sheet.crop((x*128,y*128,(x+1)*128,(y+1)*128))
        difference=ImageChops.difference(image,packed)
        assert max(value[1] for value in difference.getextrema())<=1, (direction,sample)
        checked+=1
    assert len(hashes)==4
report={'frames_checked':checked,'directions':8,'distinct_frames_per_direction':4,
        'packing_pixel_tolerance':1,'alpha_margins':'PASS',
        'production_facing_mapping':'NOT VERIFIED','artistic_acceptance':'NOT VERIFIED'}
(folder/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ROBOT_ATLAS_VERIFIED',json.dumps(report))
