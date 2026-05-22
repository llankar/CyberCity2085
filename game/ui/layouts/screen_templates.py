"""Shared four-zone screen layout contracts for management/tactical screens."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScreenLayoutTemplate:
    """Canonical four-zone grammar applied across strategic UI screens."""

    name: str
    zone_1_global_state: str
    zone_2_selected_element: str
    zone_3_available_actions: str
    zone_4_predicted_consequences: str


OverviewLayout = ScreenLayoutTemplate(
    name="OverviewLayout",
    zone_1_global_state="Zone 1: état global",
    zone_2_selected_element="Zone 2: élément sélectionné",
    zone_3_available_actions="Zone 3: actions disponibles",
    zone_4_predicted_consequences="Zone 4: conséquences prévues",
)

DecisionLayout = ScreenLayoutTemplate(
    name="DecisionLayout",
    zone_1_global_state="Zone 1: état global",
    zone_2_selected_element="Zone 2: élément sélectionné",
    zone_3_available_actions="Zone 3: actions disponibles",
    zone_4_predicted_consequences="Zone 4: conséquences prévues",
)

RosterLayout = ScreenLayoutTemplate(
    name="RosterLayout",
    zone_1_global_state="Zone 1: état global",
    zone_2_selected_element="Zone 2: élément sélectionné",
    zone_3_available_actions="Zone 3: actions disponibles",
    zone_4_predicted_consequences="Zone 4: conséquences prévues",
)

TacticalLayout = ScreenLayoutTemplate(
    name="TacticalLayout",
    zone_1_global_state="Zone 1: état global",
    zone_2_selected_element="Zone 2: élément sélectionné",
    zone_3_available_actions="Zone 3: actions disponibles",
    zone_4_predicted_consequences="Zone 4: conséquences prévues",
)


def required_zones() -> tuple[str, str, str, str]:
    return (
        "zone_1_global_state",
        "zone_2_selected_element",
        "zone_3_available_actions",
        "zone_4_predicted_consequences",
    )
