"""Art-calibrated HQ regions shared by drawing, hover and pointer dispatch."""

from dataclasses import dataclass
from .world_map_beacons import Rect

HQ_ART = "assets/ui/headquarters/tower_visual_2.png"
HQ_ART_SIZE = (1672, 941)
ROOMS = (
    ("command", "COMMAND CORE", "target"),
    ("city", "CITY GRID", "city"),
    ("squad", "SQUAD OPS", "squad"),
    ("assets", "ASSET BAY", "layers"),
    ("research", "RESEARCH LAB", "research"),
    ("intel", "INTEL ARCHIVE", "intel"),
)
# Measured interior edges in the original 1672×941 images, bottom-left origin.
VISUAL_ROOMS = (
    (270, 635, 773, 778),
    (874, 635, 1398, 778),
    (265, 495, 774, 623),
    (873, 495, 1398, 623),
    (266, 346, 775, 484),
    (873, 346, 1398, 484),
)
LEGACY_ROOMS = (
    (320, 650, 765, 785),
    (892, 650, 1373, 771),
    (274, 503, 768, 630),
    (880, 497, 1384, 630),
    (270, 351, 775, 488),
    (881, 349, 1384, 492),
)
# The aircraft deck is a seventh, full-width destination in the artwork.  It is
# deliberately separate from ``ROOMS`` because F4/Asset Bay remains the vehicle
# management room while this region launches the mission world map.
# Measured outer walls of the lower aircraft bay. The frame spans the building,
# but does not leak into the city backdrop on either side.
VISUAL_HANGAR = (195, 70, 1452, 337)
LEGACY_HANGAR = (195, 70, 1452, 337)


@dataclass(frozen=True)
class HeadquartersLayout:
    width: int
    height: int
    scale: float
    art: Rect
    header: Rect
    resources: tuple[Rect, ...]
    rooms: tuple[Rect, ...]
    labels: tuple[Rect, ...]
    hangar: Rect
    hangar_label: Rect
    footer: Rect
    navigation: tuple[Rect, ...]


def headquarters_layout(w, h, legacy=False, text_scale=1.0):
    u = min(w / 1672, h / 941)
    aw, ah = 1672 * u, 941 * u
    ox, oy = (w - aw) / 2, (h - ah) / 2
    source = LEGACY_ROOMS if legacy else VISUAL_ROOMS
    rooms = tuple(
        Rect(ox + x0 * u, oy + y0 * u, ox + x1 * u, oy + y1 * u)
        for x0, y0, x1, y1 in source
    )
    labels = tuple(
        Rect(
            r.left + 14 * u,
            r.bottom + 5 * u,
            r.left + r.width * 0.76,
            r.bottom + 41 * u,
        )
        for r in rooms
    )
    hx0, hy0, hx1, hy1 = LEGACY_HANGAR if legacy else VISUAL_HANGAR
    hangar = Rect(ox + hx0 * u, oy + hy0 * u, ox + hx1 * u, oy + hy1 * u)
    hangar_label = Rect(
        hangar.left + 28 * u,
        hangar.bottom + 14 * u,
        min(hangar.right - 28 * u, hangar.left + 510 * u),
        hangar.bottom + 64 * u,
    )
    footer = Rect(
        15 * u,
        12 * u,
        w - 15 * u,
        max(66 * u, 55 * text_scale) if text_scale > 1 else 66 * u,
    )
    nav_width = (footer.width - 20 * u) / 7
    nav = tuple(
        Rect(
            footer.left + 10 * u + i * nav_width,
            footer.bottom + 6 * u,
            footer.left + 10 * u + (i + 1) * nav_width,
            footer.top - 6 * u,
        )
        for i in range(7)
    )
    hud_left = w * 0.40
    gap = 12 * u
    cell = (w - hud_left - 25 * u - 4 * gap) / 5
    card_h = max(60 * u, 52 * text_scale)
    card_top = h - 10 * u
    resources = tuple(
        Rect(
            hud_left + i * (cell + gap),
            card_top - card_h,
            hud_left + i * (cell + gap) + cell,
            card_top,
        )
        for i in range(5)
    )
    return HeadquartersLayout(
        w,
        h,
        u,
        Rect(ox, oy, ox + aw, oy + ah),
        Rect(0, card_top - card_h - 10 * u, w, h),
        resources,
        rooms,
        labels,
        hangar,
        hangar_label,
        footer,
        nav,
    )


def headquarters_target_at(w, h, x, y, legacy=False, text_scale=1.0):
    layout = headquarters_layout(w, h, legacy, text_scale)
    for i, rect in enumerate(layout.navigation):
        if rect.contains(x, y):
            return ROOMS[i][0] if i < 6 else "close"
    for i, rect in enumerate(layout.rooms):
        if rect.contains(x, y):
            return ROOMS[i][0]
    if layout.hangar.contains(x, y):
        return "hangar"
    return None
