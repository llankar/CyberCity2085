from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "experiments" / "2d_to_3d"


def test_sprite_review_uses_current_top_down_zoom_formula():
    import importlib.util
    import pytest
    spec = importlib.util.spec_from_file_location('sprite_review', LAB / 'prepare_sprite_review.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.combat_heights(1920, 1080, 7680, 4320, .015)
    assert result['overview_zoom'] == pytest.approx(.18)
    assert result['close_zoom'] == pytest.approx(.54)
    assert result['overview_human_px'] == pytest.approx(20.736)
    assert result['close_human_px'] == pytest.approx(62.208)


def test_material_tint_preserves_binary_geometry_chunks():
    import importlib.util
    import json
    import struct
    spec = importlib.util.spec_from_file_location('glb_factors', LAB / 'blender' / 'glb_material_factors.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = json.dumps({'materials': [{'name': 'armor_helios.002'}]}).encode()
    payload += b' ' * (-len(payload) % 4)
    tail = struct.pack('<II', 4, 0x004E4942) + b'ABCD'
    class MemoryFile:
        data = struct.pack('<III', 0x46546C67, 2, 20 + len(payload) + len(tail)) + struct.pack('<II', len(payload), 0x4E4F534A) + payload + tail
        def read_bytes(self):
            return self.data
        def write_bytes(self, data):
            self.data = data
    file = MemoryFile()
    factor = [0.1, 0.2, 0.3, 1]
    assert module.apply_material_factors(file, {'armor_helios': factor}) == ['armor_helios.002']
    size = struct.unpack_from('<I', file.data, 12)[0]
    assert json.loads(file.data[20:20 + size])['materials'][0]['pbrMetallicRoughness']['baseColorFactor'] == factor
    assert file.data[20 + size:] == tail
    assert struct.unpack_from('<I', file.data, 8)[0] == len(file.data)


def test_experiment_is_isolated_from_runtime():
    assert (LAB / "blender" / "process_mesh.py").is_file()
    assert (LAB / "blender" / "render_atlas.py").is_file()
    assert (LAB / "blender" / "create_mpfb_character.py").is_file()
    assert (LAB / "blender" / "create_hardsurface_crate.py").is_file()
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


def test_procedural_crate_is_real_geometry_and_external_only():
    source = (LAB / "blender" / "create_hardsurface_crate.py").read_text(encoding="utf-8")
    assert 'output.drive.upper() != "E:"' in source
    assert 'primitive_cube_add' in source
    assert 'modifier = obj.modifiers.new("EdgeBevel", "BEVEL")' in source
    assert 'export_format="GLB"' in source

