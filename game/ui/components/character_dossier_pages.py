"""The four non-Skills pages of Operative Dossier 2.0.

This module is deliberately presentation-only.  Every value is projected from
the existing character, equipment, mission and cyberware models; mutations are
routed back through ``ManagementView`` hit actions.
"""

from __future__ import annotations

import arcade

from game.agents.cyberware import (
    BY_ID,
    MAX_HUMANITY,
    ZONE_ORDER,
    catalogue_for_zone,
    combat_bonuses,
    humanity_remaining,
    is_eligible_role,
)
from game.management.equipment import EQUIPMENT_SLOTS, Armor, Weapon
from game.ui.layouts.world_map_beacons import Rect
from game.ui.portraits import portrait_path_for_character

from .character_sheet import VIOLET
from .squad_style import CYAN, GOLD, MINT, MUTED, RED, TEXT


SLOT_LABELS = {
    "primary_weapon": "PRIMARY",
    "sidearm": "SIDEARM",
    "armor": "ARMOR",
    "utility_item": "UTILITY",
    "psi_focus": "PSI FOCUS",
    "special_gear": "SPECIAL",
}


def _panel(p, rect: Rect, title: str, color=CYAN):
    p.paint.panel(rect, color)
    p.label(title, rect.left + 14 * p.u, rect.top - 22 * p.u, 15, color, bold=True, width=rect.width - 28 * p.u)


def _columns(r: Rect, weights, gap):
    usable = r.width - gap * (len(weights) - 1)
    total = sum(weights)
    result = []
    x = r.left
    for weight in weights:
        width = usable * weight / total
        result.append(Rect(x, r.bottom, x + width, r.top))
        x += width + gap
    return result


def _rows(r: Rect, count, gap):
    height = (r.height - gap * (count - 1)) / count
    return [Rect(r.left, r.top - (i + 1) * height - i * gap, r.right, r.top - i * (height + gap)) for i in range(count)]


def draw_page(p, bounds: Rect, page: str):
    if page == "overview":
        draw_overview(p, bounds)
    elif page == "inventory":
        draw_inventory(p, bounds)
    elif page == "cyberware":
        draw_cyberware(p, bounds)
    elif page == "journal":
        draw_journal(p, bounds)


