"""Asset Bay cards and profile; acquisition/repair/pilot rules stay in controllers."""

from game.management.spec_ops_assets import asset_catalog
from game.management.equipment import (
    AVAILABILITY_RESEARCH,
    default_equipment_catalog,
    equipment_power_band,
    equipment_power_score,
    equipment_purchase_price,
)
from game.ui.components.equipment_art import equipment_art_path
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, TEXT, MUTED


def draw(k, left, center, right):
    """Draw the Asset Bay armory by default, with vehicles kept as a peer mode."""
    mode = k.selection.get("asset_bay_mode", "armory")
    if mode == "vehicles":
        _draw_vehicles(k, left, center, right)
    else:
        _draw_armory(k, left, center, right)


def _mode_tabs(k, area, mode):
    u = k.u
    row = Rect(area.left, area.top - 42 * u, area.right, area.top)
    gap = 7 * u
    half = (row.width - gap) / 2
    k.action(Rect(row.left, row.bottom, row.left + half, row.top), "ARMORY", "department_select", ("asset_bay_mode", "armory"), selected=mode == "armory", primary=mode == "armory")
    k.action(Rect(row.left + half + gap, row.bottom, row.right, row.top), "VEHICLES", "department_select", ("asset_bay_mode", "vehicles"), selected=mode == "vehicles")
    return Rect(area.left, area.bottom, area.right, row.bottom - 9 * u)


