"""Reject sprite/frame mismatches rather than stretching an asset or lifting floor.
Uses already reviewed art annotations; never derives identity from collision IDs.
"""
import json,math
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'godot/combat_missions_ui/art/environment'

def main():
    path=ART/'environment_art.json';data=json.loads(path.read_text());enabled=0;rejected=0
    for name,record in data['maps'].items():
        for prop in record['props']:
            b=prop['bounds_uv'];w=(b[2]-b[0])*record['image_size'][0];h=(b[3]-b[1])*record['image_size'][1]
            choices=[]
            for yaw in [0,90,180,270]:
                p=ART/'props25'/f'{prop["asset"]}-{yaw}.png'
                with Image.open(p) as im:
                    box=im.getbbox();aw,ah=box[2]-box[0],box[3]-box[1]
                fit=min(w/aw,h/ah);coverage=aw*ah*fit*fit/(w*h)
                choices.append((coverage,-yaw,yaw))
            coverage,_,yaw=max(choices)
            prop['yaw']=yaw;prop['frame_coverage']=round(coverage,4)
            prop['enabled']=coverage>=.66
            prop['detail_status']='pending_native_review' if prop['enabled'] else 'original_retained_frame_mismatch'
            if prop['enabled']:enabled+=1
            else:rejected+=1
        improved={p['source_object_id'] for p in record['props'] if p['enabled'] and not p.get('partial_source_object',False)}
        survey=json.loads((ROOT/'assets/maps'/name.replace('.png','.walls.json')).read_text())
        record['remaining_2d']=[w['id'] for w in survey['walls'] if w['id'] not in improved]
        replaced={p['source_object_id'] for p in record['props'] if p['enabled']}
        record['source_foreground_layers']=[w['id'] for w in survey['walls'] if w['id'] not in replaced and w.get('blocks_sight',True)]
        record['art_status']='partial' if improved else 'source_layers_pending_matched_asset'
        record['issues']=['Architecture and remaining unmodelled objects retain source-art foreground layers.','Whole-map artistic completion is not claimed.']
        if any(not p['enabled'] for p in record['props']):record['issues'].append('Rejected mismatched sprite placement(s); source artwork retained.')
    path.write_text(json.dumps(data,indent=2)+'\n')
    print('PLACEMENT_REVIEW',enabled,'enabled;',rejected,'kept in original art')
if __name__=='__main__':main()
