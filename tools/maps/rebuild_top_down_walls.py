"""Rebuild reviewed wall surveys from source traces; reject tactical changes.

The camera projection never changes texture_top_left coordinates. This command
reconstructs outlines/cells and validates source hashes before replacing files.
It will not silently overwrite a wall edited independently of its source trace.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from game.map_geometry import stroke_outline

def rebuild(image, stored, traces):
    width,height=traces['canvas_size']
    walls=[]
    for trace in traces['walls']:
        if 'rect' in trace:
            x0,y0,x1,y1=trace['rect'];outline=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
        else:
            outline=trace['polygon'] if 'polygon' in trace else stroke_outline(trace['points'],trace['width'])
        mask=Image.new('L',(width,height));ImageDraw.Draw(mask).polygon([tuple(p) for p in outline],fill=255)
        sampled=mask.resize((40,28),Image.Resampling.BOX)
        cells=[[x,y] for y in range(28) for x in range(40) if sampled.getpixel((x,y))>=45] if trace.get('collision',True) else []
        walls.append(dict(id=trace['id'],kind=trace.get('kind','solid_obstacle'),blocks_sight=trace.get('blocks_sight',True),reviewed=True,cells=cells,outline_uv=[[x/width,y/height] for x,y in outline]))
    regenerated=dict(stored,walls=walls)
    assert regenerated==stored,f'{image.name}: trace/survey discrepancy; manual review required, no tactical overwrite'
    with Image.open(image) as source:assert list(source.size)==stored['image_size']
    assert sha256(image.read_bytes()).hexdigest()==stored['image_sha256'],f'{image.name}: stale source'
    return regenerated

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps',type=Path,default=Path('assets/maps'))
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args();results=[];pending=[]
    for path in sorted(args.maps.glob('*.walls.json')):
        stored=json.loads(path.read_text());image=path.with_name(stored['image'])
        traces=json.loads(image.with_suffix('.wall-traces.json').read_text())
        result=rebuild(image,stored,traces)
        pending.append((path,result))
        results.append(dict(map=image.name,source_sha256=stored['image_sha256'],walls=len(result['walls']),vertices=sum(len(w.get('outline_uv',[])) for w in result['walls']),tactical_geometry_unchanged=True))
    # Validate the entire catalogue before replacing any survey.
    if args.write:
        for path,result in pending:
            # Preserve existing canonical formatting when already identical.
            # Reconstructing and writing the verified source bytes is idempotent.
            original=path.read_text();assert json.loads(original)==result
            path.write_text(original)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(dict(projection='source_top_down',coordinates='texture_top_left',regenerated=len(results),maps=results),indent=2)+'\n')
    print(f'WALL_REBUILD_PASSED {len(results)} maps, {sum(x["walls"] for x in results)} walls; source hashes and tactical geometry unchanged',flush=True)
if __name__=='__main__':main()