def draw_overview(p, r: Rect):
    u, c = p.u, p.character
    left, middle, right = _columns(r, (29, 43, 28), 12 * u)
    identity_h = left.height * .58
    identity = Rect(left.left, left.top - identity_h, left.right, left.top)
    _panel(p, identity, "OPERATIVE IDENTITY", CYAN)
    portrait = Rect(identity.left + 12*u, identity.bottom + 62*u, identity.left + identity.width*.47, identity.top - 44*u)
    p.image(portrait_path_for_character(c), portrait)
    x = portrait.right + 12*u
    p.label(c.name.upper(), x, identity.top - 58*u, 24, TEXT, bold=True, width=identity.right-x-10*u)
    p.label(p.role_label, x, identity.top - 91*u, 15, GOLD, bold=True)
    lines = [
        f"LEVEL {c.stats.level}", f"XP {c.stats.xp:,} / {p.data.xp_target:,}",
        f"LOYALTY {c.loyalty}", f"RECOVERY {c.recovery_turns} d",
        f"HP {c.stats.hp} / {c.stats.max_hp}", f"STRESS {c.stress}%",
    ]
    for i, line in enumerate(lines):
        p.label(line, x, identity.top - (126 + i*25)*u, 12, MINT if i >= 4 else TEXT, width=identity.right-x-8*u)

    specs = Rect(left.left, left.bottom, left.right, identity.bottom - 12*u)
    _panel(p, specs, "SPECIALIZATIONS", GOLD)
    talents = [item for item in p.data.talents if item.state == "UNLOCKED"]
    if not talents:
        p.paragraph("No specialization unlocked.", Rect(specs.left+14*u, specs.bottom+12*u, specs.right-14*u, specs.top-48*u), 12, MUTED)
    for i, item in enumerate(talents[:4]):
        y = specs.top - (55 + i*55)*u
        p.label(item.node.name.upper(), specs.left+16*u, y, 12, MINT, bold=True, width=specs.width-32*u)
        p.label(item.node.description, specs.left+16*u, y-21*u, 10, TEXT, width=specs.width-32*u)
    p.hit(specs, "dossier_tab", "skills", "Open skills and specializations")

    attr = Rect(middle.left, middle.top-middle.height*.34, middle.right, middle.top)
    _panel(p, attr, "ATTRIBUTES", CYAN)
    cells = _columns(Rect(attr.left+12*u, attr.bottom+12*u, attr.right-12*u, attr.top-45*u), (1,1,1,1,1), 7*u)
    for box, key in zip(cells, ("str", "agi", "psi", "def", "con")):
        p.paint.panel(box, VIOLET if key == "psi" else CYAN)
        p.label(key.upper(), box.center[0], box.top-24*u, 12, MUTED, anchor_x="center")
        model_key = "defense" if key == "def" else key
        p.label(str(p.data.attributes[model_key]), box.center[0], box.center[1]-8*u, 24, TEXT, bold=True, anchor_x="center")
    ready = Rect(middle.left, attr.bottom-12*u-middle.height*.24, middle.right, attr.bottom-12*u)
    _panel(p, ready, "READINESS", CYAN)
    metrics = list(p.data.derived.items())[:6]
    rcells = _columns(Rect(ready.left+12*u, ready.bottom+12*u, ready.right-12*u, ready.top-45*u), (1,1,1,1,1,1), 6*u)
    for box, (key, value) in zip(rcells, metrics):
        p.paint.panel(box, CYAN)
        p.label(key.upper(), box.center[0], box.top-20*u, 9, MUTED, anchor_x="center", width=box.width-4*u)
        p.label(str(value), box.center[0], box.bottom+20*u, 19, TEXT, bold=True, anchor_x="center")
    loadout = Rect(middle.left, middle.bottom, middle.right, ready.bottom-12*u)
    _panel(p, loadout, "INVENTORY // LOADOUT", CYAN)
    for i, slot in enumerate(EQUIPMENT_SLOTS):
        y = loadout.top - (53+i*35)*u
        item = c.loadout.item_for_slot(slot)
        p.label(SLOT_LABELS[slot], loadout.left+15*u, y, 10, CYAN, bold=True, width=loadout.width*.28)
        p.label(item.name if item else "— EMPTY —", loadout.left+loadout.width*.31, y, 11, TEXT if item else MUTED, width=loadout.width*.56)
        hit = Rect(loadout.left+8*u, y-14*u, loadout.right-8*u, y+14*u)
        p.hit(hit, "dossier_overview_inventory", slot, "Open this Inventory slot")

    mission = Rect(right.left, right.top-right.height*.39, right.right, right.top)
    _panel(p, mission, "ACTIVE ASSIGNMENT", GOLD)
    m = p.gs.active_mission
    if m:
        p.label(m.title.upper(), mission.left+14*u, mission.top-55*u, 17, GOLD, bold=True, width=mission.width-28*u)
        p.label(f"RISK {m.risk_level}   //   REWARD {m.fund_reward:,}", mission.left+14*u, mission.top-88*u, 12, RED, bold=True)
        p.paragraph(m.objective_text, Rect(mission.left+14*u, mission.bottom+18*u, mission.right-14*u, mission.top-105*u), 12, TEXT)
        p.hit(mission, "dossier_tab", "journal", "Open mission journal")
    else:
        p.label("NO ACTIVE MISSION", mission.center[0], mission.center[1], 14, MUTED, anchor_x="center")
    cyber = Rect(right.left, right.top-right.height*.70, right.right, mission.bottom-12*u)
    _panel(p, cyber, "CYBERWARE", VIOLET)
    installed = [BY_ID[key] for key in c.installed_cyberware if key in BY_ID]
    p.label(f"HUMANITY {humanity_remaining(c.installed_cyberware)} / {MAX_HUMANITY}", cyber.left+14*u, cyber.top-54*u, 16, GOLD, bold=True)
    for i, item in enumerate(installed[:4]):
        p.label(f"{item.zone}: {item.name}", cyber.left+14*u, cyber.top-(86+i*29)*u, 11, TEXT, width=cyber.width-28*u)
    p.hit(cyber, "dossier_tab", "cyberware", "Manage cyberware")
    squad = Rect(right.left, right.bottom, right.right, cyber.bottom-12*u)
    _panel(p, squad, f"SQUAD {len(p.gs.selected_agent_names)}/5", CYAN)
    selected = [ch for ch in p.gs.characters if ch.name in p.gs.selected_agent_names]
    for i, agent in enumerate(selected[:5]):
        p.label(agent.name.upper(), squad.left+14*u, squad.top-(52+i*32)*u, 11, TEXT, bold=True, width=squad.width*.48)
        p.label(f"HP {agent.stats.hp}/{agent.stats.max_hp}  STRESS {agent.stress}%", squad.right-14*u, squad.top-(52+i*32)*u, 9, MINT, anchor_x="right", width=squad.width*.48)


