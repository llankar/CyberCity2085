"""Responsive operative-dossier geometry and row paging, independent of Arcade."""

from dataclasses import dataclass
from math import ceil
from .world_map_beacons import Rect


@dataclass(frozen=True)
class CharacterSheetLayout:
    width: int
    height: int
    scale: float
    header: Rect
    banner: Rect
    identity: Rect
    talents: Rect
    attributes: Rect
    readiness: Rect
    schematic: Rect
    skills: Rect
    footer: Rect

    # Shared command-painter section hooks, with dossier-specific contents.
    @property
    def roster(self):
        return self.identity

    @property
    def equipment(self):
        return self.attributes

    @property
    def mission(self):
        return self.skills


def character_sheet_layout(width, height):
    u = min(width / 1672, height / 941)
    margin = max(10, 18 * u)
    gap = max(9, 14 * u)
    available = width - 2 * margin - 2 * gap
    left_w = available * 0.32
    middle_w = available * 0.315
    left = margin
    middle = left + left_w + gap
    right = middle + middle_w + gap
    top = height - max(112, 142 * u)
    bottom = max(18, 30 * u)
    identity_h = min(390 * u, (top - bottom) * (0.46 if height < 850 else 0.53))
    identity = Rect(left, top - identity_h, left + left_w, top)
    talents = Rect(left, bottom, left + left_w, identity.bottom - gap)
    attributes = Rect(middle, top - 255 * u, middle + middle_w, top)
    readiness = Rect(
        middle,
        attributes.bottom - gap - 190 * u,
        middle + middle_w,
        attributes.bottom - gap,
    )
    lower = max(74, 100 * u)
    schematic = Rect(middle, lower, middle + middle_w, readiness.bottom - gap)
    skills = Rect(right, lower, width - margin, top)
    footer = Rect(middle, bottom, width - margin, lower - 15 * u)
    return CharacterSheetLayout(
        width,
        height,
        u,
        Rect(0, height - max(52, 63 * u), width, height),
        Rect(margin, top + 17 * u, width - margin, height - max(56, 75 * u)),
        identity,
        talents,
        attributes,
        readiness,
        schematic,
        skills,
        footer,
    )


@dataclass(frozen=True)
class PagedGrid:
    columns: int
    visible_rows: int
    first_row: int
    total_rows: int
    cards: tuple[tuple[int, Rect], ...]

    @property
    def max_first_row(self):
        return max(0, self.total_rows - self.visible_rows)


def paged_grid(bounds, count, columns, min_height, gap, first_row=0):
    rows = max(1, int((bounds.height + gap) / (min_height + gap)))
    total = ceil(count / columns)
    first = max(0, min(first_row, max(0, total - rows)))
    height = (bounds.height - (rows - 1) * gap) / rows
    width = (bounds.width - (columns - 1) * gap) / columns
    cards = []
    for index in range(first * columns, min(count, (first + rows) * columns)):
        row = index // columns - first
        col = index % columns
        x = bounds.left + col * (width + gap)
        top = bounds.top - row * (height + gap)
        cards.append(
            (
                index,
                Rect(
                    x,
                    max(bounds.bottom, top - height),
                    min(bounds.right, x + width),
                    top,
                ),
            )
        )
    return PagedGrid(columns, rows, first, total, tuple(cards))
