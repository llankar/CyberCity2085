"""Mission-specific cinematic scene and exact tactical-map inspection."""

import arcade
from game.ui.layouts.world_map_beacons import Rect
from .squad_style import CYAN, GOLD, TEXT, MUTED


def draw_scene(p, r):
    u = p.u
    p.paint.panel(r, CYAN)
    image = Rect(r.left + 7 * u, r.bottom + 7 * u, r.right - 7 * u, r.top - 7 * u)
    p.image(p.art, image)
    objective = Rect(r.left + 14 * u, r.top - 142 * u, r.right - 14 * u, r.top - 14 * u)
    p.paint.panel(objective, GOLD)
    p.icon("target", objective.left + 25 * u, objective.top - 25 * u, 30, GOLD)
    p.label(
        p.tr("objective"),
        objective.left + 49 * u,
        objective.top - 25 * u,
        25,
        GOLD,
        bold=True,
        width=objective.width - 115 * u,
    )
    p.scroll_text(
        "objective",
        Rect(
            objective.left + 15 * u,
            objective.bottom + 12 * u,
            objective.right - 15 * u,
            objective.top - 50 * u,
        ),
        p.lines["objective"],
        size=18,
        pager_rect=objective,
    )
    bottom = Rect(
        r.left + 14 * u, r.bottom + 14 * u, r.right - 14 * u, r.bottom + 205 * u
    )
    p.paint.panel(bottom, CYAN)
    thumb = Rect(
        bottom.left + 10 * u,
        bottom.bottom + 10 * u,
        bottom.left + bottom.width * 0.48,
        bottom.top - 10 * u,
    )
    if p.view._map_texture:
        p.texture(p.view._map_texture, thumb, cover=False)
    else:
        p.label(
            p.tr("no_map"),
            *thumb.center,
            14,
            MUTED,
            anchor_x="center",
            width=thumb.width
        )
    arcade.draw_lrbt_rectangle_outline(
        thumb.left, thumb.right, thumb.bottom, thumb.top, (*CYAN, 170), 1
    )
    p.hit(thumb, "map", tooltip=p.tr("inspect_map"))
    p.regions["map_preview"] = thumb
    x = thumb.right + 13 * u
    width = bottom.right - x - 10 * u
    p.label(p.tr("tactical"), x, bottom.top - 23 * u, 19, CYAN, bold=True, width=width)
    from game.ui.screens.mission_briefing_view import pressure_label

    theme = str(p.mission.enemy_theme).replace("_", " ").upper()
    intel = [
        p.facts["hostile_estimate"],
        p.tr("enemy", name=theme),
        p.tr("pressure", value=pressure_label(p.mission.district_pressure)),
        p.tr("inspect_map"),
    ]
    p.scroll_text(
        "intel",
        Rect(x, bottom.bottom + 12 * u, bottom.right - 12 * u, bottom.top - 47 * u),
        intel,
        size=14,
    )
    # A slow narrow scan across the scene, behind all text and away from the cards.
    scan_y = bottom.top + (
        (p.view._elapsed * 18) % max(1, objective.bottom - bottom.top)
    )
    arcade.draw_line(image.left, scan_y, image.right, scan_y, (*CYAN, 45), 1)
