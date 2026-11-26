"""Remove source prop drawings only under surveyed replacement rectangles on E:."""
import json,hashlib,argparse
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];LAB=Path('E:/CyberCity2085-3d-lab')
NAME='city_interior_research_lab'

def prepare(source,survey):
    original=np.asarray(source.convert('RGB')).copy();height,width=original.shape[:2]
    mask=np.zeros((height,width),dtype=np.uint8)
    sx=width/survey['canvas_size'][0];sy=height/survey['canvas_size'][1]
    for item in survey['walls']:
        if item['id'] in ('west_wall','east_wall'):continue
        if item.get('kind') == 'water':continue
        if 'polygon' in item:
            points=np.array([[round(x*sx),round(y*sy)] for x,y in item['polygon']],dtype=np.int32)
            cv2.fillPoly(mask,[points],255)
        elif 'rect' in item:
            x1,y1,x2,y2=item['rect']
            mask[round(y1*sy):round(y2*sy),round(x1*sx):round(x2*sx)]=255
        elif 'points' in item:
            points=np.array([[round(x*sx),round(y*sy)] for x,y in item['points']],dtype=np.int32)
            cv2.polylines(mask,[points],False,255,max(1,round(item['width']*(sx+sy)/2)))
    # Inferred hidden floor, not recovered authentic art. Work at survey scale;
    # write back only masked pixels so original corridors are byte-identical.
    small=cv2.resize(original,tuple(survey['canvas_size']),interpolation=cv2.INTER_AREA)
    smallmask=cv2.resize(mask,tuple(survey['canvas_size']),interpolation=cv2.INTER_NEAREST)
    repaired=cv2.inpaint(small,smallmask,5,cv2.INPAINT_TELEA)
    repaired=cv2.resize(repaired,(width,height),interpolation=cv2.INTER_CUBIC)
    result=original.copy();result[mask>0]=repaired[mask>0]
    return Image.fromarray(result),mask

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map',default=NAME)
    parser.add_argument('--output',type=Path,default=LAB/'generated/phase2/lab248')
    parser.add_argument('--objects',help='Comma-separated identifiers of actual 3D replacements')
    args=parser.parse_args()
    if Path(args.map).name!=args.map or '/' in args.map or '\\' in args.map:raise ValueError('Invalid map identifier')
    source=ROOT/f'assets/maps/{args.map}.png';raw=source.read_bytes()
    survey=json.loads((ROOT/f'assets/maps/{args.map}.wall-traces.json').read_text())
    if args.objects:
        requested=set(args.objects.split(','));known={r['id'] for r in survey['walls']}
        if not requested<=known:raise ValueError('Unknown source object identifiers')
        survey['walls']=[r for r in survey['walls'] if r['id'] in requested]
    out=args.output.resolve()
    if not out.is_relative_to((LAB/'generated').resolve()):raise ValueError('Output must remain in E: generated experiments')
    out.mkdir(parents=True,exist_ok=True)
    result,mask=prepare(Image.open(source),survey);result.save(out/'floor.png')
    Image.fromarray(mask).save(out/'replacement_mask.png')
    assert source.read_bytes()==raw
    (out/'floor.json').write_text(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),'method':'Inferred floor only inside surveyed replacement rectangles; original corridors retained','masked_pixels':int(np.count_nonzero(mask))},indent=2))
    print('LAB248_FLOOR_PREPARED',int(np.count_nonzero(mask)))

if __name__=='__main__':main()
