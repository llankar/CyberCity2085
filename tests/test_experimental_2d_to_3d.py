from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "experiments" / "2d_to_3d"


def test_experiment_is_isolated_from_runtime():
    assert (LAB / "blender" / "process_mesh.py").is_file()
    assert (LAB / "godot" / "project.godot").is_file()
    assert not (LAB / "outputs").exists()


def test_godot_preview_loads_external_glb_without_hard_dependency():
    source = (LAB / "godot" / "preview.gd").read_text(encoding="utf-8")
    assert "GLTFDocument.new()" in source
    assert "--model=" in source
    assert "E:/CyberCity2085-3d-lab" in source

