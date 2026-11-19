"""Pack reviewed drawn poses. No reflected directions or synthetic walk frames."""
import argparse,hashlib,json,math,shutil,statistics
from pathlib import Path
from PIL import Image
from import_artist_variants import clean_alpha
ROOT=Path(__file__).resolve().parents[2]
SIZE=256;BASELINE=244;BODY=216

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def extract(image,row,col):
    frame=image.crop((col*image.width//4,row*image.height//4,(col+1)*image.width//4,(row+1)*image.height//4)).convert('RGBA')
    # Generated transparent backdrops can contain low-alpha grey haze. Keep
    # opaque anatomy, real antialiasing and connected details, not the backdrop.
    frame.putalpha(frame.getchannel('A').point(lambda a:max(0,min(255,round((a-160)*255/95)))))
    frame=clean_alpha(frame);bounds=frame.getchannel('A').getbbox()
    if not bounds:raise ValueError('Empty pose')
    return frame.crop(bounds)

def feet_x(frame):
    alpha=frame.getchannel('A');top=round(frame.height*.86);weights=[]
    for x in range(frame.width):weights.append(sum(alpha.getpixel((x,y)) for y in range(top,frame.height)))
    total=sum(weights)
    if not total:return frame.width*.5
    return sum(x*w for x,w in enumerate(weights))/total

def normalise(frames):
    horizontal_limits=[]
    for frame in frames:
        anchor=feet_x(frame)
        if anchor>0:horizontal_limits.append((SIZE/2-2)/anchor)
        if frame.width-anchor>0:horizontal_limits.append((SIZE/2-2)/(frame.width-anchor))
    scale=min(BODY/statistics.median(f.height for f in frames),228/max(f.width for f in frames),*horizontal_limits)
    result=[]
    for source in frames:
        frame=source.resize((max(1,round(source.width*scale)),max(1,round(source.height*scale))),Image.Resampling.LANCZOS)
        x=round(SIZE/2-feet_x(source)*scale);y=BASELINE-frame.height
        if x<2 or x+frame.width>SIZE-2:raise ValueError('Weapon/body would be clipped; review the source framing')
        tile=Image.new('RGBA',(SIZE,SIZE));tile.paste(frame,(x,y));result.append(tile)
    return result

def sheet_directions(item, count, offset=0):
    """Map source rows or pose pairs to the engine's facing indices."""
    order = item.get('direction_indices', list(range(offset, offset + count)))
    if (not isinstance(order, list) or len(order) != count
            or any(type(index) is not int or not 0 <= index < 8 for index in order)
            or len(set(order)) != count):
        raise ValueError('direction_indices must contain distinct engine facings from 0 to 7')
    return order

def build(key,config):
    specs=config['clips'] if isinstance(config,dict) else config
    applicable=config.get('applicable_clips') if isinstance(config,dict) else None
    exemptions=config.get('non_applicable_clips',{}) if isinstance(config,dict) else {}
    review_status=config.get('review_status','native_review_pending') if isinstance(config,dict) else 'native_review_pending'
    directory=ROOT/'assets/combat_visual/source_sheets'/key;directory.mkdir(parents=True,exist_ok=True)
    clips={};provenance=[]
    for item in specs:
        source=Path(item['path']);name=item['clip']+'-'+item['layout']+'-'+str(len(provenance))+'.png';
        if source.resolve()!=(directory/name).resolve():shutil.copyfile(source,directory/name)
        image=Image.open(source).convert('RGBA');layout=item['layout'];clip=item['clip']
        directions=clips.setdefault(clip,{})
        if layout in ['front','rear']:
            order=sheet_directions(item,4,4 if layout=='rear' else 0)
            for row,direction in enumerate(order):
                if direction in directions:raise ValueError(f'{clip}: repeated facing {direction}')
                directions[direction]=normalise([extract(image,row,col) for col in range(4)])
        elif layout in ['idle_pairs','action_pairs']:
            order=sheet_directions(item,8)
            for pair,direction in enumerate(order):
                if direction in directions:raise ValueError(f'{clip}: repeated facing {direction}')
                row=pair//2;col=(pair%2)*2
                directions[direction]=normalise([extract(image,row,col),extract(image,row,col+1)])
        elif layout == 'action_rows':
            poses = item.get('pose_indices', list(range(8)))
            if not isinstance(poses, list) or not poses:
                raise ValueError('pose_indices must be a nonempty list')
            sheet_directions({'direction_indices': poses}, len(poses))
            order = sheet_directions(item, len(poses))
            for pose, direction in zip(poses, order):
                if direction in directions:
                    raise ValueError(f'{clip}: repeated facing {direction}')
                row, col = divmod(pose, 4)
                directions[direction] = normalise([
                    extract(image, row, col),
                    extract(image, row + 2, col),
                ])
        else:raise ValueError(layout)
        provenance.append(dict(file=(directory/name).relative_to(ROOT).as_posix(),sha256=digest(source),clip=clip,layout=layout,method='New drawn poses and viewpoints from original character reference; no flat-image rotation or mirrored facings.'))
        if 'direction_indices' in item:
            provenance[-1]['direction_indices']=order
        if layout == 'action_rows' and 'pose_indices' in item:
            provenance[-1]['pose_indices']=poses
    files=[];animations={}
    clip_order=['idle','move','fire','melee','cover','hit','death','psi','heal']
    for name in [clip for clip in clip_order if clip in clips]:
        directions=clips[name]
        if set(directions)!=set(range(8)):raise ValueError(name+': eight reviewed directions required')
        rows=[]
        for direction in range(8):
            row=[]
            for frame in directions[direction]:row.append(len(files));files.append(frame)
            rows.append(row)
        animations[name]=dict(fps=2 if name=='idle' else 8,loop=name in {'idle','move'},rows=rows)
    columns=8;atlas=Image.new('RGBA',(columns*SIZE,math.ceil(len(files)/columns)*SIZE))
    for i,frame in enumerate(files):atlas.paste(frame,((i%columns)*SIZE,(i//columns)*SIZE))
    out=ROOT/'assets/combat_visual/animations';out.mkdir(parents=True,exist_ok=True);path=out/(key+'.png');atlas.save(path)
    original=ROOT/'assets/units'/(key+'_512.png')
    required=applicable or clip_order
    missing=[clip for clip in required if clip not in animations]
    coverage='complete' if not missing else 'partial'
    data=dict(texture=path.relative_to(ROOT).as_posix(),texture_sha256=digest(path),frame_size=[SIZE,SIZE],anchor_uv=[.5,BASELINE/SIZE],reference_height_uv=BODY/SIZE,directions='E,SE,S,SW,W,NW,N,NE',animations=animations,source_image=original.relative_to(ROOT).as_posix(),source_sha256=digest(original),provenance=provenance,required_clips=required,non_applicable_clips=exemptions,coverage=coverage,missing_clips=missing,review_status=review_status)
    (out/(key+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    print('DRAWN_CLIPS_PACKED',key,len(files),'frames;',coverage,'action coverage')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('plan',type=Path);args=parser.parse_args()
    for key,specs in json.loads(args.plan.read_text()).items():build(key,specs)
