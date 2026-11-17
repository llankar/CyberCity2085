"""Intel archive: selectable dossiers, readable campaign threads and live situation."""

from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, PURPLE, TEXT, MUTED
from game.ui.components.utilities.reports import report_lines


def draw_intel(k, left, center, right):
    from game.ui.screens.campaign_panel import (
        build_intel_fragment_browser,
        build_global_scenario_summary,
    )

    gs = k.gs
    u = k.u
    browser = build_intel_fragment_browser(gs)
    fragments = browser["entries"]
    scenario = build_global_scenario_summary(gs)
    mode = k.selection.get("intel_mode", "fragments")
    labels = {
        "fragments": k.word("DOSSIERS", "DOSSIERS"),
        "events": k.word("JOURNAL", "JOURNAL"),
        "campaign": k.word("CAMPAGNE", "CAMPAIGN"),
        "debrief": k.word("RAPPORTS", "REPORTS"),
    }
    k.panel(left, k.tr("intel"), "journal")
    r = k.body(left)
    half = (r.width - 8 * u) / 2
    for i, (key, title) in enumerate(labels.items()):
        x = r.left + (i % 2) * (half + 8 * u)
        top = r.top - (i // 2) * 45 * u
        k.action(
            Rect(x, top - 37 * u, x + half, top),
            title,
            "department_select",
            ("intel_mode", key),
            selected=mode == key,
        )
    module_labels = {
        "hungry_tide": "STARVERS / HUNGRY TIDE",
        "three_sevens": "THREE SEVENS",
        "pharmacorp": "PHARMACORP",
        "novatek": "NOVATEK",
        "hidden_ai": k.word("SIGNAL INCONNU / IA", "UNKNOWN SIGNAL / AI"),
    }
    if mode == "fragments":
        rows = [
            (f["id"], f["title"], str(f["source"]).replace("_", " ")) for f in fragments
        ]
    elif mode == "events":
        rows = [
            (i, str(text), k.tr("events"))
            for i, text in reversed(list(enumerate(gs.event_log)))
        ]
    elif mode == "campaign":
        rows = [(key, title, k.tr("campaign")) for key, title in module_labels.items()]
    else:
        debrief = gs.latest_mission_debrief or {}
        rows = [
            (
                "debrief",
                debrief.get("mission_title") or k.tr("debrief"),
                k.tr("detail"),
            ),
            ("aftermath", k.tr("aftermath"), k.word("ÉTAT DES AGENTS", "AGENT STATUS")),
        ]
    selected = k.selection.get("intel_" + mode, rows[0][0] if rows else None)
    area = Rect(r.left, r.bottom, r.right, r.top - 100 * u)
    for i, (key, title, subtitle), card in k.page("archive_" + mode, rows, area, 77):
        k.card(
            card,
            title,
            subtitle,
            action="department_select",
            data=("intel_" + mode, key),
            selected=selected == key,
            tooltip=title,
        )
    k.panel(center, labels.get(mode, k.tr("detail")), "journal")
    r = k.body(center)
    if k.view.room_ui.texture_override:
        k.texture(
            k.view.room_ui.texture_override,
            Rect(r.left, r.top - 172 * u, r.right, r.top),
        )
    k.badge(
        f'ACT {scenario["current_act"]} / {scenario["act_title"]}',
        Rect(r.left, r.top - 204 * u, r.right, r.top - 166 * u),
        PURPLE,
    )
    if mode == "fragments":
        f = next((f for f in fragments if f["id"] == selected), None)
        text = (
            "\n\n".join(
                [
                    f["title"],
                    f["lore_text"],
                    str(f["mechanical_relevance"]),
                    ", ".join(f["factions"]),
                ]
            )
            if f
            else k.tr("empty")
        )
    elif mode == "events":
        text = (
            str(gs.event_log[selected])
            if selected is not None and 0 <= selected < len(gs.event_log)
            else k.tr("empty")
        )
    elif mode == "campaign":
        text = (
            module_labels.get(selected, "")
            + "\n\n"
            + "\n".join(report_lines(scenario.get(selected, {})))
        )
    else:
        text = "\n".join(
            report_lines(
                (gs.latest_mission_debrief or {})
                if selected == "debrief"
                else getattr(gs, "latest_agent_aftermath", [])
            )
        ) or k.tr("empty")
    k.document(
        "intel_" + mode + "_detail_" + str(selected),
        text,
        Rect(r.left, r.bottom, r.right, r.top - 225 * u),
        19,
    )
    k.panel(right, k.tr("campaign"), "target")
    r = k.body(right)
    k.stat(
        Rect(r.left, r.top - 115 * u, r.right, r.top),
        k.word("PROGRESSION / ACTE", "PROGRESS / ACT"),
        f'{scenario["act_progress"]} / {scenario["act_required"]}',
        "target",
        color=PURPLE,
        fraction=scenario["act_progress"] / max(1, scenario["act_required"]),
    )
    k.stat(
        Rect(r.left, r.top - 226 * u, r.right, r.top - 129 * u),
        k.word("RENSEIGNEMENTS DÉCOUVERTS", "INTEL DISCOVERED"),
        str(scenario["discovered_intel_count"]),
        "journal",
        color=CYAN,
    )
    status = (
        "WARSAW : "
        + scenario["warsaw_status"]
        + "\nNEW YORK : "
        + scenario["new_york_status"]
        + "\n\n"
    )
    status += (
        k.word("MENACES CONNUES", "KNOWN THREATS")
        + "\n"
        + "\n".join(map(str, scenario["major_known_threats"]))
    )
    status += (
        "\n\n"
        + k.word("ÉVÉNEMENTS MONDIAUX", "GLOBAL EVENTS")
        + "\n"
        + "\n".join(map(str, scenario["unresolved_global_events"]))
    )
    status += "\n\n" + "\n".join(report_lines(scenario["world_state_change_feed"]))
    k.document(
        "campaign_report", status, Rect(r.left, r.bottom, r.right, r.top - 246 * u), 17
    )