def _draw_armory(k, left, center, right):
    gs, u = k.gs, k.u
    catalog = default_equipment_catalog()
    families = list(catalog)
    family = k.selection.get("armory_family", families[0])
    if family not in catalog:
        family = families[0]
    items = list(catalog[family])
    sort_mode = k.selection.get("armory_sort", "power")
    if sort_mode == "price":
        items.sort(key=lambda item: (equipment_purchase_price(item), item.name))
    elif sort_mode == "owned":
        items.sort(key=lambda item: (-gs.owned_equipment.get(item.id, 0), item.name))
    else:
        items.sort(key=lambda item: (equipment_power_score(item), item.name))
    selected_id = k.selection.get("armory_item", items[0].id if items else "")
    if selected_id not in {item.id for item in items}:
        selected_id = items[0].id if items else ""
        k.selection["armory_item"] = selected_id
    selected = next((item for item in items if item.id == selected_id), None)

    k.panel(left, "ASSET BAY // ARMORY", "layers")
    area = _mode_tabs(k, k.body(left), "armory")
    mission = Rect(area.left, area.top - 39 * u, area.right, area.top)
    k.action(mission, "MISSION HANGAR // CHOOSE MISSION", "open_mission_map", primary=True, tooltip="Open mission selection from the hangar")
    area = Rect(area.left, area.bottom, area.right, mission.bottom - 8 * u)
    cols = 2
    gap = 6 * u
    tab_h = 33 * u
    tab_w = (area.width - gap) / cols
    for index, name in enumerate(families):
        row, col = divmod(index, cols)
        top = area.top - row * (tab_h + gap)
        x = area.left + col * (tab_w + gap)
        k.action(Rect(x, top - tab_h, x + tab_w, top), name.replace("_", " ").upper(), "department_select", ("armory_family", name), selected=name == family)
    rows = (len(families) + cols - 1) // cols
    list_area = Rect(area.left, area.bottom, area.right, area.top - rows * (tab_h + gap) - 8 * u)
    for _, item, card in k.page("armory", items, list_area, 75):
        owned = gs.owned_equipment.get(item.id, 0)
        assigned = owned - gs.equipment_available_count(item.id)
        locked = item.availability_group == AVAILABILITY_RESEARCH and item.research_project_id not in gs.completed_research
        state = "LOCKED" if locked else f"OWN {owned} / READY {max(0, owned-assigned)}"
        k.card(card, item.name, f"{item.availability_group} // {state}", action="department_select", data=("armory_item", item.id), selected=item.id == selected_id, color=GOLD if item.id == selected_id else CYAN, tooltip=item.description)

    k.panel(center, f"CATALOG // {family.replace('_', ' ').upper()}", "coins")
    area = k.body(center)
    top = Rect(area.left, area.top - 37 * u, area.right, area.top)
    width = (top.width - 12 * u) / 3
    for index, key in enumerate(("power", "price", "owned")):
        x = top.left + index * (width + 6 * u)
        k.action(Rect(x, top.bottom, x + width, top.top), key.upper(), "department_select", ("armory_sort", key), selected=sort_mode == key)
    grid = Rect(area.left, area.bottom, area.right, top.bottom - 10 * u)
    selected_index = next((i for i, x in enumerate(items) if x.id == selected_id), 0)
    follow_signature = (family, sort_mode, selected_id)
    follow_selection = k.selection.get("_armory_catalog_follow") != follow_signature
    k.selection["_armory_catalog_follow"] = follow_signature
    for _, item, card in k.page(
        "armory_catalog",
        items,
        grid,
        104,
        selected=selected_index if follow_selection else None,
    ):
        k.surface(card, GOLD if item.id == selected_id else CYAN, selected=item.id == selected_id)
        art = Rect(card.left + 7 * u, card.bottom + 7 * u, card.left + 91 * u, card.top - 7 * u)
        k.image(equipment_art_path(item, family), art, cover=False)
        x = art.right + 10 * u
        owned = gs.owned_equipment.get(item.id, 0)
        ready = gs.equipment_available_count(item.id)
        k.label(item.name.upper(), x, card.top - 23 * u, 17, TEXT, bold=True, width=card.right - x - 8 * u)
        k.label(f"{equipment_power_band(item)} // ₦{equipment_purchase_price(item):,}", x, card.top - 48 * u, 13, GOLD, width=card.right - x - 8 * u)
        k.label(f"OWNED {owned} // RESERVE {ready}", x, card.bottom + 18 * u, 13, MINT if ready else MUTED, width=card.right - x - 8 * u)
        k.hit(card, "department_select", ("armory_item", item.id), item.description)

    k.panel(right, "ITEM DETAILS", "layers")
    area = k.body(right)
    if selected is None:
        k.paragraph(k.tr("empty"), area)
        return
    art = Rect(area.left, area.top - 205 * u, area.right, area.top)
    k.surface(art, GOLD)
    # Equipment thumbnails are deliberately contained rather than cropped: long
    # rifles and blades must remain completely visible in the detail viewport.
    k.image(
        equipment_art_path(selected, family),
        Rect(art.left + 18 * u, art.bottom + 18 * u, art.right - 18 * u, art.top - 18 * u),
        cover=False,
    )
    y = art.bottom - 18 * u
    k.label(selected.name.upper(), area.left, y, 24, TEXT, bold=True, width=area.width)
    y -= 30 * u
    k.label(f"ACCESS {selected.availability_group} // POWER {equipment_power_band(selected)} // ₦{equipment_purchase_price(selected):,}", area.left, y, 13, GOLD, width=area.width)
    y -= 29 * u
    effects = [f"{key.upper()} {value:+}" for key, value in selected.stat_bonuses.items() if value]
    if hasattr(selected, "damage_bonus"):
        effects += [f"DMG +{selected.damage_bonus}", f"RANGE {selected.range_cells}"]
    if hasattr(selected, "mitigation"):
        effects += [f"MITIGATION +{selected.mitigation}"]
    detail = selected.description + "\n\n" + " // ".join(effects)
    locked = selected.availability_group == AVAILABILITY_RESEARCH and selected.research_project_id not in gs.completed_research
    if locked:
        project = gs.research_tree.project(selected.research_project_id)
        detail += "\n\nRESEARCH REQUIRED: " + (project.name if project else selected.research_project_id)
    k.document("armory_detail", detail, Rect(area.left, area.bottom + 62 * u, area.right, y), 16)
    price = equipment_purchase_price(selected)
    label = "RESEARCH REQUIRED" if locked else f"BUY ONE // ₦{price:,}"
    k.action(Rect(area.left, area.bottom, area.right, area.bottom + 50 * u), label, "asset_buy_equipment", selected.id, enabled=not locked and gs.available_funds >= price, primary=not locked and gs.available_funds >= price, tooltip=detail)


