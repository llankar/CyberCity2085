"""Combat handoff and recovery panel, sharing the utility shell."""

import arcade
from game.ui.components.utilities.shell import UtilityDeck
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, RED, TEXT


class HandoffDeck(UtilityDeck):
    def draw(self, v):
        self.gs = v.game_state
        title = (
            self.word("COMBAT / LIAISON INTERROMPUE", "COMBAT / CONNECTION INTERRUPTED")
            if v._launch_failed
            else self.word("DÉPLOIEMENT EN COURS", "DEPLOYMENT IN PROGRESS")
        )
        self.start(v, title, v.mission.title, fractions=(0.45, 0.55))
        left, right = self.layout.columns
        u = self.u
        self.paint.panel(left, CYAN)
        from game.ui.components.squad_mission import mission_art_path

        self.image(
            mission_art_path(v.mission),
            Rect(
                left.left + 5 * u,
                left.bottom + 5 * u,
                left.right - 5 * u,
                left.top - 5 * u,
            ),
        )
        self.panel(
            right, self.word("CENTRE DE DÉPLOIEMENT", "DEPLOYMENT CONTROL"), "target"
        )
        r = self.body(right)
        self.document(
            "handoff_status",
            v.mission.title + "\n\n" + v._status,
            Rect(r.left, r.bottom + 245 * u, r.right, r.top),
            23,
        )
        items = [
            (self.word("RÉESSAYER [R]", "RETRY [R]"), arcade.key.R),
            (self.word("CHOISIR GODOT [G]", "CHOOSE GODOT [G]"), arcade.key.G),
            (self.word("COMBAT ARCADE [F]", "ARCADE COMBAT [F]"), arcade.key.F),
        ]
        for i, (label, key) in enumerate(items):
            bottom = r.bottom + (2 - i) * 67 * u
            self.action(
                Rect(r.left, bottom, r.right, bottom + 51 * u),
                label,
                "handoff_key",
                key,
                enabled=v._launch_failed,
                primary=i == 0,
            )
        self.footer(self.word("RETOUR [ÉCHAP]", "BACK [ESC]"), "handoff_key")
        v._hits[-1].data = arcade.key.ESCAPE
        self.end()
