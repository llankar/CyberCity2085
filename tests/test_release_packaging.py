from pathlib import Path
import json
import subprocess
import sys
import pytest

from game import runtime


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_game_resolves_its_bundled_godot(tmp_path, monkeypatch):
    from game.combat import godot_bridge
    from tools.packaging_helpers import godot_executable_data

    executable = tmp_path / "bin" / "godot" / "Godot.exe"
    executable.parent.mkdir(parents=True)
    executable.touch()
    monkeypatch.setenv("CYBERCITY_PACKAGE_GODOT", str(executable))
    assert godot_executable_data() == [(str(executable), "bin/godot")]
    monkeypatch.setattr(godot_bridge.sys, "frozen", True, raising=False)
    monkeypatch.setattr(godot_bridge.sys, "executable", str(tmp_path / "CyberCity2085.exe"))
    assert godot_bridge.find_godot_executable() == str(executable)


def test_frozen_windows_smoke_rejects_missing_bundled_godot(tmp_path, monkeypatch):
    from game import release_smoke

    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "CyberCity2085.exe"))
    with pytest.raises(RuntimeError, match="Missing bundled Windows Godot executable"):
        release_smoke.run_smoke()


def test_release_spec_bundles_required_runtime_directories():
    spec = (ROOT / "CyberCity2085.spec").read_text(encoding="utf-8")
    for required in ('root / "assets"', 'root / "scenes"', 'root / "godot"'):
        assert required in spec
    assert 'name="CyberCity2085"' in spec
    assert 'contents_directory="."' in spec


def test_package_includes_atlases_and_map_art_without_authoring_sheets(tmp_path):
    from tools.packaging_helpers import runtime_asset_data

    assets = tmp_path / "assets"
    for name in ("combat_visual/animations", "combat_visual/source_sheets", "maps/presentation", "units"):
        (assets / name).mkdir(parents=True)
    (assets / "combat_visual/catalog.json").touch()
    (assets / "README.md").touch()

    assert dict(runtime_asset_data(assets)) == {
        str(assets / "README.md"): "assets",
        str(assets / "combat_visual/animations"): "assets/combat_visual/animations",
        str(assets / "combat_visual/catalog.json"): "assets/combat_visual",
        str(assets / "maps"): "assets/maps",
        str(assets / "units"): "assets/units",
    }


def test_release_assets_include_cyberware_atlas_directory():
    from tools.packaging_helpers import runtime_asset_data

    assets = ROOT / "assets"
    packaged = dict(runtime_asset_data(assets))
    assert str(assets / "ui") in packaged
    assert packaged[str(assets / "ui")] == "assets/ui"
    assert (assets / "ui/cyberware/cyberware_atlas.png").stat().st_size > 0


def test_arcade_version_data_is_a_file_in_the_package():
    from tools.packaging_helpers import normalize_arcade_data

    shader = ("arcade/resources/system/shader.glsl", "source/shader.glsl", "DATA")
    for destination in ("arcade/VERSION/VERSION", r"arcade\VERSION\VERSION", "arcade/VERSION"):
        assert normalize_arcade_data([(destination, "source/VERSION", "DATA"), shader]) == [
            ("arcade/VERSION", "source/VERSION", "DATA"), shader,
        ]


def test_campaign_qa_is_dispatched_only_when_driver_is_present(monkeypatch):
    import importlib
    from types import SimpleNamespace
    from unittest.mock import Mock
    import main

    loader = Mock(side_effect=ModuleNotFoundError(name="tools.check_campaign_return"))
    monkeypatch.setattr(importlib, "import_module", loader)
    assert main.main(["--qa-campaign", "--campaign-play"]) == 2
    loader.assert_called_once_with("tools.check_campaign_return")
    driver = Mock()
    loader.side_effect = None
    loader.return_value = SimpleNamespace(main=driver)
    assert main.main(["--qa-campaign", "--campaign-play"]) == 0
    driver.assert_called_once_with(["--campaign-play"])


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


def test_frozen_build_footer_retains_actual_packaged_identity(tmp_path, monkeypatch):
    from tools.packaging_helpers import build_identity_data
    from game import version
    data=build_identity_data(tmp_path,label="BUILD abc1234")
    stamp=Path(data[0][0])
    assert data[0][1]=="." and json.loads(stamp.read_text())["label"]=="BUILD abc1234"
    monkeypatch.setattr(version.sys,"frozen",True,raising=False)
    monkeypatch.setattr(version.sys,"_MEIPASS",str(stamp.parent),raising=False)
    monkeypatch.delenv("CYBERCITY_BUILD_REVISION",raising=False)
    monkeypatch.setattr(version,"version",lambda name: (_ for _ in ()).throw(version.PackageNotFoundError(name)))
    version.build_label.cache_clear()
    assert version.build_label()=="BUILD abc1234"
    version.build_label.cache_clear()
