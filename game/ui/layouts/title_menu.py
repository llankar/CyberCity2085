"""Responsive main-menu framing, independent of graphics and campaign state."""

from dataclasses import dataclass
from .world_map_beacons import Rect


@dataclass(frozen=True)
class TitleLayout:
    width: int
    height: int
    scale: float
    logo: Rect
    subtitle: Rect
    buttons: tuple[Rect, ...]
    footer: Rect
    motion: Rect
    notice: Rect


def title_layout(w, h):
    u = min(w / 1672, h / 941)
    cx = w / 2
    button_w, button_h, gap = 424 * u, 68 * u, 18 * u
    top = h * 0.60
    buttons = tuple(
        Rect(
            cx - button_w / 2,
            top - i * (button_h + gap) - button_h,
            cx + button_w / 2,
            top - i * (button_h + gap),
        )
        for i in range(4)
    )
    return TitleLayout(
        w,
        h,
        u,
        Rect(cx - 478 * u, h * 0.744, cx + 478 * u, h * 0.87),
        Rect(cx - 345 * u, h * 0.707, cx + 345 * u, h * 0.744),
        buttons,
        Rect(20 * u, 25 * u, w - 20 * u, 71 * u),
        Rect(37 * u, 29 * u, 320 * u, 67 * u),
        Rect(
            cx - 370 * u,
            buttons[-1].bottom - 43 * u,
            cx + 370 * u,
            buttons[-1].bottom - 12 * u,
        ),
    )
