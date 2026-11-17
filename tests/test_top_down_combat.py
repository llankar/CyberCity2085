"""Map art and unit scale share a reversible presentation-only projection."""
import json
from pathlib import Path
import shutil
import subprocess
import pytest
ROOT=Path(__file__).resolve().parents[1]

def test_all_maps_have_explicit_art_scale():
    data=json.loads((ROOT/'godot/combat_missions_ui/art/environment/map_presentation.json').read_text())
    expected={p.name.replace('.walls.json','.png') for p in (ROOT/'assets/maps').glob('*.walls.json')}
    assert set(data['maps'])==expected
    assert all(.015<=v['human_height_ratio']<=.10 for v in data['maps'].values())

def test_native_projection_wall_alignment_and_token_scale():
    executable=shutil.which('godot') or shutil.which('godot4')
    if not executable:pytest.skip('Godot unavailable')
    result=subprocess.run([executable,'--headless','--audio-driver','Dummy','--path',str(ROOT/'godot/combat_missions_ui'),'--script','tests/top_down_regression.gd','--quit-after','300'],capture_output=True,text=True,timeout=120)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output,output
    assert 'TOP_DOWN_CHECKS_PASSED 122' in output,output
