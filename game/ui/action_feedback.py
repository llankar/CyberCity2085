"""Standardized UI feedback and confirmation prompts for critical actions."""

from __future__ import annotations

from game.ui.widgets.notification_center import NotificationCenter


def action_message(action: str, ok: bool, detail: str = "") -> tuple[str, str]:
    status = "SUCCESS" if ok else "FAILURE"
    base = {
        "recruitment": "Recruitment",
        "budget_allocation": "Budget allocation",
        "mission_launch": "Mission launch",
        "save": "Save",
        "load": "Load",
    }.get(action, action.replace("_", " ").title())
    text = f"{base} {status.lower()}"
    if detail:
        text = f"{text}: {detail}"
    return status.lower(), text


def confirm_message(action: str) -> str:
    if action == "mission_launch_risk":
        return "Confirmation required: launch risky mission? Repeat action to confirm."
    if action == "spend_funds":
        return "Confirmation required: this action spends funds and cannot be undone."
    return "Confirmation required before irreversible action."


def push_action(center: NotificationCenter, action: str, ok: bool, detail: str = "") -> str:
    level, text = action_message(action, ok, detail)
    if level == "success":
        center.success(text)
    else:
        center.failure(text)
    return text