def _draw_vehicles(k, left, center, right):
    gs = k.gs
    v = k.view
    u = k.u
    assets = gs.spec_ops_assets
    k.panel(left, f'{k.tr("hangar")}  {len(assets)}', "assets")
    vehicle_body = _mode_tabs(k, k.body(left), "vehicles")
    for index, asset, r in k.page(
        "hangar", assets, vehicle_body, 110, selected=v._asset_cursor
    ):
        selected = index == v._asset_cursor
        k.surface(r, GOLD if selected else CYAN, selected=selected)
        k.hit(
            r,
            "asset_select",
            index,
            f"{asset.name} / {asset.display_role} / {asset.maintenance.integrity}%",
        )
        portrait = Rect(
            r.left + 8 * u, r.bottom + 8 * u, r.left + 85 * u, r.top - 8 * u
        )
        k.image(v._asset_portrait_path(asset), portrait)
        # Portrait stays in a dedicated column; text is placed alongside it.
        k.surface(
            Rect(r.left + 91 * u, r.bottom + 5 * u, r.right - 5 * u, r.top - 5 * u),
            GOLD if selected else CYAN,
        )
        x = r.left + 103 * u
        k.label(
            asset.name.upper(),
            x,
            r.top - 23 * u,
            20,
            TEXT,
            bold=True,
            width=r.right - x - 10 * u,
        )
        k.label(
            asset.display_role, x, r.top - 47 * u, 14, MUTED, width=r.right - x - 10 * u
        )
        k.meter(
            Rect(x, r.bottom + 24 * u, r.right - 14 * u, r.bottom + 31 * u),
            asset.maintenance.integrity / 100,
            MINT if asset.is_deployable else RED,
        )
        k.label(
            f"{asset.maintenance.integrity}%  /  ₦{asset.deploy_cost:,}",
            x,
            r.bottom + 12 * u,
            13,
            CYAN,
            width=r.right - x - 10 * u,
        )
    k.panel(center, k.tr("profile"), "layers")
    if assets:
        index = min(max(v._asset_cursor, 0), len(assets) - 1)
        v._asset_cursor = index
        profile(k, assets[index], index, k.body(center))
    else:
        k.paragraph(k.tr("empty"), k.body(center))
    k.panel(right, k.tr("catalog"), "coins")
    catalog = asset_catalog()
    area = k.body(right)
    mission_button = Rect(area.left, area.top - 44 * u, area.right, area.top)
    k.action(
        mission_button,
        "MISSION HANGAR  //  CHOOSE MISSION",
        "open_mission_map",
        primary=True,
        tooltip="Open mission selection from the hangar",
    )
    area = Rect(area.left, area.bottom, area.right, area.top - 55 * u)
    # Legacy catalogue arrows still own the same catalogue cursor.
    first = getattr(v, "_catalog_scroll", 0) % max(1, len(catalog))
    ordered = list(enumerate(catalog))
    ordered = ordered[first:] + ordered[:first]
    capacity = max(1, int((area.height - 48 * u) / (140 * u)))
    for offset, (index, asset) in enumerate(ordered[:capacity]):
        top = area.top - offset * 140 * u
        r = Rect(area.left, top - 130 * u, area.right, top)
        k.surface(r, CYAN)
        k.image(
            v._asset_portrait_path(asset),
            Rect(r.left + 7 * u, r.top - 82 * u, r.left + 81 * u, r.top - 8 * u),
        )
        x = r.left + 91 * u
        cost = getattr(asset, "_acquire_cost", 5_000)
        k.label(
            asset.name,
            x,
            r.top - 20 * u,
            17,
            TEXT,
            bold=True,
            width=r.right - x - 10 * u,
        )
        k.label(
            asset.display_role, x, r.top - 44 * u, 14, MUTED, width=r.right - x - 10 * u
        )
        k.label(
            f'{k.tr("deploy")}  ₦{asset.deploy_cost:,}',
            x,
            r.top - 68 * u,
            14,
            CYAN,
            width=r.right - x - 10 * u,
        )
        k.action(
            Rect(
                r.left + 10 * u, r.bottom + 9 * u, r.right - 10 * u, r.bottom + 43 * u
            ),
            f'{k.tr("buy")}  ₦{cost:,}',
            "catalog_acquire_by_id",
            asset.id,
            enabled=gs.available_funds >= cost,
            primary=gs.available_funds >= cost,
            tooltip=f"{asset.name} / ₦{cost:,} / {asset.display_role}",
        )
    y = area.bottom
    k.action(
        Rect(area.left, y, area.left + 45 * u, y + 33 * u), "‹", "catalog_scroll", -1
    )
    k.label(
        f"{first+1} / {len(catalog)}",
        *Rect(area.left + 50 * u, y, area.right - 50 * u, y + 33 * u).center,
        14,
        MUTED,
        anchor_x="center",
    )
    k.action(
        Rect(area.right - 45 * u, y, area.right, y + 33 * u), "›", "catalog_scroll", 1
    )


