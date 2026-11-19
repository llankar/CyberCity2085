"""All twelve skills, in a responsive paged grid with true linked-attribute totals."""

from game.i18n import t
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.typography import get_text_size, scale_font_size
from game.agents.sheet_schema import SKILL_MAX_RANK
from .character_sheet import VIOLET, LOCKED
from .squad_style import CYAN, GOLD, TEXT, MUTED

ICONS = {
    "firearms": "rifle",
    "close_combat": "fist",
    "tactics": "next",
    "tech": "chip",
    "medicine": "heal",
    "influence": "squad",
    "stealth": "stealth",
    "composure": "head",
    "psychokinesis": "psi",
    "pyrokinesis": "flame",
    "cryokinesis": "ice",
    "telepathy": "brain",
}


def draw_skills(p, r):
    u = p.u
    p.panel(r, p.tr("skills"), "settings")
    area = Rect(r.left + 12 * u, r.bottom + 14 * u, r.right - 12 * u, r.top - 61 * u)
    columns = 2 if r.width < 490 else 3
    minimum = max(132, 145 * u) * (1.12 if get_text_size() == "large" else 1)
    grid = p.grid("skills", area, len(p.data.skills), columns, minimum)
    p.pager("skills", r, grid)
    for index, rect in grid.cards:
        skill = p.data.skills[index]
        p.visible_skills.add(skill.key)
        name = t("sheet.skill." + skill.key, p.gs.ui_language)
        color = (
            VIOLET
            if skill.key in ("psychokinesis", "telepathy")
            else GOLD if skill.key == "pyrokinesis" else CYAN
        )
        action = "sheet_spend_skill_rank" if skill.can_spend else "sheet_info"
        data = (p.index, skill.key) if skill.can_spend else ("skill", skill.key)
        tooltip = p.tr(
            "skill_help",
            name=name,
            attribute=skill.attribute.upper(),
            base=skill.attribute_value,
            rank=skill.rank,
            total=skill.total,
        )
        if skill.rank >= SKILL_MAX_RANK:
            tooltip += " · " + p.tr("max_rank")
        elif not skill.can_spend:
            tooltip += " · " + p.tr("no_points")
        p.card(rect, color, action, data, tooltip, ("skill", skill.key))
        p.icon(ICONS[skill.key], rect.left + 25 * u, rect.top - 25 * u, 27, color)
        font = scale_font_size(max(13, 14 * u))
        while font > 12 and p.paint.fit(name, rect.width - 58 * u, font, True) != name:
            font -= 1
        p.text(
            name,
            rect.left + 47 * u,
            rect.top - 24 * u,
            font,
            TEXT,
            bold=True,
            anchor_y="center",
            accessibility=False,
        )
        p.label(
            f"[{skill.attribute.upper()}: {skill.attribute_value}]",
            rect.right - 12 * u,
            rect.top - 45 * u,
            12,
            MUTED,
            anchor_x="right",
        )
        y = rect.bottom + 64 * u
        p.label(
            p.tr("rank", rank=skill.rank, max=SKILL_MAX_RANK),
            rect.left + 12 * u,
            y + 18 * u,
            12,
            TEXT,
        )
        p.meter(
            Rect(rect.left + 12 * u, y - 1 * u, rect.right - 12 * u, y + 7 * u),
            skill.rank / SKILL_MAX_RANK,
            color,
            segments=SKILL_MAX_RANK,
        )
        p.label(
            p.tr("total_label"),
            rect.left + 12 * u,
            rect.bottom + 27 * u,
            16,
            color,
            bold=True,
        )
        p.label(
            str(skill.total),
            rect.right - 49 * u,
            rect.bottom + 27 * u,
            27,
            color,
            bold=True,
            anchor_x="right",
        )
        plus = Rect(
            rect.right - 40 * u,
            rect.bottom + 12 * u,
            rect.right - 10 * u,
            rect.bottom + 42 * u,
        )
        p.paint.panel(plus, GOLD if skill.can_spend else LOCKED)
        p.label(
            "+",
            *plus.center,
            24,
            GOLD if skill.can_spend else LOCKED,
            anchor_x="center",
            bold=True,
        )
