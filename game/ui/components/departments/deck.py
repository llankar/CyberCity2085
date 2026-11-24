"""Shared department shell, list pagination and original-controller routing."""

import arcade
from game.ui.components.document_kit import DocumentKit
from game.ui.layouts.department_deck import department_layout
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, TEXT, MUTED, PURPLE
from .copy import word

ROOMS = ("command", "city", "squad", "assets", "research", "intel")
ROOM_BACKGROUNDS = {
    "command": "assets/ui/base_command_center/command_core.png",
    "city": "assets/ui/base_command_center/city_operations.png",
    "squad": "assets/ui/base_command_center/squad_operations.png",
    "assets": "assets/ui/base_command_center/asset_bay.png",
    "research": "assets/ui/base_command_center/research_lab.png",
    "intel": "assets/ui/base_command_center/intel_archive.png",
}

# Each room illustration has a different value range.  These restrained
# per-room values keep the art visible without letting bright details compete
# with copy.  Cards remain slightly denser than their parent panes and controls
# denser again, preserving a clear interaction hierarchy.
ROOM_GLASS = {
    "command": (174, 198, 222, 118),
    "city": (182, 204, 224, 126),
    "squad": (186, 208, 226, 130),
    "assets": (184, 206, 226, 128),
    "research": (180, 204, 224, 124),
    "intel": (176, 200, 222, 120),
}


