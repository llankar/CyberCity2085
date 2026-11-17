"""Optional real-Arcade interaction and screenshot regression."""

import json
import os
from pathlib import Path
import subprocess
import sys
import pytest


@pytest.mark.skipif(
    sys.platform != "linux" or not os.environ.get("DISPLAY"),
    reason="Real Arcade capture requires an X11 display",
)
def test_world_map_live_interactions_at_three_resolutions(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.check_world_map_visual",
            "--output",
            str(tmp_path),
        ],
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, "ALSOFT_DRIVERS": "null"},
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((tmp_path / "report.json").read_text())
    assert [c["size"] for c in report["checks"]] == [
        [1672, 941],
        [1280, 720],
        [1920, 1080],
    ]
    assert all(c["selections_checked"] == c["beacons"] == 12 for c in report["checks"])
    assert report["navigation_and_launch"] and report["bundled_font_verified"]
    assert len(list(tmp_path.glob("*.png"))) == 5
