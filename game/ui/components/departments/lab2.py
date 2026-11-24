"""R&D Lab 2.0 presentation over the existing campaign research model."""

from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, TEXT, MUTED, PURPLE
from .research import _draw_base_upgrades, _draw_mode_tabs


def draw_research(k, left, center, right):
    gs, u = k.gs, k.u
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
    categories = sorted({p.category for p in projects})
    category = k.selection.get("research_category", "all")
    if category != "all" and category not in categories:
        category = "all"
    filtered = [p for p in projects if category == "all" or p.category == category]

    k.panel(left, k.word("FILE DE RECHERCHE", "RESEARCH QUEUE"), "layers")
    body = _draw_mode_tabs(k, k.body(left), mode)
    queue_bottom = body.bottom + 180*u
    queue = Rect(body.left, queue_bottom, body.right, body.top)
    active_rows = [(tree.projects[pid], record) for pid, record in active.items() if pid in tree.projects]
    if active_rows:
        for _, (project, record), card in k.page("research_queue", active_rows, queue, 104):
            ratio = max(0.0, min(1.0, record.days_elapsed/project.days_required))
            k.card(card, project.name, f"{record.days_remaining} d LEFT", color=PURPLE)
            k.meter(Rect(card.left+14*u, card.bottom+12*u, card.right-14*u, card.bottom+20*u), ratio, PURPLE)
    else:
        k.paragraph(k.word("AUCUNE RECHERCHE ACTIVE", "NO ACTIVE RESEARCH"), queue, 17, MUTED)
    status = Rect(body.left, body.bottom, body.right, queue_bottom-12*u)
    k.surface(status, CYAN)
    k.label(k.word("ÉTAT DU LABO", "LAB STATUS"), status.left+14*u, status.top-25*u, 18, CYAN, bold=True)
    for i, (label, color) in enumerate(((f"{len(active_rows)} ACTIVE", PURPLE), (f"{len(completed)} COMPLETED", MINT), (f"{len(available)} AVAILABLE", GOLD))):
        k.label(label, status.left+14*u, status.top-(57+i*28)*u, 16, color)
    k.label(k.word("PROGRESSION PAR JOUR DE CAMPAGNE", "PROGRESS PER CAMPAIGN DAY"), status.left+14*u, status.bottom+18*u, 13, MUTED, width=status.width-28*u)

    k.panel(center, k.word("PROJETS DE RECHERCHE", "RESEARCH PROJECTS"), "chip")
    body = k.body(center)
    keys, cols, gap = ["all"]+categories, 4, 6*u
    tab_h = 34*u
    tab_w = (body.width-gap*(cols-1))/cols
    for i, key in enumerate(keys):
        row, col = divmod(i, cols)
        top = body.top-row*(tab_h+gap)
        x = body.left+col*(tab_w+gap)
        k.action(Rect(x, top-tab_h, x+tab_w, top), key.replace("_", " ").upper(), "department_select", ("research_category", key), selected=key == category)
    rows = (len(keys)+cols-1)//cols
    list_area = Rect(body.left, body.bottom, body.right, body.top-rows*(tab_h+gap)-5*u)
    selected = k.selection.get("research", filtered[0].id if filtered else None)
    if selected not in {p.id for p in filtered}:
        selected = filtered[0].id if filtered else None
    for _, project, card in k.page("research", filtered, list_area, 82):
        state = k.tr("completed") if project.id in completed else k.tr("active") if project.id in active else k.tr("ready") if project.id in available_ids else k.tr("locked")
        k.card(card, project.name, f"{project.category.upper()} / {state}", action="department_select", data=("research", project.id), selected=project.id == selected, color=PURPLE, tooltip=project.description)

    k.panel(right, k.word("DÉTAILS DE RECHERCHE", "RESEARCH DETAILS"), "chip")
    body = k.body(right)
    if selected is None:
        k.paragraph(k.tr("empty"), body, 18, MUTED)
        return
    project = tree.projects[selected]
    k.image("assets/ui/base_command_center/research_lab.png", Rect(body.left, body.top-155*u, body.right, body.top))
    k.surface(Rect(body.left, body.top-158*u, body.right, body.top-108*u), PURPLE)
    k.label(project.name, body.left+13*u, body.top-133*u, 23, TEXT, bold=True, width=body.width-26*u)
    y = body.top-176*u
    half = (body.width-10*u)/2
    k.stat(Rect(body.left, y-78*u, body.left+half, y), k.word("COÛT", "COST"), f"¥{project.funds_cost}", "coins", color=GOLD)
    k.stat(Rect(body.left+half+10*u, y-78*u, body.right, y), k.word("DURÉE", "DURATION"), f"{project.days_required} d", "clock", color=PURPLE)
    effects = [f"{name.replace('_', ' ').upper()} {value:+}" for name, value in project.stat_modifiers.items()]
    effects += [flag.replace(".", " / ").upper() for flag in project.unlock_flags]
    if project.unlocked_equipment_ids:
        from game.management.equipment import default_equipment_catalog
        equipment_names = {
            item.id: item.name
            for items in default_equipment_catalog().values()
            for item in items
        }
        effects += [
            k.word("ACHAT DÉBLOQUÉ : ", "PURCHASE UNLOCKED: ")
            + equipment_names.get(item_id, item_id)
            for item_id in project.unlocked_equipment_ids
        ]
    prerequisites = [tree.projects[x].name if x in tree.projects else x for x in project.requires]
    missing = [tree.projects[x].name for x in project.requires if x not in completed and x in tree.projects]
    detail = project.description + "\n\n" + project.category.upper()
    if effects:
        detail += "\n\n" + k.word("RÉSULTATS : ", "RESULTS: ") + "\n" + "\n".join(effects)
    if prerequisites:
        detail += "\n\n" + k.word("PRÉREQUIS : ", "REQUIRES: ") + ", ".join(prerequisites)
    if missing:
        detail += "\n" + k.word("MANQUANT : ", "MISSING: ") + ", ".join(missing)
    k.document("research_detail", detail, Rect(body.left, body.bottom+62*u, body.right, y-92*u), 16)
    index = next((i for i, item in enumerate(available) if item.id == project.id), 0)
    enabled = project.id in available_ids and gs.available_funds >= project.funds_cost
    k.action(Rect(body.left, body.bottom, body.right, body.bottom+48*u), k.word("LANCER LA RECHERCHE", "START RESEARCH"), f"start_research_{index}", enabled=enabled, primary=True, icon="chip", tooltip=detail)
