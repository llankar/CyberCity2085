"""Import explicit image-reviewed placements; never classify collision names.

Only a reviewed decision and an exact source hash permit adding a candidate.
The frame validator still rejects a placement whose sprite does not fit.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'godot/combat_missions_ui/art/environment'


def main():
    source = ART / 'environment_art.json'
    catalog = json.loads(source.read_text())
    reviews = json.loads((ART / 'expansion_reviews.json').read_text())
    count = 0
    for review in reviews['candidates']:
        key = 'art25_detail_' + review['source_object_id']
        # A later native review may revoke approval; remove its old managed entry.
        for name in review['aliases']:
            record=catalog['maps'][name]
            record['props']=[p for p in record['props'] if p['id']!=key]
        if review['decision'] != 'replace':
            continue
        assert review['visual_review'] == 'detail_crop_inspected'
        for name in review['aliases']:
            record = catalog['maps'][name]
            assert record['image_sha256'] == review['source_sha256']
            survey = json.loads((ROOT / 'assets/maps' / name.replace('.png', '.walls.json')).read_text())
            assert survey['image_sha256'] == review['source_sha256']
            assert review['source_object_id'] in {w['id'] for w in survey['walls']}
            prop = dict(id=key, source_object_id=review['source_object_id'],
                        asset=review['asset'], yaw=review.get('author_yaw', 0),
                        bounds_uv=review['bounds_uv'], enabled=False,
                        source_review='detail_crop_sheet', review_index=review['index'],
                        detail_status='pending_frame_and_native_validation')
            if 'author_yaw' in review:
                prop['author_yaw'] = review['author_yaw']
            if 'assembly' in review:
                prop['assembly'] = review['assembly']
            for optional in ['erase_overhang_uv','erase_bounds_uv','partial_source_object']:
                if optional in review:prop[optional]=review[optional]
            existing = [p for p in record['props'] if p['id'] != key]
            existing.append(prop)
            record['props'] = existing
            record['validation'].update(native_render='pending', picking_zoom='pending')
            count += 1
    source.write_text(json.dumps(catalog, indent=2) + '\n')
    print('REVIEWED_EXPANSION_IMPORTED', count)


if __name__ == '__main__':
    main()
