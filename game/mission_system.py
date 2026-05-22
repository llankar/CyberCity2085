"""Mission selection and resolution rules independent of Arcade views."""

import random

from .gamestate import GameState
from .mission_generation import generate_mission_board
from .mission_templates import (
    MissionComplication,
    MissionTemplate,
)


def ensure_mission_templates(game_state: GameState) -> None:
    """Ensure there is a selectable mission board and clamp the selected index."""
    if (
        not game_state.mission_templates
        or game_state.mission_board_generated_day != game_state.calendar.current_day
    ):
        game_state.mission_templates = generate_mission_board(game_state)
        game_state.mission_board_generated_day = game_state.calendar.current_day
        game_state.selected_mission_index = 0
    game_state.selected_mission_index %= len(game_state.mission_templates)


def selected_mission(game_state: GameState) -> MissionTemplate:
    """Return the currently selected mission template."""
    ensure_mission_templates(game_state)
    return game_state.mission_templates[game_state.selected_mission_index]


def clone_selected_mission(game_state: GameState) -> MissionTemplate:
    """Return a copy of the selected mission so runtime mutations do not alter templates."""
    return MissionTemplate.from_dict(selected_mission(game_state).to_dict())


def launch_selected_mission(game_state: GameState) -> MissionTemplate:
    """Set the active mission and apply launch pressure."""
    selected = selected_mission(game_state)
    if selected.id in game_state.unavailable_mission_ids:
        game_state.add_event(
            f"Mission unavailable: {selected.title} route is disrupted."
        )
        raise ValueError(f"Mission unavailable: {selected.title}")
    mission = MissionTemplate.from_dict(selected.to_dict())
    game_state.active_mission = mission
    game_state.apply_active_mission_pressure()
    return mission


def pick_complication(
    mission: MissionTemplate | None,
    already_triggered: MissionComplication | None = None,
) -> MissionComplication | None:
    """Choose a mission complication when risk/tags make one eligible."""
    if not mission or already_triggered:
        return None
    tag_intensity = sum(tag.intensity for tag in mission.tags)
    risk_score = mission.risk_level + tag_intensity
    eligible = [
        complication
        for complication in mission.possible_complications
        if risk_score >= complication.risk_threshold
        or any(
            tag.name in {mission_tag.name for mission_tag in mission.tags}
            for tag in complication.tags
        )
    ]
    if not eligible:
        return None
    return random.choice(eligible)


def resolve_mission_outcome(
    game_state: GameState,
    mission: MissionTemplate | None,
    victory: bool,
    triggered_complication: MissionComplication | None = None,
) -> MissionComplication | None:
    """Apply success/failure consequences and any complication fallout."""
    if not mission:
        return None

    consequences = (
        mission.success_consequences if victory else mission.failure_consequences
    )
    for consequence in consequences:
        game_state.apply_consequence(consequence)

    game_state.award_mission_funds(mission, victory)

    complication = pick_complication(mission, triggered_complication)
    if complication:
        consequence = complication.consequence
        if not consequence.affected_faction:
            consequence.affected_faction = mission.target_faction
        game_state.apply_consequence(consequence)
        game_state.add_event(f"Complication triggered: {complication.trigger_text}")

    game_state.active_mission = None
    duration_days = max(1, int(getattr(mission, "duration_days", 1)))
    game_state.advance_days(
        duration_days, "mission success" if victory else "mission failure"
    )
    return complication
