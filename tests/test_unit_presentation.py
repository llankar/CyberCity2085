"""Visual categories must never change the underlying combat unit records."""
import shutil
import subprocess
from pathlib import Path
import pytest


def test_native_entity_scale_and_shadow_profiles_preserve_combat_records():
    executable=shutil.which('godot') or shutil.which('godot4')
    if not executable:pytest.skip('Godot runtime unavailable')
    project=Path(__file__).resolve().parents[1]/'godot/combat_missions_ui'
    result=subprocess.run([executable,'--headless','--audio-driver','Dummy','--path',str(project),
                           '--script','tests/unit_presentation_regression.gd','--quit-after','120'],
                          capture_output=True,text=True,timeout=30)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output,output
    assert 'UNIT_PRESENTATION_CHECKS_PASSED' in output,output
