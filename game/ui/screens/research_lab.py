"""Research lab panel text for the corporate command tower."""

from __future__ import annotations

from ...management.research import ResearchProject, ResearchTree, create_starter_research_tree


def _project_label(project: ResearchProject) -> str:
    return f"{project.name} ({project.days_required}d, ¥{project.funds_cost})"


def _build_research_tree_lines(
    tree: ResearchTree,
    completed: set[str],
    active_ids: set[str],
    max_lines: int = 8,
) -> list[str]:
    """Render available projects as a compact dependency tree."""
    available_projects = tree.available_projects(completed, active_ids)
    if not available_projects:
        return ["Tree: no available branch (complete active projects)."]

    by_parent: dict[str | None, list[ResearchProject]] = {None: []}
    for project in available_projects:
        parent = project.requires[0] if project.requires else None
        by_parent.setdefault(parent, []).append(project)

    for children in by_parent.values():
        children.sort(key=lambda item: (item.category, item.name))

    lines = ["Research tree:"]
    roots = by_parent.get(None, [])
    for root in roots:
        lines.append(f"• {_project_label(root)}")
        for child in by_parent.get(root.id, [])[:2]:
            lines.append(f"  └─ {_project_label(child)}")

    if len(lines) > max_lines:
        clipped = lines[: max_lines - 1]
        clipped.append("  …more branches available")
        return clipped
    return lines


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
        "Recommended action: prioriser un projet court si la pression augmente.",
    ]
    if active_research:
        for active in active_research[:2]:
            project = tree.project(active.project_id)
            name = project.name if project else active.project_id
            lines.append(f"ACTIVE {name}: {active.days_remaining}d remaining")
    else:
        lines.append("No active project. Choose a starter study.")

    lines.extend(_build_research_tree_lines(tree, completed, active_ids, max_lines=9 - len(lines)))

    if completed:
        lines.append(
            f"Completed: {len(completed)} | Unlocks {len(getattr(game_state, 'research_unlock_flags', []))}"
        )
    else:
        lines.append("Completed: none")
    return lines[:9]
