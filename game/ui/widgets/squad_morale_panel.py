"""Reusable squad morale widget model and compact text rendering."""

from __future__ import annotations

from dataclasses import dataclass

from ...management.morale import SquadMoraleSummary
from ..accessibility.states import label_with_non_color_indicator


@dataclass(frozen=True)
class SquadMoraleWidgetLine:
    """One render-ready morale line."""

    text: str
    emphasis: str = "normal"


def _short_bar(value: int, width: int = 8) -> str:
    safe = max(0, min(100, int(value)))
    filled = int(round((safe / 100) * width))
    return "█" * filled + "·" * (width - filled)


def _trend_symbol(delta: int) -> str:
    if delta <= -5:
        return "↓"
    if delta >= 5:
        return "↑"
    return "→"


def build_squad_morale_panel_lines(summary: SquadMoraleSummary) -> list[SquadMoraleWidgetLine]:
    """Build reusable compact lines: global morale + per-agent contributions."""
    header = SquadMoraleWidgetLine(
        (
            f"Squad morale {_short_bar(summary.global_morale)} {summary.global_morale}/100 "
            f"[{summary.state}] {_trend_symbol(summary.trend_delta)}"
        ),
        emphasis="header",
    )
    if not summary.contributions:
        return [header, SquadMoraleWidgetLine("No active squad assigned.", emphasis="muted")]

    lines = [header]
    for contribution in summary.contributions:
        state = "normal" if contribution.delta >= 0 else "active"
        lines.append(
            SquadMoraleWidgetLine(
                label_with_non_color_indicator(
                    f"{contribution.name}: {_short_bar(contribution.morale, width=6)} "
                    f"{contribution.morale}/100 ({contribution.delta:+d})",
                    state,
                )
            )
        )
    return lines
