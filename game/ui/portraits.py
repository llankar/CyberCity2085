"""Deterministic portrait asset selection."""

from __future__ import annotations

from functools import lru_cache
from hashlib import sha1
from pathlib import Path

LEGACY_AGENT_PORTRAIT_COUNT = 24
AGENT_PORTRAIT_COUNT = 50
ROBOT_PORTRAIT_COUNT = 50
PORTRAIT_COUNT = LEGACY_AGENT_PORTRAIT_COUNT
PORTRAIT_DIR = "assets/ui/portraits"


def _stable_index(seed: str, pool_size: int) -> int:
    if pool_size <= 0:
        return 1
    digest = sha1(seed.strip().lower().encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % pool_size + 1


def _normalize_sex(sex: str | None) -> str:
    cleaned = (sex or "").strip().lower()
    if cleaned in {"female", "f"}:
        return "female"
    if cleaned in {"male", "m"}:
        return "male"
    return ""


def portrait_sex_for_agent(name: str, role: str) -> str:
    """Return a deterministic sex split for portrait routing."""
    return "female" if _stable_index(f"{name}:{role}:sex", 2) == 1 else "male"


@lru_cache(maxsize=256)
def _portrait_exists(path: str) -> bool:
    return Path(path).exists()


def _legacy_agent_portrait_path(name: str, role: str) -> str:
    seed = f"{name.strip().lower()}:{role.strip().lower()}:legacy"
    index = _stable_index(seed, LEGACY_AGENT_PORTRAIT_COUNT)
    return f"{PORTRAIT_DIR}/agent_{index:02d}.png"


def portrait_path_for_agent(name: str, role: str, sex: str | None = None) -> str:
    """Return a stable generated portrait path for an agent identity."""
    sex_key = _normalize_sex(sex) or portrait_sex_for_agent(name, role)
    seed = f"{name.strip().lower()}:{role.strip().lower()}:{sex_key}"
    index = _stable_index(seed, AGENT_PORTRAIT_COUNT)
    path = f"{PORTRAIT_DIR}/agent_{sex_key}_{index:02d}.png"
    if _portrait_exists(path):
        return path
    legacy_path = _legacy_agent_portrait_path(name, role)
    if _portrait_exists(legacy_path):
        return legacy_path
    return path


def portrait_path_for_robot(identifier: str, role: str = "robot") -> str:
    """Return a stable generated portrait path for a robot identity."""
    seed = f"{identifier.strip().lower()}:{role.strip().lower()}:robot"
    index = _stable_index(seed, ROBOT_PORTRAIT_COUNT)
    path = f"{PORTRAIT_DIR}/robot_{index:02d}.png"
    if _portrait_exists(path):
        return path
    return f"{PORTRAIT_DIR}/robot_combat.png"


def portrait_path_for_character(character) -> str:
    """Return a stable generated portrait path for a Character-like object."""
    role = getattr(character, "role", "samurai")
    if str(role).lower() in {"robot", "combat_robot", "support_robot", "drone"}:
        return portrait_path_for_robot(getattr(character, "name", "robot"), role)
    return portrait_path_for_agent(
        getattr(character, "name", "agent"),
        role,
        getattr(character, "sex", ""),
    )
