from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from game.character import Character
from game.combat.godot_bridge import _agent_payload, find_godot_executable


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "godot" / "combat_missions_ui"


def test_godot_handoff_carries_cybereyes_vision_range():
    assert _agent_payload(Character("Baseline", role="sniper"))["vision_range"] == 15
    assert _agent_payload(
        Character("Scout", role="sniper", installed_cyberware=["smart_eye"])
    )["vision_range"] == 16
    assert _agent_payload(
        Character("Hunter", role="sniper", installed_cyberware=["predator_optics"])
    )["vision_range"] == 17
    assert _agent_payload(
        Character("Oracle", role="sniper", installed_cyberware=["omniscient_optics"])
    )["vision_range"] == 18


def test_godot_fog_los_and_enemy_awareness_regression():
    executable = find_godot_executable()
    if not executable:
        pytest.skip("Godot executable unavailable")
    executable_path = Path(executable)
    console_executable = executable_path.with_name(executable_path.stem + "_console.exe")
    if console_executable.exists():
        executable = str(console_executable)
    result = subprocess.run(
        [
            executable,
            "--headless",
            "--audio-driver",
            "Dummy",
            "--path",
            str(PROJECT),
            "--script",
            "tests/fog_of_war_regression.gd",
            "--quit-after",
            "500",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SCRIPT ERROR:" not in output, output
    assert "GODOT_FOG_OF_WAR_CHECKS_PASSED" in output, output
