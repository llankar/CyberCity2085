"""Regression checks for the isolated Godot combat spike."""

from __future__ import annotations

import json
from pathlib import Path

SPIKE_ROOT = Path("experiments/godot_combat_spike")
STATE_SAMPLE = SPIKE_ROOT / "samples" / "mission_state.json"


def test_godot_spike_project_remains_outside_main_runtime() -> None:
    assert (SPIKE_ROOT / "project.godot").exists()
    spike_files = [
        path
        for path in SPIKE_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".gd", ".tscn", ".godot"}
    ]
    assert spike_files, "spike should contain a tiny Godot project"

    joined = "\n".join(path.read_text(encoding="utf-8") for path in spike_files)
    assert "res://" in joined
    assert "game/" not in joined
    assert "import arcade" not in joined.lower()
    assert "from arcade import" not in joined.lower()


def test_sample_state_matches_current_combat_state_contract() -> None:
    payload = json.loads(STATE_SAMPLE.read_text(encoding="utf-8"))

    assert payload["mission_id"] == "godot_combat_spike_01"
    assert payload["turn"] in {"player", "enemy"}
    assert payload["turn_number"] >= 1
    assert payload["result"] in {"in_progress", "victory", "defeat"}
    assert len(payload["units"]) == 4
    assert [unit["team"] for unit in payload["units"]].count("agent") == 2
    assert [unit["team"] for unit in payload["units"]].count("enemy") == 2

    required_unit_keys = {"id", "team", "role", "hp", "max_hp", "ap", "position"}
    for unit in payload["units"]:
        assert required_unit_keys <= unit.keys()
        assert isinstance(unit["id"], str) and unit["id"]
        assert unit["team"] in {"agent", "enemy"}
        assert 0 <= unit["hp"] <= unit["max_hp"]
        assert unit["ap"] >= 0
        assert set(unit["position"].keys()) == {"x", "y"}
        assert 0 <= unit["position"]["x"] < 8
        assert 0 <= unit["position"]["y"] < 6


def test_spike_documents_json_export_and_decision_gate() -> None:
    readme = (SPIKE_ROOT / "README.md").read_text(encoding="utf-8")
    report = Path("docs/gameplay/engine_evaluation.md").read_text(encoding="utf-8")

    for expected in ["mission_id", "units", "hp", "ap", "result"]:
        assert expected in readme
        assert expected in report
    assert "must remain disconnected" in readme
    assert "not branch" in report.lower()
