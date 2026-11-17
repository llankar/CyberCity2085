"""Data-driven research presentation; original controllers own all mutations."""

from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, TEXT, MUTED, PURPLE


def draw_research(k, left, center, right):
    gs = k.gs
    u = k.u
    tree = gs.research_tree
    completed = set(gs.completed_research)
    active = {a.project_id: a for a in gs.active_research}
    available = tree.available_projects(completed, set(active))
    available_ids = {p.id for p in available}
    projects = list(tree.projects.values())
    k.panel(left, k.tr("research"), "chip")
    r = k.body(left)
    selected = k.selection.get("research", projects[0].id if projects else None)
    if selected not in tree.projects:
        selected = projects[0].id if projects else None
    for i, p, card in k.page("research", projects, r, 83):
        state = (
            k.tr("completed")
            if p.id in completed
            else (
                k.tr("active")
                if p.id in active
                else k.tr("ready") if p.id in available_ids else k.tr("locked")
            )
        )
        k.card(
            card,
            p.name,
            f"{p.category.upper()} / {state}",
            action="department_select",
            data=("research", p.id),
            selected=p.id == selected,
            color=PURPLE,
            tooltip=p.description,
        )
    k.panel(center, k.tr("profile"), "chip")
    r = k.body(center)
    if selected is not None:
        p = tree.projects[selected]
        if k.view.room_ui.texture_override:
            k.texture(
                k.view.room_ui.texture_override,
                Rect(r.left, r.top - 170 * u, r.right, r.top),
            )
        k.paint.panel(Rect(r.left, r.top - 173 * u, r.right, r.top - 115 * u), PURPLE)
        k.label(
            p.name,
            r.left + 14 * u,
            r.top - 144 * u,
            27,
            TEXT,
            bold=True,
            width=r.width - 28 * u,
        )
        y = r.top - 192 * u
        half = (r.width - 12 * u) / 2
        k.stat(
            Rect(r.left, y - 90 * u, r.left + half, y),
            k.word("COÛT", "COST"),
            f"¥{p.funds_cost}",
            "coins",
            color=GOLD,
        )
        k.stat(
            Rect(r.left + half + 12 * u, y - 90 * u, r.right, y),
            k.word("DURÉE", "DURATION"),
            (
                f"{p.days_required} j"
                if gs.ui_language == "fr"
                else f"{p.days_required} d"
            ),
            "clock",
            color=PURPLE,
        )
        detail = (
            p.description
            + "\n\n"
            + p.category.upper()
            + "\n"
            + ", ".join(f"{a} {b:+}" for a, b in p.stat_modifiers.items())
            + "\n"
            + ", ".join(p.unlock_flags)
        )
        if p.requires:
            detail += (
                "\n"
                + k.word("PRÉREQUIS : ", "REQUIRES: ")
                + ", ".join(
                    tree.projects[a].name if a in tree.projects else a
                    for a in p.requires
                )
            )
        k.document(
            "research_detail",
            detail,
            Rect(r.left, r.bottom + 65 * u, r.right, y - 112 * u),
            17,
        )
        k.action(
            Rect(r.left, r.bottom, r.right, r.bottom + 47 * u),
            k.word("LANCER LA RECHERCHE", "START RESEARCH"),
            f"start_research_{next((i for i,x in enumerate(available) if x.id==p.id),0)}",
            enabled=p.id in available_ids and gs.available_funds >= p.funds_cost,
            primary=True,
            icon="chip",
            tooltip=detail,
        )
    k.panel(right, k.word("AVANCEMENT", "PROGRESS"), "layers")
    r = k.body(right)
    rows = []
    for pid, a in active.items():
        p = tree.projects[pid]
        rows.append(
            (
                p.name,
                k.word(
                    f"{a.days_remaining} j RESTANTS / {a.days_elapsed} j ÉCOULÉS",
                    f"{a.days_remaining} d LEFT / {a.days_elapsed} d ELAPSED",
                ),
                1 - a.days_remaining / p.days_required,
                PURPLE,
            )
        )
    rows += [
        (tree.projects[pid].name, k.tr("completed"), 1, MINT)
        for pid in completed
        if pid in tree.projects
    ]
    for i, (name, status, ratio, color), card in k.page(
        "research_progress", rows, r, 90
    ):
        k.card(card, name, status, color=color)
        k.meter(
            Rect(
                card.left + 16 * u,
                card.bottom + 12 * u,
                card.right - 16 * u,
                card.bottom + 18 * u,
            ),
            ratio,
            color,
        )
    if not rows:
        k.paragraph(k.tr("empty"), r, 18, MUTED)
