"""Data-driven research presentation; original controllers own all mutations."""

from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, TEXT, MUTED, PURPLE


def draw_research(k, left, center, right):
    gs = k.gs
    u = k.u
    mode = k.selection.get("research_mode", "research")
    if mode == "base":
        _draw_base_upgrades(k, left, center, right)
        return
    tree = gs.research_tree
    completed = set(gs.completed_research)
    active = {a.project_id: a for a in gs.active_research}
    available = tree.available_projects(completed, set(active))
    available_ids = {p.id for p in available}
    projects = list(tree.projects.values())
    k.panel(left, k.tr("research"), "chip")
    r = k.body(left)
    r = _draw_mode_tabs(k, r, mode)
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
        k.surface(Rect(r.left, r.top - 173 * u, r.right, r.top - 115 * u), PURPLE)
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
            f"₦{p.funds_cost:,}",
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
        if p.unlocked_equipment_ids:
            from game.management.equipment import default_equipment_catalog
            equipment_names = {
                item.id: item.name
                for items in default_equipment_catalog().values()
                for item in items
            }
            detail += "\n" + k.word("ÉQUIPEMENTS DÉBLOQUÉS : ", "EQUIPMENT UNLOCKED: ")
            detail += ", ".join(
                equipment_names.get(item_id, item_id)
                for item_id in p.unlocked_equipment_ids
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


def _draw_base_upgrades(k, left, center, right):
    from game.management.base_upgrades import BASE_UPGRADES, VEHICLE_UPGRADES
    gs, u = k.gs, k.u
    k.panel(left, "BASE UPGRADES", "layers")
    area = _draw_mode_tabs(k, k.body(left), "base")
    choices = list(BASE_UPGRADES) + list(VEHICLE_UPGRADES)
    selected = k.selection.get("base_upgrade", choices[0].id)
    for _, item, card in k.page("base_upgrades", choices, area, 78):
        vehicle = item in VEHICLE_UPGRADES
        owned = item.id in (gs.vehicle_upgrade_ids if vehicle else gs.base_upgrade_ids)
        if item.id == "hangar": owned = gs.hangar.is_max_level
        k.card(card, item.name, "INSTALLED" if owned else ("VEHICLE" if vehicle else "BASE") + f" // ₦{item.cost:,}", action="department_select", data=("base_upgrade", item.id), selected=item.id == selected, color=GOLD if vehicle else CYAN, tooltip=item.description)
    item = next((x for x in choices if x.id == selected), choices[0])
    vehicle = item in VEHICLE_UPGRADES
    k.panel(center, "UPGRADE DETAILS", "chip")
    body = k.body(center)
    k.label(item.name, body.left+12*u, body.top-30*u, 23, TEXT, bold=True, width=body.width-24*u)
    k.paragraph(item.description + "\n\n" + item.effect, Rect(body.left+12*u, body.bottom+90*u, body.right-12*u, body.top-65*u), 16, TEXT)
    if item.id == "hangar":
        nxt = gs.hangar.next_upgrade
        label = "MAX LEVEL" if nxt is None else f"UPGRADE HANGAR // ₦{nxt[3]:,}"
        enabled = bool(nxt and gs.can_afford(nxt[3]))
        action, data = "upgrade_hangar", None
    else:
        owned = item.id in (gs.vehicle_upgrade_ids if vehicle else gs.base_upgrade_ids)
        label = "INSTALLED" if owned else f"INSTALL // ₦{item.cost:,}"
        enabled = not owned and gs.can_afford(item.cost)
        action, data = "purchase_base_upgrade", (item.id, vehicle)
    k.action(Rect(body.left, body.bottom, body.right, body.bottom+55*u), label, action, data, enabled=enabled, primary=True)
    k.panel(right, "DEPLOYMENT VEHICLE", "assets")
    body = k.body(right)
    k.label("NIGHTHAWK VTOL", body.left+12*u, body.top-28*u, 22, GOLD, bold=True)
    vehicle_art = Rect(
        body.left + 12*u,
        body.top - 250*u,
        body.right - 12*u,
        body.top - 48*u,
    )
    k.image(
        "assets/units/vehicle_aerial_military_04_vtol_stealth_dropship_512.png",
        vehicle_art,
        cover=False,
    )
    installed = [x for x in VEHICLE_UPGRADES if x.id in gs.vehicle_upgrade_ids]
    text = "ACTIVE MODULES\n\n" + ("\n".join(f"• {x.name}: {x.effect}" for x in installed) if installed else "No vehicle modules installed.")
    k.document(
        "vehicle_modules",
        text,
        Rect(body.left, body.bottom, body.right, vehicle_art.bottom - 10*u),
        16,
    )


def _draw_mode_tabs(k, area: Rect, mode: str) -> Rect:
    """Draw readable local tabs and return the remaining list area."""
    u = k.u
    tabs = Rect(area.left, area.top - 44*u, area.right, area.top)
    gap = 7*u
    half = (tabs.width-gap)/2
    k.action(Rect(tabs.left, tabs.bottom, tabs.left+half, tabs.top), "RESEARCH", "department_select", ("research_mode", "research"), selected=mode == "research")
    k.action(Rect(tabs.left+half+gap, tabs.bottom, tabs.right, tabs.top), "BASE + VEHICLE", "department_select", ("research_mode", "base"), selected=mode == "base", primary=mode == "base")
    return Rect(area.left, area.bottom, area.right, tabs.bottom-10*u)