def draw_inventory(p, r: Rect):
    u, c = p.u, p.character
    loadout, catalog, detail = _columns(r, (31, 36, 33), 12*u)
    _panel(p, loadout, "LOADOUT // EQUIPPED GEAR", CYAN)
    selected_slot = getattr(p.view, "dossier_inventory_slot", "primary_weapon")
    selected_id = getattr(p.view, "dossier_inventory_item", None)
    for row, slot in zip(_rows(Rect(loadout.left+10*u, loadout.bottom+12*u, loadout.right-10*u, loadout.top-45*u), 6, 8*u), EQUIPMENT_SLOTS):
        active = selected_slot == slot
        p.paint.panel(row, GOLD if active else CYAN, selected=active)
        item = c.loadout.item_for_slot(slot)
        p.label(SLOT_LABELS[slot], row.left+12*u, row.top-19*u, 10, CYAN, bold=True)
        p.label(item.name.upper() if item else "— EMPTY —", row.left+12*u, row.center[1]-9*u, 13, TEXT if item else MUTED, bold=True, width=row.width-24*u)
        p.hit(row, "dossier_inventory_slot", slot, "Show compatible equipment")
    _panel(p, catalog, f"AVAILABLE // {SLOT_LABELS[selected_slot]}", CYAN)
    items = p.view.equipment_catalog.get(selected_slot, [])
    rows = _rows(Rect(catalog.left+10*u, catalog.bottom+12*u, catalog.right-10*u, catalog.top-45*u), max(1, min(8, len(items))), 5*u)
    for row, item in zip(rows, items[:8]):
        active = selected_id == item.id
        equipped = c.loadout.item_for_slot(selected_slot)
        p.paint.panel(row, GOLD if active else VIOLET if equipped and equipped.id == item.id else CYAN, selected=active)
        p.label(item.name.upper(), row.left+10*u, row.center[1]+8*u, 11, TEXT, bold=True, width=row.width-20*u)
        bonuses = "  ".join(f"{k.upper()} {v:+d}" for k,v in item.stat_bonuses.items()) or "NO ATTRIBUTE BONUS"
        p.label(bonuses, row.left+10*u, row.center[1]-12*u, 9, MINT, width=row.width-20*u)
        p.hit(row, "dossier_inventory_item", item.id, "Inspect item")
    _panel(p, detail, "ITEM DETAILS // COMPARISON", CYAN)
    chosen = next((item for item in items if item.id == selected_id), None) or (items[0] if items else None)
    if chosen:
        equipped = c.loadout.item_for_slot(selected_slot)
        p.label(chosen.name.upper(), detail.left+16*u, detail.top-58*u, 20, TEXT, bold=True, width=detail.width-32*u)
        kind = "WEAPON" if isinstance(chosen, Weapon) else "ARMOR" if isinstance(chosen, Armor) else "GEAR"
        p.label(kind, detail.left+16*u, detail.top-87*u, 11, VIOLET, bold=True)
        p.paragraph(chosen.description, Rect(detail.left+16*u, detail.top-185*u, detail.right-16*u, detail.top-105*u), 12, TEXT)
        y = detail.top-215*u
        all_stats = sorted(set(chosen.stat_bonuses) | set(equipped.stat_bonuses if equipped else {}))
        for key in all_stats:
            old = equipped.stat_bonuses.get(key, 0) if equipped else 0
            new = chosen.stat_bonuses.get(key, 0)
            delta = new-old
            p.label(f"{key.upper():<12} {old:+d}  →  {new:+d}   ({delta:+d})", detail.left+16*u, y, 12, MINT if delta>0 else RED if delta<0 else MUTED, width=detail.width-32*u)
            y -= 29*u
        metrics = []
        if isinstance(chosen, Weapon):
            old_weapon = equipped if isinstance(equipped, Weapon) else None
            metrics.extend([
                ("RANGE", old_weapon.range_cells if old_weapon else 0, chosen.range_cells),
                ("DAMAGE", old_weapon.damage_bonus if old_weapon else 0, chosen.damage_bonus),
            ])
        if isinstance(chosen, Armor):
            old_armor = equipped if isinstance(equipped, Armor) else None
            metrics.append(("MITIGATION", old_armor.mitigation if old_armor else 0, chosen.mitigation))
        for label, old, new in metrics:
            delta = new-old
            p.label(f"{label:<12} {old:+d}  →  {new:+d}   ({delta:+d})", detail.left+16*u, y, 12, MINT if delta>0 else RED if delta<0 else MUTED, width=detail.width-32*u)
            y -= 29*u
        equip = Rect(detail.left+16*u, detail.bottom+18*u, detail.right-16*u, detail.bottom+64*u)
        p.paint.panel(equip, GOLD, selected=True)
        p.label("EQUIP" if not equipped or equipped.id != chosen.id else "REMOVE", *equip.center, 13, GOLD, bold=True, anchor_x="center")
        if not equipped or equipped.id != chosen.id:
            p.hit(equip, "dossier_equip_item", (selected_slot, chosen.id), "Equip selected item")
        else:
            p.hit(equip, "dossier_unequip", selected_slot, "Remove equipped item")


