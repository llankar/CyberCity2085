"""Research lab panel text for the corporate command tower."""

from __future__ import annotations

from ..management.research import ResearchTree, create_starter_research_tree


def build_research_lab_lines(
    game_state: object, tree: ResearchTree | None = None
) -> list[str]:
    """Build compact UI copy for active, available, and completed research."""
    tree = tree or getattr(game_state, "research_tree", create_starter_research_tree())
    active_research = list(getattr(game_state, "active_research", []))
    completed = set(getattr(game_state, "completed_research", []))
    active_ids = {active.project_id for active in active_research}

    resources = getattr(game_state, "strategic_resources", {})
    lines = [
        f"Funds {getattr(game_state, 'available_funds', 0)} | Lab queue {len(active_research)}",
        f"Intel reserve {resources.get('intel', 0)}",
    ]
    if active_research:
        for active in active_research[:2]:
            project = tree.project(active.project_id)
            name = project.name if project else active.project_id
            lines.append(f"ACTIVE {name}: {active.days_remaining}d remaining")
    else:
        lines.append("No active project. Choose a starter study.")

    available = tree.available_projects(completed, active_ids)
    for index, project in enumerate(available[:3], start=1):
        lines.append(
            f"{index}. {project.name} [{project.category.replace('_', ' ')}] "
            f"{project.funds_cost} funds / {project.days_required}d"
        )

    if completed:
        lines.append(
            f"Completed: {len(completed)} | Unlocks {len(getattr(game_state, 'research_unlock_flags', []))}"
        )
    else:
        lines.append("Completed: none")
    return lines[:7]
