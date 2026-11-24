"""Identity pane: real portrait, progression and operational state."""

import arcade
from game.character import is_deployable
from game.ui.layouts.world_map_beacons import Rect
from game.ui.portraits import portrait_path_for_character
from .squad_style import CYAN, GOLD, MINT, RED, TEXT, MUTED


def draw_identity(p, r):
    u = p.u
    c = p.character
    p.paint.panel(r, CYAN, selected=True, fill_alpha=p.sheet_card_fill_alpha)
    portrait = Rect(
        r.left + 12 * u, r.bottom + 86 * u, r.left + r.width * 0.49, r.top - 12 * u
    )
    p.image(portrait_path_for_character(c), portrait)
    arcade.draw_lrbt_rectangle_outline(
        portrait.left, portrait.right, portrait.bottom, portrait.top, (*CYAN, 170), 1.5
    )
    x = portrait.right + 14 * u
    right = r.right - 14 * u
    top = r.top - 27 * u
    width = right - x
    p.label(c.name.upper(), x, top, 27, TEXT, bold=True, width=width)
    p.label(p.role_label, x, top - 33 * u, 17, GOLD, bold=True, width=width)
    p.paint.panel(
        Rect(x, top - 77 * u, min(right, x + 125 * u), top - 52 * u),
        CYAN,
        fill_alpha=p.sheet_card_fill_alpha,
    )
    p.label(
        p.tr("level", level=c.stats.level),
        x + 10 * u,
        top - 64 * u,
        14,
        TEXT,
        bold=True,
        width=width - 12 * u,
    )
    y = top - 105 * u
    p.label("XP", x, y, 15, MUTED)
    p.label(
        f"{c.stats.xp:,} / {p.data.xp_target:,}",
        right,
        y,
        13,
        TEXT,
        anchor_x="right",
        width=width - 25 * u,
    )
    p.meter(
        Rect(x, y - 16 * u, right, y - 10 * u),
        c.stats.xp / max(1, p.data.xp_target),
        CYAN,
        segments=10,
    )
    for label, value in [
        (p.tr("loyalty"), str(c.loyalty)),
        (p.tr("recovery"), p.tr("days", count=c.recovery_turns)),
    ]:
        y -= 32 * u
        p.label(label, x, y, 15, MUTED, width=width * 0.57)
        p.label(value, right, y, 15, TEXT, anchor_x="right", width=width * 0.43)
    status = (
        p.tr("ready")
        if is_deployable(c)
        else p.tr("recovering") if c.recovery_turns > 0 else p.tr("unavailable")
    )
    status_rect = Rect(x, r.bottom + 90 * u, right, r.bottom + 118 * u)
    if status_rect.top < y - 9 * u:
        p.paint.panel(
            status_rect,
            MINT if is_deployable(c) else GOLD,
            fill_alpha=p.sheet_card_fill_alpha,
        )
        p.label(
            status,
            *status_rect.center,
            12,
            MINT if is_deployable(c) else GOLD,
            bold=True,
            anchor_x="center",
            width=status_rect.width - 10 * u,
        )
    for i, (key, value, fraction, color, icon) in enumerate(
        [
            (
                "hp",
                f"{c.stats.hp} / {c.stats.max_hp}",
                c.stats.hp / max(1, c.stats.max_hp),
                MINT,
                "heart",
            ),
            (
                "stress",
                f'{c.stress} / {p.data.derived["stress_cap"]}',
                c.stress / max(1, p.data.derived["stress_cap"]),
                GOLD,
                "bolt",
            ),
        ]
    ):
        y = r.bottom + (61 - i * 35) * u
        p.icon(icon, r.left + 23 * u, y + 6 * u, 20, color)
        p.label(p.tr(key), r.left + 43 * u, y + 6 * u, 13, TEXT, bold=True)
        p.label(value, r.right - 14 * u, y + 6 * u, 13, TEXT, anchor_x="right")
        p.meter(
            Rect(r.left + 43 * u, y - 11 * u, r.right - 14 * u, y - 4 * u),
            fraction,
            color,
            segments=10,
        )
    p.hit(
        r,
        "sheet_info",
        ("identity", c.name),
        p.tr(
            "identity_help",
            xp=c.stats.xp,
            target=p.data.xp_target,
            stress=c.stress,
            cap=p.data.derived["stress_cap"],
        ),
    )
