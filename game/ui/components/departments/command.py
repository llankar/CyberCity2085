"""Data-driven command presentation; original controllers own all mutations."""

from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, TEXT, MUTED, PURPLE


def draw_command(k, left, center, right):
    from game.management.weekly_planning import DIRECTIVES, build_management_forecast

    gs = k.gs
    u = k.u
    f = build_management_forecast(gs)
    k.panel(left, k.tr("forecast"), "coins")
    r = k.body(left)
    k.label(
        gs.calendar.campaign_date_label,
        r.left,
        r.top - 14 * u,
        24,
        GOLD,
        bold=True,
        width=r.width,
    )
    labels = [
        (k.tr("income"), f.projected_income, "coins"),
        (k.tr("net"), f.projected_net, "coins"),
        (k.tr("maintenance"), f.asset_upkeep, "assets"),
    ]
    y = r.top - 47 * u
    for title, value, icon in labels:
        k.stat(
            Rect(r.left, y - 85 * u, r.right, y),
            title,
            f"¥{value:+,}" if title == k.tr("net") else f"¥{value:,}",
            icon,
            color=GOLD if value < 0 else CYAN,
        )
        y -= 96 * u
    k.label(k.tr("budget"), r.left, y - 13 * u, 17, CYAN, bold=True, width=r.width)
    y -= 45 * u
    upgrades = {
        "research": {"intel": 5},
        "security": {"credits": 10, "salvage": 2},
        "politics": {"influence": 3},
        "black_ops": {"credits": 5, "intel": 3},
    }
    for key, cost in upgrades.items():
        title = f'{key.replace("_"," ").upper()}  {gs.corp_budget.get(key,0)}'
        subtitle = " / ".join(f"{name} −{amount}" for name, amount in cost.items())
        k.action(
            Rect(r.left, y - 34 * u, r.right, y),
            title,
            "corp_upgrade_" + key,
            enabled=all(gs.strategic_resources.get(a, 0) >= b for a, b in cost.items()),
            tooltip=subtitle,
        )
        y -= 42 * u
    k.action(
        Rect(r.left, r.bottom, r.right, r.bottom + 43 * u),
        k.tr("advance"),
        "advance_day",
        primary=True,
        icon="next",
    )
    context = k.word("PROCHAINE RENTRÉE : JOUR ", "NEXT PAYOUT: DAY ") + str(
        gs.next_weekly_income_date
    )
    context += (
        "\n"
        + k.word("AGENTS PRÊTS : ", "READY AGENTS: ")
        + f"{f.ready_agents} / {f.total_agents}"
    )
    context += (
        "\n"
        + k.word("JOUR / SEMAINE : ", "DAY / WEEK: ")
        + f"{gs.calendar.current_day} / {gs.calendar.current_week}"
    )
    k.panel(center, k.tr("events"), "journal")
    r = k.body(center)
    events = gs.active_events
    if events:
        selected = min(k.pages.get("crises", 0), len(events) - 1)
        event = events[selected]
        k.capacities["crises"] = (len(events), 1, r)
        k.badge(
            f"{selected+1} / {len(events)}",
            Rect(r.left, r.top - 33 * u, r.left + 84 * u, r.top),
            GOLD,
        )
        for i, step in enumerate([-1, 1]):
            k.action(
                Rect(
                    r.right - (86 - i * 46) * u,
                    r.top - 33 * u,
                    r.right - (46 - i * 46) * u,
                    r.top,
                ),
                "‹" if step < 0 else "›",
                "department_page",
                ("crises", step),
            )
        k.paragraph(
            event.title,
            Rect(r.left, r.top - 110 * u, r.right, r.top - 48 * u),
            24,
            GOLD,
        )
        k.document(
            "event_description",
            event.description
            + "\n\n"
            + context
            + "\n"
            + k.word("EXPIRATION : JOUR ", "EXPIRES: DAY ")
            + str(event.expires_day),
            Rect(r.left, r.top - 280 * u, r.right, r.top - 116 * u),
        )
        choice_area = Rect(r.left, r.bottom, r.right, r.top - 295 * u)
        for ci, choice, button in k.page(
            "event_choices", list(enumerate(event.choices)), choice_area, 66
        ):
            actual, choice = choice
            k.action(
                button,
                choice.label,
                f"event_response_{selected}_{actual}",
                tooltip=choice.label,
            )
    else:
        if k.view.room_ui.texture_override:
            k.texture(
                k.view.room_ui.texture_override,
                Rect(r.left, r.bottom + 210 * u, r.right, r.top),
            )
        k.document(
            "command_context",
            k.tr("empty") + "\n\n" + context,
            Rect(r.left, r.bottom, r.right, r.bottom + 190 * u),
            17,
        )
    k.panel(right, k.tr("directives"), "target")
    r = k.body(right)
    k.label(
        k.tr("selected") if f.directive_locked else k.tr("directives"),
        r.left,
        r.top - 12 * u,
        15,
        GOLD,
        width=r.width,
    )
    y = r.top - 32 * u
    for directive in DIRECTIVES:
        card = Rect(r.left, y - 172 * u, r.right, y)
        selected = f.selected_directive == directive.id
        k.paint.panel(card, GOLD if selected else CYAN, selected=selected)
        k.label(
            directive.title,
            card.left + 12 * u,
            card.top - 20 * u,
            18,
            TEXT,
            bold=True,
            width=card.width - 24 * u,
        )
        k.paragraph(
            directive.promise,
            Rect(
                card.left + 12 * u,
                card.top - 91 * u,
                card.right - 12 * u,
                card.top - 37 * u,
            ),
            14,
            MINT,
        )
        k.paragraph(
            directive.consequence,
            Rect(
                card.left + 12 * u,
                card.top - 133 * u,
                card.right - 12 * u,
                card.top - 93 * u,
            ),
            13,
            MUTED,
        )
        k.action(
            Rect(
                card.left + 10 * u,
                card.bottom + 8 * u,
                card.right - 10 * u,
                card.bottom + 36 * u,
            ),
            f'¥{directive.cost} / {k.tr("selected") if selected else k.word("CHOISIR","CHOOSE")}',
            "weekly_directive_" + directive.id,
            enabled=not f.directive_locked and gs.available_funds >= directive.cost,
            selected=selected,
            tooltip=directive.promise + " / " + directive.consequence,
        )
        y -= 182 * u
    k.label(
        f"{f.threat_level.upper()} / {f.district_pressure}%",
        r.left,
        r.bottom + 12 * u,
        17,
        RED if f.district_pressure >= 50 else CYAN,
        width=r.width,
    )
