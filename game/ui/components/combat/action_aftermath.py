"""Build short-lived tactical aftermath lines for HUD readability."""

from __future__ import annotations


def build_action_aftermath_line(
    *,
    action_label: str,
    damage: int = 0,
    status_applied: str | None = None,
    suppression_created: bool = False,
    skill_check_outcome: str | None = None,
) -> str:
    """Return a compact causal line for the fixed HUD aftermath zone."""
    segments: list[str] = [action_label]
    segments.append(f"DMG {max(0, damage)}")
    if status_applied:
        segments.append(f"STATUT {status_applied}")
    if suppression_created:
        segments.append("SUPPRESSION créée")
    if skill_check_outcome:
        segments.append(skill_check_outcome)
    return " | ".join(segments)
