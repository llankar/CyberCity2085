"""CPU post-production for our Blender renders; source maps are never touched.
A 3x3 median removes isolated path-tracing speckles inside opaque materials.
Original alpha and antialiased silhouettes remain byte-identical.
"""
import argparse,json
from pathlib import Path
from PIL import Image,ImageFilter

def finish(path):
    with Image.open(path) as source:
        image=source.convert('RGBA');alpha=image.getchannel('A')
        rgb=image.convert('RGB');filtered=rgb.filter(ImageFilter.MedianFilter(3))
        interior=alpha.point(lambda a:255 if a>250 else 0)
        rgb=Image.composite(filtered,rgb,interior);rgb.putalpha(alpha)
        assert rgb.getchannel('A').tobytes()==alpha.tobytes()
        rgb.save(path)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path);parser.add_argument('--only',default='');args=parser.parse_args()
    allowed=Path(__file__).resolve().parents[2]/'godot/combat_missions_ui/art/environment'
    if not args.directory.resolve().is_relative_to(allowed.resolve()):parser.error('Only generated environment-art directories may be modified')
    manifest=args.directory/'library.json'
    data=json.loads(manifest.read_text()) if manifest.exists() else {'schema_version':1,'assets':{}}
    for path in args.directory.glob('*.png'):
        if not args.only or path.stem.startswith(args.only+'-'):finish(path)
    data['postproduction']='3x3 median on opaque material interiors only; original alpha retained'
    data['generator']='Blender 4.3 Cycles; editable .blend sources retain render settings'
    manifest.write_text(json.dumps(data,indent=2)+'\n')
    print('RENDER_FINISH_PASSED',len(list(args.directory.glob('*.png'))))
if __name__=='__main__':main()
