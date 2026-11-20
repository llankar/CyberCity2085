"""Shared paginated readers and selectable lists; no campaign mutations."""

from game.ui.components.visual_kit import VisualKit
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, TEXT, MUTED
from game.ui.theme.typography import scale_font_size


class DocumentKit(VisualKit):
    def __init__(self):
        super().__init__()
        self.pages = {}
        self.capacities = {}
        self.selection = {}
        self._documents = {}

    def begin(self, *args, **kwargs):
        super().begin(*args, **kwargs)
        self.capacities = {}

    def page(self, name, rows, r, row_h, selected=None):
        u = self.u
        capacity = max(1, int((r.height - 42 * u) / (row_h * u + 8 * u)))
        count = len(rows)
        pages = max(1, (count + capacity - 1) // capacity)
        current = max(0, min(self.pages.get(name, 0), pages - 1))
        if selected is not None:
            current = min(pages - 1, max(0, selected // capacity))
        self.pages[name] = current
        self.capacities[name] = (pages, capacity, r)
        for index in range(current * capacity, min(count, (current + 1) * capacity)):
            top = r.top - (index - current * capacity) * (row_h + 8) * u
            yield index, rows[index], Rect(r.left, top - row_h * u, r.right, top)
        if pages > 1:
            y = r.bottom
            self.action(
                Rect(r.left, y, r.left + 38 * u, y + 30 * u),
                "‹",
                "department_page",
                (name, -1),
            )
            self.label(
                f"{current+1} / {pages}",
                *Rect(r.left + 43 * u, y, r.right - 43 * u, y + 30 * u).center,
                14,
                MUTED,
                anchor_x="center",
            )
            self.action(
                Rect(r.right - 38 * u, y, r.right, y + 30 * u),
                "›",
                "department_page",
                (name, 1),
            )

    def document(self, name, text, rect, size=16, color=TEXT, *, headings=(), keep_paragraphs=False):
        font = scale_font_size(max(13, size * self.u))
        # Preserve paragraphs and all data through explicit reader pages.
        key = (str(text), rect.width, font)
        lines = self._documents.get(key)
        if lines is None:
            lines = []
            for paragraph in str(text).split("\n"):
                line = ""
                for word in paragraph.split():
                    # Preserve even long identifiers and executable paths.
                    pieces = []
                    while word and self.paint.fit(word, rect.width, font) != word:
                        split = max(
                            1,
                            len(self.paint.fit(word, rect.width, font).rstrip("…")) - 1,
                        )
                        pieces.append(word[:split])
                        word = word[split:]
                    if word:
                        pieces.append(word)
                    for piece in pieces:
                        candidate = (line + " " + piece).strip()
                        if (
                            line
                            and self.paint.fit(candidate, rect.width, font) != candidate
                        ):
                            lines.append(line)
                            line = piece
                        else:
                            line = candidate
                lines.append(line)
            if len(self._documents) > 128:
                self._documents.clear()
            self._documents[key] = lines
        leading = max(21 * self.u, font * 1.5)
        capacity = max(1, int((rect.height - 37 * self.u) / leading))
        page_lines = []
        start = 0
        while start < len(lines):
            end = min(start + capacity, len(lines))
            if keep_paragraphs and end < len(lines) and lines[end]:
                boundary = end
                while boundary > start and lines[boundary - 1]:
                    boundary -= 1
                if boundary > start:
                    end = boundary
            page_lines.append(lines[start:end])
            start = end
            if keep_paragraphs:
                while start < len(lines) and not lines[start]:
                    start += 1
        pages = max(1, len(page_lines))
        self.pages[name] = min(self.pages.get(name, 0), pages - 1)
        page = self.pages[name]
        self.capacities[name] = (pages, capacity, rect)
        for i, line in enumerate(page_lines[page] if page_lines else ()):
            self.label(
                line,
                rect.left,
                rect.top - leading * (i + 0.5),
                size,
                CYAN if line in headings else color,
                bold=line in headings,
                width=rect.width,
            )
        if pages > 1:
            self.action(
                Rect(
                    rect.left,
                    rect.bottom,
                    rect.left + 40 * self.u,
                    rect.bottom + 30 * self.u,
                ),
                "‹",
                "department_page",
                (name, -1),
            )
            self.label(
                f"{page+1}/{pages}",
                *Rect(
                    rect.left + 45 * self.u,
                    rect.bottom,
                    rect.right - 45 * self.u,
                    rect.bottom + 30 * self.u,
                ).center,
                13,
                MUTED,
                anchor_x="center",
            )
            self.action(
                Rect(
                    rect.right - 40 * self.u,
                    rect.bottom,
                    rect.right,
                    rect.bottom + 30 * self.u,
                ),
                "›",
                "department_page",
                (name, 1),
            )

    def turn_page(self, name, step):
        pages, _, _ = self.capacities.get(name, (1, 1, None))
        self.pages[name] = (self.pages.get(name, 0) + step) % pages
