"""Generate roadmap documentation snippets from a prioritized backlog."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class BacklogTask:
    id: str
    title: str
    domain: str
    priority: int
    emotional_weight: int
    modularity_weight: int
    scope_weight: int


BACKLOG_TASKS: List[BacklogTask] = [
    BacklogTask("AGENT-01", "Create post-mission narrative debrief scenes based on consequences.", "agent", 10, 10, 7, 8),
    BacklogTask("AGENT-02", "Add support dialogue between stressed agents in the recovery room.", "agent", 10, 9, 8, 8),
    BacklogTask("MISSION-01", "Introduce multi-stage objective variants with readable branches.", "mission", 9, 7, 9, 7),
    BacklogTask("UI-01", "Show a recent-event narrative feed in the command center.", "ui", 8, 8, 8, 8),
    BacklogTask("TEST-01", "Cover daily mission generation with additional regression tests.", "tests", 8, 6, 10, 9),
    BacklogTask("DOC-01", "Document emotion-centered design rules and scope control.", "docs", 7, 6, 9, 10),
    BacklogTask("AGENT-03", "Add a mentor/protege link history between recruited agents.", "agent", 9, 10, 8, 8),
    BacklogTask("MISSION-02", "Add light dynamic complications influenced by district pressure.", "mission", 8, 7, 8, 9),
    BacklogTask("UI-02", "Create a compact squad morale panel in the RPG view.", "ui", 8, 9, 8, 8),
    BacklogTask("TEST-02", "Validate daily mission seed stability with deterministic tests.", "tests", 7, 5, 10, 9),
    BacklogTask("DOC-02", "Add examples of agent emotional loops to the roadmap.", "docs", 7, 7, 8, 10),
    BacklogTask("AGENT-04", "Link serious wounds to temporary narrative aftereffects.", "agent", 9, 10, 7, 8),
    BacklogTask("MISSION-03", "Create an evacuation mission that prioritizes agent survival.", "mission", 8, 9, 8, 8),
    BacklogTask("UI-03", "Highlight critical choices that affect team relationships.", "ui", 8, 8, 8, 9),
    BacklogTask("TEST-03", "Add integration tests for stress, recovery, and calendar flow.", "tests", 8, 6, 10, 9),
    BacklogTask("DOC-03", "Describe the backlog -> next steps -> roadmap pipeline in docs.", "docs", 7, 5, 9, 10),
    BacklogTask("AGENT-05", "Add personality traits that modulate mission logs.", "agent", 9, 9, 8, 8),
    BacklogTask("MISSION-04", "Add light narrative rewards based on the targeted faction.", "mission", 8, 8, 8, 9),
    BacklogTask("UI-04", "Show mission tags and expected emotional impact at launch.", "ui", 7, 8, 8, 9),
    BacklogTask("TEST-04", "Test domain-tag consistency in markdown exports.", "tests", 7, 5, 10, 10),
    BacklogTask("DOC-04", "Create a maintainability checklist for new features.", "docs", 7, 5, 9, 10),
    BacklogTask("UI-05", "Add a text size setting with small, medium, and large presets in SettingsView.", "ui", 7, 8, 8, 9),
    # Wave 6 - Global Campaign Scenario
    BacklogTask("CAMP-01", "Persist CampaignState and WorldState in GameState (5 acts).", "campaign", 10, 10, 9, 8),
    BacklogTask("CAMP-02", "25 narrative intel fragments spread across the 5 acts.", "campaign", 10, 10, 8, 7),
    BacklogTask("CAMP-03", "10 story missions injected into the mission board.", "campaign", 9, 9, 8, 7),
    BacklogTask("CAMP-04", "Campaign engine: tick_campaign, act progression, Hungry Tide.", "campaign", 9, 8, 9, 8),
    BacklogTask("CAMP-05", "Global Scenario panel in the Intel room (world state + intel).", "campaign", 9, 9, 8, 7),
    BacklogTask("CAMP-06", "Act progress overlay + sfx_intel_reveal / sfx_act_advance sounds.", "campaign", 8, 9, 7, 6),
    BacklogTask("CAMP-07", "Intel fragments integrated into the management screen narrative feed.", "campaign", 8, 9, 8, 7),
    # Wave 5 - Gameplay Depth, Battle Spectacle & Mission Variety
    BacklogTask("BATTLE-W5A2", "AI target scoring - injured priority, threat roles, distance.", "battle", 9, 7, 8, 7),
    BacklogTask("BATTLE-W5A3", "Show narrative debrief lines with tone colors.", "battle", 9, 9, 8, 7),
    BacklogTask("BATTLE-W5B1", "2-second mission intro sequence with scan line and fade-in title.", "battle", 8, 8, 7, 6),
    BacklogTask("BATTLE-W5B2", "12% critical hit system: x2 damage, CRITICAL! popup, shake.", "battle", 9, 8, 8, 7),
    BacklogTask("BATTLE-W5B3", "Floating +XP text above the shooter on each kill.", "battle", 7, 8, 8, 7),
    BacklogTask("BATTLE-W5B4", "Atmospheric mood: scanlines, neon glow, rain on rain/fog maps.", "battle", 8, 7, 7, 6),
    BacklogTask("BATTLE-W5C1", "Defense objective: hold N turns, defeat if enemy reaches the position.", "battle", 8, 8, 8, 7),
    BacklogTask("BATTLE-W5C2", "Assassination objective: target marker + instant win on kill.", "battle", 8, 8, 7, 7),
    BacklogTask("BATTLE-W5D1", "Post-combat agent promotion screen when an agent levels up.", "battle", 9, 10, 8, 7),
    BacklogTask("BATTLE-W5D2", "Morale events in combat: allies KIA -> 30% SUPPRESSED on survivors.", "battle", 8, 10, 7, 7),
    # Mission View Professional Upgrade - Phase 1 (Visual Polish)
    BacklogTask("BATTLE-A01", "Create a mission briefing screen before battle view launch.", "battle", 10, 9, 8, 7),
    BacklogTask("BATTLE-P01", "Enable camera pan with Shift+arrows and recenter on the active unit.", "battle", 9, 6, 7, 6),
    BacklogTask("BATTLE-P02", "Add floating damage numbers above hit units.", "battle", 9, 8, 8, 7),
    BacklogTask("BATTLE-A02", "Add a pre-combat deployment phase for positioning agents.", "battle", 9, 8, 8, 7),
    BacklogTask("BATTLE-A03", "Enrich the post-battle debrief screen with per-agent stats and rewards.", "battle", 9, 9, 8, 7),
    BacklogTask("BATTLE-P03", "Convert the action bar to icon+label format with the design system.", "battle", 8, 7, 8, 7),
    BacklogTask("BATTLE-P04", "Add an in-battle pause menu (Esc) with summary/settings/abandon.", "battle", 8, 6, 7, 7),
    BacklogTask("BATTLE-G01", "Wire terrain pathfinding to the existing walkability mask in combat.", "battle", 8, 5, 9, 8),
    BacklogTask("BATTLE-G02", "Improve enemy AI with cover-seeking and flanking.", "battle", 8, 6, 8, 8),
    BacklogTask("BATTLE-G03", "Enable dynamic mid-battle events from complications.py.", "battle", 8, 8, 7, 8),
    BacklogTask("BATTLE-P05", "Promote the combat log panel to a player-accessible side view.", "battle", 7, 7, 8, 7),
    BacklogTask("BATTLE-G04", "Add status effects (suppressed, bleeding, stunned) to units.", "battle", 7, 7, 8, 8),
]


def load_backlog() -> list[BacklogTask]:
    """Load backlog tasks from local constants."""
    return list(BACKLOG_TASKS)


def _task_score(task: BacklogTask) -> int:
    return (
        task.priority * 5
        + task.emotional_weight * 4
        + task.modularity_weight * 3
        + task.scope_weight * 2
    )


def compute_next_steps(limit: int = 20) -> list[BacklogTask]:
    """Compute the next most valuable coding steps with stable ordering."""
    ranked = sorted(
        load_backlog(),
        key=lambda task: (-_task_score(task), task.domain, task.id),
    )
    return ranked[:limit]


def render_markdown(steps: Iterable[BacklogTask]) -> str:
    """Render a stable markdown block for roadmap docs."""
    lines = ["## Next 20 Coding Steps", ""]
    for index, step in enumerate(steps, start=1):
        lines.append(f"{index}. [{step.domain}] {step.id} — {step.title}")
    lines.append("")
    return "\n".join(lines)


def write_docs(output_path: str = "docs/roadmap.md") -> Path:
    """Write generated markdown to the target roadmap file."""
    path = Path(output_path)
    generated = render_markdown(compute_next_steps(limit=20))
    path.write_text(generated, encoding="utf-8")
    return path


if __name__ == "__main__":
    output = write_docs()
    print(f"Generated next steps in {output}")
