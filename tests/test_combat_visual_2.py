"""Behavioral checks for the visual layer and its honest asset gate."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest
from PIL import Image

from tools.audit_combat_visuals import validate_atlas, REQUIRED

ROOT = Path(__file__).resolve().parents[1]


def test_atlas_validator_rejects_duplicate_poses_and_directions(tmp_path):
    texture = tmp_path/'atlas.png'
    Image.new('RGBA',(16,16),(10,20,30,255)).save(texture)
    data = {'texture':'atlas.png','frame_size':[8,8], 'animations':{
        name:{'fps':8,'rows':[[0,0] for _ in range(8)]} for name in REQUIRED}}
    manifest = tmp_path/'unit.json'
    manifest.write_text(json.dumps(data))
    errors = validate_atlas(manifest,tmp_path)
    assert any('static/duplicate' in error for error in errors)
    assert any('duplicated directions' in error for error in errors)


def test_atlas_validator_rejects_missing_art_and_out_of_bounds(tmp_path):
    Image.new('RGBA',(8,8),(10,20,30,255)).save(tmp_path/'atlas.png')
    manifest = tmp_path/'unit.json'
    manifest.write_text(json.dumps({'texture':'atlas.png','frame_size':[8,8],
        'animations':{'idle':{'fps':8,'rows':[[0,4] for _ in range(8)]}}}))
    errors = validate_atlas(manifest,tmp_path)
    assert any('missing clip: death' in error for error in errors)
    assert any('out of bounds' in error for error in errors)


def test_atlas_validator_accepts_distinct_eight_direction_test_fixture(tmp_path):
    # Synthetic pixels exercise validation only; never shipped as character art.
    image = Image.new('RGBA',(16*8,8))
    for index in range(16):
        image.paste((index*10,255-index*10,index,255),(index*8,0,index*8+8,8))
    image.save(tmp_path/'atlas.png')
    manifest = tmp_path/'unit.json'
    manifest.write_text(json.dumps({'texture':'atlas.png','frame_size':[8,8],
        'animations':{name:{'fps':8,'rows':[[d*2,d*2+1] for d in range(8)]} for name in REQUIRED}}))
    assert validate_atlas(manifest,tmp_path) == []


def test_godot_visual_runtime_all_maps_actions_and_result(tmp_path):
    executable = shutil.which('godot') or shutil.which('godot4')
    if not executable: pytest.skip('Godot unavailable')
    from game.character import Character
    from game.gamestate import GameState
    from game.mission_templates import MissionTemplate
    from game.combat.godot_bridge import build_godot_combat_payload
    mission = MissionTemplate(id='visual_test',title='Visual regression',objective_text='Hack terminal',
        target_faction='Corp 37',district='Chrome',district_pressure={},starting_enemy_count=3,
        risk_level=3,objective_type='hack')
    state = GameState(characters=[Character('Vera')],selected_agent_names=['Vera'])
    payload = build_godot_combat_payload(state,mission)
    # Mission outputs from the test must stay isolated from the user's campaign.
    payload['asset_base_dir'] = str(ROOT)
    path = tmp_path/'mission_handoff.json'
    path.write_text(json.dumps(payload))
    result = subprocess.run([executable,'--headless','--audio-driver','Dummy','--path',
        str(ROOT/'godot/combat_missions_ui'),'--script','res://tests/visual_regression.gd',
        '--','--handoff',str(path),'--result-root',str(tmp_path)],capture_output=True,text=True,timeout=60,cwd=ROOT)
    output = result.stdout+result.stderr
    assert result.returncode == 0, output
    assert 'SCRIPT ERROR' not in output, output
    assert 'VISUAL_CHECK_FAILED' not in output, output
    assert 'failures=0' in output, output
    exported = json.loads((tmp_path/'runtime/godot_combat/mission_result.json').read_text())
    assert exported['schema_version'] == 1
    assert exported['outcome'] == 'victory'
