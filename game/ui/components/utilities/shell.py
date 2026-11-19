"""Visual 2.x shell and input bridge; calls existing screen controllers."""

from game.ui.components.document_kit import DocumentKit
from game.ui.layouts.department_deck import department_layout
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, TEXT, MUTED

BACKGROUND = "assets/missions/backgrounds/city/city_01_neon_alley.jpg"


class UtilityDeck(DocumentKit):
    def __init__(self):
        super().__init__()
        from game.ui.screens.settings_screen import load_settings
        from game.ui.theme.typography import get_text_size, set_text_size

        text_size = get_text_size()
        self.reduced_motion = load_settings().reduced_motion
        set_text_size(text_size)

    def start(
        self,
        view,
        title,
        subtitle="",
        background=BACKGROUND,
        fractions=(0.32, 0.36, 0.32),
    ):
        w, h = view.window.width, view.window.height
        self.begin(view, w, h, background)
        # Global utility pages inherit campaign language when opened from management.
        if self.gs is None:
            self.gs = getattr(getattr(view, "_return_view", None), "game_state", None)
        self.layout = department_layout(w, h, fractions)
        r = self.layout.header
        u = self.u
        self.paint.panel(r, CYAN)
        self.label(
            "CYBERCITY 2085",
            r.left + 22 * u,
            r.top - 21 * u,
            22,
            CYAN,
            bold=True,
            width=r.width * 0.3,
        )
        self.label(
            title,
            r.left + 22 * u,
            r.bottom + 23 * u,
            30,
            TEXT,
            bold=True,
            width=r.width * 0.8,
        )
        if subtitle:
            self.label(
                subtitle,
                r.right - 20 * u,
                r.top - 23 * u,
                15,
                MUTED,
                anchor_x="right",
                width=r.width * 0.64,
            )

    def body(self, r):
        return Rect(
            r.left + 16 * self.u,
            r.bottom + 16 * self.u,
            r.right - 16 * self.u,
            r.top - 62 * self.u,
        )

    def footer(self, label, action="continue", secondary=None, hint=None):
        r = self.layout.footer
        u = self.u
        self.paint.panel(r, CYAN)
        if secondary:
            self.action(
                Rect(
                    r.left + 12 * u,
                    r.bottom + 8 * u,
                    r.left + r.width * 0.36,
                    r.top - 8 * u,
                ),
                secondary[0],
                secondary[1],
                danger=True,
            )
        self.action(
            Rect(
                r.left + r.width * 0.48,
                r.bottom + 8 * u,
                r.right - 12 * u,
                r.top - 8 * u,
            ),
            label,
            action,
            primary=True,
            icon="next",
        )
        self.label(
            hint
            or self.word(
                "TAB / FLÈCHES · ESPACE : ACTIVER", "TAB / ARROWS · SPACE: ACTIVATE"
            ),
            r.left,
            r.top + 15 * u,
            13,
            MUTED,
            width=r.width * 0.48,
        )

    def activate(self, hit):
        if hit.action == "ui_disabled":
            return True
        if hit.action == "report_agent":
            self.selection["report_agent"] = hit.data
            return True
        if hit.action == "report_mission":
            self.selection.pop("report_agent", None)
            return True
        if hit.action == "report_agent":
            self.selection["report_agent"] = hit.data
            self.pages["agent_report"] = 0
            return True
        if hit.action == "report_mission":
            self.selection.pop("report_agent", None)
            return True
        if hit.action == "department_page":
            self.turn_page(*hit.data)
            return True
        return False

    def motion(self, x, y):
        self.hover = next(
            ((a.action, a.data) for a in reversed(self.view._hits) if a.contains(x, y)),
            None,
        )

    def keyboard(self, key):
        import arcade

        hits = [h for h in self.view._hits if h.action != "ui_disabled"]
        if key in (arcade.key.TAB, arcade.key.UP, arcade.key.DOWN) and hits:
            index = next(
                (i for i, h in enumerate(hits) if (h.action, h.data) == self.hover), -1
            )
            hit = hits[(index + (-1 if key == arcade.key.UP else 1)) % len(hits)]
            self.hover = (hit.action, hit.data)
            return True
        if key == arcade.key.SPACE:
            return next((h for h in hits if (h.action, h.data) == self.hover), False)
        return False