def profile(k, asset, index, r):
    u = k.u
    gs = k.gs
    art = Rect(r.left, r.top - 198 * u, r.left + r.width * 0.40, r.top)
    k.surface(art, CYAN)
    k.image(
        k.view._asset_portrait_path(asset),
        Rect(art.left + 4 * u, art.bottom + 4 * u, art.right - 4 * u, art.top - 4 * u),
    )
    x = art.right + 16 * u
    k.paragraph(asset.name.upper(), Rect(x, r.top - 70 * u, r.right, r.top), 25, GOLD)
    k.label(asset.display_role, x, r.top - 88 * u, 17, CYAN, width=r.right - x)
    k.badge(
        k.tr("ready") if asset.is_deployable else k.tr("unavailable"),
        Rect(x, r.top - 135 * u, r.right, r.top - 104 * u),
        MINT if asset.is_deployable else RED,
    )
    k.label(
        f'{k.tr("integrity")}  {asset.maintenance.integrity}%',
        x,
        r.top - 159 * u,
        15,
        TEXT,
        width=r.right - x,
    )
    k.meter(
        Rect(x, r.top - 182 * u, r.right, r.top - 174 * u),
        asset.maintenance.integrity / 100,
        CYAN,
    )
    y = r.top - 212 * u
    stats = asset.combat_stats()
    values = [
        ("hp", f"{stats.hp}/{stats.max_hp}"),
        ("defense", asset.armor.defense_bonus),
        ("plating", asset.armor.plating),
        ("missile", asset.missile_capacity),
        ("ap", asset.action_points),
    ]
    width = (r.width - 24 * u) / 5
    for i, (name, value) in enumerate(values):
        box = Rect(
            r.left + i * (width + 6 * u),
            y - 72 * u,
            r.left + i * (width + 6 * u) + width,
            y,
        )
        k.surface(box, CYAN)
        k.label(
            k.tr(name),
            box.left + 8 * u,
            box.top - 16 * u,
            12,
            MUTED,
            width=box.width - 16 * u,
        )
        k.label(
            str(value),
            box.left + 8 * u,
            box.bottom + 24 * u,
            28,
            CYAN,
            bold=True,
            width=box.width - 16 * u,
        )
    y -= 91 * u
    k.label(k.tr("weapons"), r.left, y, 17, CYAN, bold=True)
    y -= 18 * u
    weapons = "  /  ".join(
        f"{p.name} · RNG {p.range_cells} · DMG +{p.damage_bonus}"
        for p in asset.hardpoints
    ) or k.tr("empty")
    k.paragraph(weapons, Rect(r.left, y - 67 * u, r.right, y), 15)
    k.label(
        f'{k.tr("maintenance")}  ₦{asset.maintenance.base_upkeep:,}  //  {k.tr("deploy")} ₦{asset.deploy_cost:,}',
        r.left,
        y - 82 * u,
        14,
        MUTED,
        width=r.width,
    )
    if getattr(asset, "pilot_required", False):
        y -= 112 * u
        k.label(
            k.tr("pilot")
            + "  /  "
            + str(getattr(asset, "pilot_agent_name", None) or "—"),
            r.left,
            y,
            16,
            GOLD,
            width=r.width,
        )
        rows = list(gs.characters)
        first = k.pages.get("pilots", 0) * 4
        pages = max(1, (len(rows) + 3) // 4)
        k.pages["pilots"] = min(k.pages.get("pilots", 0), pages - 1)
        first = k.pages["pilots"] * 4
        width = (r.width - 6 * u) / 2
        for i, char in enumerate(rows[first : first + 4]):
            bx = r.left + (i % 2) * (width + 6 * u)
            by = y - 46 * u - (i // 2) * 39 * u
            k.action(
                Rect(bx, by, bx + width, by + 33 * u),
                char.name,
                "assign_pilot",
                (index, char.name),
                selected=getattr(asset, "pilot_agent_name", None) == char.name,
            )
        y -= 128 * u
        k.action(
            Rect(r.left, y, r.left + 82 * u, y + 29 * u),
            k.tr("clear"),
            "assign_pilot",
            (index, None),
            danger=True,
        )
        k.capacities["pilots"] = (pages, 4, r)
        if pages > 1:
            k.action(
                Rect(r.right - 90 * u, y, r.right - 50 * u, y + 29 * u),
                "‹",
                "department_page",
                ("pilots", -1),
            )
            k.action(
                Rect(r.right - 40 * u, y, r.right, y + 29 * u),
                "›",
                "department_page",
                ("pilots", 1),
            )
    buttons = Rect(r.left, r.bottom, r.right, r.bottom + 43 * u)
    width = (buttons.width - 8 * u) / 2
    cost = asset.maintenance.repair_cost
    k.action(
        Rect(buttons.left, buttons.bottom, buttons.left + width, buttons.top),
        f'{k.tr("repair")} ₦{cost:,}',
        "asset_repair",
        index,
        enabled=cost > 0 and gs.available_funds >= cost,
        tooltip=f'{k.tr("repair")} / ₦{cost:,}',
    )
    selected = asset.id in gs.selected_asset_ids
    k.action(
        Rect(buttons.left + width + 8 * u, buttons.bottom, buttons.right, buttons.top),
        k.tr("selected") if selected else k.tr("deploy"),
        "asset_deploy_toggle",
        index,
        enabled=selected or asset.is_deployable,
        selected=selected,
        primary=not selected and asset.is_deployable,
    )
