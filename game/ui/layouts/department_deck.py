"""Pure responsive geometry for every remaining management department."""

from dataclasses import dataclass
from game.ui.layouts.world_map_beacons import Rect


@dataclass(frozen=True)
class DepartmentLayout:
    scale: float
    header: Rect
    content: Rect
    footer: Rect
    columns: tuple[Rect, ...]


def department_layout(width, height, fractions=(0.28, 0.42, 0.30)):
    u = max(0.70, min(width / 1672, height / 941, 1.7))
    gap = 14 * u
    content = Rect(18 * u, 102 * u, width - 18 * u, height - 112 * u)
    available = content.width - gap * (len(fractions) - 1)
    columns = []
    x = content.left
    total = sum(fractions)
    for fraction in fractions:
        w = available * fraction / total
        columns.append(Rect(x, content.bottom, x + w, content.top))
        x += w + gap
    return DepartmentLayout(
        u,
        Rect(18 * u, height - 90 * u, width - 18 * u, height - 16 * u),
        content,
        Rect(18 * u, 16 * u, width - 18 * u, 78 * u),
        tuple(columns),
    )
