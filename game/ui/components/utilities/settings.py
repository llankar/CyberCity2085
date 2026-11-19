"""Responsive three-column settings console using the common UI kit."""

from game.ui.components.utilities.shell import UtilityDeck
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MUTED, TEXT, MINT


class SettingsDeck(UtilityDeck):
    def draw(self, v):
        from game.ui.screens.settings_screen import (
            _RESOLUTIONS,
            _available_screens,
            _screen_label,
            _TEXT_SIZE_OPTIONS,
            normalize_text_size,
        )

        self.gs = getattr(getattr(v, "_return_view", None), "game_state", None)
        self.start(v, self.word("PARAMÈTRES SYSTÈME", "SYSTEM SETTINGS"))
        s = v._settings
        u = self.u
        left, center, right = self.layout.columns
        self.panel(left, self.word("AFFICHAGE", "DISPLAY"), "layers")
        self.panel(
            center,
            self.word("ACCESSIBILITÉ / AUDIO", "ACCESSIBILITY / AUDIO"),
            "settings",
        )
        self.panel(
            right, self.word("COMBAT / COMMANDES", "COMBAT / CONTROLS"), "target"
        )
        screens = _available_screens()
        values = [f"{w} × {h}" for w, h in _RESOLUTIONS]
        y = self.body(left).top
        y = self.cycle(
            self.body(left),
            y,
            self.word("Résolution", "Resolution"),
            values[s.resolution_index % len(values)],
            "res_prev",
            "res_next",
        )
        y = self.cycle(
            self.body(left),
            y,
            self.word("Écran", "Monitor"),
            _screen_label(screens[s.display_index % len(screens)], s.display_index),
            "screen_prev",
            "screen_next",
        )
        y = self.toggle(
            self.body(left),
            y,
            self.word("Plein écran", "Fullscreen"),
            s.fullscreen,
            "toggle_fullscreen",
        )
        y = self.toggle(
            self.body(left),
            y,
            self.word("Grille tactique", "Tactical grid"),
            s.show_grid,
            "toggle_grid",
        )
        y = self.toggle(
            self.body(left),
            y,
            self.word("Contraste élevé", "High contrast"),
            s.high_contrast,
            "toggle_contrast",
        )
        r = self.body(center)
        y = r.top
        y = self.cycle(
            r,
            y,
            self.word("Taille du texte", "Text size"),
            self.word(
                ["Petit", "Moyen", "Grand"][
                    _TEXT_SIZE_OPTIONS.index(normalize_text_size(s.text_size))
                ],
                s.text_size.title(),
            ),
            "text_prev",
            "text_next",
        )
        y = self.toggle(
            r,
            y,
            self.word("Audio activé", "Audio enabled"),
            s.audio_enabled,
            "toggle_audio",
        )
        y = self.toggle(
            r,
            y,
            self.word("Secousses caméra", "Camera shake"),
            s.camera_shake,
            "toggle_shake",
        )
        y = self.toggle(
            r,
            y,
            self.word("Animations réduites", "Reduced motion"),
            s.reduced_motion,
            "toggle_motion",
        )
        self.paragraph(
            self.word(
                "Les changements sont appliqués et enregistrés avec le bouton ci-dessous.",
                "Apply and save commits your display, audio and accessibility preferences.",
            ),
            Rect(r.left, r.bottom, r.right, y - 12 * u),
            17,
            MUTED,
        )
        r = self.body(right)
        self.label(
            "TACTICAL CONTROLS",
            r.left,
            r.top - 15 * u,
            18,
            CYAN,
            bold=True,
            width=r.width,
        )
        shortcuts = self.word(
            "F1–F6   Départements\nD   Jour suivant\nS / L   Sauvegarder / charger\nB   Mission / N   Recrutement\nFLÈCHES   Navigation\nENTRÉE   Confirmer\nÉCHAP   Retour",
            "F1–F6   Departments\nD   Advance day\nS / L   Save / load\nB   Mission / N   Recruitment\nARROWS   Navigation\nENTER   Confirm\nESC   Back",
        )
        self.document(
            "shortcuts", shortcuts, Rect(r.left, r.bottom, r.right, r.top - 41 * u), 18
        )
        self.footer(
            self.word("APPLIQUER ET SAUVEGARDER", "SAVE & APPLY"),
            "save_apply",
            (self.word("RETOUR [ÉCHAP]", "BACK [ESC]"), "back"),
        )
        if v._msg_timer > 0:
            self.label(
                v._message,
                self.layout.footer.left,
                self.layout.footer.top + 40 * u,
                16,
                MINT,
                width=self.layout.footer.width,
            )
        self.end()

    def cycle(self, r, y, label, value, prev, next):
        u = self.u
        box = Rect(r.left, y - 118 * u, r.right, y)
        self.card(box, label)
        self.label(
            value,
            r.left + 48 * u,
            y - 78 * u,
            18,
            GOLD,
            anchor_y="center",
            width=r.width - 96 * u,
        )
        self.action(
            Rect(r.left + 10 * u, y - 100 * u, r.left + 40 * u, y - 57 * u), "‹", prev
        )
        self.action(
            Rect(r.right - 40 * u, y - 100 * u, r.right - 10 * u, y - 57 * u), "›", next
        )
        return y - 130 * u

    def toggle(self, r, y, label, value, action):
        u = self.u
        box = Rect(r.left, y - 73 * u, r.right, y)
        self.paint.panel(box, CYAN)
        self.label(
            label,
            r.left + 13 * u,
            y - 23 * u,
            18,
            TEXT,
            bold=True,
            width=r.width - 26 * u,
        )
        self.action(
            Rect(r.right - 85 * u, y - 63 * u, r.right - 10 * u, y - 35 * u),
            "ON" if value else "OFF",
            action,
            selected=value,
        )
        return y - 85 * u
