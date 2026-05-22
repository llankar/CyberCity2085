from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NextActionGuidance:
    text: str
    target_screen: str
    target_room: str


def _injured_agents(game_state) -> int:
    return sum(1 for c in getattr(game_state, "characters", []) if getattr(c, "recovery_turns", 0) > 0)


def compute_next_action(game_state, screen: str) -> NextActionGuidance:
    resources = getattr(game_state, "strategic_resources", {})
    missions = getattr(game_state, "mission_templates", [])
    selected = getattr(game_state, "selected_agent_names", [])

    if getattr(game_state, "available_funds", 0) <= 0:
        return NextActionGuidance("Advance one day to recover emergency funding.", "corp", "executive")
    if not missions:
        return NextActionGuidance("Advance one day to generate new mission opportunities.", "city", "records")
    if _injured_agents(game_state) >= max(1, len(getattr(game_state, "characters", [])) // 2):
        return NextActionGuidance("Open Medbay and rotate injured agents out of deployment.", "squad", "medbay")
    if not getattr(game_state, "research_unlock_flags", []):
        return NextActionGuidance("Start a research project to unlock strategic options.", "corp", "research")
    if len(selected) < 2:
        return NextActionGuidance("Select 2 more agents to complete your squad.", "squad", "armory")
    if int(resources.get("credits", 0)) <= 2 and int(resources.get("intel", 0)) <= 1:
        return NextActionGuidance("Open Mission Board and choose a low-risk resource mission.", "squad", "ops")
    if screen == "battle":
        return NextActionGuidance("Choose a drop zone to begin tactical insertion.", "battle", "maps")
    return NextActionGuidance("Launch the selected mission to keep initiative.", "squad", "insertion")
