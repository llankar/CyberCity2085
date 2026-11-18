import hashlib,json
from pathlib import Path
from PIL import Image
from tools.audit_entity_scale import build_inventory,render_inventory


def fixture(root):
    maps=root/'assets/maps';maps.mkdir(parents=True)
    profiles={}
    for name,ratio in [('a.png',.03),('b.png',.05)]:
        image=maps/name;Image.new('RGB',(200,100),(40,60,80)).save(image)
        (maps/(Path(name).stem+'.walls.json')).write_text(json.dumps(dict(image=name,image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),image_size=[200,100])))
        profiles[name]=dict(profile='test',human_height_ratio=ratio)
    directory=root/'godot/combat_missions_ui/art/environment';directory.mkdir(parents=True)
    (directory/'map_presentation.json').write_text(json.dumps(dict(maps=profiles)))
    scripts=root/'godot/combat_missions_ui/scripts';scripts.mkdir(parents=True)
    for name in ['map_presentation.gd','unit_presentation.gd']:(scripts/name).write_text('fixture')


def test_shared_art_conflicting_estimates_are_flagged_not_validated(tmp_path):
    fixture(tmp_path);r=build_inventory(tmp_path,2)
    assert r['surveyed_maps']==2 and r['distinct_source_images']==1
    assert r['shared_art'][0]['conflicting_estimates']
    assert r['verified_scale_maps']==0
    assert all(row['anchors']==[] and row['calibration_status']=='NOT VERIFIED' for row in r['maps'])
    assert r['maps'][0]['standing_human_source_pixel_equivalent']==6
    assert 'NOT VERIFIED' in render_inventory(r)


def test_inventory_reports_source_integrity_and_missing_images(tmp_path):
    fixture(tmp_path);Image.new('RGB',(10,10)).save(tmp_path/'assets/maps/a.png')
    (tmp_path/'assets/maps/b.png').unlink()
    r=build_inventory(tmp_path,2)
    assert r['source_integrity_issues']==2 and r['verified_scale_maps']==0


def test_inventory_is_read_only_and_preserves_existing_files(tmp_path):
    fixture(tmp_path);before={p.relative_to(tmp_path):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    build_inventory(tmp_path,2)
    after={p.relative_to(tmp_path):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert before==after


def test_runtime_clamp_is_reported_without_applying_a_correction(tmp_path):
    fixture(tmp_path);p=tmp_path/'godot/combat_missions_ui/art/environment/map_presentation.json';data=json.loads(p.read_text());data['maps']['a.png']['human_height_ratio']=.002;p.write_text(json.dumps(data))
    r=build_inventory(tmp_path,2);row=r['maps'][0]
    assert row['configured_human_ratio']==.002 and row['current_human_ratio']==.015
    assert row['calibration_status']=='NOT VERIFIED' and row['issues']
