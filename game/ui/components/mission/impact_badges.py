"""Badge-like textual indicators for mission emotional and stress context."""

from __future__ import annotations


def format_stress_band(stress_band: str | None) -> str:
    mapping = {
        "critical": "Stress: CRITICAL",
        "high": "Stress: HIGH",
        "medium": "Stress: MEDIUM",
        "low": "Stress: LOW",
    }
    return mapping.get((stress_band or "").lower(), "Stress: UNKNOWN")


def format_launch_state(lock_reason: str | None) -> str:
    if not lock_reason:
        return "Launch status: READY"
    return f"Launch status: LOCKED ({lock_reason})"
