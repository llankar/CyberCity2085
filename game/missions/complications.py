from __future__ import annotations

import random

from game.consequences import Consequence
from game.mission_templates import MissionComplication


_COMPLICATION_TABLE: dict[str, tuple[dict[str, str], ...]] = {
    "low": (
        {"key": "signal_noise", "name": "Signal Noise", "trigger": "Encrypted comms crackle and delay callouts."},
        {"key": "street_detour", "name": "Street Detour", "trigger": "A patrol sweep closes the shortest alley route."},
    ),
    "medium": (
        {"key": "watcher_drone", "name": "Watcher Drone", "trigger": "A low-orbit drone tracks heat signatures near the objective."},
        {"key": "crowd_choke", "name": "Crowd Choke", "trigger": "Night-market foot traffic compresses movement lanes."},
    ),
    "high": (
        {"key": "counterintel_ping", "name": "Counterintel Ping", "trigger": "Corporate counterintel flags the operation in real time."},
        {"key": "rapid_response", "name": "Rapid Response", "trigger": "A rapid-response squad is rerouted toward the extraction line."},
    ),
}

_TAG_HINTS: dict[str, str] = {
    "stealth": "signal_noise",
    "extraction": "street_detour",
    "rescue": "crowd_choke",
    "sabotage": "watcher_drone",
    "data": "counterintel_ping",
    "infiltration": "counterintel_ping",
    "assault": "rapid_response",
}


def _pressure_bucket(district_pressure: int) -> str:
    if district_pressure >= 70:
        return "high"
    if district_pressure >= 35:
        return "medium"
    return "low"


def _to_complication(entry: dict[str, str], pressure_level: str) -> MissionComplication:
    return MissionComplication(
        key=f"mod_{entry['key']}",
        name=entry["name"],
        trigger_text=entry["trigger"],
        risk_threshold=1 if pressure_level == "low" else 2 if pressure_level == "medium" else 3,
        relation_impact="low",
        tags=[],
        consequence=Consequence(),
    )


def select_complications(
    district_pressure: int,
    mission_tags: list[str] | tuple[str, ...] | None,
    seed: int | None = None,
) -> list[MissionComplication]:
    """Pure selector: pressure + mission tags -> 1..2 compact complications.

    The output is intentionally lightweight (narrative flavor only) and never exceeds
    two entries to preserve scope control and avoid hidden difficulty spikes.
    """
    tags = [str(tag).strip().lower() for tag in (mission_tags or []) if str(tag).strip()]
    level = _pressure_bucket(max(0, int(district_pressure)))
    pool = list(_COMPLICATION_TABLE[level])
    rng_seed = seed if seed is not None else (district_pressure * 131) + sum(ord(ch) for ch in "|".join(sorted(tags)))
    rng = random.Random(rng_seed)

    preferred_keys = {hint for tag, hint in _TAG_HINTS.items() if tag in tags}
    preferred = [entry for entry in pool if entry["key"] in preferred_keys]
    fallback = [entry for entry in pool if entry["key"] not in preferred_keys]

    selected: list[dict[str, str]] = []
    if preferred:
        selected.append(rng.choice(preferred))

    count = 2 if level == "high" else 1
    remaining_pool = [entry for entry in (preferred + fallback) if entry not in selected]
    rng.shuffle(remaining_pool)
    selected.extend(remaining_pool[: max(0, count - len(selected))])

    return [_to_complication(entry, level) for entry in selected[:2]]
