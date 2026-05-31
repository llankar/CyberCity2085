"""Narrative feed item formatting helpers."""

from __future__ import annotations

from dataclasses import dataclass

from ....i18n import t
from ....narrative.event_feed import NarrativeFeedEntry
from ...accessibility.states import label_with_non_color_indicator

_CATEGORY_ICONS = {
    "agent": "🧠",
    "consequence": "⚠",
    "mission": "🎯",
    "faction": "🤝",
    "system": "🛰",
    "base": "🏙",
}

_CATEGORY_LABELS = {
    "agent": "AGENT",
    "consequence": "CONSEQUENCE",
    "mission": "MISSION",
    "faction": "FACTION",
    "system": "SYSTEM",
    "base": "BASE",
}

_TONE_BY_CATEGORY = {
    "agent": "positive",
    "mission": "tense",
    "faction": "recovery",
    "consequence": "loss",
    "system": "tense",
    "base": "tense",
}


@dataclass(frozen=True)
class NarrativeFeedWidgetLine:
    text: str
    emphasis: str = "normal"
    category: str = "base"
    tone: str = "tense"


def readable_relative_timestamp(age_steps: int, language: str | None = None) -> str:
    if age_steps <= 0:
        return t("feed.just_now", language)
    if age_steps == 1:
        return t("feed.one_ago", language)
    return t("feed.many_ago", language, count=age_steps)


def to_widget_line(entry: NarrativeFeedEntry, age_steps: int, clip: int = 120, language: str | None = None) -> NarrativeFeedWidgetLine:
    category = entry.category if entry.category in _CATEGORY_LABELS else "base"
    icon = _CATEGORY_ICONS[category]
    label = _CATEGORY_LABELS[category]
    tone = _TONE_BY_CATEGORY.get(category, "tense")
    rel_time = readable_relative_timestamp(age_steps, language)
    body = entry.text.strip()
    if len(body) > clip:
        body = body[: clip - 1].rstrip() + "..."
    rendered = f"{icon} [{label}] ({tone}) {body} | {rel_time}"
    return NarrativeFeedWidgetLine(
        text=label_with_non_color_indicator(rendered, "normal"),
        emphasis="normal",
        category=category,
        tone=tone,
    )
