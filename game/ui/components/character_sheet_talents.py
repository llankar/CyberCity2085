"""Capability cards driven by the actual role tree, prerequisites and point balance."""

from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.typography import get_text_size, scale_font_size
from .character_sheet import VIOLET, LOCKED
from .squad_style import CYAN, GOLD, MINT, TEXT, MUTED


def wrap_words(p, text, width, size, max_lines):
    words = text.split()
    lines = []
    while words and len(lines) < max_lines:
        line = words.pop(0)
        while (
            words
            and p.paint.fit(line + " " + words[0], width, size, False)
            == line + " " + words[0]
        ):
            line += " " + words.pop(0)
        lines.append(line)
    if words:
        lines[-1] = p.paint.fit(lines[-1] + "…", width, size, False)
    return lines


def draw_talents(p, r):
    u = p.u
    p.panel(r, p.tr("specializations"), "target")
    area = Rect(r.left + 12 * u, r.bottom + 12 * u, r.right - 12 * u, r.top - 57 * u)
    columns = 2 if r.width < 480 else 3
    minimum = max(128, 140 * u) * (1.18 if get_text_size() == "large" else 1)
    grid = p.grid("talents", area, len(p.data.talents), columns, minimum)
    p.pager("talents", r, grid)
    if not p.data.talents:
        p.icon(
            "robot" if p.character.role == "robot" else "target", *area.center, 65, CYAN
        )
        p.label(
            p.tr("no_tree"),
            area.center[0],
            area.bottom + 27 * u,
            14,
            MUTED,
            width=area.width - 20 * u,
            anchor_x="center",
        )
        return
    for index, rect in grid.cards:
        talent = p.data.talents[index]
        node = talent.node
        p.visible_talents.add(node.id)
        owned = talent.state == "UNLOCKED"
        available = talent.state == "AVAILABLE"
        color = MINT if owned else GOLD if available else LOCKED
        action = "unlock_talent" if available else "sheet_info"
        data = (p.index, node.id) if available else ("talent", node.id)
        bonuses = "  ".join(
            f"{value:+} {key.upper()}" for key, value in node.bonuses.items()
        )
        reason = p.tr("state." + talent.state)
        if talent.missing_names:
            reason += " · " + p.tr("requires", names=", ".join(talent.missing_names))
        if talent.needs_point:
            reason += " · " + p.tr("needs_talent")
        tooltip = node.name + ": " + node.description + "\n" + reason + " · " + bonuses
        p.card(rect, color, action, data, tooltip, ("talent", node.id))
        icon = (
            "psi"
            if p.character.role == "psi"
            else "sword" if p.character.role == "samurai" else "target"
        )
        p.icon(icon, rect.left + 21 * u, rect.top - 22 * u, 23, color)
        p.label(
            f"T{node.tier}",
            rect.right - 8 * u,
            rect.top - 13 * u,
            11,
            color,
            bold=True,
            anchor_x="right",
        )
        font = scale_font_size(max(12, 13 * u))
        names = wrap_words(p, node.name.upper(), rect.width - 52 * u, font, 2)
        y = rect.top - 29 * u
        for line in names:
            p.label(
                line,
                rect.left + 40 * u,
                y,
                13,
                TEXT,
                bold=True,
                width=rect.width - 50 * u,
            )
            y -= 17 * u
        desc_size = scale_font_size(max(12, 12 * u))
        line_height = max(15 * u, desc_size * 1.15)
        y -= 5 * u
        max_lines = max(1, min(4, int((y - (rect.bottom + 44 * u)) / line_height)))
        for line in wrap_words(
            p, node.description, rect.width - 20 * u, desc_size, max_lines
        ):
            p.label(line, rect.left + 10 * u, y, 12, TEXT, width=rect.width - 20 * u)
            y -= line_height
        p.label(
            bonuses,
            rect.left + 10 * u,
            rect.bottom + 36 * u,
            12,
            MINT if owned else TEXT,
            bold=True,
            width=rect.width - 20 * u,
        )
        p.label(
            p.tr("state." + talent.state),
            rect.center[0],
            rect.bottom + 16 * u,
            11,
            color,
            bold=True,
            anchor_x="center",
            width=rect.width - 16 * u,
        )
