"""Real view/engine input checks in a separate explicitly hidden GL process."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.skipif(sys.platform != "win32" and not os.environ.get("DISPLAY"),
                    reason="Hidden GL integration needs Windows or a display server")
@pytest.mark.parametrize("width,height,hide_log", [(960,640,False),(1280,720,True)])
def test_real_fire_input_flow_without_desktop_control(tmp_path, width, height, hide_log):
    output = tmp_path / "fire.png"
    command = [sys.executable,"-m","tools.render_tactical_snapshot","--output",str(output),
               "--width",str(width),"--height",str(height),"--deployment","--begin-battle",
               "--targeting","--exercise-fire","--settle-effects","--pan-x","64","--pan-y","-32"]
    if hide_log:
        command.append("--hide-log")
    process = subprocess.run(command,cwd=Path(__file__).resolve().parents[1],
                             capture_output=True,text=True,timeout=45)
    assert process.returncode == 0, process.stdout+process.stderr
    result = json.loads(process.stdout.strip().splitlines()[-1])
    assert result["visible_window"] is False and output.is_file()
    assert result["input_checks"]["actor_ap_after"] == result["input_checks"]["actor_ap_before"]-1
    assert result["input_checks"]["target_hp_after"] < result["input_checks"]["target_hp_before"]
    assert len(result["input_checks"]["checks"]) == 6
    assert result["input_checks"]["outgoing_edge_flash_alpha"] == 0
    assert result["omitted_captions"] == []
    assert result["sidebar_draws"] == {"target_lock":False,"combat_log":not hide_log,"initiative":hide_log}


@pytest.mark.skipif(sys.platform != "win32" and not os.environ.get("DISPLAY"),
                    reason="Hidden GL integration needs Windows or a display server")
@pytest.mark.parametrize("width,height", [(960,640),(1280,720)])
def test_real_end_confirmation_and_enemy_phase_return(tmp_path, width, height):
    output = tmp_path / "next_turn.png"
    process = subprocess.run(
        [sys.executable,"-m","tools.render_tactical_snapshot","--output",str(output),
         "--width",str(width),"--height",str(height),"--deployment","--begin-battle",
         "--exercise-turn","--pan-x","64","--pan-y","-32"],
        cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,timeout=45)
    assert process.returncode == 0, process.stdout+process.stderr
    result = json.loads(process.stdout.strip().splitlines()[-1])
    assert result["visible_window"] is False
    assert result["turn_checks"]["turn_after"] == result["turn_checks"]["turn_before"]+1
    assert result["turn_checks"]["next_phase"] == "player"
    assert len(result["turn_checks"]["agents_ended"]) == 4
    assert len(result["turn_checks"]["checks"]) == 4
    assert result["omitted_captions"] == []
