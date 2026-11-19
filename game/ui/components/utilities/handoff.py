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
            right, self.word("ÉTAT DE LA MISSION", "MISSION STATUS"), "target"
        )
        r = self.body(right)
        items = [
            (self.word("RÉESSAYER [R]", "RETRY [R]"), arcade.key.R),
            (self.word("CHOISIR GODOT [G]", "CHOOSE GODOT [G]"), arcade.key.G),
            (self.word("COMBAT ARCADE [F]", "ARCADE COMBAT [F]"), arcade.key.F),
        ]
        if not v._launch_failed:
            items.clear()
        record=getattr(v.game_state,"combat_sessions",{}).get(getattr(getattr(v,"launch_result",None),"session_id",""),{})
        from pathlib import Path
        channels=record.get("session",{})
        recoverable=any(Path(channels[key]).is_file() for key in ["result_path","prepared_path"] if channels.get(key))
        if v._launch_failed and not recoverable and channels.get("snapshot_path") and Path(channels["snapshot_path"]).is_file():
            items.insert(0,(self.word("REPRENDRE LE COMBAT [S]", "RESUME COMBAT [S]"),arcade.key.S))
        self.document(
            "handoff_status",
            v.mission.title + "\n\n" + v._status,
            Rect(r.left, r.bottom + (len(items)*60+20) * u, r.right, r.top),
            23,
        )
        for i, (label, key) in enumerate(items):
            bottom = r.bottom + (len(items)-1-i) * 60 * u
            self.action(
                Rect(r.left, bottom, r.right, bottom + 46 * u),
                label,
                "handoff_key",
                key,
                enabled=v._launch_failed,
                primary=i == 0,
            )
        if v._launch_failed:
            self.footer(self.word("RETOUR [ÉCHAP]", "BACK [ESC]"), "handoff_key")
            v._hits[-1].data = arcade.key.ESCAPE
        self.end()
