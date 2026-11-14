"""Stable public boundary for the complete mission lifecycle.

The legacy ``game.mission_system`` module remains as a compatibility facade for
old saves, tests, and extensions. New release-path UI imports this module.
"""

from game.mission_system import (
    apply_faction_narrative_rewards,
    clone_selected_mission,
    ensure_mission_templates,
    evaluate_mission_objective_phase,
    format_skill_check_outcome,
    launch_selected_mission,
    mission_objective_branch_summary,
    pick_complication,
    resolve_mission_outcome,
    selected_mission,
)

__all__ = [
    "apply_faction_narrative_rewards",
    "clone_selected_mission",
    "ensure_mission_templates",
    "evaluate_mission_objective_phase",
    "format_skill_check_outcome",
    "launch_selected_mission",
    "mission_objective_branch_summary",
    "pick_complication",
    "resolve_mission_outcome",
    "selected_mission",
]
