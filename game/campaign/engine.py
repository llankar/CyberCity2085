"""Campaign engine — pure tick function called from GameState.advance_one_day().

tick_campaign(game_state) drives:
  - Hungry Tide progress (weekly advance)
  - Calendar-milestone intel reveals
  - Act-advance checks
  - Story event triggers
  - World state updates from discovered intel
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.gamestate import GameState

from .campaign_state import CampaignState
from .intel_fragments import FRAGMENTS_BY_ID, fragments_for_act, IntelFragment
from .story_events import STORY_EVENT_SPECS

import random as _rnd

# Act advancement thresholds (story missions completed)
_ADVANCE_THRESHOLDS = {1: 3, 2: 4, 3: 5, 4: 5, 5: 999}


def tick_campaign(game_state: "GameState") -> None:
    """Advance the global campaign state by one in-game day.

    Called from GameState.advance_one_day(). Pure side effects on game_state.
    """
    c = game_state.campaign
    day = game_state.calendar.current_day

    # ── 1. Hungry Tide: +2 every 7 days ──────────────────────────────────────
    if day > 0 and day % 7 == 0 and c.current_act >= 2:
        increment = 3 if c.current_act >= 4 else 2
        c.world.hungry_tide_progress = min(100, c.world.hungry_tide_progress + increment)
        if c.world.hungry_tide_progress >= 100 and c.world.new_york_status != "siege":
            c.world.new_york_status = "siege"
            _reveal_intel(game_state, "act5_new_york_siege")
            game_state.add_event("THE TIDE HAS REACHED NEW YORK. THE SIEGE HAS BEGUN.")

    # ── 2. Calendar-milestone intel reveals ───────────────────────────────────
    if day > 0 and day % 7 == 0:
        _try_calendar_reveal(game_state)

    # ── 3. Story event triggers (act-gated, one-time) ─────────────────────────
    _check_story_event_triggers(game_state)

    # ── 4. Act-advance check ──────────────────────────────────────────────────
    _check_act_advance(game_state)


def record_story_mission_complete(game_state: "GameState", story_mission_id: str) -> None:
    """Call this when a story mission is completed (from end_battle resolution)."""
    from .story_missions import STORY_MISSIONS_BY_ID
    c = game_state.campaign
    mission = STORY_MISSIONS_BY_ID.get(story_mission_id)
    if mission is None or mission.act != c.current_act:
        return

    c.act_progress += 1
    game_state.add_event(
        f"[STORY] Story mission complete: {mission.title}. "
        f"Act {c.current_act} progress: {c.act_progress}/{c.missions_required}."
    )

    # Reveal intel rewards
    for frag_id in mission.intel_rewards:
        _reveal_intel(game_state, frag_id)

    # Apply world effects
    for attr, value in mission.world_effects.items():
        if hasattr(c.world, attr):
            setattr(c.world, attr, value)
def _reveal_intel(game_state: "GameState", fragment_id: str) -> None:
    """Reveal an intel fragment if not already discovered."""
    c = game_state.campaign
    fragment = FRAGMENTS_BY_ID.get(fragment_id)
    if fragment is None:
        return
    if fragment.act > c.current_act:
        return  # not yet reachable
    if not c.discover_intel(fragment_id):
        return  # already known

    # Update world state if fragment carries a world trigger
    if fragment.world_trigger and fragment.world_value:
        if hasattr(c.world, fragment.world_trigger):
            setattr(c.world, fragment.world_trigger, fragment.world_value)

    game_state.add_event(f"[INTEL] {fragment.title}: {fragment.text[:80]}…")

    # Play intel-reveal sound if audio is live
    try:
        from game.audio import SoundManager
        SoundManager.get().play("sfx_intel_reveal")
    except Exception:
        pass


def _try_calendar_reveal(game_state: "GameState") -> None:
    """Randomly reveal one calendar_milestone fragment for the current act."""
    c = game_state.campaign
    candidates = [
        f for f in fragments_for_act(c.current_act)
        if f.source == "calendar_milestone" and f.id not in c.discovered_intel
    ]
    if candidates:
        fragment = _rnd.choice(candidates)
        _reveal_intel(game_state, fragment.id)


def _check_story_event_triggers(game_state: "GameState") -> None:
    """Fire act-gated story events that haven't been seen yet."""
    from game.management.events import EventTemplate, EventChoice, ActiveEvent
    c = game_state.campaign
    day = game_state.calendar.current_day

    # Determine which story events should fire this act
    _ACT_EVENT_DAYS = {
        1: [5, 12],   # days within the act when events fire
        2: [3, 9],
        3: [4, 10],
        4: [3, 8],
        5: [2, 6],
    }
    trigger_days = _ACT_EVENT_DAYS.get(c.current_act, [5])

    for spec in STORY_EVENT_SPECS:
        tid = spec["trigger_id"]
        if spec["act"] != c.current_act:
            continue
        if tid in c.act_triggers_seen:
            continue
        # Fire based on act_progress milestones (progress 0 fires first event, 2 fires second)
        act_events_for_act = [s for s in STORY_EVENT_SPECS if s["act"] == c.current_act]
        event_index = act_events_for_act.index(spec) if spec in act_events_for_act else 0
        required_progress = event_index * 1  # fire at 0, 1, 2... story missions

        if c.act_progress < required_progress:
            continue

        c.act_triggers_seen.append(tid)

        # Reveal associated intel
        if spec.get("intel_reveal"):
            _reveal_intel(game_state, spec["intel_reveal"])

        # Apply world effects
        for attr, value in spec.get("world_effect", {}).items():
            if hasattr(c.world, attr):
                setattr(c.world, attr, value)

        # Create an active event in the management screen
        try:
            _fire_management_event(game_state, spec, day)
        except Exception:
            game_state.add_event(f"[CAMPAIGN] {spec['title']}: {spec['description'][:80]}…")

        game_state.add_event(f"[ACT {c.current_act}] {spec['title']}")
        break  # only one story event per tick


