"""Source-bound art coverage and real rendered-resource provenance."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import pytest
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'godot/combat_missions_ui/art/environment'

def test_every_map_has_reviewed_separate_art_and_an_honest_inventory():
    catalog=json.loads((ART/'environment_art.json').read_text())['maps']
    surveys=list((ROOT/'assets/maps').glob('*.walls.json'))
    assert len(catalog)==len(surveys)==122
    for p in surveys:
        source=json.loads(p.read_text());entry=catalog[source['image']]
        assert entry['image_sha256']==source['image_sha256']
        assert hashlib.sha256((p.parent/source['image']).read_bytes()).hexdigest()==entry['image_sha256']
        ids={x['id'] for x in source['walls']}
        assert entry['props'] and entry['validation']['artistically_complete'] is False
        improved=set()
        for prop in entry['props']:
            assert prop['source_object_id'] in ids
            if prop['enabled'] and not prop.get('partial_source_object',False):improved.add(prop['source_object_id'])
            assert prop['source_review'] in {'overview_contact_sheet','detail_crop_sheet'}
            assert all(0<=v<=1 for v in prop['bounds_uv'])
            assert 'cells' not in prop and 'blocks_sight' not in prop
            for yaw in [0,90,180,270]:assert (ART/'props25'/f'{prop["asset"]}-{yaw}.png').is_file()
            assert (ART/'props25'/f'{prop["asset"]}.blend').is_file()
        assert set(entry['remaining_2d'])==ids-improved

@pytest.mark.parametrize('script,sentinel',[
    ('environment_art25_regression.gd','ENVIRONMENT_ART25_CHECKS_PASSED 122'),
    ('weapon_balance_regression.gd','WEAPON_BALANCE_CHECKS_PASSED'),
])
def test_native_contract(script,sentinel):
    exe=shutil.which('godot') or shutil.which('godot4')
    if not exe:pytest.skip('Godot unavailable')
    result=subprocess.run([exe,'--headless','--audio-driver','Dummy','--path',str(ROOT/'godot/combat_missions_ui'),'--script','tests/'+script,'--quit-after','300'],capture_output=True,text=True,timeout=120)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output,output
    assert sentinel in output,output


def test_production_frames_have_real_transparency_and_complete_silhouettes():
    from PIL import Image
    library=json.loads((ART/'props25/library.json').read_text())
    assert len(library['assets'])==36
    for family in library['assets']:
        for yaw in [0,90,180,270]:
            with Image.open(ART/'props25'/f'{family}-{yaw}.png') as image:
                image.load()
                assert image.mode=='RGBA'
                alpha=image.getchannel('A');bounds=alpha.getbbox()
                # Generated RGBA can quantize an opaque interior to 254/255.
                assert bounds and alpha.getextrema()[0]==0 and alpha.getextrema()[1]>=250
                assert bounds[0]>0 and bounds[1]>0 and bounds[2]<image.width and bounds[3]<image.height


def test_expansion_decisions_are_visually_reviewed_and_bound_to_exact_art():
    reviews=json.loads((ART/'expansion_reviews.json').read_text())['candidates']
    catalog=json.loads((ART/'environment_art.json').read_text())['maps']
    assert len(reviews)==363
    for name,entry in catalog.items():
        for prop in entry['props']:
            if prop['source_review']!='detail_crop_sheet':continue
            review=reviews[prop['review_index']]
            assert review['visual_review']=='detail_crop_inspected'
            assert review['decision']=='replace'
            assert name in review['aliases'] and entry['image_sha256']==review['source_sha256']
            assert (prop['asset'],prop['source_object_id'],prop['bounds_uv'])==(review['asset'],review['source_object_id'],review['bounds_uv'])
            if prop['enabled'] and 'author_yaw' in prop:assert prop['yaw']==prop['author_yaw']
            if 'assembly' in prop:
                library=json.loads((ART/'props25/library.json').read_text())
                for key,value in prop['assembly'].items():assert library['assets'][prop['asset']]['assembly'][key]==value
            for polygon in prop.get('erase_overhang_uv',[]):
                assert len(polygon)>=3
                assert all(len(point)==2 and all(0<=v<=1 for v in point) for point in polygon)
            assert prop.get('erase_overhang_uv',[])==review.get('erase_overhang_uv',[])


def test_published_sprite_checksums_match_production_manifest():
    library=json.loads((ART/'props25/library.json').read_text())
    for key,record in library['files'].items():
        assert hashlib.sha256((ART/'props25'/key).read_bytes()).hexdigest()==record['sha256']


def test_reviewed_narrow_furniture_has_matching_capacity_and_facing():
    catalog=json.loads((ART/'environment_art.json').read_text())['maps']
    library=json.loads((ART/'props25/library.json').read_text())
    seen=set()
    for record in catalog.values():
        for prop in record['props']:
            family=prop['asset']
            if family not in {'single_bed','field_cot','transit_bench2','transit_bench4'}:continue
            if not prop['enabled']:continue
            seen.add(family)
            metadata=library['assets'][family]['assembly']
            if family in {'single_bed','field_cot'}:
                assert metadata['sleepers']==1 and metadata['pillows']==1
                assert prop['assembly']['sleepers']==1
            else:
                assert prop['assembly']['seats']==metadata['seats']
                assert 'metal' in metadata['material']
            assert prop['yaw']==prop['author_yaw']
    assert seen=={'single_bed','field_cot','transit_bench2','transit_bench4'}
    # This source bed faces left; the previous generic annotation faced upwards.
    shelter=catalog['wasteland_inner_07_apartment_shelter.png']
    left=next(p for p in shelter['props'] if p['source_object_id']=='bed_nw')
    assert left['asset']=='single_bed' and left['yaw']==90
