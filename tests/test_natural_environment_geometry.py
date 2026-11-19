"""Natural-geometry annotations are image-bound render data, not collision edits."""
import hashlib
import json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'godot/combat_missions_ui/art/environment/natural_geometry.json'


def test_reviewed_geometry_is_bound_to_real_unchanged_source_art():
    data=json.loads(CATALOG.read_text())
    assert data['schema_version']==1 and data['coordinates']=='texture_top_left'
    count=0
    families=set()
    for name,record in data['maps'].items():
        image=ROOT/'assets/maps'/name
        assert hashlib.sha256(image.read_bytes()).hexdigest()==record['image_sha256']
        survey=json.loads(image.with_suffix('.walls.json').read_text())
        ids={w['id'] for w in survey['walls']}
        for key,prop in record['props'].items():
            assert key in ids
            assert 'cells' not in prop and 'outline_uv' not in prop
            assert prop['material'] in {'fabric','wood','metal','stone'}
            families.add(prop['family']);count+=1
            origin,u,v=prop['origin'],prop['axis_u'],prop['axis_v']
            assert abs(u[0]*v[1]-u[1]*v[0])>0
            for a,b in [(0,0),(0,1),(1,0),(1,1)]:
                assert all(0<=origin[i]+u[i]*a+v[i]*b<=1 for i in [0,1])
    assert count==28
    assert {'sofa','armchair','table','console','crate','machine','wall','partition','bench'}==families


def test_legacy_depth_is_retained_as_an_explicit_renderer_fallback():
    scene=(ROOT/'godot/combat_missions_ui/scripts/combat_mission_ui.gd').read_text()
    assert '--legacy-environment' in scene
    assert 'environment_depth_legacy.gd' in scene
    assert 'if depth!=null' in scene


def test_natural_volume_ignores_collision_polygons_and_does_not_classify_by_name():
    model=(ROOT/'godot/combat_missions_ui/scripts/environment_depth.gd').read_text()
    assert model.count('_collision_uvs')==1
    assert 'Catalog.annotation' in model
    assert '"sofa" in id' not in model and '"wall" in id' not in model
