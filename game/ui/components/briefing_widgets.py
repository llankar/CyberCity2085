"""Paged text cards: measured lines, full content, no scissor/text-batch conflict."""

import arcade
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.typography import scale_font_size
from .squad_style import CYAN, TEXT, MUTED


def wrapped_lines(painter, paragraphs, width, size):
    lines = []
    for paragraph in paragraphs:
        for source in str(paragraph).splitlines() or [""]:
            line = ""
            for word in source.split():
                candidate = (line + " " + word).strip()
                if line and painter.fit(candidate, width, size, False) != candidate:
                    lines.append(line)
                    line = ""
                # Break very long tokens rather than silently dropping characters.
                while painter.fit(word, width, size, False) != word and len(word) > 1:
                    n = max(1, len(painter.fit(word, width, size, False).rstrip("…")))
                    lines.append(word[:n])
                    word = word[n:]
                line = (line + " " + word).strip()
            lines.append(line)
        lines.append("")
    return lines[:-1]


def scroll_card(p, key, rect, title, paragraphs, color=CYAN, icon="intel", size=15):
    u = p.u
    p.paint.panel(rect, color)
    heading = max(40 * u, scale_font_size(14) * 1.65)
    p.icon(icon, rect.left + 23 * u, rect.top - heading / 2, 25, color)
    p.label(
        title,
        rect.left + 43 * u,
        rect.top - heading / 2,
        21,
        color,
        bold=True,
        width=rect.width - 112 * u,
    )
    arcade.draw_line(
        rect.left + 12 * u,
        rect.top - heading,
        rect.right - 12 * u,
        rect.top - heading,
        (*color, 100),
        1,
    )
    area = Rect(
        rect.left + 13 * u,
        rect.bottom + 11 * u,
        rect.right - 13 * u,
        rect.top - heading - 9 * u,
    )
    p.scroll_text(key, area, paragraphs, size=size, color=TEXT, pager_rect=rect)


def scroll_text(p, key, area, paragraphs, size=15, color=TEXT, pager_rect=None):
    font = scale_font_size(max(13, size * p.u))
    step = max(font * 1.3, 20 * p.u)
    lines = wrapped_lines(p.paint, paragraphs, area.width, font)
    capacity = max(1, int(area.height / step))
    inline_pager = pager_rect is None and len(lines) > capacity
    if inline_pager:
        area = Rect(area.left, area.bottom + 28 * p.u, area.right, area.top)
        capacity = max(1, int(area.height / step))
    maximum = max(0, len(lines) - capacity)
    first = max(0, min(p.offsets.get(key, 0), maximum))
    p.offsets[key] = first
    p.scroll_regions[key] = (area, maximum)
    p.visible_lines[key] = (first, capacity, len(lines))
    y = area.top - step / 2
    for line in lines[first : first + capacity]:
        p.text(line, area.left, y, font, color, anchor_y="center", accessibility=False)
        y -= step
    if maximum:
        r = pager_rect or Rect(
            area.left, area.bottom - 28 * p.u, area.right, area.bottom
        )
        p.pager(key, r, first, maximum)
        x = area.right + 5 * p.u
        arcade.draw_line(x, area.bottom, x, area.top, (*CYAN, 55), 2)
        height = max(8 * p.u, area.height * capacity / len(lines))
        top = area.top - (area.height - height) * first / maximum
        arcade.draw_line(x, top - height, x, top, CYAN, 2)
