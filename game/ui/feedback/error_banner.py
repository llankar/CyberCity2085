"""Error banner for failed actions in tactical UI."""

from __future__ import annotations


def build_error_banner(action: str, reason: str) -> str:
    return f"[ERROR] {action}: {reason}"
