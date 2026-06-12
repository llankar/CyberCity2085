"""Win32 window overlay: position Godot's borderless window over Arcade's window.

True child-window embedding (SetParent) does not work inside OpenGL windows —
SwapBuffers overwrites the compositor's work every frame.  The approach here is:
  1. Find Godot's HWND once it starts.
  2. Strip its title bar / border.
  3. Move it to the same screen rect as Arcade's window.
  4. Hide Arcade's window so only Godot is visible.
  5. On combat end: hide Godot, show Arcade, terminate the Godot process.

Windows-only. Every function is a safe no-op on Linux/macOS.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes
import os
import sys
from typing import Optional

_WIN = sys.platform == "win32"

if _WIN:
    _u32 = ctypes.windll.user32
    _k32 = ctypes.windll.kernel32

    _WNDENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.wintypes.HWND,
        ctypes.wintypes.LPARAM,
    )
    _GWL_STYLE      = -16
    _WS_CAPTION     = 0x00C00000
    _WS_THICKFRAME  = 0x00040000
    _WS_SYSMENU     = 0x00080000
    _WS_MINIMIZEBOX = 0x00020000
    _WS_MAXIMIZEBOX = 0x00010000
    _SWP_FRAMECHANGED = 0x0020
    _SWP_NOACTIVATE   = 0x0010
    _SWP_NOZORDER     = 0x0004
    _SWP_SHOWWINDOW   = 0x0040
    _SW_HIDE    = 0
    _SW_SHOW    = 5
    _PROCESS_TERMINATE = 0x0001


# ── HWND discovery ────────────────────────────────────────────────────────────

def get_process_hwnd(pid: int) -> Optional[int]:
    """Return the first visible top-level HWND owned by *pid*, or None."""
    if not _WIN:
        return None
    found: list[int] = []

    @_WNDENUMPROC
    def _cb(hwnd: int, _lparam: int) -> bool:
        w_pid = ctypes.wintypes.DWORD(0)
        _u32.GetWindowThreadProcessId(hwnd, ctypes.byref(w_pid))
        if w_pid.value == pid and _u32.IsWindowVisible(hwnd):
            found.append(hwnd)
            return False
        return True

    _u32.EnumWindows(_cb, 0)
    return found[0] if found else None


def get_current_process_hwnd() -> Optional[int]:
    """Return the HWND of the current process (Arcade's window)."""
    return get_process_hwnd(os.getpid())


# ── Window geometry ───────────────────────────────────────────────────────────

def get_window_screen_rect(hwnd: int) -> tuple[int, int, int, int]:
    """Return (x, y, width, height) of *hwnd*'s CLIENT area in screen coordinates.

    Uses GetClientRect + ClientToScreen so the result excludes Arcade's title bar
    and window borders.  Godot (made borderless) placed at this rect will have the
    same drawable area as Arcade's viewport, keeping viewport sizes identical.
    """
    if not _WIN:
        return 0, 0, 1280, 720
    client = ctypes.wintypes.RECT()
    _u32.GetClientRect(hwnd, ctypes.byref(client))
    pt = ctypes.wintypes.POINT(0, 0)
    _u32.ClientToScreen(hwnd, ctypes.byref(pt))
    return pt.x, pt.y, client.right - client.left, client.bottom - client.top


# ── Overlay helpers ───────────────────────────────────────────────────────────

def make_borderless_at(hwnd: int, x: int, y: int, w: int, h: int) -> None:
    """Remove title bar / border from *hwnd* and place it at the given screen rect."""
    if not _WIN:
        return
    style = _u32.GetWindowLongW(hwnd, _GWL_STYLE)
    style &= ~(_WS_CAPTION | _WS_THICKFRAME | _WS_SYSMENU |
               _WS_MINIMIZEBOX | _WS_MAXIMIZEBOX)
    _u32.SetWindowLongW(hwnd, _GWL_STYLE, style)
    _u32.SetWindowPos(
        hwnd, 0, x, y, w, h,
        _SWP_FRAMECHANGED | _SWP_NOACTIVATE | _SWP_NOZORDER | _SWP_SHOWWINDOW,
    )


def hide_window(hwnd: int) -> None:
    """Hide *hwnd* without destroying it."""
    if not _WIN:
        return
    _u32.ShowWindow(hwnd, _SW_HIDE)


def show_window(hwnd: int) -> None:
    """Show *hwnd* and bring it to the foreground."""
    if not _WIN:
        return
    _u32.ShowWindow(hwnd, _SW_SHOW)
    _u32.SetForegroundWindow(hwnd)


# ── Process control ───────────────────────────────────────────────────────────

def terminate_pid(pid: int) -> None:
    """Forcibly terminate a process by PID (Win32 TerminateProcess)."""
    if not _WIN:
        return
    handle = _k32.OpenProcess(_PROCESS_TERMINATE, False, pid)
    if handle:
        _k32.TerminateProcess(handle, 0)
        _k32.CloseHandle(handle)
