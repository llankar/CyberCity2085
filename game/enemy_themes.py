"""Enemy theme helpers for battle missions and asset routing."""

from __future__ import annotations

from typing import Any

ENEMY_THEME_GENERIC = "generic"
ENEMY_THEME_STARVER = "starver"
ENEMY_THEME_MUTANT = "mutant"
ENEMY_THEME_RAIDER = "raider"
ENEMY_THEME_CORP_SAMURAI = "corp_samurai"
ENEMY_THEME_CORP_SAMURAI_ROBOT = "corp_samurai_robot"
ENEMY_THEME_CORP_SAMURAI_POWER_ARMOR = "corp_samurai_power_armor"
ENEMY_THEME_CORP_37 = "corp_37"
ENEMY_THEME_CORP_37_ROBOT = "corp_37_robot"
ENEMY_THEME_CORP_37_POWER_ARMOR = "corp_37_power_armor"

ENEMY_THEMES: tuple[str, ...] = (
    ENEMY_THEME_GENERIC,
    ENEMY_THEME_STARVER,
    ENEMY_THEME_MUTANT,
    ENEMY_THEME_RAIDER,
    ENEMY_THEME_CORP_SAMURAI,
    ENEMY_THEME_CORP_SAMURAI_ROBOT,
    ENEMY_THEME_CORP_SAMURAI_POWER_ARMOR,
    ENEMY_THEME_CORP_37,
    ENEMY_THEME_CORP_37_ROBOT,
    ENEMY_THEME_CORP_37_POWER_ARMOR,
)

_THEME_ALIASES = {
    "": ENEMY_THEME_GENERIC,
    "generic": ENEMY_THEME_GENERIC,
    "humanoid": ENEMY_THEME_GENERIC,
    "starvers": ENEMY_THEME_STARVER,
    "mutants": ENEMY_THEME_MUTANT,
    "raiders": ENEMY_THEME_RAIDER,
    "samurai": ENEMY_THEME_CORP_SAMURAI,
    "ninja": ENEMY_THEME_CORP_SAMURAI,
    "cyber_samurai": ENEMY_THEME_CORP_SAMURAI,
    "cyber_ninja": ENEMY_THEME_CORP_SAMURAI,
    "corp_samurai": ENEMY_THEME_CORP_SAMURAI,
    "corp_samurai_robot": ENEMY_THEME_CORP_SAMURAI_ROBOT,
    "corp_samurai_power_armor": ENEMY_THEME_CORP_SAMURAI_POWER_ARMOR,
    "three_sevens": ENEMY_THEME_CORP_37,
    "three sevens": ENEMY_THEME_CORP_37,
    "37": ENEMY_THEME_CORP_37,
    "corp_37": ENEMY_THEME_CORP_37,
    "corp_37_robot": ENEMY_THEME_CORP_37_ROBOT,
    "corp_37_power_armor": ENEMY_THEME_CORP_37_POWER_ARMOR,
}

_STATS_BY_THEME: dict[str, dict[str, float]] = {
    ENEMY_THEME_GENERIC: {"hp": 1.00, "str": 1.00, "agi": 1.00, "def": 1.00, "range": 3},
    ENEMY_THEME_STARVER: {"hp": 1.20, "str": 1.05, "agi": 0.80, "def": 0.85, "range": 1},
    ENEMY_THEME_MUTANT: {"hp": 1.45, "str": 1.25, "agi": 0.90, "def": 1.00, "range": 2},
    ENEMY_THEME_RAIDER: {"hp": 1.10, "str": 1.10, "agi": 1.15, "def": 0.95, "range": 3},
    ENEMY_THEME_CORP_SAMURAI: {"hp": 1.00, "str": 1.20, "agi": 1.35, "def": 1.00, "range": 4},
    ENEMY_THEME_CORP_SAMURAI_ROBOT: {"hp": 1.35, "str": 1.20, "agi": 1.00, "def": 1.25, "range": 4},
    ENEMY_THEME_CORP_SAMURAI_POWER_ARMOR: {"hp": 1.85, "str": 1.45, "agi": 0.85, "def": 1.65, "range": 3},
    ENEMY_THEME_CORP_37: {"hp": 1.15, "str": 1.20, "agi": 1.00, "def": 1.10, "range": 3},
    ENEMY_THEME_CORP_37_ROBOT: {"hp": 1.40, "str": 1.25, "agi": 0.95, "def": 1.30, "range": 4},
    ENEMY_THEME_CORP_37_POWER_ARMOR: {"hp": 1.95, "str": 1.50, "agi": 0.80, "def": 1.75, "range": 3},
}


def normalize_enemy_theme(theme: Any) -> str:
    """Return a stable enemy theme key."""
    raw = str(theme or "").strip().lower().replace("-", "_").replace(" ", "_")
    return _THEME_ALIASES.get(raw, raw if raw in ENEMY_THEMES else ENEMY_THEME_GENERIC)


def enemy_theme_stat_scale(theme: Any) -> dict[str, float]:
    """Return the stat multiplier profile for a theme."""
    return dict(_STATS_BY_THEME.get(normalize_enemy_theme(theme), _STATS_BY_THEME[ENEMY_THEME_GENERIC]))


def enemy_sprite_filename(theme: Any, subtype: Any) -> str:
    """Return the battle-token filename for a themed enemy subtype."""
    theme_key = normalize_enemy_theme(theme)
    subtype_key = str(subtype or "grunt").strip().lower() or "grunt"
    if theme_key == ENEMY_THEME_GENERIC:
        return f"enemy_{subtype_key}.png"
    return f"enemy_{theme_key}_{subtype_key}.png"


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def mission_enemy_theme(mission: Any) -> str:
    """Derive a themed enemy roster for a mission when one is not explicit."""
    if mission is None:
        return ENEMY_THEME_GENERIC

    explicit = normalize_enemy_theme(getattr(mission, "enemy_theme", None))
    if explicit != ENEMY_THEME_GENERIC:
        return explicit

    text_bits = [
        str(getattr(mission, "id", "")),
        str(getattr(mission, "title", "")),
        str(getattr(mission, "target_faction", "")),
        str(getattr(mission, "district", "")),
        str(getattr(mission, "objective_text", "")),
    ]
    tags = getattr(mission, "tags", []) or []
    for tag in tags:
        text_bits.append(str(getattr(tag, "name", tag)))
    haystack = " ".join(text_bits).strip().lower()

    risk = int(getattr(mission, "risk_level", 1) or 1)
    if _contains_any(haystack, ("badlands", "wasteland", "outskirts", "outside", "frontier", "raider", "mutant", "starver")):
        if risk >= 8:
            return ENEMY_THEME_RAIDER
        if risk >= 5:
            return ENEMY_THEME_MUTANT
        return ENEMY_THEME_STARVER

    if _contains_any(haystack, ("three sevens", "37", "samurai", "ninja", "shogun")):
        if risk >= 8:
            return ENEMY_THEME_CORP_37_POWER_ARMOR
        if risk >= 6:
            return ENEMY_THEME_CORP_37_ROBOT
        return ENEMY_THEME_CORP_37

    if _contains_any(haystack, ("corp", "corporate", "company", "security")):
        if risk >= 8:
            return ENEMY_THEME_CORP_SAMURAI_POWER_ARMOR
        if risk >= 6:
            return ENEMY_THEME_CORP_SAMURAI_ROBOT
        return ENEMY_THEME_CORP_SAMURAI

    return ENEMY_THEME_GENERIC
