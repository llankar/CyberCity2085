"""Check rendered cell contrast on bright and dark terrain."""
import os
from pathlib import Path
import shutil
import subprocess
import pytest

@pytest.mark.skipif(not os.environ.get('DISPLAY'),reason='Native renderer requires a display')
def test_reachable_cells_have_visible_pixel_contrast():
    executable=shutil.which('godot') or shutil.which('godot4')
    if not executable:pytest.skip('Godot unavailable')
    project=Path(__file__).resolve().parents[1]/'godot/combat_missions_ui'
    result=subprocess.run([executable,'--path',str(project),'--rendering-method','gl_compatibility','--audio-driver','Dummy','--script','tests/movement_visibility_regression.gd','--quit-after','150'],capture_output=True,text=True,timeout=30)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output,output
    assert 'MOVEMENT_VISIBILITY_CHECKS_PASSED' in output,output
