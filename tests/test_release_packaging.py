from pathlib import Path

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
