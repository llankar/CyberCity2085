"""Standardized UI feedback and confirmation prompts for critical actions."""

from __future__ import annotations

from game.ui.feedback.confirm_dialog import build_confirm_message
from game.ui.feedback.error_banner import build_error_banner
from game.ui.feedback.toast_center import FeedbackToast, dispatch_toast
from game.ui.widgets.notification_center import NotificationCenter


_ACTION_LABELS = {
    "recruitment":      "Recruitment",
    "budget_allocation":"Budget allocation",
    "mission_launch":   "Mission launch",
    "save":             "Save",
    "load":             "Load",
    "upgrade":          "Upgrade",
    "advance_day":      "Day advance",
    "asset_repair":     "Asset repair",
    "asset_acquire":    "Asset acquisition",
    "stat_upgrade":     "Stat upgrade",
    "start_research":   "Research started",
    "talent_unlock":    "Talent unlock",
    "remove_agent":     "Agent removal",
}


def action_message(action: str, ok: bool, detail: str = "") -> tuple[str, str]:
    level = "success" if ok else "failure"
    action_label = _ACTION_LABELS.get(action, action.replace("_", " ").title())
    result = "completed" if ok else "failed"
    impact = detail or "funds/stress/time unchanged"
    next_step = "Continue strategic planning" if ok else "Review resources and retry"
    toast = FeedbackToast(action_label, result, impact, next_step)
    return level, toast.message


def skill_check_feedback(
    *,
    check_name: str,
    rolled_value: int,
    total_value: int,
    threshold: int,
) -> str:
    """Build a compact one-line skill-check outcome for action feedback surfaces."""
    result = "SUCCESS" if total_value >= threshold else "FAILURE"
    return (
        f"{check_name}: roll {rolled_value} / total {total_value} "
        f"vs {threshold} => {result}"
    )


def confirm_message(action: str) -> str:
    return build_confirm_message(action)


def push_action(center: NotificationCenter, action: str, ok: bool, detail: str = "") -> str:
    level, text = action_message(action, ok, detail)
    if not ok and detail:
        text = f"{text} | {build_error_banner(action, detail)}"
    impact = detail or "n/a"
    if not ok and detail:
        impact = f"{impact}; {build_error_banner(action, detail)}"
    toast = FeedbackToast(action, "completed" if ok else "failed", impact, "Proceed")
    return dispatch_toast(center, "success" if ok else "failure", toast)
