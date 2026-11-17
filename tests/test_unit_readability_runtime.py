"""Check real GPU pixels, including source alpha and atlas-frame parity."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import pytest


@pytest.mark.skipif(
    sys.platform != "linux" or not os.environ.get("DISPLAY"),
    reason="Native shader pixel checks require X11",
)
def test_living_units_are_solid_and_brighter_than_the_terrain():
    executable = shutil.which("godot") or shutil.which("godot4")
    if not executable:
        pytest.skip("Godot runtime is required")
    project = Path(__file__).resolve().parents[1] / "godot/combat_missions_ui"
    result = subprocess.run(
        [
            executable,
            "--path",
            str(project),
            "--rendering-method",
            "gl_compatibility",
            "--audio-driver",
            "Dummy",
            "--script",
            "tests/unit_readability_regression.gd",
            "--quit-after",
            "150",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SCRIPT ERROR" not in output and "SHADER ERROR" not in output, output
    assert "UNIT_READABILITY_CHECKS_PASSED" in output, output
