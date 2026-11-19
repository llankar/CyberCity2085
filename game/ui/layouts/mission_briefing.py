"""Pure responsive geometry for the military briefing."""

from dataclasses import dataclass
from .world_map_beacons import Rect


@dataclass(frozen=True)
class BriefingLayout:
    width: int
    height: int
    scale: float
    header: Rect
    banner: Rect
    scene: Rect
    risk: Rect
    duration: Rect
    reward: Rect
    stress: Rect
    complications: Rect
    impact: Rect
    squad: Rect
    support: Rect
    success: Rect
    failure: Rect
    abort: Rect
    deploy: Rect


def briefing_layout(width, height):
    u = min(width / 1672, height / 941)
    m, g = 14 * u, 14 * u
    top, bottom = height - 151 * u, 115 * u
    available = width - 2 * m - 2 * g
    lw, cw = available * 0.37, available * 0.235
    x, z = m + lw + g, m + lw + g + cw + g
    rh = top - bottom
    gap = g
    risk = Rect(x, top - 99 * u, x + cw, top)
    duration = Rect(
        x, risk.bottom - gap - 88 * u, x + (cw - gap) / 2, risk.bottom - gap
    )
    reward = Rect(duration.right + gap, duration.bottom, x + cw, duration.top)
    stress = Rect(x, duration.bottom - gap - 99 * u, x + cw, duration.bottom - gap)
    remaining = stress.bottom - gap - bottom
    complications = Rect(
        x, stress.bottom - gap - remaining * 0.48, x + cw, stress.bottom - gap
    )
    impact = Rect(x, bottom, x + cw, complications.bottom - gap)
    sqbottom = top - rh * 0.52
    squad = Rect(z, sqbottom, width - m, top)
    support = Rect(z, sqbottom - gap - rh * 0.20, width - m, sqbottom - gap)
    mid = (z + width - m - gap) / 2
    return BriefingLayout(
        width,
        height,
        u,
        Rect(m, height - 60 * u, width - m, height - 5 * u),
        Rect(m, top + 14 * u, width - m, height - 66 * u),
        Rect(m, bottom, m + lw, top),
        risk,
        duration,
        reward,
        stress,
        complications,
        impact,
        squad,
        support,
        Rect(z, bottom, mid, support.bottom - gap),
        Rect(mid + gap, bottom, width - m, support.bottom - gap),
        Rect(width * 0.24, 22 * u, width * 0.45, 93 * u),
        Rect(width * 0.47, 22 * u, width * 0.76, 93 * u),
    )
