"""Confirmation rules for costly or irreversible actions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfirmRule:
    key: str
    message: str


CONFIRM_RULES = {
    "mission_launch_risk": ConfirmRule(
        "mission_launch_risk",
        "Confirmation required: risky launch may trigger agent breakdown. Repeat action to confirm.",
    ),
    "spend_funds": ConfirmRule(
        "spend_funds",
        "Confirmation required: this spend is costly and cannot be fully undone.",
    ),
    "load": ConfirmRule(
        "load",
        "Confirmation required: loading overwrites current unsaved progress.",
    ),
}


def build_confirm_message(action_key: str) -> str:
    return CONFIRM_RULES.get(
        action_key,
        ConfirmRule(action_key, "Confirmation required before irreversible action."),
    ).message
