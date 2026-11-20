"""Pack reviewed drawn poses. No reflected directions or synthetic walk frames."""
import argparse,hashlib,json,math,shutil,statistics
from pathlib import Path
from PIL import Image, ImageFilter
from import_artist_variants import clean_alpha
ROOT=Path(__file__).resolve().parents[2]
SIZE=256;BASELINE=244;BODY=216

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def extract(image,row,col,trim_top=0,edge_erosion=0):
    frame=image.crop((col*image.width//4,row*image.height//4,(col+1)*image.width//4,(row+1)*image.height//4)).convert('RGBA')
    if type(trim_top) is not int or not 0 <= trim_top < frame.height:
        raise ValueError('trim_top must be a nonnegative number of pixels within the cell')
    if trim_top:
        frame = frame.crop((0, trim_top, frame.width, frame.height))
    # Generated transparent backdrops can contain low-alpha grey haze. Keep
    # opaque anatomy, real antialiasing and connected details, not the backdrop.
    frame.putalpha(frame.getchannel('A').point(lambda a:max(0,min(255,round((a-160)*255/95)))))
    frame=clean_alpha(frame)
    if edge_erosion:
        frame.putalpha(frame.getchannel('A').filter(ImageFilter.MinFilter(2 * edge_erosion + 1)))
    bounds=frame.getchannel('A').getbbox()
    if not bounds:raise ValueError('Empty pose')
    return frame.crop(bounds)

def feet_x(frame):
    alpha=frame.getchannel('A');top=round(frame.height*.86);weights=[]
    for x in range(frame.width):weights.append(sum(alpha.getpixel((x,y)) for y in range(top,frame.height)))
    total=sum(weights)
    if not total:return frame.width*.5
    return sum(x*w for x,w in enumerate(weights))/total

def normalise(frames, body_height=BODY):
    horizontal_limits=[]
    for frame in frames:
        anchor=feet_x(frame)
        if anchor>0:horizontal_limits.append((SIZE/2-2)/anchor)
        if frame.width-anchor>0:horizontal_limits.append((SIZE/2-2)/(frame.width-anchor))
    scale=min(body_height/statistics.median(f.height for f in frames),228/max(f.width for f in frames),*horizontal_limits)
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
    body_height=config.get('body_height', BODY) if isinstance(config,dict) else BODY
    if type(body_height) is not int or not 1 <= body_height <= BODY:
        raise ValueError('body_height must be an integer between 1 and the default body height')
    directory=ROOT/'assets/combat_visual/source_sheets'/key;directory.mkdir(parents=True,exist_ok=True)
    clips={};provenance=[]
    for item in specs:
        source=Path(item['path']);name=item['clip']+'-'+item['layout']+'-'+str(len(provenance))+'.png';
        if source.resolve()!=(directory/name).resolve():shutil.copyfile(source,directory/name)
        image=Image.open(source).convert('RGBA');layout=item['layout'];clip=item['clip']
        pose_height = item.get('body_height', body_height)
        if type(pose_height) is not int or not 1 <= pose_height <= BODY:
            raise ValueError(f'{clip}: body_height must be an integer between 1 and the default body height')
        directions=clips.setdefault(clip,{})
        if layout in ['front','rear']:
            poses = item.get('pose_indices', list(range(4)))
            if (not isinstance(poses, list) or not poses
                    or any(type(row) is not int or not 0 <= row < 4 for row in poses)
                    or len(set(poses)) != len(poses)):
                raise ValueError('walk pose_indices must be distinct rows or columns from 0 to 3')
            offset = 4 if layout == 'rear' else 0
            order = sheet_directions(item, len(poses), offset) if 'direction_indices' in item else [row + offset for row in poses]
            for row,direction in zip(poses, order):
                if direction in directions:raise ValueError(f'{clip}: repeated facing {direction}')
                if item.get('transpose', False):
                    directions[direction]=normalise([extract(image,col,row) for col in range(4)], pose_height)
                else:
                    directions[direction]=normalise([extract(image,row,col) for col in range(4)], pose_height)
        elif layout in ['idle_pairs','action_pairs']:
            poses = item.get('pose_indices', list(range(8)))
            if not isinstance(poses, list) or not poses:
                raise ValueError('pose_indices must be a nonempty list')
            sheet_directions({'direction_indices': poses}, len(poses))
            order=sheet_directions(item,len(poses))
            for pair,direction in zip(poses, order):
                if direction in directions:raise ValueError(f'{clip}: repeated facing {direction}')
                row=pair//2;col=(pair%2)*2
                directions[direction]=normalise([extract(image,row,col),extract(image,row,col+1)], pose_height)
        elif layout == 'action_rows':
            follow_through = image
            follow_source = item.get('follow_through_path')
            if follow_source:
                follow_source = Path(follow_source)
                follow_dest = directory / (Path(name).stem + '-follow-through.png')
                if follow_source.resolve() != follow_dest.resolve():
                    shutil.copyfile(follow_source, follow_dest)
                follow_through = Image.open(follow_source).convert('RGBA')
            poses = item.get('pose_indices', list(range(8)))
            if not isinstance(poses, list) or not poses:
                raise ValueError('pose_indices must be a nonempty list')
            sheet_directions({'direction_indices': poses}, len(poses))
            order = sheet_directions(item, len(poses))
            for pose, direction in zip(poses, order):
                if direction in directions:
                    raise ValueError(f'{clip}: repeated facing {direction}')
                row, col = divmod(pose, 4)
                erosion = item.get('edge_erosion', 0)
                directions[direction] = normalise([
                    extract(image, row, col, item.get('lead_trim_top', 0), erosion),
                    extract(follow_through, row + 2, col, edge_erosion=erosion),
                ], pose_height)
        else:raise ValueError(layout)
        provenance.append(dict(file=(directory/name).relative_to(ROOT).as_posix(),sha256=digest(source),clip=clip,layout=layout,method='New drawn poses and viewpoints from original character reference; no flat-image rotation or mirrored facings.'))
        if 'direction_indices' in item:
            provenance[-1]['direction_indices']=order
        if layout in ('front', 'rear', 'action_rows', 'idle_pairs', 'action_pairs') and 'pose_indices' in item:
            provenance[-1]['pose_indices']=poses
        if layout in ('front', 'rear') and item.get('transpose', False):
            provenance[-1]['transpose']=True
        if layout == 'action_rows' and item.get('follow_through_path'):
            provenance[-1]['follow_through'] = {
                'file': follow_dest.relative_to(ROOT).as_posix(), 'sha256': digest(follow_source)
            }
        if layout == 'action_rows' and item.get('lead_trim_top'):
            provenance[-1]['lead_trim_top'] = item['lead_trim_top']
        if layout == 'action_rows' and item.get('edge_erosion'):
            provenance[-1]['edge_erosion'] = item['edge_erosion']
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
    data=dict(texture=path.relative_to(ROOT).as_posix(),texture_sha256=digest(path),frame_size=[SIZE,SIZE],anchor_uv=[.5,BASELINE/SIZE],reference_height_uv=body_height/SIZE,directions='E,SE,S,SW,W,NW,N,NE',animations=animations,source_image=original.relative_to(ROOT).as_posix(),source_sha256=digest(original),provenance=provenance,required_clips=required,non_applicable_clips=exemptions,coverage=coverage,missing_clips=missing,review_status=review_status)
    (out/(key+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    print('DRAWN_CLIPS_PACKED',key,len(files),'frames;',coverage,'action coverage')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('plan',type=Path);args=parser.parse_args()
    for key,specs in json.loads(args.plan.read_text()).items():build(key,specs)
