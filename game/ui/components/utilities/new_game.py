"""Campaign setup presentation; original input and campaign creation retained."""

from game.ui.components.utilities.shell import UtilityDeck
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, TEXT, MUTED


class NewGameDeck(UtilityDeck):
    def draw(self, v):
        from game.ui.new_game_options import DIFFICULTY_LABELS

        self.start(
            v,
            self.word("NOUVELLE CAMPAGNE", "NEW CAMPAIGN"),
            self.word("INITIALISATION DU COMMANDEMENT", "COMMAND INITIALIZATION"),
            fractions=(0.36, 0.64),
        )
        u = self.u
        left, right = self.layout.columns
        self.paint.panel(left, CYAN)
        self.image(
            "assets/ui/title/city_visual_2.png",
            Rect(
                left.left + 5 * u,
                left.bottom + 5 * u,
                left.right - 5 * u,
                left.top - 5 * u,
            ),
        )
        self.badge(
            "COVERT OPERATIONS COMMAND",
            Rect(
                left.left + 16 * u,
                left.bottom + 18 * u,
                left.right - 16 * u,
                left.bottom + 58 * u,
            ),
            CYAN,
        )
        self.panel(
            right,
            self.word("IDENTITÉ DE LA CORPORATION", "CORPORATE IDENTITY"),
            "squad",
        )
        r = self.body(right)
        for i, (label, value) in enumerate(
            [
                (self.word("CORPORATION", "CORPORATION"), v._corp),
                (self.word("VILLE", "CITY"), v._city),
            ]
        ):
            top = r.top - i * 135 * u
            self.label(label, r.left, top - 14 * u, 18, CYAN, bold=True)
            box = Rect(r.left, top - 102 * u, r.right, top - 39 * u)
            self.paint.panel(
                box, GOLD if v._focus == i else CYAN, selected=v._focus == i
            )
            cursor = "_" if v._focus == i and int(v._elapsed * 2) % 2 == 0 else ""
            self.label(
                value + cursor,
                box.left + 18 * u,
                box.center[1],
                28,
                TEXT,
                width=box.width - 36 * u,
            )
            bounds = (box.left, box.bottom, box.right, box.top)
            if i == 0:
                v._hit_corp = bounds
            else:
                v._hit_city = bounds
        y = r.top - 293 * u
        self.label(
            self.word("DIFFICULTÉ", "DIFFICULTY"), r.left, y, 20, CYAN, bold=True
        )
        width = (r.width - 20 * u) / 3
        v._hit_diffs = []
        for i, (label, description, _) in enumerate(DIFFICULTY_LABELS):
            box = Rect(
                r.left + i * (width + 10 * u),
                y - 177 * u,
                r.left + i * (width + 10 * u) + width,
                y - 25 * u,
            )
            self.card(
                box, label, selected=v._diff == i, color=GOLD if v._diff == i else CYAN
            )
            self.paragraph(
                description,
                Rect(
                    box.left + 14 * u,
                    box.bottom + 12 * u,
                    box.right - 14 * u,
                    box.top - 48 * u,
                ),
                16,
                MUTED,
            )
            v._hit_diffs.append((box.left, box.bottom, box.right, box.top))
        self.footer(
            self.word("LANCER LA CAMPAGNE [ENTRÉE]", "START CAMPAIGN [ENTER]"), "start"
        )
        hit = v._hits[-1]
        v._hit_start = (hit.left, hit.bottom, hit.right, hit.top)
        self.end()
