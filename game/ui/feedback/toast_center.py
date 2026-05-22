"""Toast-style feedback payload and dispatch helpers."""

from __future__ import annotations

from dataclasses import dataclass

from game.ui.widgets.notification_center import NotificationCenter


@dataclass(frozen=True)
class FeedbackToast:
    action: str
    result: str
    impact: str
    next_step: str

    @property
    def message(self) -> str:
        return (
            f"Action: {self.action} | Result: {self.result} | "
            f"Impact: {self.impact} | Next: {self.next_step}"
        )


def dispatch_toast(center: NotificationCenter, level: str, toast: FeedbackToast) -> str:
    if level == "success":
        center.success(toast.message)
    elif level == "warning":
        center.warning(toast.message)
    else:
        center.failure(toast.message)
    return toast.message
