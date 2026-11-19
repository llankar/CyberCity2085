"""Recruitment overlay: real portraits, full candidate dossiers, shared actions."""

import arcade
from game.ui.components.utilities.shell import UtilityDeck
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, TEXT, MUTED


class RecruitmentDeck(UtilityDeck):
    def draw(self, v, w, h):
        self.gs = v.game_state
        original = v._hits
        self.start(
            v,
            self.word("RECRUTEMENT / DOSSIERS", "RECRUITMENT / DOSSIERS"),
            f"¥{v.game_state.available_funds:,}",
            fractions=(0.32, 0.68),
        )
        u = self.u
        left, right = self.layout.columns
        self.panel(
            left, self.word("CANDIDATS DISPONIBLES", "AVAILABLE CANDIDATES"), "squad"
        )
        area = self.body(left)
        rows = v.pending_recruit_candidates
        selected = min(self.selection.get("candidate", 0), len(rows) - 1)
        for i, c, r in self.page("candidates", rows, area, 106, selected=None):
            self.paint.panel(r, GOLD if i == selected else CYAN, selected=i == selected)
            self.image(
                c.portrait_path,
                Rect(r.left + 8 * u, r.bottom + 8 * u, r.left + 86 * u, r.top - 8 * u),
            )
            self.label(
                c.name.upper(),
                r.left + 99 * u,
                r.top - 25 * u,
                20,
                TEXT,
                bold=True,
                width=r.width - 112 * u,
            )
            self.label(
                c.role.upper(),
                r.left + 99 * u,
                r.top - 52 * u,
                15,
                CYAN,
                width=r.width - 112 * u,
            )
            self.label(
                f"¥{c.price}", r.left + 99 * u, r.bottom + 21 * u, 21, GOLD, bold=True
            )
            self.hit(r, "recruit_preview", i, c.background)
        self.panel(right, self.word("DOSSIER OPÉRATIF", "OPERATIVE DOSSIER"), "journal")
        r = self.body(right)
        if selected >= 0:
            c = rows[selected]
            art = Rect(r.left, r.bottom + 75 * u, r.left + r.width * 0.38, r.top)
            self.image(c.portrait_path, art)
            x = art.right + 24 * u
            self.label(
                c.name.upper(),
                x,
                r.top - 23 * u,
                32,
                GOLD,
                bold=True,
                width=r.right - x,
            )
            self.label(
                c.role.upper(),
                x,
                r.top - 64 * u,
                23,
                CYAN,
                bold=True,
                width=r.right - x,
            )
            text = "\n\n".join(
                [
                    c.function,
                    c.stat_line(),
                    c.skill_line(),
                    c.background,
                    self.word("AVANTAGES", "ADVANTAGES")
                    + "\n"
                    + " / ".join(c.advantages),
                ]
            )
            self.document(
                "candidate_detail",
                text,
                Rect(x, r.bottom + 75 * u, r.right, r.top - 99 * u),
                18,
            )
            self.action(
                Rect(r.left, r.bottom, r.right, r.bottom + 52 * u),
                self.word("RECRUTER", "HIRE") + f"  ¥{c.price}",
                "recruit_candidate",
                selected,
                enabled=v.game_state.available_funds >= c.price,
                primary=True,
            )
        self.footer(
            self.word("ACTUALISER [N]", "REFRESH [N]"),
            "recruit_prompt",
            (self.word("FERMER [ÉCHAP]", "CLOSE [ESC]"), "recruit_close"),
        )
        self.end()
        v._modal_hits = list(v._hits)
        v._hits = original
