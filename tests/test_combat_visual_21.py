"""Verify calibrated presentation against unchanged tactical rules on every map."""
from pathlib import Path
import shutil
import subprocess

import pytest


def test_complete_catalogue_projection_picking_and_unchanged_rules():
    executable = shutil.which("godot") or shutil.which("godot4")
    if not executable:
        pytest.skip("Godot unavailable")
    project = Path(__file__).resolve().parents[1] / "godot/combat_missions_ui"
    result = subprocess.run(
        [executable, "--headless", "--audio-driver", "Dummy", "--path", str(project),
         "--script", "tests/combat_21_regression.gd", "--quit-after", "300"],
        capture_output=True, text=True, timeout=120,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SCRIPT ERROR" not in output, output
    assert "SHADER ERROR" not in output, output
    assert "COMBAT_21_CATALOG_PASSED 122" in output, output