class DepartmentDeck(DocumentKit):
    def __init__(self):
        super().__init__()
        # Large department text surfaces reveal the room art while cards and
        # actionable controls keep their stronger default fill for readability.
        self.panel_fill_alpha = 182
        self.card_fill_alpha = 204
        self.stat_fill_alpha = 210
        self.compact_fill_alpha = 214
        self.control_fill_alpha = 226
        self.background_overlay_alpha = 126
        self.pages = {}
        self.selection = {}
        self.capacities = {}
        self.focus_index = -1

    def tr(self, key):
        return word(key, self.gs.ui_language)

    def draw(self, view, w, h):
        self.gs = view.game_state
        self.room = view.room_ui.active_room_key
        (
            self.panel_fill_alpha,
            self.card_fill_alpha,
            self.control_fill_alpha,
            self.background_overlay_alpha,
        ) = ROOM_GLASS.get(self.room, ROOM_GLASS["command"])
        self.stat_fill_alpha = min(218, self.card_fill_alpha + 6)
        self.compact_fill_alpha = min(222, self.card_fill_alpha + 10)
        self.layout = department_layout(
            w, h, (0.30, 0.36, 0.34) if self.room == "command" else (0.29, 0.42, 0.29)
        )
        # Dedicated art establishes a distinct place for every department.  The
        # headquarters crop remains a compatibility fallback, never the primary UI.
        background = ROOM_BACKGROUNDS.get(self.room) or view.room_ui.texture_override
        self.begin(
            view,
            w,
            h,
            background or "assets/missions/backgrounds/city/city_01_neon_alley.jpg",
            overlay_alpha=self.background_overlay_alpha,
        )
        self.view = view
        self.header()
        from . import assets, strategy

        painter = (
            assets.draw
            if self.room == "assets"
            else getattr(strategy, "draw_" + self.room)
        )
        painter(self, *self.layout.columns)
        self.footer()
        self.notice()
        self.end()

    def header(self):
        r = self.layout.header
        u = self.u
        self.paint.panel(r, CYAN, fill_alpha=self.control_fill_alpha)
        self.icon(self.room, r.left + 30 * u, r.center[1], 38)
        self.label(
            "CYBERCITY 2085",
            r.left + 60 * u,
            r.top - 20 * u,
            22,
            CYAN,
            bold=True,
            width=330 * u,
        )
        self.label(
            self.tr(self.room),
            r.left + 60 * u,
            r.bottom + 22 * u,
            29,
            TEXT,
            bold=True,
            width=360 * u,
        )
        self.resource_bar(
            self.gs,
            Rect(
                r.left + r.width * 0.34,
                r.bottom + 7 * u,
                r.right - 75 * u,
                r.top - 7 * u,
            ),
        )
        from game.ui.room_interaction import close_button_rect

        close = close_button_rect(self.view.window.width, self.view.window.height)
        self.action(
            Rect(close.left, close.bottom, close.right, close.top),
            "×",
            "squad_close",
            danger=True,
        )

    def body(self, r):
        return Rect(
            r.left + 14 * self.u,
            r.bottom + 14 * self.u,
            r.right - 14 * self.u,
            r.top - 61 * self.u,
        )

    def click(self, action, data):
        if action == "ui_disabled":
            return
        if action == "department_room":
            self.view._open_hub_room(data)
        elif action == "department_select":
            self.selection[data[0]] = data[1]
            if data[0] == "research":
                self.pages["research_detail"] = 0
        elif action == "department_page":
            name, step = data
            if name == "hangar":
                pages, capacity, _ = self.capacities[name]
                size = len(self.gs.spec_ops_assets)
                if size:
                    page = (self.pages.get(name, 0) + step) % pages
                    self.view._asset_cursor = min(page * capacity, size - 1)
            else:
                self.turn_page(name, step)
        else:
            self.view._dispatch(action, data)

    def motion(self, x, y):
        self.hover = None
        for hit in reversed(self.view._hits):
            if hit.contains(x, y):
                self.hover = (hit.action, hit.data)
                break

    def scroll(self, x, y, step):
        for name, (_, _, rect) in self.capacities.items():
            if rect and rect.contains(x, y):
                self.click("department_page", (name, -1 if step > 0 else 1))
                return

    def key(self, key):
        hits = [h for h in self.view._hits if h.action != "ui_disabled"]
        if not hits:
            return
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.TAB):
            self.focus_index = (
                self.focus_index + (-1 if key == arcade.key.UP else 1)
            ) % len(hits)
            hit = hits[self.focus_index]
            self.hover = (hit.action, hit.data)
        elif key == arcade.key.SPACE and self.focus_index >= 0:
            hit = hits[self.focus_index % len(hits)]
            self.click(hit.action, hit.data)

    def footer(self):
        r = self.layout.footer
        u = self.u
        self.paint.panel(r, CYAN, fill_alpha=self.control_fill_alpha)
        gap = 6 * u
        labels = [
            "F1 CORE",
            "F2 CITY",
            "F3 SQUAD",
            "F4 ASSETS",
            "F5 LAB",
            "F6 INTEL",
        ]
        controls = [
            (label, "department_room", room, room == self.room)
            for label, room in zip(labels, ROOMS)
        ]
        controls += [
            ("‹", "slot_delta", -1, False),
            (str(self.view.selected_save_slot), "ui_disabled", None, False),
            ("›", "slot_delta", 1, False),
            (self.tr("save"), "save", None, False),
            (self.word("CHARGER", "LOAD"), "load", None, False),
            ("SYS", "squad_settings", None, False),
            (self.word("BASE", "BASE"), "squad_close", None, False),
        ]
        weights = [1] * 6 + [0.28, 0.28, 0.28, 0.8, 0.8, 0.4, 0.9]
        available = r.width - 20 * u - gap * (len(controls) - 1)
        x = r.left + 10 * u
        for item, weight in zip(controls, weights):
            label, action, data, selected = item
            width = available * weight / sum(weights)
            self.action(
                Rect(x, r.bottom + 9 * u, x + width, r.top - 9 * u),
                label,
                action,
                data,
                selected=selected,
            )
            x += width + gap

    def notice(self):
        latest = self.view.notifications.latest_text_lines(1)
        text = self.view.message or (latest[0] if latest else "")
        if self.hover:
            hit = next(
                (
                    h
                    for h in reversed(self.view._hits)
                    if (h.action, h.data) == self.hover
                ),
                None,
            )
            if hit and hit.tooltip:
                text = hit.tooltip.replace("\n", " / ")
        self.label(
            text,
            self.layout.footer.left + 8 * self.u,
            self.layout.footer.top + 17 * self.u,
            14,
            GOLD,
            width=self.layout.footer.width - 16 * self.u,
        )
