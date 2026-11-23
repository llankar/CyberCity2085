"""Asset Bay cards and profile; acquisition/repair/pilot rules stay in controllers."""

from game.management.spec_ops_assets import asset_catalog
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, TEXT, MUTED


def draw(k, left, center, right):
    gs = k.gs
    v = k.view
    u = k.u
    assets = gs.spec_ops_assets
    k.panel(left, f'{k.tr("hangar")}  {len(assets)}', "assets")
    for index, asset, r in k.page(
        "hangar", assets, k.body(left), 110, selected=v._asset_cursor
    ):
        selected = index == v._asset_cursor
        k.paint.panel(r, GOLD if selected else CYAN, selected=selected)
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
        k.paint.panel(
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
            f"{asset.maintenance.integrity}%  /  ¥{asset.deploy_cost}",
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
        k.paint.panel(r, CYAN)
        k.image(
            v._asset_portrait_path(asset),
            Rect(r.left + 7 * u, r.top - 82 * u, r.left + 81 * u, r.top - 8 * u),
        )
        x = r.left + 91 * u
        cost = getattr(asset, "_acquire_cost", 60)
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
            f'{k.tr("deploy")}  ¥{asset.deploy_cost}',
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
            f'{k.tr("buy")}  ¥{cost}',
            "catalog_acquire_by_id",
            asset.id,
            enabled=gs.available_funds >= cost,
            primary=gs.available_funds >= cost,
            tooltip=f"{asset.name} / ¥{cost} / {asset.display_role}",
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
    k.paint.panel(art, CYAN)
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
        k.paint.panel(box, CYAN)
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
        f'{k.tr("maintenance")}  ¥{asset.maintenance.base_upkeep}  //  {k.tr("deploy")} ¥{asset.deploy_cost}',
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
        f'{k.tr("repair")} ¥{cost}',
        "asset_repair",
        index,
        enabled=cost > 0 and gs.available_funds >= cost,
        tooltip=f'{k.tr("repair")} / ¥{cost}',
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
