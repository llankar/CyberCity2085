"""Slice an approved 4x4 generated prop atlas; preserve Blender blocking sources.
No source-map image is read or modified. Columns are authored yaw 0/90/180/270.
"""
import argparse,json,shutil,hashlib
from collections import deque
from pathlib import Path
from PIL import Image,ImageChops,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'godot/combat_missions_ui/art/environment/props25'
NAMES=['sofa','console','wreck','rust_wreck']

def clean_alpha(frame):
    alpha=frame.getchannel('A');mask=alpha.point(lambda a:255 if a>=180 else 0)
    pixels=mask.load();components=[]
    for y in range(mask.height):
        for x in range(mask.width):
            if not pixels[x,y]:continue
            queue=deque([(x,y)]);pixels[x,y]=0;points=[]
            while queue:
                px,py=queue.popleft();points.append((px,py))
                for nx,ny in [(px-1,py),(px+1,py),(px,py-1),(px,py+1)]:
                    if 0<=nx<mask.width and 0<=ny<mask.height and pixels[nx,ny]:pixels[nx,ny]=0;queue.append((nx,ny))
            components.append(points)
    assert components,'Empty artist sprite'
    largest=max(map(len,components));keep=Image.new('L',frame.size);target=keep.load()
    for points in components:
        if len(points)>=max(64,largest*.02):
            for x,y in points:target[x,y]=255
    # Retain antialiasing around the actual connected silhouettes, not stray haze.
    keep=keep.filter(ImageFilter.MaxFilter(5));frame.putalpha(ImageChops.multiply(alpha,keep))
    return frame

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('atlas',type=Path);parser.add_argument('--families',default=','.join(NAMES));parser.add_argument('--name',default='artist_atlas.png');args=parser.parse_args()
    names=args.families.split(',');assert len(names)==4
    assert Path(args.name).name==args.name
    OUT.mkdir(parents=True,exist_ok=True);backup=OUT/'blender_blocking';backup.mkdir(exist_ok=True)
    source=Image.open(args.atlas).convert('RGBA')
    if args.atlas.resolve()!=(OUT/args.name).resolve():shutil.copyfile(args.atlas,OUT/args.name)
    for row,name in enumerate(names):
        for col,yaw in enumerate([0,90,180,270]):
            target=OUT/f'{name}-{yaw}.png'
            if target.exists() and not (backup/target.name).exists():shutil.copyfile(target,backup/target.name)
            box=(col*source.width//4,row*source.height//4,(col+1)*source.width//4,(row+1)*source.height//4)
            frame=clean_alpha(source.crop(box))
            bounds=frame.getbbox();assert bounds is not None
            assert bounds[0]>0 and bounds[1]>0 and bounds[2]<frame.width and bounds[3]<frame.height, f'{name}/{yaw}: clipped silhouette'
            frame.save(target)
    manifest=OUT/'library.json';data=json.loads(manifest.read_text())
    old=data.get('artist_variants',{})
    if 'source' in old:old={old['source']:old}
    data['artist_variants']=old
    data['artist_variants'][args.name]={'source':args.name,'source_sha256':hashlib.sha256(args.atlas.read_bytes()).hexdigest(),'families':names,'method':'Image-generation artwork finish from authored Blender atlas; separate transparent sprites','blender_sources':'Editable geometric blocking models, not an exact reconstruction of the finished artwork'}
    for name in names:
        data['assets'][name]['art_finish']='generated_artist_variant'
        data['assets'][name]['atlas_source']=args.name
    data['files']={}
    for family in data['assets']:
        for yaw in [0,90,180,270]:
            path=OUT/f'{family}-{yaw}.png'
            with Image.open(path) as frame:
                data['files'][path.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':list(frame.size),'alpha_bounds':list(frame.getchannel('A').getbbox())}
    manifest.write_text(json.dumps(data,indent=2)+'\n')
    print('ARTIST_VARIANTS_IMPORTED 16 transparent sprites')
if __name__=='__main__':main()
