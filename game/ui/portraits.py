"""Deterministic portrait asset selection."""

from __future__ import annotations

from functools import lru_cache
from hashlib import sha1
from pathlib import Path

from ..enemy_themes import (
    ENEMY_THEME_CORP_37,
    ENEMY_THEME_CORP_37_POWER_ARMOR,
    ENEMY_THEME_CORP_37_ROBOT,
    ENEMY_THEME_CORP_SAMURAI,
    ENEMY_THEME_CORP_SAMURAI_POWER_ARMOR,
    ENEMY_THEME_CORP_SAMURAI_ROBOT,
    ENEMY_THEME_GENERIC,
    ENEMY_THEME_MUTANT,
    ENEMY_THEME_RAIDER,
    ENEMY_THEME_STARVER,
    normalize_enemy_theme,
)

LEGACY_AGENT_PORTRAIT_COUNT = 124
AGENT_PORTRAIT_COUNT = 50
ROBOT_PORTRAIT_COUNT = 75
POWER_ARMOR_PORTRAIT_COUNT = 25
PORTRAIT_COUNT = LEGACY_AGENT_PORTRAIT_COUNT
PORTRAIT_DIR = "assets/ui/portraits"

ENEMY_PORTRAIT_COUNTS: dict[str, int] = {
    ENEMY_THEME_STARVER: 10,
    ENEMY_THEME_MUTANT: 20,
    ENEMY_THEME_RAIDER: 20,
    ENEMY_THEME_CORP_SAMURAI: 20,
    ENEMY_THEME_CORP_SAMURAI_ROBOT: 20,
    ENEMY_THEME_CORP_SAMURAI_POWER_ARMOR: 20,
    ENEMY_THEME_CORP_37: 20,
    ENEMY_THEME_CORP_37_ROBOT: 20,
    ENEMY_THEME_CORP_37_POWER_ARMOR: 20,
}


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


def portrait_path_for_power_armor(identifier: str, role: str = "power_armor") -> str:
    """Return a stable generated portrait path for a power-armor identity."""
    seed = f"{identifier.strip().lower()}:{role.strip().lower()}:armor"
    index = _stable_index(seed, POWER_ARMOR_PORTRAIT_COUNT)
    path = f"{PORTRAIT_DIR}/power_armor_{index:02d}.png"
    if _portrait_exists(path):
        return path
    if "heavy" in role.strip().lower():
        return f"{PORTRAIT_DIR}/power_armor_heavy_pilot.png"
    return f"{PORTRAIT_DIR}/power_armor_pilot.png"


def portrait_path_for_character(character) -> str:
    """Return a stable generated portrait path for a Character-like object."""
    role = getattr(character, "role", "samurai")
    role_key = str(role).lower()
    if role_key in {"robot", "combat_robot", "support_robot", "drone"}:
        return portrait_path_for_robot(getattr(character, "name", "robot"), role)
    if role_key in {"power_armor", "heavy_armor"}:
        return portrait_path_for_power_armor(getattr(character, "name", "armor"), role)
    return portrait_path_for_agent(
        getattr(character, "name", "agent"),
        role,
        getattr(character, "sex", ""),
    )


def portrait_path_for_enemy(identifier: str, theme: str, subtype: str = "grunt") -> str:
    """Return a stable generated portrait path for a themed enemy identity."""
    theme_key = normalize_enemy_theme(theme)
    subtype_key = str(subtype or "grunt").strip().lower() or "grunt"
    if theme_key == ENEMY_THEME_GENERIC:
        return f"{PORTRAIT_DIR}/enemy_{subtype_key}.png"

    count = ENEMY_PORTRAIT_COUNTS.get(theme_key, 20)
    seed = f"{identifier.strip().lower()}:{theme_key}:{subtype_key}:enemy"
    index = _stable_index(seed, count)
    path = f"{PORTRAIT_DIR}/enemy_{theme_key}_{index:02d}.png"
    if _portrait_exists(path):
        return path

    fallback = f"{PORTRAIT_DIR}/enemy_{subtype_key}.png"
    if _portrait_exists(fallback):
        return fallback
    return path
