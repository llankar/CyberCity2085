"""Data-driven city presentation; original controllers own all mutations."""

from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, TEXT, MUTED, PURPLE


def draw_city(k, left, center, right):
    gs = k.gs
    d = gs.district
    u = k.u
    k.panel(left, k.tr("district"), "target")
    r = k.body(left)
    k.paragraph(d.name.upper(), Rect(r.left, r.top - 68 * u, r.right, r.top), 26, GOLD)
    k.label(d.control_faction, r.left, r.top - 86 * u, 16, CYAN, width=r.width)
    y = r.top - 115 * u
    for title, value, color in [
        ("stability", d.stability, MINT),
        ("unrest", d.unrest, GOLD),
        ("media", d.media_heat, RED),
    ]:
        k.stat(
            Rect(r.left, y - 120 * u, r.right, y),
            k.tr(title),
            f"{value} / 100",
            "target",
            color=color,
            fraction=value / 100,
        )
        y -= 135 * u
    k.panel(center, k.tr("upgrades"), "gears")
    r = k.body(center)
    if k.view.room_ui.texture_override:
        k.texture(
            k.view.room_ui.texture_override,
            Rect(r.left, r.top - 150 * u, r.right, r.top),
        )
    y = r.top - 168 * u
    costs = {
        "armaments": {"credits": 5, "salvage": 3},
        "garrisons": {"credits": 10, "influence": 2},
        "defense_zones": {"credits": 5, "salvage": 5},
    }
    for key, cost in costs.items():
        r2 = Rect(r.left, y - 126 * u, r.right, y)
        k.paint.panel(r2, CYAN)
        k.label(
            k.tr(key),
            r2.left + 14 * u,
            r2.top - 22 * u,
            23,
            TEXT,
            bold=True,
            width=r2.width - 30 * u,
        )
        k.label(
            str(gs.city_budget.get(key, 0)),
            r2.right - 18 * u,
            r2.top - 22 * u,
            23,
            GOLD,
            anchor_x="right",
        )
        label = " / ".join(f"{a} −{b}" for a, b in cost.items())
        k.label(
            label, r2.left + 14 * u, r2.top - 53 * u, 15, MUTED, width=r2.width - 28 * u
        )
        k.action(
            Rect(
                r2.left + 12 * u,
                r2.bottom + 10 * u,
                r2.right - 12 * u,
                r2.bottom + 48 * u,
            ),
            k.word("AMÉLIORER +10", "UPGRADE +10"),
            "city_upgrade_" + key,
            enabled=all(gs.strategic_resources.get(a, 0) >= b for a, b in cost.items()),
            icon="next",
        )
        y -= 141 * u
    k.panel(right, k.tr("factions"), "squad")
    r = k.body(right)
    factions = sorted(gs.factions, key=lambda f: f.hostility_to_player, reverse=True)
    for i, faction, card in k.page("factions", factions, r, 115):
        color = (
            RED
            if faction.hostility_to_player >= 70
            else GOLD if faction.hostility_to_player >= 40 else CYAN
        )
        k.card(
            card,
            faction.name,
            f'{k.tr("influence")} {faction.influence}',
            color=color,
            tooltip=faction.name,
        )
        k.label(
            f'{k.tr("hostility")} {faction.hostility_to_player}%',
            card.left + 16 * u,
            card.bottom + 33 * u,
            15,
            color,
            width=card.width - 30 * u,
        )
        k.meter(
            Rect(
                card.left + 16 * u,
                card.bottom + 12 * u,
                card.right - 16 * u,
                card.bottom + 19 * u,
            ),
            faction.hostility_to_player / 100,
            color,
        )
