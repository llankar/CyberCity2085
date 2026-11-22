"""Variable-size deployment roster and selected support asset cards."""

import arcade
from game.i18n import t
from game.agent_readiness import stress_state_label
from game.ui.theme.typography import scale_font_size
from game.ui.layouts.world_map_beacons import Rect
from game.ui.portraits import portrait_path_for_character
from game.narrative.agent_memory import tactical_memory_summary
from .briefing_content import support_art
from .squad_style import CYAN, GOLD, MINT, RED, TEXT, MUTED


def draw_squad(p, r):
    u = p.u
    p.panel(r, p.tr("squad"), "squad")
    area = Rect(r.left + 12 * u, r.bottom + 65 * u, r.right - 12 * u, r.top - 59 * u)
    minimum = max(100 * u, 100, scale_font_size(13) * 8)
    count = max(1, min(5, int((area.width + 8 * u) / (minimum + 8 * u))))
    maximum = max(0, len(p.agents) - count)
    first = max(0, min(p.offsets.get("squad", 0), maximum))
    p.offsets["squad"] = first
    p.scroll_regions["squad"] = (r, maximum)
    p.visible_lines["squad"] = (first, count, len(p.agents))
    if maximum:
        p.pager("squad", r, first, maximum)
    if not p.agents:
        p.label(
            p.tr("no_agents"),
            *area.center,
            19,
            MUTED,
            anchor_x="center",
            width=area.width - 20 * u,
        )
    width = (area.width - (count - 1) * 8 * u) / count
    for index, agent in enumerate(p.agents[first : first + count]):
        x = area.left + index * (width + 8 * u)
        card = Rect(x, area.bottom, x + width, area.top)
        color = RED if agent.stress >= 65 else GOLD if agent.stress >= 35 else CYAN
        p.paint.panel(card, color)
        line_h = max(23 * u, scale_font_size(14) * 1.45)
        portrait = Rect(
            card.left + 4 * u,
            card.bottom + 25 * u + 3 * line_h,
            card.right - 4 * u,
            card.top - 4 * u,
        )
        p.image(portrait_path_for_character(agent), portrait)
        p.label(
            agent.name.upper(),
            card.left + 6 * u,
            card.bottom + 26 * u + 2 * line_h,
            18,
            TEXT,
            bold=True,
            width=card.width - 12 * u,
        )
        role = t("squad.role." + agent.role, p.gs.ui_language)
        if role.startswith("squad."):
            role = agent.role.upper()
        p.label(
            role,
            card.left + 6 * u,
            card.bottom + 26 * u + line_h,
            13,
            GOLD,
            width=card.width - 12 * u,
        )
        p.label(
            t("briefing.state." + stress_state_label(agent.stress), p.gs.ui_language),
            card.left + 6 * u,
            card.bottom + 26 * u,
            12,
            color,
            width=card.width - 44 * u,
        )
        p.label(
            f"{agent.stress}%",
            card.right - 6 * u,
            card.bottom + 26 * u,
            14,
            color,
            anchor_x="right",
        )
        p.meter(
            Rect(
                card.left + 6 * u,
                card.bottom + 6 * u,
                card.right - 6 * u,
                card.bottom + 11 * u,
            ),
            agent.stress / 100,
            color,
            8,
        )
        memory = tactical_memory_summary(getattr(agent, "history", []))
        details = (
            f"{agent.name} · {role} · {agent.stats.hp}/{agent.stats.max_hp} "
            f"{p.tr('hp')} · {agent.stress}%"
        )
        if memory:
            details += f" · REMEMBERS: {memory}"
        p.hit(
            card,
            "info",
            agent.name,
            details,
        )
    avg = sum(a.stress for a in p.agents) // max(1, len(p.agents))
    color = RED if avg >= 65 else GOLD if avg >= 35 else MINT
    avgbox = Rect(
        r.left + 12 * u, r.bottom + 12 * u, r.right - 12 * u, r.bottom + 53 * u
    )
    p.paint.panel(avgbox, color)
    p.icon("brain", avgbox.left + 22 * u, avgbox.center[1], 27, color)
    p.label(
        p.tr("average", n=avg),
        avgbox.left + 45 * u,
        avgbox.center[1],
        21,
        color,
        bold=True,
        width=avgbox.width - 60 * u,
    )


def draw_support(p, r):
    u = p.u
    p.panel(r, p.tr("support"), "cube")
    area = Rect(r.left + 12 * u, r.bottom + 8 * u, r.right - 12 * u, r.top - 49 * u)
    maximum = max(0, len(p.assets) - 1)
    first = max(0, min(p.offsets.get("support", 0), maximum))
    p.offsets["support"] = first
    p.scroll_regions["support"] = (r, maximum)
    p.visible_lines["support"] = (first, 1, len(p.assets))
    if maximum:
        p.pager("support", r, first, maximum)
    if not p.assets:
        p.label(
            p.tr("none_assets"),
            *area.center,
            17,
            MUTED,
            anchor_x="center",
            width=area.width,
        )
        return
    asset = p.assets[first]
    portrait = Rect(area.left, area.bottom, area.left + area.height * 1.15, area.top)
    art = support_art(asset)
    if art:
        p.image(art, portrait)
    else:
        p.icon("cube", *portrait.center, 55, CYAN)
    x = portrait.right + 14 * u
    width = area.right - x
    p.label(asset.name.upper(), x, area.top - 13 * u, 22, TEXT, bold=True, width=width)
    role = getattr(asset, "display_role", getattr(asset, "asset_type", ""))
    localized_role = t("briefing.support." + asset.asset_type, p.gs.ui_language)
    if localized_role.startswith("briefing."):
        localized_role = str(role).upper()
    p.label(localized_role, x, area.top - 37 * u, 15, CYAN, width=width * 0.72)
    p.label(
        p.tr("cost", n=asset.deploy_cost),
        area.right,
        area.bottom + 13 * u,
        16,
        GOLD,
        anchor_x="right",
        width=width,
    )
