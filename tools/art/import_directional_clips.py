"""Pack reviewed drawn poses. No reflected directions or synthetic walk frames."""
import argparse,hashlib,json,math,os,shutil,statistics
from pathlib import Path
from PIL import Image, ImageFilter
from import_artist_variants import clean_alpha
ROOT=Path(__file__).resolve().parents[2]
SOURCE_ROOT=Path(os.environ.get('CYBERCITY_SOURCE_ASSETS', ROOT.parent/'CyberCity2085-SourceAssets')).resolve()
SIZE=256;BASELINE=244;BODY=216

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def apply_chroma_key(image, key, inner=4, outer=255):
    """Turn a flat opaque backdrop into clean alpha and remove its edge colour."""
    if (not isinstance(key, list) or len(key) != 3
            or any(type(channel) is not int or not 0 <= channel <= 255 for channel in key)):
        raise ValueError('chroma_key must contain three RGB integers from 0 to 255')
    if (type(inner) is not int or type(outer) is not int
            or not 0 <= inner < outer <= 255):
        raise ValueError('chroma tolerances must satisfy 0 <= inner < outer <= 255')
    source=image.convert('RGBA');result=Image.new('RGBA',source.size);pixels=[]
    kr,kg,kb=key
    for red,green,blue,source_alpha in source.getdata():
        distance=max(abs(red-kr),abs(green-kg),abs(blue-kb))
        alpha=max(0,min(255,round((distance-inner)*255/(outer-inner))))
        alpha=round(alpha*source_alpha/255)
        if not alpha:
            pixels.append((0,0,0,0));continue
        fraction=alpha/255
        clean=list(max(0,min(255,round((value-(1-fraction)*backdrop)/fraction)))
                   for value,backdrop in ((red,kr),(green,kg),(blue,kb)))
        if alpha < 255:
            key_channels=[index for index,value in enumerate(key) if value >= 200]
            other_channels=[index for index,value in enumerate(key) if value <= 55]
            if key_channels and other_channels:
                cap=max(clean[index] for index in other_channels)+32
                for index in key_channels:clean[index]=min(clean[index],cap)
        pixels.append((*clean,alpha))
    result.putdata(pixels)
    return result

def apply_connected_chroma_key(image, key, inner=4, outer=255):
    """Key only backdrop-coloured pixels connected to the canvas border.

    This preserves enclosed light paint and highlights that happen to match a
    generated white backdrop.  OpenCV is imported lazily because ordinary
    transparent-sheet imports do not need it.
    """
    import cv2
    import numpy as np

    if (not isinstance(key, list) or len(key) != 3
            or any(type(channel) is not int or not 0 <= channel <= 255 for channel in key)):
        raise ValueError('chroma_key must contain three RGB integers from 0 to 255')
    if (type(inner) is not int or type(outer) is not int
            or not 0 <= inner < outer <= 255):
        raise ValueError('chroma tolerances must satisfy 0 <= inner < outer <= 255')
    rgba=np.asarray(image.convert('RGBA')).copy()
    distance=np.max(np.abs(rgba[:,:,:3].astype(np.int16)-np.array(key,dtype=np.int16)),axis=2)
    candidates=(distance < outer).astype(np.uint8)
    count,labels=cv2.connectedComponents(candidates,connectivity=4)
    border_labels=np.unique(np.concatenate((labels[0,:],labels[-1,:],labels[:,0],labels[:,-1])))
    connected=np.isin(labels,border_labels[border_labels != 0])
    alpha=np.full(distance.shape,255,dtype=np.float32)
    alpha[connected]=np.clip((distance[connected]-inner)*255/(outer-inner),0,255)
    alpha*=rgba[:,:,3]/255
    partial=connected & (alpha > 0) & (alpha < 255)
    fraction=np.maximum(alpha/255,1/255)
    for channel,backdrop in enumerate(key):
        cleaned=(rgba[:,:,channel]-(1-fraction)*backdrop)/fraction
        rgba[:,:,channel][partial]=np.clip(np.rint(cleaned[partial]),0,255).astype(np.uint8)
    rgba[:,:,3]=np.rint(alpha).astype(np.uint8)
    rgba[rgba[:,:,3] == 0,:3]=0
    return Image.fromarray(rgba)

