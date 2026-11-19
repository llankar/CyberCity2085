import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_benchmark_fixture_forces_rendered_frames_without_tactical_mutation():
    source = (ROOT / "godot/combat_missions_ui/tests/capture_combat_21.gd").read_text()
    assert '"--gpu-benchmark"' in source
    assert "await RenderingServer.frame_post_draw" in source
    assert "DisplayServer.VSYNC_DISABLED" in source
    benchmark = source[source.index("func benchmark_rendered_frames"):source.index("func verify_interactions")]
    assert "player_units" not in benchmark and "enemy_units" not in benchmark


def test_archived_windows_gpu_benchmark_is_native_and_complete():
    report = json.loads((ROOT / "docs/reports/windows_gpu_benchmark_system.json").read_text(encoding="utf-8-sig"))
    native = report["native"]
    system = report["system"]
    assert report["status"] == "PASS" and report["completion_marker"] is True
    assert "NVIDIA GeForce RTX 5070 Ti" == native["adapter"]
    assert native["renderer"] == "gl_compatibility" and native["frames"] == 2400
    assert native["average_fps"] > 60 and native["minimum_fps"] > 60
    assert native["peak_static_memory_bytes"] > native["static_memory_bytes"] > 0
    assert system["gpu_samples"] >= 10
    assert 0 < system["average_total_cpu_percent"] <= 100
    assert 0 < system["average_gpu_percent"] <= system["peak_gpu_percent"] <= 100
    assert 0 < system["average_gpu_memory_mib"] <= system["peak_gpu_memory_mib"]
