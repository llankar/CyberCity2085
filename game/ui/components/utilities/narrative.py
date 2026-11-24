"""Narrative mission presentation; the original resolution state machine is retained."""

from game.ui.components.utilities.shell import UtilityDeck
from game.ui.layouts.world_map_beacons import Rect
from game.ui.theme.visual import CYAN, GOLD, MINT, RED, PURPLE, TEXT, MUTED
from game.ui.portraits import portrait_path_for_character


class NarrativeDeck(UtilityDeck):
    def draw(self, v):
        self.gs = v.game_state
        self.start(
            v,
            v._mission.title.upper(),
            {
                "reading": self.word("TRANSMISSION", "TRANSMISSION"),
                "agent_select": self.word("SÉLECTION", "SELECTION"),
                "result": self.word("RÉSULTAT", "RESULT"),
                "complete": self.word("RAPPORT FINAL", "FINAL REPORT"),
            }[v._state],
            v._bg_tex,
            fractions=(0.57, 0.43),
        )
        u = self.u
        left, right = self.layout.columns
        scene = v._current_scene()
        self.panel(
            left,
            self.word("SITUATION / TRANSMISSION", "SITUATION / TRANSMISSION"),
            "journal",
        )
        r = self.body(left)
        if v._bg_tex:
            self.texture(
                v._bg_tex, Rect(r.left, r.top - r.height * 0.37, r.right, r.top)
            )
        text = scene.text
        title = self.word("OPÉRATEURS", "OPERATIVES")
        if v._state == "agent_select":
            choice = scene.choices[v._pending_choice_idx]
            text += (
                "\n\n"
                + choice.label
                + "\n"
                + f"{choice.skill_check.skill.upper()} / DC {choice.skill_check.difficulty}"
            )
            title = self.word("SÉLECTIONNER UN AGENT", "SELECT OPERATIVE")
        elif v._state == "result" and v._check_result and v._pending_choice:
            from game.text_missions.text_mission_runner import RESULT_LABELS

            result, roll, total, next_id = v._check_result
            nxt = v._mission.scenes.get(next_id)
            text = (
                RESULT_LABELS[result]
                + f"\n\nROLL {roll} / TOTAL {total} / DC {v._pending_choice.skill_check.difficulty}\n\n"
            )
            if nxt:
                text += (
                    nxt.text + f"\n\n₦{nxt.fund_delta:+} / STRESS {nxt.stress_delta:+}"
                )
        elif v._state == "complete":
            text += f'\n\n{scene.outcome.upper() if scene.outcome else ""}\n₦{v._total_funds_earned:+} / STRESS {v._total_stress:+}'
        self.document(
            "scene_" + v._scene_id + "_" + v._state,
            text,
            Rect(r.left, r.bottom, r.right, r.top - r.height * 0.40),
            19,
        )
        self.panel(right, title, "squad")
        r = self.body(right)
        agents = v._deployed_agents()
        selecting = v._state == "agent_select"
        selected = v._selected_agent_idx if selecting else v._preselected_agent_idx
        choices = scene.choices
        skill = (
            choices[v._pending_choice_idx].skill_check.skill
            if selecting
            else (choices[0].skill_check.skill if choices else None)
        )
        # Reserve lower region for every choice and its true skill total/difficulty.
        agent_area = (
            Rect(r.left, r.top - r.height * 0.57, r.right, r.top)
            if v._state == "reading"
            else r
        )
        for i, char, card in self.page(
            "narrative_agents",
            agents,
            agent_area,
            116,
            selected=selected if selecting and selected >= 0 else None,
        ):
            self.paint.panel(
                card, GOLD if i == selected else CYAN, selected=i == selected
            )
            self.image(
                portrait_path_for_character(char),
                Rect(
                    card.left + 8 * u,
                    card.bottom + 8 * u,
                    card.left + 91 * u,
                    card.top - 8 * u,
                ),
            )
            x = card.left + 105 * u
            self.label(
                char.name.upper(),
                x,
                card.top - 22 * u,
                22,
                TEXT,
                bold=True,
                width=card.right - x - 12 * u,
            )
            self.label(
                str(getattr(char, "role", "")).upper(),
                x,
                card.top - 50 * u,
                15,
                CYAN,
                width=card.right - x - 12 * u,
            )
            if skill:
                from game.ui.screens.text_mission_view import _agent_skill_breakdown

                attr, attr_val, rank, total = _agent_skill_breakdown(char, skill)
                self.label(
                    f"{skill.upper()}  {attr.upper()} {attr_val} + {rank} = {total}",
                    x,
                    card.bottom + 25 * u,
                    15,
                    GOLD,
                    width=card.right - x - 12 * u,
                )
            self.hit(card, "select_agent" if selecting else "preselect_agent", i)
        if v._state == "reading":
            from game.text_missions.text_mission_runner import best_skill_agent
            from game.ui.screens.text_mission_view import _agent_skill_total

            area = Rect(r.left, r.bottom, r.right, agent_area.bottom - 13 * u)
            for i, choice, card in self.page("narrative_choices", choices, area, 91):
                chk = choice.skill_check
                name, best = best_skill_agent(agents, chk.skill)
                if 0 <= selected < len(agents):
                    name = agents[selected].name
                    best = _agent_skill_total(agents[selected], chk.skill)
                self.card(
                    card,
                    choice.label,
                    f"{chk.skill.upper()} {best} / DC {chk.difficulty}",
                    action="choose",
                    data=i,
                    color=GOLD,
                    tooltip=f"{choice.label} / {name}: {best} vs {chk.difficulty}",
                )
            self.footer(
                self.word("SÉLECTIONNER UNE OPTION CI-DESSUS", "SELECT A CHOICE ABOVE"),
                "ui_disabled",
                secondary=(self.word("ABANDONNER [ÉCHAP]", "ABORT [ESC]"), "abort"),
            )
        elif selecting:
            self.footer(
                self.word("CONFIRMER L’AGENT [ENTRÉE]", "ROLL WITH OPERATIVE [ENTER]"),
                "confirm_agent",
                secondary=(
                    self.word("RETOUR AUX CHOIX", "BACK TO CHOICES"),
                    "cancel_agent",
                ),
            )
        elif v._state == "result":
            self.footer(self.word("CONTINUER", "CONTINUE"), "continue_result")
            v._hits[-1].data = v._check_result[3]
        else:
            self.footer(self.word("RETOUR À LA BASE", "RETURN TO BASE"), "return_base")
        self.end()
