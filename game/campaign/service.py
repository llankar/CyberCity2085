"""Stable public boundary for campaign progression behavior.

State remains on :class:`GameState`; the implementation stays in the focused
campaign engine while callers no longer depend on its internal module layout.
"""

from .engine import record_story_mission_complete, tick_campaign

__all__ = ["record_story_mission_complete", "tick_campaign"]
