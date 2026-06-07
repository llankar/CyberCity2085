"""Pure mid-battle event rules for tactical combat.

The functions in this module do not import Arcade, play sounds, create sprites,
or mutate UI overlays.  They translate mission complications and turn milestones
into descriptive results that a renderer can interpret.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Literal

from game.mission_templates import MissionComplication, MissionTemplate

CombatEventEffect = Literal["reinforcements", "blackout"]
CombatEventResultType = Literal[
    "spawn_enemy",
    "visibility_changed",
    "log_message",
    "screen_shake",
    "sound_key",
]


@dataclass(frozen=True)
class CombatEventTrigger:
    """Turn milestone that can activate a combat event once."""

    turn_at_least: int

    def matches(self, turn_number: int) -> bool:
        return turn_number >= self.turn_at_least


@dataclass(frozen=True)
class CombatEvent:
    """A render-agnostic combat event derived from a mission complication."""

    key: str
    name: str
    effect: CombatEventEffect
    trigger: CombatEventTrigger
    source: str = "complication"


@dataclass(frozen=True)
class CombatEventResult:
    """Descriptive event output consumed by BattleView or tests."""

    kind: CombatEventResultType
    event_key: str
    label: str = ""
    message: str = ""
    payload: dict[str, Any] = field(default_factory=dict)


_COMPLICATION_EFFECTS: dict[str, CombatEventEffect] = {
    "mod_rapid_response": "reinforcements",
    "rapid_response": "reinforcements",
    "mod_watcher_drone": "blackout",
    "watcher_drone": "blackout",
    "mod_counterintel_ping": "blackout",
    "counterintel_ping": "blackout",
}

_EFFECT_TRIGGERS: dict[CombatEventEffect, CombatEventTrigger] = {
    "reinforcements": CombatEventTrigger(turn_at_least=3),
    "blackout": CombatEventTrigger(turn_at_least=2),
}


def events_from_mission(mission: MissionTemplate | None) -> list[CombatEvent]:
    """Build active combat events from the mission's known complications."""
    if mission is None:
        return []
    events: list[CombatEvent] = []
    for complication in mission.possible_complications or []:
        event = event_from_complication(complication)
        if event is not None:
            events.append(event)
    return events


def event_from_complication(complication: MissionComplication) -> CombatEvent | None:
    """Return a combat event for a supported complication key, if any."""
    effect = _COMPLICATION_EFFECTS.get(complication.key)
    if effect is None:
        return None
    return CombatEvent(
        key=complication.key,
        name=complication.name,
        effect=effect,
        trigger=_EFFECT_TRIGGERS[effect],
    )


def resolve_combat_events(
    events: Iterable[CombatEvent],
    *,
    turn_number: int,
    triggered_keys: Iterable[str] = (),
    battlefield_size: tuple[int, int] = (1280, 720),
) -> tuple[list[CombatEventResult], set[str]]:
    """Resolve newly triggered events and return results plus triggered keys.

    ``triggered_keys`` is copied before use, so callers can keep the function
    pure at their boundary or store the returned set in their own state.
    """
    updated_triggered = set(triggered_keys)
    results: list[CombatEventResult] = []
    for event in events:
        if event.key in updated_triggered or not event.trigger.matches(turn_number):
            continue
        updated_triggered.add(event.key)
        results.extend(_results_for_event(event, battlefield_size=battlefield_size))
    return results, updated_triggered


def _results_for_event(
    event: CombatEvent,
    *,
    battlefield_size: tuple[int, int],
) -> list[CombatEventResult]:
    if event.effect == "reinforcements":
        return _reinforcement_results(event, battlefield_size=battlefield_size)
    if event.effect == "blackout":
        return _blackout_results(event)
    return []


def _reinforcement_results(
    event: CombatEvent,
    *,
    battlefield_size: tuple[int, int],
) -> list[CombatEventResult]:
    width, height = battlefield_size
    safe_height = max(128, height)
    positions = (
        (32, safe_height // 2 - 96),
        (max(32, width - 32), safe_height // 2 + 96),
    )
    spawn_results = [
        CombatEventResult(
            kind="spawn_enemy",
            event_key=event.key,
            label=event.name,
            payload={
                "position": position,
                "unit_type": "grunt",
                "enemy_subtype": "grunt",
                "stats": {"hp": 4, "max_hp": 4, "agi": 2, "defense": 1},
            },
        )
        for position in positions
    ]
    return [
        *spawn_results,
        CombatEventResult(
            kind="sound_key",
            event_key=event.key,
            label=event.name,
            payload={"key": "sfx_reinforce"},
        ),
        CombatEventResult(
            kind="screen_shake",
            event_key=event.key,
            label=event.name,
            payload={"intensity": 10},
        ),
        CombatEventResult(
            kind="log_message",
            event_key=event.key,
            label=event.name,
            message=f"⚠ REINFORCEMENTS: {event.name}",
            payload={"banner": f"COMPLICATION: {event.name} — Reinforcements incoming!"},
        ),
    ]


def _blackout_results(event: CombatEvent) -> list[CombatEventResult]:
    return [
        CombatEventResult(
            kind="visibility_changed",
            event_key=event.key,
            label=event.name,
            payload={"fog_radius": 3, "duration_turns": 2},
        ),
        CombatEventResult(
            kind="log_message",
            event_key=event.key,
            label=event.name,
            message=f"⚠ BLACKOUT: {event.name}",
            payload={"banner": f"COMPLICATION: {event.name} — Visibility reduced!"},
        ),
    ]
