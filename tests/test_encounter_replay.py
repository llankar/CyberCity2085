"""Limited replays preserve cases/caps and never silently run another matrix."""

import json
import sys

from tools import simulate_encounters as cli


def test_limited_replay_only_runs_the_original_limited_case(monkeypatch, tmp_path):
    case = dict(map_file="city_industrial_dockside_terminal.png", theme="corp_37_robot", level=4,
                risk=5, count=6, seed=17, policy="objective_counterplay", layout="open",
                objective_kind="extract", turns=60, outcome="turn_limit")
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"combat_sources_sha256": "old-sources",
                                    "runs": [case, {**case, "outcome": "victory"}]}), encoding="utf-8")
    calls = []
    def simulate(**kwargs):
        calls.append(kwargs)
        return {"map_file": case["map_file"], "outcome": "victory"}
    def unrelated_matrix(_):
        raise AssertionError("Replay must not run the unrelated authored matrix")
    monkeypatch.setattr(cli, "simulate_encounter", simulate)
    monkeypatch.setattr(cli, "authored_rows", unrelated_matrix)
    output = tmp_path / "replayed.json"
    monkeypatch.setattr(sys, "argv", ["simulate", "--scenario", "authored", "--retest-limits", str(baseline), "--output", str(output)])
    assert cli.main() == 0
    assert len(calls) == 1
    assert calls[0]["seed"] == 17 and calls[0]["max_turns"] == 60
    assert calls[0]["policy"] == case["policy"] and calls[0]["objective_kind"] == "extract"
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["limited_retest_only"] and report["baseline_sources_sha256"] == "old-sources"
    assert report["summary"] == {"victory": 1} and len(report["runs"]) == 1
