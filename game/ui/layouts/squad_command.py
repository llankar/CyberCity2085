"""Responsive geometry for Squad Command; no rendering or campaign mutations."""

from dataclasses import dataclass
from .world_map_beacons import Rect


@dataclass(frozen=True)
class SquadCommandLayout:
    width: int
    height: int
    scale: float
    header: Rect
    roster: Rect
    equipment: Rect
    mission: Rect
    footer: Rect

    @property
    def columns(self):
        return (self.roster, self.equipment, self.mission)


def squad_command_layout(width, height):
    scale = min(width / 1672, height / 941)
    margin = max(14, 24 * scale)
    gap = max(8, 12 * scale)
    header_height = max(60, 72 * scale)
    footer_height = max(96, 112 * scale)
    bottom = footer_height + max(23, 22 * scale)
    top = height - header_height - 20 * scale
    usable = width - 2 * margin - 2 * gap
    roster_width = usable * 0.25
    equipment_width = usable * 0.38
    x = margin
    roster = Rect(x, bottom, x + roster_width, top)
    x = roster.right + gap
    equipment = Rect(x, bottom, x + equipment_width, top)
    mission = Rect(equipment.right + gap, bottom, width - margin, top)
    return SquadCommandLayout(
        width,
        height,
        scale,
        Rect(0, height - header_height, width, height),
        roster,
        equipment,
        mission,
        Rect(0, 0, width, footer_height),
    )


def visible_roster_range(count, cursor, first, capacity=5):
    first = max(0, min(first, max(0, count - capacity)))
    return range(first, min(count, first + capacity))
