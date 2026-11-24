from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "experiments" / "2d_to_3d"


def test_experiment_is_isolated_from_runtime():
    assert (LAB / "blender" / "process_mesh.py").is_file()
    assert (LAB / "blender" / "render_atlas.py").is_file()
    assert (LAB / "blender" / "create_mpfb_character.py").is_file()
    assert (LAB / "godot" / "project.godot").is_file()
    assert not (LAB / "outputs").exists()


def test_godot_preview_loads_external_glb_without_hard_dependency():
    source = (LAB / "godot" / "preview.gd").read_text(encoding="utf-8")
    assert "GLTFDocument.new()" in source
    assert "--model=" in source
    assert "E:/CyberCity2085-3d-lab" in source


def test_atlas_renderer_has_eight_directions_and_transparency():
    source = (LAB / "blender" / "render_atlas.py").read_text(encoding="utf-8")
    assert "for index in range(8)" in source
    assert "film_transparent = True" in source
    assert "_atlas.png" in source


def test_mpfb_character_generator_keeps_large_outputs_on_external_drive():
    source = (LAB / "blender" / "create_mpfb_character.py").read_text(encoding="utf-8")
    assert 'path.drive.upper() != "E:"' in source
    assert 'add_builtin_rig(human, "game_engine"' in source
    assert 'export_format="GLB"' in source

