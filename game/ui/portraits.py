"""Deterministic agent portrait asset selection."""

from __future__ import annotations

from hashlib import sha1

PORTRAIT_COUNT = 24
PORTRAIT_DIR = "assets/ui/portraits"


def portrait_path_for_agent(name: str, role: str) -> str:
    """Return a stable generated portrait path for an agent identity."""
    seed = f"{name.strip().lower()}:{role.strip().lower()}".encode("utf-8")
    index = int(sha1(seed).hexdigest()[:8], 16) % PORTRAIT_COUNT + 1
    return f"{PORTRAIT_DIR}/agent_{index:02d}.png"


def portrait_path_for_character(character) -> str:
    """Return a stable generated portrait path for a Character-like object."""
    return portrait_path_for_agent(
        getattr(character, "name", "agent"), getattr(character, "role", "samurai")
    )
