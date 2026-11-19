"""Small, engine-neutral helpers for the tactical battle camera."""

from __future__ import annotations


def camera_pan_limits(view_width: float, view_height: float) -> tuple[float, float]:
    """Return restrained pan limits that keep the battlefield in view."""
    return min(192.0, max(0.0, view_width / 8)), min(128.0, max(0.0, view_height / 8))


def clamp_camera_pan(
    pan_x: float, pan_y: float, view_width: float, view_height: float, *, hud_bottom: float = 0
) -> tuple[float, float]:
    """Clamp a requested pan to the overscanned tactical map bounds."""
    limit_x, limit_y = camera_pan_limits(view_width, view_height)
    lower_limit = limit_y
    if hud_bottom > 0:
        lower_limit = max(limit_y,min(view_height/2,hud_bottom+32))
    return (
        max(-limit_x, min(limit_x, float(pan_x))),
        max(-lower_limit, min(limit_y, float(pan_y))),
    )


def camera_pan_to_focus(
    position: tuple[float, float], view_width: float, view_height: float, *, hud_bottom: float = 0
) -> tuple[float, float]:
    """Return the bounded pan that brings a world position toward screen centre."""
    return clamp_camera_pan(
        position[0] - view_width / 2,
        position[1] - (view_height+hud_bottom) / 2,
        view_width,
        view_height,
        hud_bottom=hud_bottom,
    )


def keep_focus_visible(position, pan, view_width, view_height, *, hud_bottom=0, margin=32):
    """Minimal camera change to reveal a selected unit; preserve deliberate pan otherwise."""
    x,y=position
    px,py=pan
    if x-px<margin:
        px=x-margin
    elif x-px>view_width-margin:
        px=x-view_width+margin
    if y-py<hud_bottom+margin:
        py=y-hud_bottom-margin
    elif y-py>view_height-96:
        py=y-view_height+96
    return clamp_camera_pan(px,py,view_width,view_height,hud_bottom=hud_bottom)
