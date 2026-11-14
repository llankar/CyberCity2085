"""Godot-IPC: Communication bridge between Arcade (Python) and Godot combat UI.

This module implements an inter-process communication system that allows Godot
to send mission results back to the Python campaign engine after combat completes.

On Unix-like systems, this uses a temporary FIFO pipe for two-way signaling.
On Windows, it falls back to writing a result file with timestamps; Python polls
for completion since named pipes require special handling (pywin32).
"""

from __future__ import annotations

import json
import os
import socket
import tempfile
import time
from pathlib import Path
from typing import Any, Optional


IPC_PIPE_NAME = "runtime/godot_combat/ipc_pipe"
IPC_RESULT_FILE = "runtime/godot_combat/ipc_result.json"
IPC_SIGNAL_FILE = "runtime/godot_combat/ipc_signal.txt"  # Marker file for completion on Windows


def start_ipc_server(game_state_dir: Path) -> tuple[socket.socket | None, str]:
    """Create an IPC pipe server and return the socket + path for Godot to write to.

    On Unix-like systems, uses a FIFO pipe with Unix domain sockets.
    On Windows, creates a temporary named pipe file marker that Godot polls.

    Args:
        game_state_dir: Directory where the IPC pipe file should be created.

    Returns:
        Tuple of (server_socket, pipe_path_string). On Windows, socket is None.
    """
    # Clean up any stale pipe from previous runs
    pipe_path = game_state_dir / IPC_PIPE_NAME
    if pipe_path.exists():
        pipe_path.unlink()

    # Create the FIFO pipe
    os.mkfifo(str(pipe_path))

    # Unix domain sockets only work on Unix-like systems
    use_unix_socket = not (os.name == "nt")  # nt = Windows
    
    if use_unix_socket:
        # Open server end for reading (blocking mode)
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind(str(pipe_path))
        server_socket.listen(1)
        server_socket.setblocking(False)  # Non-blocking for Python polling

        return server_socket, str(pipe_path.absolute())
    else:
        # Windows fallback: no actual pipe, just a marker file path
        # Godot will write to ipc_result.json and set ipc_signal.txt when done
        return None, str(pipe_path.absolute())


def read_ipc_result(game_state_dir: Path, timeout: float = 30.0) -> Optional[dict[str, Any]]:
    """Read the result JSON file written by Godot and optionally wait for IPC signal.

    Args:
        game_state_dir: Directory containing the IPC files.
        timeout: Seconds to wait for IPC signal before returning.

    Returns:
        Parsed JSON dict if available, None otherwise.
    """
    import time

    pipe_path = game_state_dir / IPC_PIPE_NAME
    result_path = game_state_dir / IPC_RESULT_FILE

    # Read result file (may already exist from previous mission)
    if result_path.exists():
        try:
            with open(result_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Wait for IPC signal via the pipe
    start_time = time.time()
    while (result_path.exists() and 
           (time.time() - start_time) < timeout):
        try:
            return json.loads(result_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, IOError):
            time.sleep(0.1)

    return None


def read_ipc_result_blocking(game_state_dir: Path, timeout: float = 30.0) -> Optional[dict[str, Any]]:
    """Block until Godot writes a result JSON file (with optional IPC signal).

    This is the primary method used by Python after launching Godot combat.
    
    Args:
        game_state_dir: Directory containing the IPC files.
        timeout: Maximum seconds to wait for result.

    Returns:
        Parsed JSON dict when Godot finishes, None if timeout.
    """
    import time

    pipe_path = game_state_dir / IPC_PIPE_NAME
    result_path = game_state_dir / IPC_RESULT_FILE

    # First check if result already exists (non-blocking)
    while result_path.exists():
        try:
            with open(result_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            time.sleep(0.05)

    # Wait for Godot to complete and write result file
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        if result_path.exists():
            try:
                with open(result_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                time.sleep(0.05)
        
        # Check for Windows signal file (marker that Godot is done)
        signal_file = game_state_dir / IPC_SIGNAL_FILE
        if signal_file.exists():
            try:
                with open(signal_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content == "COMBAT_COMPLETE":
                        # Signal file exists, result should be ready now
                        if result_path.exists():
                            with open(result_path, 'r', encoding='utf-8') as f:
                                return json.load(f)
            except (IOError, OSError):
                pass

        time.sleep(0.1)

    return None


def send_ipc_result_to_python(game_state_dir: Path, combat_result: dict[str, Any]) -> bool:
    """Write combat result to file for Python to read.

    This function is called from Godot MissionResults.gd when combat completes.

    Args:
        game_state_dir: Directory where result should be written.
        combat_result: Dictionary containing mission combat results.

    Returns:
        True if result was written successfully, False otherwise.
    """
    result_path = game_state_dir / IPC_RESULT_FILE
    
    # Write the JSON result file
    try:
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(combat_result, f, indent=2)
        
        # Try to signal Python via IPC pipe if it's running
        import time
        time.sleep(0.1)  # Brief pause for file I/O
        
        pipe_path = game_state_dir / IPC_PIPE_NAME
        if pipe_path.exists():
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect(str(pipe_path))
                # Send success signal (not JSON result - Python reads the file anyway)
                sock.sendall(b'COMBAT_COMPLETE\n')
                sock.close()
            except (socket.error, ConnectionRefusedError):
                pass  # Python not ready to receive signal

        return True
    except Exception:
        return False


def cleanup_ipc_files(game_state_dir: Path) -> None:
    """Remove IPC pipe and result files after communication is complete."""
    import time
    
    pipe_path = game_state_dir / IPC_PIPE_NAME
    result_path = game_state_dir / IPC_RESULT_FILE
    
    # Give some time for Python to finish reading
    time.sleep(0.2)
    
    if pipe_path.exists():
        try:
            pipe_path.unlink()
        except Exception:
            pass
    
    if result_path.exists():
        try:
            result_path.unlink()
        except Exception:
            pass