def _fire_management_event(game_state: "GameState", spec: dict, day: int) -> None:
    """Instantiate a story event as an ActiveEvent in game_state.active_events."""
    from game.management.events import EventTemplate, EventChoice, ActiveEvent

    # Map category string to a safe fallback
    category = spec.get("category", "CITY_POLITICS")

    choices = [
        EventChoice(
            key=c["key"],
            label=c["label"],
            effects=c.get("effects", {}),
            summary=c.get("summary", ""),
        )
        for c in spec.get("choices", [])
    ]

    template = EventTemplate(
        id=spec["id"],
        title=spec["title"],
        category=category,
        description=spec["description"],
        severity=spec.get("severity", 5),
        choices=choices,
        expiration_days=spec.get("expiration_days", 7),
        weight=0,  # story events are not randomly rolled
    )
    event = ActiveEvent(
        id=game_state.next_event_id,
        template=template,
        created_day=day,
        expires_day=day + template.expiration_days,
    )
    game_state.next_event_id += 1
    game_state.active_events.append(event)


def _check_act_advance(game_state: "GameState") -> None:
    """Advance to the next act if progress threshold is met."""
    c = game_state.campaign
    if c.current_act >= 5:
        return
    required = _ADVANCE_THRESHOLDS.get(c.current_act, 5)
    if c.act_progress < required:
        return
    if f"act_{c.current_act}_complete" in c.act_triggers_seen:
        return

    c.act_triggers_seen.append(f"act_{c.current_act}_complete")
    old_act = c.current_act
    c.current_act += 1
    c.act_progress = 0

    from .acts import ACT_TITLES
    new_title = ACT_TITLES.get(c.current_act, f"Act {c.current_act}")
    game_state.add_event(
        f"[CAMPAIGN] ACT {c.current_act} BEGINS — {new_title.upper()}"
    )

    # Play act-advance sound
    try:
        from game.audio import SoundManager
        SoundManager.get().play("sfx_act_advance")
    except Exception:
        pass

    # Store pending act-advance notification for the management screen overlay
    game_state._pending_act_advance = (c.current_act, new_title)
