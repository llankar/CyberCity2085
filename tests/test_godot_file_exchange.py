"""Portable result exchange and child lifecycle; never launches a native UI."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from game.combat import godot_ipc as ipc
from game.combat.godot_bridge import launch_godot_combat_ui_blocking


def test_session_paths_are_local_and_stale_results_are_cleared(tmp_path):
    (tmp_path / ipc.IPC_RESULT_FILE).write_text('{"outcome":"victory"}')
    unrelated = tmp_path / "campaign.json"
    unrelated.write_text("preserve")
    server, signal = ipc.start_ipc_server(tmp_path)
    assert server is None
    assert Path(signal).parent == tmp_path
    assert not (tmp_path / ipc.IPC_RESULT_FILE).exists()
    assert unrelated.read_text() == "preserve"
    assert not (tmp_path / "runtime").exists()


def test_atomic_result_roundtrip_and_cleanup(tmp_path):
    result = {"outcome": "defeat", "funds_earned": 0, "casualties": ["Rook"]}
    assert ipc.send_ipc_result_to_python(tmp_path, result)
    assert ipc.read_ipc_result(tmp_path) == result
    assert ipc.read_ipc_result_blocking(tmp_path, timeout=0) == result
    assert not (tmp_path / (ipc.IPC_RESULT_FILE + ".tmp")).exists()
    ipc.cleanup_ipc_files(tmp_path)
    assert ipc.read_ipc_result(tmp_path) is None


def test_missing_partial_and_non_object_json_respect_deadline(tmp_path):
    assert ipc.read_ipc_result_blocking(tmp_path, timeout=0.01) is None
    path = tmp_path / ipc.IPC_RESULT_FILE
    for content in ('{"outcome":', '[]', 'null'):
        path.write_text(content)
        assert ipc.read_ipc_result_blocking(tmp_path, timeout=0.01) is None


def run_blocking(tmp_path, process, **kwargs):
    with patch("game.combat.godot_bridge.copy_audio_assets"), \
         patch("game.combat.godot_bridge.write_godot_combat_handoff", return_value=tmp_path / "handoff.json"), \
         patch("game.combat.godot_bridge.build_godot_combat_command", return_value=["fake-godot"]), \
         patch("game.combat.godot_bridge.subprocess.Popen", return_value=process):
        return launch_godot_combat_ui_blocking(None, None, handoff_path=tmp_path / "handoff.json", **kwargs)


def test_early_child_exit_returns_fallback_immediately(tmp_path):
    process = Mock()
    process.poll.return_value = 17
    result = run_blocking(tmp_path, process)
    assert not result.launched
    assert "exited (17)" in result.message
    assert result.combat_result is None
    process.terminate.assert_not_called()


def test_explicit_timeout_terminates_and_reaps_only_its_child(tmp_path):
    process = Mock()
    process.poll.return_value = None
    result = run_blocking(tmp_path, process, timeout=0)
    assert not result.launched
    assert "timed out" in result.message
    process.terminate.assert_called_once()
    process.wait.assert_called_once_with(timeout=5)


def test_completed_result_is_returned_before_cleanup(tmp_path):
    process = Mock()
    process.poll.return_value = 0
    expected = {"outcome": "victory", "funds_earned": 40}
    with patch("game.combat.godot_ipc.read_ipc_result", return_value=expected):
        result = run_blocking(tmp_path, process)
    assert result.launched
    assert result.combat_result == expected


def test_setup_errors_return_a_fallback_instead_of_escaping(tmp_path):
    with patch("game.combat.godot_ipc.start_ipc_server", side_effect=OSError("read-only")):
        result = launch_godot_combat_ui_blocking(None, None, handoff_path=tmp_path / "handoff.json")
    assert not result.launched
    assert "read-only" in result.message
