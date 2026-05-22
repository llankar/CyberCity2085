"""Conventions de rédaction pour les briefs mission (UI-04)."""

from __future__ import annotations

from collections.abc import Iterable

MAX_EMOTIONAL_IMPACT_CHARS = 96
NEUTRAL_IMPACT_FALLBACK = "Impact émotionnel modéré, vigilance et cohésion recommandées."

_EMOTIONAL_LEXICON = {
    "low": "tension contenue",
    "medium": "charge émotionnelle notable",
    "high": "charge émotionnelle élevée",
    "critical": "séquelles émotionnelles probables",
}


def normalize_mission_tags(tagged_items: Iterable[object]) -> list[str]:
    """Normalise des tags mission vers un format UI stable (snake_case, trié, unique)."""
    normalized: set[str] = set()
    for tag in tagged_items:
        raw = getattr(tag, "name", str(tag)).strip().lower()
        if not raw:
            continue
        normalized.add(raw.replace("-", "_").replace(" ", "_"))
    return sorted(normalized)


def build_short_emotional_impact(level: str | None, text: str | None) -> str:
    """Retourne une phrase émotionnelle courte, vocabulaire cohérent, fallback neutre."""
    normalized_level = (level or "").strip().lower()
    emotional_anchor = _EMOTIONAL_LEXICON.get(normalized_level)
    base = (text or "").strip()
    if not emotional_anchor and not base:
        return NEUTRAL_IMPACT_FALLBACK
    if not base:
        base = f"Mission avec {emotional_anchor}."
    if emotional_anchor and emotional_anchor not in base.lower():
        base = f"{base.rstrip('.')} ({emotional_anchor})."
    if len(base) > MAX_EMOTIONAL_IMPACT_CHARS:
        base = f"{base[: MAX_EMOTIONAL_IMPACT_CHARS - 1].rstrip()}…"
    return base or NEUTRAL_IMPACT_FALLBACK