def prepare_source(image,item):
    key=item.get('chroma_key')
    if key is None:return image
    if item.get('connected_chroma_key',False):
        return apply_connected_chroma_key(image,key,item.get('chroma_inner',4),item.get('chroma_outer',255))
    return apply_chroma_key(image,key,item.get('chroma_inner',4),item.get('chroma_outer',255))

def extract(image,row,col,trim_top=0,edge_erosion=0,grid_rows=4,clean_components=True):
    if type(grid_rows) is not int or grid_rows < 1:
        raise ValueError('grid_rows must be a positive integer')
    frame=image.crop((col*image.width//4,row*image.height//grid_rows,(col+1)*image.width//4,(row+1)*image.height//grid_rows)).convert('RGBA')
    if type(trim_top) is not int or not 0 <= trim_top < frame.height:
        raise ValueError('trim_top must be a nonnegative number of pixels within the cell')
    if trim_top:
        frame = frame.crop((0, trim_top, frame.width, frame.height))
    # Generated transparent backdrops can contain low-alpha grey haze. Keep
    # opaque anatomy, real antialiasing and connected details, not the backdrop.
    frame.putalpha(frame.getchannel('A').point(lambda a:max(0,min(255,round((a-160)*255/95)))))
    if clean_components:frame=clean_alpha(frame)
    if edge_erosion:
        frame.putalpha(frame.getchannel('A').filter(ImageFilter.MinFilter(2 * edge_erosion + 1)))
    bounds=frame.getchannel('A').getbbox()
    if not bounds:raise ValueError('Empty pose')
    return frame.crop(bounds)

def extract_grid(image,row,col,grid_cols,grid_rows,edge_erosion=0,clean_components=True):
    if min(grid_cols,grid_rows) < 1 or not (0 <= col < grid_cols and 0 <= row < grid_rows):
        raise ValueError('source cell must fit within the declared grid')
    frame=image.crop((col*image.width//grid_cols,row*image.height//grid_rows,
                      (col+1)*image.width//grid_cols,(row+1)*image.height//grid_rows)).convert('RGBA')
    frame.putalpha(frame.getchannel('A').point(lambda a:max(0,min(255,round((a-160)*255/95)))))
    if clean_components:frame=clean_alpha(frame)
    if edge_erosion:
        frame.putalpha(frame.getchannel('A').filter(ImageFilter.MinFilter(2*edge_erosion+1)))
    bounds=frame.getchannel('A').getbbox()
    if not bounds:raise ValueError('Empty pose')
    return frame.crop(bounds)

def validate_action_columns_rows(image):
    """Reject single-row art before it is sliced into torso/leg fragments."""
    alpha=image.getchannel('A')
    middle=image.height//2
    horizontal_ink=sum(alpha.getpixel((x,middle))>192 for x in range(image.width))
    if horizontal_ink > image.width*.01:
        raise ValueError(
            'action_columns requires two separated rows of eight poses; '
            'use single_row_pair with a complete follow-through sheet for 8x1 art')
    for boundary in range(1,8):
        x=boundary*image.width//8
        vertical_ink=sum(alpha.getpixel((x,y))>192 for y in range(image.height))
        if vertical_ink > image.height*.01:
            raise ValueError(
                'action_columns requires two separated rows of eight poses; '
                'use single_row_pair with a complete follow-through sheet for 8x1 art')
    for col in range(8):
        top=image.crop((col*image.width//8,0,(col+1)*image.width//8,image.height//2))
        bottom=image.crop((col*image.width//8,image.height//2,
                           (col+1)*image.width//8,image.height))
        top_bounds=top.getchannel('A').point(lambda alpha:255 if alpha>192 else 0).getbbox()
        bottom_bounds=bottom.getchannel('A').point(lambda alpha:255 if alpha>192 else 0).getbbox()
        if not top_bounds or not bottom_bounds:
            raise ValueError(
                'action_columns requires two separated rows of eight poses; '
                'use single_row_pair with a complete follow-through sheet for 8x1 art')

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
    directory=SOURCE_ROOT/'assets/combat_visual/source_sheets'/key;directory.mkdir(parents=True,exist_ok=True)
    clips={};provenance=[]
    for item in specs:
        source=Path(item['path']);name=item['clip']+'-'+item['layout']+'-'+str(len(provenance))+'.png';
        if source.resolve()!=(directory/name).resolve():shutil.copyfile(source,directory/name)
        image=prepare_source(Image.open(source).convert('RGBA'),item);layout=item['layout'];clip=item['clip']
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
            source_row_offset = item.get('source_row_offset', 0)
            grid_rows = item.get('grid_rows', 4)
            clean_components = not item.get('keep_disconnected_details', False)
            if (type(source_row_offset) is not int or source_row_offset < 0
                    or type(grid_rows) is not int or grid_rows < 1
                    or source_row_offset + max(poses) >= grid_rows):
                raise ValueError('walk source rows must fit within grid_rows')
            for row,direction in zip(poses, order):
                if direction in directions:raise ValueError(f'{clip}: repeated facing {direction}')
                source_row = row + source_row_offset
                erosion = item.get('edge_erosion', 0)
                if item.get('transpose', False):
                    directions[direction]=normalise([extract(image,col,source_row,edge_erosion=erosion,grid_rows=grid_rows,clean_components=clean_components) for col in range(4)], pose_height)
                else:
                    directions[direction]=normalise([extract(image,source_row,col,edge_erosion=erosion,grid_rows=grid_rows,clean_components=clean_components) for col in range(4)], pose_height)
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
        elif layout == 'action_columns':
            validate_action_columns_rows(image)
            order=sheet_directions(item,8)
            erosion=item.get('edge_erosion',0)
            clean_components=not item.get('keep_disconnected_details',False)
            for source_col,direction in enumerate(order):
                directions[direction]=normalise([
                    extract_grid(image,0,source_col,8,2,erosion,clean_components),
                    extract_grid(image,1,source_col,8,2,erosion,clean_components),
                ],pose_height)
        elif layout == 'single_row_pair':
            follow_source=Path(item['follow_through_path'])
            follow_dest=directory/(Path(name).stem+'-follow-through.png')
            if follow_source.resolve()!=follow_dest.resolve():
                shutil.copyfile(follow_source,follow_dest)
            follow_through=prepare_source(Image.open(follow_source).convert('RGBA'),item)
            order=sheet_directions(item,8)
            erosion=item.get('edge_erosion',0)
            clean_components=not item.get('keep_disconnected_details',False)
            for source_col,direction in enumerate(order):
                directions[direction]=normalise([
                    extract_grid(image,0,source_col,8,1,erosion,clean_components),
                    extract_grid(follow_through,0,source_col,8,1,erosion,clean_components),
                ],pose_height)
        elif layout == 'walk_columns':
            intermediate_source=Path(item['intermediate_path'])
            intermediate_dest=directory/(Path(name).stem+'-intermediate.png')
            if intermediate_source.resolve()!=intermediate_dest.resolve():
                shutil.copyfile(intermediate_source,intermediate_dest)
            intermediate=Image.open(intermediate_source).convert('RGBA')
            order=sheet_directions(item,8)
            for source_col,direction in enumerate(order):
                directions[direction]=normalise([
                    extract_grid(image,0,source_col,8,2),
                    extract_grid(intermediate,0,source_col,8,2),
                    extract_grid(image,1,source_col,8,2),
                    extract_grid(intermediate,1,source_col,8,2),
                ],pose_height)
        elif layout == 'single_row_walk':
            phase_sources=[Path(path) for path in item.get('phase_paths',[])]
            if len(phase_sources)!=3:
                raise ValueError('single_row_walk requires exactly three phase_paths after the lead path')
            phase_images=[image]
            phase_files=[]
            for phase_index,phase_source in enumerate(phase_sources,1):
                phase_dest=directory/(Path(name).stem+f'-phase-{phase_index}.png')
                if phase_source.resolve()!=phase_dest.resolve():
                    shutil.copyfile(phase_source,phase_dest)
                phase_images.append(prepare_source(Image.open(phase_source).convert('RGBA'),item))
                phase_files.append((phase_source,phase_dest))
            order=sheet_directions(item,8)
            erosion=item.get('edge_erosion',0)
            clean_components=not item.get('keep_disconnected_details',False)
            for source_col,direction in enumerate(order):
                directions[direction]=normalise([
                    extract_grid(phase,0,source_col,8,1,erosion,clean_components) for phase in phase_images
                ],pose_height)
        elif layout == 'walk_rows':
            order=sheet_directions(item,8)
            erosion=item.get('edge_erosion',0)
            clean_components=not item.get('keep_disconnected_details',False)
            for source_col,direction in enumerate(order):
                directions[direction]=normalise([
                    extract_grid(image,source_row,source_col,8,4,erosion,clean_components)
                    for source_row in range(4)
                ],pose_height)
        else:raise ValueError(layout)
        provenance.append(dict(file=(directory/name).relative_to(ROOT).as_posix(),sha256=digest(source),clip=clip,layout=layout,method='New drawn poses and viewpoints from original character reference; no flat-image rotation or mirrored facings.'))
        if 'direction_indices' in item:
            provenance[-1]['direction_indices']=order
        if layout in ('front', 'rear', 'action_rows', 'idle_pairs', 'action_pairs') and 'pose_indices' in item:
            provenance[-1]['pose_indices']=poses
        if layout in ('front', 'rear') and item.get('transpose', False):
            provenance[-1]['transpose']=True
        if layout in ('front', 'rear') and item.get('grid_rows', 4) != 4:
            provenance[-1]['grid_rows'] = item['grid_rows']
            provenance[-1]['source_row_offset'] = item.get('source_row_offset', 0)
        if layout in ('front','rear') and item.get('edge_erosion'):
            provenance[-1]['edge_erosion']=item['edge_erosion']
        if layout in ('front','rear','action_columns','single_row_pair','single_row_walk','walk_rows') and item.get('keep_disconnected_details'):
            provenance[-1]['keep_disconnected_details']=True
        if layout == 'action_rows' and item.get('follow_through_path'):
            provenance[-1]['follow_through'] = {
                'file': follow_dest.relative_to(ROOT).as_posix(), 'sha256': digest(follow_source)
            }
        if layout == 'action_rows' and item.get('lead_trim_top'):
            provenance[-1]['lead_trim_top'] = item['lead_trim_top']
        if layout == 'action_rows' and item.get('edge_erosion'):
            provenance[-1]['edge_erosion'] = item['edge_erosion']
        if layout == 'walk_columns':
            provenance[-1]['intermediate']={
                'file':intermediate_dest.relative_to(ROOT).as_posix(),
                'sha256':digest(intermediate_source),
            }
        if layout == 'single_row_pair':
            provenance[-1]['follow_through']={
                'file':follow_dest.relative_to(ROOT).as_posix(),
                'sha256':digest(follow_source),
            }
        if layout == 'single_row_walk':
            provenance[-1]['phases']=[{
                'file':phase_dest.relative_to(ROOT).as_posix(),
                'sha256':digest(phase_source),
            } for phase_source,phase_dest in phase_files]
        if layout in ('single_row_pair','single_row_walk','walk_rows') and item.get('edge_erosion'):
            provenance[-1]['edge_erosion']=item['edge_erosion']
        if item.get('chroma_key') is not None:
            provenance[-1]['chroma_key']=item['chroma_key']
            provenance[-1]['chroma_inner']=item.get('chroma_inner',4)
            provenance[-1]['chroma_outer']=item.get('chroma_outer',255)
            if item.get('connected_chroma_key',False):
                provenance[-1]['connected_chroma_key']=True
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
    data=dict(texture=path.relative_to(ROOT).as_posix(),texture_sha256=digest(path),frame_size=[SIZE,SIZE],anchor_uv=[.5,BASELINE/SIZE],reference_height_uv=body_height/SIZE,directions='E,SE,S,SW,W,NW,N,NE',animations=animations,source_image=original.relative_to(SOURCE_ROOT).as_posix(),source_sha256=digest(original),provenance=provenance,required_clips=required,non_applicable_clips=exemptions,coverage=coverage,missing_clips=missing,review_status=review_status)
    (out/(key+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    print('DRAWN_CLIPS_PACKED',key,len(files),'frames;',coverage,'action coverage')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('plan',type=Path);args=parser.parse_args()
    for key,specs in json.loads(args.plan.read_text()).items():build(key,specs)