def draw_cyberware(p, r: Rect):
    u, c = p.u, p.character
    summary, zones, catalog, detail = _columns(r, (22, 25, 27, 26), 10*u)
    _panel(p, summary, "CYBERWARE MAP", VIOLET)
    figure = Rect(summary.left+20*u, summary.bottom+150*u, summary.right-20*u, summary.top-52*u)
    _draw_anatomy(p, figure, getattr(p.view, "dossier_cyberware_zone", ZONE_ORDER[0]))
    if p.view._elapsed < getattr(p.view, "dossier_cyber_scan_until", 0.0):
        progress = 1.0 - max(0.0, p.view.dossier_cyber_scan_until - p.view._elapsed) / 0.6
        scan_y = figure.bottom + figure.height * progress
        arcade.draw_line(figure.left, scan_y, figure.right, scan_y, (*GOLD, 235), max(2, 3*u))
    remaining = humanity_remaining(c.installed_cyberware)
    p.label(f"HUMANITY {remaining} / {MAX_HUMANITY}", summary.left+15*u, summary.bottom+116*u, 16, GOLD, bold=True)
    p.label(f"INSTALLED {len(c.installed_cyberware)} / {len(ZONE_ORDER)}", summary.left+15*u, summary.bottom+82*u, 13, TEXT)
    totals = combat_bonuses(c.installed_cyberware)
    p.label("  ".join(f"{k.upper()} {v:+d}" for k,v in totals.items()) or "NO ACTIVE BONUSES", summary.left+15*u, summary.bottom+47*u, 10, MINT, width=summary.width-30*u)
    _panel(p, zones, "BODY ZONES", CYAN)
    selected_zone = getattr(p.view, "dossier_cyberware_zone", ZONE_ORDER[0])
    installed_by_zone = {BY_ID[key].zone: BY_ID[key] for key in c.installed_cyberware if key in BY_ID}
    for row, zone in zip(_rows(Rect(zones.left+9*u, zones.bottom+12*u, zones.right-9*u, zones.top-45*u), 6, 7*u), ZONE_ORDER):
        active = zone == selected_zone
        p.paint.panel(row, GOLD if active else VIOLET, selected=active)
        p.label(zone, row.left+11*u, row.top-20*u, 11, TEXT, bold=True, width=row.width-22*u)
        installed = installed_by_zone.get(zone)
        p.label(installed.name if installed else "EMPTY SLOT", row.left+11*u, row.bottom+17*u, 9, MINT if installed else MUTED, width=row.width-22*u)
        p.hit(row, "cyberware_zone", zone, "Open implant catalog")
    _panel(p, catalog, f"IMPLANT CATALOG // {selected_zone}", VIOLET)
    items = catalogue_for_zone(selected_zone)
    selected_id = getattr(p.view, "dossier_cyberware_item", None)
    for row, item in zip(_rows(Rect(catalog.left+9*u, catalog.bottom+12*u, catalog.right-9*u, catalog.top-45*u), 10, 3*u), items):
        active = selected_id == item.id
        installed = item.id in c.installed_cyberware
        affordable = item.credit_cost <= p.gs.available_funds and item.humanity_cost <= MAX_HUMANITY
        row_color = GOLD if active else MINT if installed else CYAN if affordable else MUTED
        p.paint.panel(row, row_color, selected=active)
        p.label(item.name.upper(), row.left+8*u, row.center[1]+7*u, 9, TEXT, bold=True, width=row.width-16*u)
        p.label(f"CR {item.credit_cost:,}  //  HUM -{item.humanity_cost}  //  T{item.power_tier}", row.left+8*u, row.center[1]-10*u, 8, GOLD, width=row.width-16*u)
        p.hit(row, "dossier_cyberware_item", item.id, "Inspect implant")
        quick = Rect(row.right-28*u, row.bottom+4*u, row.right-4*u, row.top-4*u)
        p.hit(quick, "cyberware_toggle", item.id, "Install or remove this implant")
    _panel(p, detail, "IMPLANT DETAILS", VIOLET)
    chosen = BY_ID.get(selected_id) if selected_id else (items[0] if items else None)
    if not is_eligible_role(c.role):
        p.paragraph("This operative chassis is not eligible for human cyberware.", Rect(detail.left+16*u, detail.bottom+20*u, detail.right-16*u, detail.top-55*u), 13, RED)
    elif chosen:
        installed = chosen.id in c.installed_cyberware
        p.label(chosen.name.upper(), detail.left+15*u, detail.top-58*u, 18, TEXT, bold=True, width=detail.width-30*u)
        p.label(f"{chosen.zone} // TIER {chosen.power_tier}", detail.left+15*u, detail.top-88*u, 11, VIOLET, bold=True)
        p.paragraph(chosen.description, Rect(detail.left+15*u, detail.top-190*u, detail.right-15*u, detail.top-108*u), 12, TEXT)
        y = detail.top-220*u
        for key, value in chosen.combat_bonuses.items():
            p.label(f"{key.upper()} {value:+d}", detail.left+15*u, y, 13, MINT, bold=True)
            y -= 28*u
        p.label(f"CREDITS {chosen.credit_cost:,}   //   HUMANITY -{chosen.humanity_cost}", detail.left+15*u, detail.bottom+88*u, 11, GOLD, bold=True, width=detail.width-30*u)
        action = Rect(detail.left+15*u, detail.bottom+20*u, detail.right-15*u, detail.bottom+66*u)
        p.paint.panel(action, RED if installed else GOLD, selected=True)
        p.label("REMOVE" if installed else "INSTALL", *action.center, 13, RED if installed else GOLD, bold=True, anchor_x="center")
        p.hit(action, "dossier_cyberware_toggle", chosen.id, "Remove implant" if installed else "Purchase and install implant")


