"""Remove source prop drawings only under surveyed replacement rectangles on E:."""
import json,hashlib,argparse
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
ROOT=Path(__file__).resolve().parents[2];LAB=Path('E:/CyberCity2085-3d-lab')
NAME='city_interior_research_lab'

def prepare(source,survey,*,include_side_walls=False):
    original=np.asarray(source.convert('RGB')).copy();height,width=original.shape[:2]
    mask=np.zeros((height,width),dtype=np.uint8)
    sx=width/survey['canvas_size'][0];sy=height/survey['canvas_size'][1]
    for item in survey['walls']:
        if not include_side_walls and item['id'] in ('west_wall','east_wall'):continue
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


def restore_surface_detail(floor, mask, sample, tile_size):
    tile = sample.convert("L").resize((tile_size,tile_size), Image.Resampling.LANCZOS)
    soft = tile.filter(ImageFilter.GaussianBlur(max(1, tile_size*.035)))
    detail = ImageChops.subtract(tile, soft, scale=1.35, offset=128)
    texture = Image.new("L", floor.size, 128)
    for row, y in enumerate(range(0, floor.height, tile_size)):
        for column, x in enumerate(range(0, floor.width, tile_size)):
            piece = ImageOps.mirror(detail) if column % 2 else detail
            texture.paste(ImageOps.flip(piece) if row % 2 else piece, (x,y))
    textured = ImageChops.add(floor, Image.merge("RGB", (texture,texture,texture)), offset=-128)
    mask_image = Image.fromarray(mask)
    alpha = ImageChops.multiply(mask_image, mask_image.filter(ImageFilter.GaussianBlur(4)))
    return Image.composite(textured, floor, alpha)


TECH_MARKET_DONORS = {
    "western_canopy": (750, 228, 818, 318),
    "central_market_stall": (1010, 356, 1076, 436),
    "east_center_market": (1320, 616, 1414, 648),
    "south_center_market": (1062, 904, 1120, 980),
    "southeast_large_canopy": (1414, 836, 1460, 914),
}


def restore_donor_pavement(floor, original, survey, donors):
    floor = floor.copy()
    original = original.convert("RGB")
    cw, ch = survey["canvas_size"]
    sx, sy = floor.width/cw, floor.height/ch

    def pixel(point):
        return round(point[0]*sx), round(point[1]*sy)

    for row in survey["walls"]:
        if row["id"] not in donors:
            continue
        x1,y1,x2,y2 = donors[row["id"]]
        donor = original.crop((*pixel((x1,y1)), *pixel((x2,y2))))
        points = [pixel(point) for point in row["polygon"]]
        xs, ys = zip(*points)
        left, top = min(xs), min(ys)
        patch = Image.new("RGB", (max(xs)-left+1,max(ys)-top+1))
        mirror = ImageOps.mirror(donor)
        for iy,y in enumerate(range(0,patch.height,donor.height)):
            for ix,x in enumerate(range(0,patch.width,donor.width)):
                tile = mirror if ix % 2 else donor
                patch.paste(ImageOps.flip(tile) if iy % 2 else tile, (x,y))
        mask = Image.new("L", patch.size)
        ImageDraw.Draw(mask).polygon([(x-left,y-top) for x,y in points], fill=255)
        alpha = ImageChops.multiply(mask, mask.filter(ImageFilter.GaussianBlur(max(2, sx*2))))
        alpha = alpha.point(lambda value: round(value*.82))
        floor.paste(patch,(left,top),alpha)
    return floor

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map',default=NAME)
    parser.add_argument('--output',type=Path,default=LAB/'generated/phase2/lab248')
    parser.add_argument('--objects',help='Comma-separated identifiers of actual 3D replacements')
    parser.add_argument('--include-side-walls',action='store_true',help='Mask replaced east and west wall drawings')
    parser.add_argument('--decorative-rects', type=json.loads, default=[],
                        help='Additional decoration footprints in survey coordinates')
    parser.add_argument('--surface-detail', type=Path,
                        help='Apply fine material detail inside the repaired footprints')
    args=parser.parse_args()
    if Path(args.map).name!=args.map or '/' in args.map or '\\' in args.map:raise ValueError('Invalid map identifier')
    source=ROOT/f'assets/maps/{args.map}.png';raw=source.read_bytes()
    survey=json.loads((ROOT/f'assets/maps/{args.map}.wall-traces.json').read_text())
    if args.objects:
        requested=set(args.objects.split(','));known={r['id'] for r in survey['walls']}
        if not requested<=known:raise ValueError('Unknown source object identifiers')
        survey['walls']=[r for r in survey['walls'] if r['id'] in requested]
    survey['walls'].extend(args.decorative_rects)
    out=args.output.resolve()
    if not out.is_relative_to((LAB/'generated').resolve()):raise ValueError('Output must remain in E: generated experiments')
    out.mkdir(parents=True,exist_ok=True)
    original = Image.open(source)
    result,mask=prepare(original,survey,include_side_walls=args.include_side_walls)
    if args.map == "city_district_tech_market":
        result = restore_donor_pavement(result, original, survey, TECH_MARKET_DONORS)
        concrete = Image.open(LAB / "sources/environment169/concrete_wall_001/diff.jpg")
        ImageOps.colorize(concrete.convert("L"), "#151f27", "#667685").save(out / "facade_concrete.png")
    if args.surface_detail:
        result = restore_surface_detail(result, mask, Image.open(args.surface_detail), max(16, result.width//40))
    result.save(out/'floor.png')
    Image.fromarray(mask).save(out/'replacement_mask.png')
    assert source.read_bytes()==raw
    (out/'floor.json').write_text(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),'method':'Inferred floor only inside surveyed replacement rectangles; original corridors retained','masked_pixels':int(np.count_nonzero(mask))},indent=2))
    print('LAB248_FLOOR_PREPARED',int(np.count_nonzero(mask)))

if __name__=='__main__':main()
