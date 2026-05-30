"""Mission selection and resolution rules independent of Arcade views."""

import random

from .gamestate import GameState
from .enemy_themes import mission_enemy_theme
from .mission_generation import generate_mission_board
from .mission_templates import (
    MissionComplication,
    MissionTemplate,
)
from .missions.objective_branches import (
    branch_summary_lines,
    evaluate_objective_phase,
    get_objective_branch,
)
from .narrative.personality_traits import modulate_mission_log_tone
from .narrative.faction_rewards import build_reward_log_entries, rewards_for_faction

def format_skill_check_outcome(
    *,
    check_name: str,
    rolled_value: int,
    total_value: int,
    threshold: int,
) -> str:
    """Return a one-line CRPG-style skill-check summary for logs/debrief."""
    result = "SUCCESS" if total_value >= threshold else "FAILURE"
    return (
        f"{check_name}: roll {rolled_value} -> total {total_value} "
        f"(target {threshold}) [{result}]"
    )


def _selected_mission_leader(game_state: GameState):
    """Return the first selected leader using canonical selected-agent names."""
    if not game_state.selected_agent_names:
        return None
    roster_by_name = {character.name: character for character in game_state.characters}
    return roster_by_name.get(game_state.selected_agent_names[0])


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
    mission.enemy_theme = mission_enemy_theme(mission)
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



def evaluate_mission_objective_phase(
    mission: MissionTemplate | None,
    objective_state: dict,
    current_phase_id: str | None = None,
) -> dict | None:
    """Evaluate one objective phase and return a UI/test-friendly payload."""
    if not mission:
        return None
    branch = get_objective_branch(mission.objective_type)
    if not branch:
        return None
    phase_id = current_phase_id or branch.start_phase
    result = evaluate_objective_phase(branch, phase_id, objective_state)
    return {
        "branch_id": branch.template_id,
        "phase_id": result.phase_id,
        "succeeded": result.succeeded,
        "issue_text": result.issue_text,
        "next_phase_id": result.next_phase_id,
        "finished": result.finished,
    }


def mission_objective_branch_summary(mission: MissionTemplate | None) -> list[str]:
    """Expose a readable branch summary for mission data/UI."""
    if not mission:
        return []
    return branch_summary_lines(mission.objective_type)

def apply_faction_narrative_rewards(
    game_state: GameState, mission: MissionTemplate | None, victory: bool
) -> list[dict[str, str]]:
    """Grant compact faction narrative beats only on partial/total mission success."""
    if not mission or not victory:
        return []

    rewards = rewards_for_faction(mission.target_faction)
    reward_entries: list[dict[str, str]] = []
    for reward in rewards:
        reward_entries.append(
            {
                "faction": mission.target_faction,
                "mission_id": mission.id,
                "mission_title": mission.title,
                "kind": reward.kind,
                "text": reward.text,
            }
        )
    game_state.faction_reward_journal.extend(reward_entries)
    game_state.faction_reward_journal = game_state.faction_reward_journal[-24:]

    for line in build_reward_log_entries(mission.target_faction, mission.title):
        game_state.add_event(line)

    return reward_entries


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
    apply_faction_narrative_rewards(game_state, mission, victory)

    complication = pick_complication(mission, triggered_complication)
    if complication:
        consequence = complication.consequence
        if not consequence.affected_faction:
            consequence.affected_faction = mission.target_faction
        game_state.apply_consequence(consequence)
        base_text = f"Complication triggered: {complication.trigger_text}"
        leader = _selected_mission_leader(game_state)
        game_state.add_event(
            modulate_mission_log_tone(
                base_text,
                getattr(leader, "personality_primary_trait", ""),
                getattr(leader, "personality_secondary_trait", ""),
            )
        )

    game_state.active_mission = None
    duration_days = max(1, int(getattr(mission, "duration_days", 1)))
    game_state.advance_days(
        duration_days, "mission success" if victory else "mission failure"
    )
    return complication