def draw_journal(p, r: Rect):
    u, c = p.u, p.character
    nav, main, archive = _columns(r, (21, 50, 29), 12*u)
    _panel(p, nav, "JOURNAL", CYAN)
    sections = (("mission", "MISSION LOG"), ("events", "EVENT TIMELINE"), ("squad", "SQUAD NOTES"), ("personal", "PERSONAL DOSSIER"))
    selected = getattr(p.view, "dossier_journal_section", "mission")
    for row, (key, label) in zip(_rows(Rect(nav.left+10*u, nav.top-280*u, nav.right-10*u, nav.top-48*u), 4, 8*u), sections):
        p.paint.panel(row, GOLD if key == selected else CYAN, selected=key == selected)
        p.label(label, *row.center, 11, TEXT, bold=True, anchor_x="center", width=row.width-12*u)
        p.hit(row, "dossier_journal_section", key, f"Open {label}")
    _panel(p, main, dict(sections)[selected], GOLD if selected == "mission" else CYAN)
    body = Rect(main.left+16*u, main.bottom+18*u, main.right-16*u, main.top-50*u)
    if selected == "mission":
        m = p.gs.active_mission
        if m:
            p.label(m.title.upper(), body.left, body.top-10*u, 20, GOLD, bold=True, width=body.width)
            p.label(f"{m.district} // RISK {m.risk_level} // REWARD {m.fund_reward:,} // {m.duration_days} DAY(S)", body.left, body.top-47*u, 11, RED, bold=True, width=body.width)
            p.paragraph(m.objective_text, Rect(body.left, body.bottom+body.height*.55, body.right, body.top-75*u), 13, TEXT)
        else:
            p.label("NO ACTIVE MISSION", body.center[0], body.top-35*u, 15, MUTED, anchor_x="center")
        completed = list(getattr(p.gs.campaign, "completed_story_missions", []))
        p.label(f"COMPLETED STORY MISSIONS // {len(completed)}", body.left, body.bottom+body.height*.48, 13, CYAN, bold=True)
        for i, mission_id in enumerate(completed[-8:]):
            p.label(mission_id, body.left+12*u, body.bottom+body.height*.42-i*27*u, 11, TEXT, width=body.width-12*u)
    elif selected == "events":
        for i, event in enumerate(reversed(p.gs.event_log[-16:])):
            p.label(str(event), body.left, body.top-(15+i*29)*u, 10, TEXT if i else GOLD, width=body.width)
    elif selected == "squad":
        agents = [agent for agent in p.gs.characters if agent.name in p.gs.selected_agent_names]
        for i, agent in enumerate(agents):
            y = body.top-(15+i*75)*u
            p.label(f"{agent.name.upper()} // {agent.role.upper()}", body.left, y, 13, CYAN, bold=True)
            p.label(f"HP {agent.stats.hp}/{agent.stats.max_hp}   STRESS {agent.stress}%   LOYALTY {agent.loyalty}", body.left, y-25*u, 11, MINT)
            history = agent.history[-1] if agent.history else "No personal history entry recorded."
            p.label(history, body.left, y-49*u, 9, MUTED, width=body.width)
    else:
        notes = list(getattr(c, "personal_notes", []))
        editor = Rect(body.left, body.bottom, body.right, body.bottom+92*u)
        if getattr(p.view, "dossier_note_editing", False):
            p.paint.panel(editor, GOLD, selected=True)
            text = p.view.dossier_note_buffer or "Type a personal note..."
            p.label(text, editor.left+10*u, editor.top-26*u, 11, TEXT if p.view.dossier_note_buffer else MUTED, width=editor.width-20*u)
            p.label("ENTER SAVE  //  ESC CANCEL", editor.right-10*u, editor.bottom+17*u, 9, GOLD, anchor_x="right")
            p.hit(editor, "dossier_note_save", tooltip="Save note")
        else:
            add = Rect(body.left, body.bottom, body.right, body.bottom+40*u)
            p.paint.panel(add, GOLD)
            p.label("+ NEW PERSONAL NOTE", *add.center, 11, GOLD, bold=True, anchor_x="center")
            p.hit(add, "dossier_note_new", tooltip="Create a persistent personal note")
        if not notes and not getattr(p.view, "dossier_note_editing", False):
            p.paragraph("No personal notes recorded. Notes are created from real player input only.", body, 13, MUTED)
        for visible_i, (index, note) in enumerate(list(enumerate(notes))[-8:]):
            row = Rect(body.left, body.top-(visible_i+1)*48*u, body.right, body.top-visible_i*48*u-4*u)
            p.paint.panel(row, RED if p.view.dossier_note_delete_pending == index else CYAN)
            p.label(str(note), row.left+9*u, row.center[1], 10, TEXT, width=row.width-72*u)
            p.hit(Rect(row.left, row.bottom, row.right-56*u, row.top), "dossier_note_edit", index, "Edit note")
            p.label("DEL?" if p.view.dossier_note_delete_pending == index else "DEL", row.right-10*u, row.center[1], 9, RED, bold=True, anchor_x="right")
            p.hit(Rect(row.right-54*u, row.bottom, row.right, row.top), "dossier_note_delete", index, "Click twice to confirm deletion")
    _panel(p, archive, "ARCHIVE // REAL DATA", CYAN)
    lines = [
        f"EVENTS {len(p.gs.event_log)}",
        f"MISSION TEMPLATES {len(p.gs.mission_templates)}",
        f"KNOWN FACTIONS {len(p.gs.factions)}",
        f"CONSEQUENCES {len(p.gs.recent_consequences)}",
        f"AGENT HISTORY {len(c.history)}",
    ]
    for i, line in enumerate(lines):
        p.label(line, archive.left+16*u, archive.top-(58+i*37)*u, 12, TEXT, bold=True, width=archive.width-32*u)
    p.paragraph("Only information already recorded by the campaign is shown. Undiscovered internal data is never exposed here.", Rect(archive.left+16*u, archive.bottom+20*u, archive.right-16*u, archive.bottom+145*u), 11, MUTED)


