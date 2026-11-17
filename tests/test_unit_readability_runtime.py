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


@pytest.mark.skipif(
    sys.platform != "linux" or not os.environ.get("DISPLAY"),
    reason="Native target presentation requires X11",
)
def test_reference_target_card_follows_enemy_and_blocks_click_through():
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
            "tests/capture_reference.gd",
            "--quit-after",
            "350",
            "--",
            "--target-reference",
        ],
        capture_output=True,
        text=True,
        timeout=45,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SCRIPT ERROR" not in output and "SHADER ERROR" not in output, output
    assert "UNIT_REFERENCE_PRESENTATION_CHECKS_PASSED" in output, output


@pytest.mark.skipif(
    sys.platform != "linux" or not os.environ.get("DISPLAY"),
    reason="Native depth comparison requires X11",
)
def test_depth_toggle_and_quality_preserve_camera_and_combat():
    executable = shutil.which("godot") or shutil.which("godot4")
    if not executable:
        pytest.skip("Godot runtime is required")
    project = Path(__file__).resolve().parents[1] / "godot/combat_missions_ui"
    result = subprocess.run(
        [executable, "--path", str(project), "--rendering-method", "gl_compatibility",
         "--audio-driver", "Dummy", "--script", "tests/capture_environment_depth.gd",
         "--quit-after", "500"], capture_output=True, text=True, timeout=90,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SCRIPT ERROR" not in output and "SHADER ERROR" not in output, output
    assert "DEPTH_COMPARISON_CAPTURE_PASSED" in output, output
