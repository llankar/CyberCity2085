"""Portable file-based result exchange for the optional Godot process.

All paths are relative to the supplied session directory. No FIFO, socket,
desktop interaction or platform-specific pipe dependency is needed.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

IPC_PIPE_NAME = "ipc_signal.txt"  # Legacy handoff key, now a completion marker.
IPC_RESULT_FILE = "ipc_result.json"
IPC_SIGNAL_FILE = IPC_PIPE_NAME


def start_ipc_server(game_state_dir: Path) -> tuple[None, str]:
    """Start a clean file-exchange session; preserve the old tuple API."""
    directory = Path(game_state_dir)
    directory.mkdir(parents=True, exist_ok=True)
    cleanup_ipc_files(directory)
    return None, str((directory / IPC_SIGNAL_FILE).resolve())


def read_ipc_result(game_state_dir: Path, timeout: float = 0.0) -> dict[str, Any] | None:
    """Read a complete JSON object, tolerating a missing/partially written file."""
    result_path = Path(game_state_dir) / IPC_RESULT_FILE
    deadline = time.monotonic() + max(0, timeout)
    while True:
        try:
            data = json.loads(result_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        time.sleep(min(0.05, remaining))


def read_ipc_result_blocking(game_state_dir: Path, timeout: float = 30.0) -> dict[str, Any] | None:
    return read_ipc_result(game_state_dir, timeout)


def send_ipc_result_to_python(game_state_dir: Path, combat_result: dict[str, Any]) -> bool:
    """Publish the JSON atomically before publishing its optional marker."""
    directory = Path(game_state_dir)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        temporary = directory / (IPC_RESULT_FILE + ".tmp")
        temporary.write_text(json.dumps(combat_result), encoding="utf-8")
        temporary.replace(directory / IPC_RESULT_FILE)
        (directory / IPC_SIGNAL_FILE).write_text("COMBAT_COMPLETE\n", encoding="utf-8")
        return True
    except (OSError, TypeError, ValueError):
        return False


def cleanup_ipc_files(game_state_dir: Path) -> None:
    for name in (IPC_RESULT_FILE, IPC_SIGNAL_FILE, IPC_RESULT_FILE + ".tmp"):
        (Path(game_state_dir) / name).unlink(missing_ok=True)
