"""Escape dismisses overlays without exiting the real Godot battle scene."""
from pathlib import Path
import shutil
import subprocess
import pytest

def test_escape_keeps_battle_running_in_both_huds():
    executable=shutil.which('godot') or shutil.which('godot4')
    if not executable:pytest.skip('Godot unavailable')
    project=Path(__file__).resolve().parents[1]/'godot/combat_missions_ui'
    result=subprocess.run([executable,'--headless','--audio-driver','Dummy','--path',str(project),'--script','tests/escape_combat_regression.gd','--quit-after','500'],capture_output=True,text=True,timeout=60)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output,output
    assert 'ESCAPE_COMBAT_CHECKS_PASSED' in output,output
