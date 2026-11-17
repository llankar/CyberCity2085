"""Run actual Godot geometry, HP, transport and complete-catalogue deployment checks."""
from pathlib import Path
import shutil
import subprocess
import pytest


@pytest.mark.parametrize('script,sentinel',[
    ('encounter_floor_regression.gd','ENCOUNTER_FLOOR_CHECKS_PASSED 122'),
    ('tactical_reference_regression.gd','TACTICAL_REFERENCE_CHECKS_PASSED'),
    ('combat_feedback_regression.gd','COMBAT_FEEDBACK_CHECKS_PASSED'),
    ('combat_polish_regression.gd','COMBAT_POLISH_CHECKS_PASSED'),
])
def test_runtime_contract(script, sentinel):
    executable = shutil.which('godot') or shutil.which('godot4')
    if not executable:
        pytest.skip('Godot runtime is required')
    project = Path(__file__).resolve().parents[1]/'godot/combat_missions_ui'
    result = subprocess.run([executable,'--headless','--path',str(project),'--script',f'tests/{script}','--quit-after','100'],capture_output=True,text=True,timeout=120)
    output = result.stdout+result.stderr
    assert result.returncode == 0, output
    assert 'SCRIPT ERROR' not in output, output
    assert sentinel in output, output
