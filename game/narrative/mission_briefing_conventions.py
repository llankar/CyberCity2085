"""Writing conventions for mission briefing copy (UI-04)."""

from __future__ import annotations

from collections.abc import Iterable

MAX_EMOTIONAL_IMPACT_CHARS = 96
NEUTRAL_IMPACT_FALLBACK = "Moderate emotional impact, keep vigilance and cohesion high."

_EMOTIONAL_LEXICON = {
    "low": "contained tension",
    "medium": "notable emotional burden",
    "high": "heavy emotional burden",
    "critical": "likely emotional scars",
}


def normalize_mission_tags(tagged_items: Iterable[object]) -> list[str]:
    """Normalize mission tags into a stable UI format (snake_case, sorted, unique)."""
    normalized: set[str] = set()
    for tag in tagged_items:
        raw = getattr(tag, "name", str(tag)).strip().lower()
        if not raw:
            continue
        normalized.add(raw.replace("-", "_").replace(" ", "_"))
    return sorted(normalized)


def build_short_emotional_impact(level: str | None, text: str | None) -> str:
    """Return a short emotional line with consistent vocabulary and a neutral fallback."""
    normalized_level = (level or "").strip().lower()
    emotional_anchor = _EMOTIONAL_LEXICON.get(normalized_level)
    base = (text or "").strip()
    if not emotional_anchor and not base:
        return NEUTRAL_IMPACT_FALLBACK
    if not base:
        base = f"Mission with {emotional_anchor}."
    if emotional_anchor and emotional_anchor not in base.lower():
        base = f"{base.rstrip('.')} ({emotional_anchor})."
    if len(base) > MAX_EMOTIONAL_IMPACT_CHARS:
        base = f"{base[: MAX_EMOTIONAL_IMPACT_CHARS - 1].rstrip()}..."
    return base or NEUTRAL_IMPACT_FALLBACK