def _draw_anatomy(p, r: Rect, selected_zone: str):
    """Resolution-independent holographic body map; no fake data is baked in."""
    u = p.u
    x = r.center[0]
    head_y = r.top - 42*u
    body_top = head_y - 42*u
    hip_y = r.bottom + r.height*.38
    color = (*CYAN, 210)
    arcade.draw_circle_outline(x, head_y, 28*u, color, 2*u)
    arcade.draw_line(x, body_top, x, hip_y, color, 4*u)
    arcade.draw_line(x, body_top-18*u, x-55*u, body_top-105*u, color, 3*u)
    arcade.draw_line(x, body_top-18*u, x+55*u, body_top-105*u, color, 3*u)
    arcade.draw_line(x, hip_y, x-37*u, r.bottom+20*u, color, 4*u)
    arcade.draw_line(x, hip_y, x+37*u, r.bottom+20*u, color, 4*u)
    points = {
        "HEAD": (x, head_y+6*u), "EYES": (x, head_y+15*u),
        "ARMS": (x+51*u, body_top-83*u), "TORSO": (x, body_top-62*u),
        "CIRCULATORY": (x-11*u, body_top-46*u), "NERVOUS SYSTEM": (x, body_top-15*u),
    }
    for zone, (px, py) in points.items():
        active = zone == selected_zone
        dot = GOLD if active else VIOLET
        if active:
            p.paint.glow(px, py, 52*u, 52*u, dot, 65)
        arcade.draw_circle_filled(px, py, (8 if active else 5)*u, dot)
        arcade.draw_circle_outline(px, py, (15 if active else 10)*u, dot, 2*u)
