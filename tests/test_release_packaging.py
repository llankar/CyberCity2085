from pathlib import Path
import json
import subprocess
import sys

from game import runtime


ROOT = Path(__file__).resolve().parents[1]


def test_release_spec_bundles_required_runtime_directories():
    spec = (ROOT / "CyberCity2085.spec").read_text(encoding="utf-8")
    for required in ('root / "assets"', 'root / "scenes"', 'root / "godot"'):
        assert required in spec
    assert 'name="CyberCity2085"' in spec
    assert 'contents_directory="."' in spec


def test_source_runtime_keeps_current_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runtime.sys, "frozen", False, raising=False)

    assert runtime.configure_runtime_directory() == tmp_path
    assert Path.cwd() == tmp_path


def test_actual_smoke_entry_point_runs_without_arcade_or_a_player_save(tmp_path):
    report_path = tmp_path / "smoke.json"
    script = "import sys; sys.modules['arcade'] = None; import main; raise SystemExit(main.main(sys.argv[1:]))"
    result = subprocess.run([sys.executable, "-c", script, "--smoke-test", "--smoke-report", str(report_path)],
                            cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "ok" and report["manual_maps"] == 122
    assert report["mp3_tracks"] >= 7 and report["save_roundtrip"]
    assert report["story_objectives_preserved"] == 15
    assert not report["game_window_opened"]
    assert report["battle"]["outcome"] == "victory" and report["battle"]["geometry_checked"]


def test_smoke_failure_writes_a_machine_readable_report(monkeypatch, tmp_path):
    import main
    import game.release_smoke as smoke
    monkeypatch.setattr(smoke, "build_battle_map_catalog", lambda: [])
    report_path = tmp_path / "failure.json"
    assert main.main(["--smoke-test", "--smoke-report", str(report_path)]) == 1
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "error" and "No bundled playable maps" in report["error"]


def test_godot_bundle_keeps_project_scripts_and_excludes_live_handoffs(tmp_path):
    from tools.packaging_helpers import godot_runtime_data
    directory = tmp_path / "godot"
    project = directory / "combat_missions_ui"
    for name in ("project.godot", "scripts/ui.gd", "runtime/godot_combat/mission_handoff.json", ".godot/editor/cache", "debug.log"):
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test", encoding="utf-8")
    files = godot_runtime_data(directory)
    assert {Path(source).name for source, destination in files} == {"project.godot", "ui.gd"}
    assert all(Path(destination).parts[0] == "godot" for source, destination in files)
