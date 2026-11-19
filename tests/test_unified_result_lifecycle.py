import shutil,subprocess
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('outcome',['victory','defeat','retreat'])
def test_godot_result_requires_confirmation_and_matching_ack(tmp_path,outcome):
    godot=shutil.which('godot')
    if not godot:pytest.skip('Godot unavailable')
    result=subprocess.run([godot,'--headless','--audio-driver','Dummy','--path',str(ROOT/'godot/combat_missions_ui'),'--script','tests/unified_result_lifecycle.gd','--','--output',str(tmp_path),'--outcome',outcome],capture_output=True,text=True,timeout=30)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output,output
    assert 'UNIFIED_RESULT_CONFIRMATION_PASSED '+outcome in output,output
