"""Full-screen narrative text mission UI.

Layout (all coordinates in screen pixels, origin bottom-left):
  Header bar     : top 44px  — mission title, scene progress, ESC hint
  Background     : full screen, dimmed to ~55% so text panel is readable
  Narrative panel: left ~62% of width, most of the height
  Agent panel    : right ~35%, same height
  Choice bar     : bottom 90px — two side-by-side choice buttons

States: "reading" → "result" → "reading" (loop) | "complete"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import arcade

from game.agents.sheet_calculations import skill_total
from game.deployment import selected_deployable_agents
from game.text_missions.text_mission_runner import (
    RESULT_COLORS,
    RESULT_LABELS,
    best_skill_agent,
    resolve_skill_check,
)
from game.ui import GameView
from game.ui.panels import _load_texture_once
from game.ui.theme.colors import colors

if TYPE_CHECKING:
    from game.text_missions.text_mission_template import (
        MissionScene,
        SceneChoice,
        TextMissionTemplate,
    )


@dataclass(frozen=True)
class _Hit:
    left: int
    bottom: int
    right: int
    top: int
    action: str
    data: object = None

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x <= self.right and self.bottom <= y <= self.top


# Maps skill key → the primary attribute used in the total formula.
_SKILL_ATTR: dict[str, str] = {
    "firearms": "agi",
    "melee": "str",
    "stealth": "agi",
    "hacking": "psi",
    "medicine": "con",
    "persuasion": "cha",
    "intimidation": "str",
    "electronics": "psi",
    "piloting": "agi",
    "explosives": "str",
    "leadership": "cha",
    "survival": "con",
}


def _agent_skill_total(char, skill_key: str) -> int:
    """Return the numeric skill total for one agent on the given skill."""
    attrs = {
        "level": int(getattr(char.stats, "level", 1)),
        "str": int(getattr(char.stats, "str", 1)),
        "agi": int(getattr(char.stats, "agi", 1)),
        "con": int(getattr(char.stats, "con", 1)),
        "cha": int(getattr(char.stats, "cha", 1)),
        "psi": int(getattr(char.stats, "psi", 1)),
    }
    return skill_total(skill_key, attrs, char.skills, {})


def _agent_skill_breakdown(char, skill_key: str) -> tuple[str, int, int, int]:
    """Return (attr_key, attr_val, rank, total) for display in agent cards."""
    attr_key = _SKILL_ATTR.get(skill_key, "agi")
    attr_val = int(getattr(char.stats, attr_key, 1))
    total = _agent_skill_total(char, skill_key)
    rank = max(0, total - attr_val)
    return attr_key, attr_val, rank, total


class TextMissionView(GameView):
    """Arcade view for a narrative text mission."""

    HEADER_H = 44
    CHOICE_BAR_H = 92
    PANEL_MARGIN = 16
    NARRATIVE_FRAC = 0.62  # left panel fraction of screen width

    def __init__(self, game_state, mission: "TextMissionTemplate") -> None:
        super().__init__(game_state)
        self._mission = mission
        self._bg_tex: arcade.Texture | None = None
        self._portrait_cache: dict[str, arcade.Texture | None] = {}

        # State machine: "reading" | "agent_select" | "result" | "complete"
        self._state = "reading"
        self._scene_id = mission.opening_scene_id
        self._pending_choice: "SceneChoice | None" = None
        self._pending_choice_idx: int = -1  # which choice triggered agent_select
        self._selected_agent_idx: int = 0  # highlighted agent in agent_select screen
        self._preselected_agent_idx: int = (
            -1
        )  # agent clicked in reading panel (-1 = none)
        # After resolve: ("great"|"success"|"partial"|"failure", roll, total, scene_id)
        self._check_result: tuple[str, int, int, str] | None = None
        self._total_funds_earned = 0
        self._total_stress = 0
        self._hits: list[_Hit] = []
        self._hover_choice_idx: int = -1  # for right-panel skill preview

    # ── Arcade lifecycle ───────────────────────────────────────────────────────

    def on_show_view(self) -> None:
        arcade.set_background_color((8, 14, 20))
        self._bg_tex = _load_texture_once(self._mission.background_path())

    def on_update(self, dt):
        self._elapsed = getattr(self, "_elapsed", 0.0) + dt
        if hasattr(self, "_visual_deck"):
            self._visual_deck.update(dt)

    def on_draw(self):
        self.clear()
        if not hasattr(self, "_visual_deck"):
            from game.ui.components.utilities.narrative import NarrativeDeck

            self._visual_deck = NarrativeDeck()
        self._elapsed = getattr(self, "_elapsed", 0.0)
        self._visual_deck.draw(self)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        xi, yi = int(x), int(y)
        for hit in self._hits:
            if hit.contains(xi, yi):
                self._handle(hit.action, hit.data)
                return

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        if hasattr(self, "_visual_deck"):
            self._visual_deck.motion(x, y)
        self._hover_choice_idx = -1
        for i, hit in enumerate(h for h in self._hits if h.action == "choose"):
            if hit.contains(int(x), int(y)):
                self._hover_choice_idx = i

    def on_key_press(self, key: int, _modifiers: int) -> None:
        if hasattr(self, "_visual_deck") and key in (arcade.key.TAB, arcade.key.SPACE):
            result = self._visual_deck.keyboard(key)
            if result and result is not True:
                self._handle(result.action, result.data)
            return
        if self._state == "agent_select":
            agents = self._deployed_agents()
            if key == arcade.key.ESCAPE:
                self._state = "reading"
                self._pending_choice_idx = -1
            elif key in (arcade.key.UP, arcade.key.W):
                self._selected_agent_idx = max(0, self._selected_agent_idx - 1)
            elif key in (arcade.key.DOWN, arcade.key.S):
                self._selected_agent_idx = min(
                    len(agents) - 1, self._selected_agent_idx + 1
                )
            elif key in (arcade.key.ENTER, arcade.key.RETURN):
                self._on_choose_confirm()
            return
        if key == arcade.key.ESCAPE:
            self._abort()

    # ── Drawing helpers ────────────────────────────────────────────────────────

    # ── READING STATE ──────────────────────────────────────────────────────────

    # ── AGENT SELECTION STATE ──────────────────────────────────────────────────

    # ── RESULT STATE ───────────────────────────────────────────────────────────

    # ── COMPLETE STATE ─────────────────────────────────────────────────────────

    # ── Action handling ────────────────────────────────────────────────────────

    def _handle(self, action: str, data: object) -> None:
        if action == "ui_disabled":
            return
        if action == "abort":
            self._abort()
            return
        if action == "department_page":
            name, step = data
            if name == "narrative_agents" and self._state == "agent_select":
                pages, capacity, _ = self._visual_deck.capacities[name]
                page = (self._visual_deck.pages.get(name, 0) + step) % pages
                self._selected_agent_idx = min(
                    page * capacity, max(0, len(self._deployed_agents()) - 1)
                )
            else:
                self._visual_deck.turn_page(name, step)
            return
        if action == "choose":
            self._on_choose_begin(int(data))  # type: ignore[arg-type]
        elif action == "preselect_agent":
            idx = int(data)  # type: ignore[arg-type]
            # Toggle: clicking the already-assigned agent deselects
            self._preselected_agent_idx = (
                idx if idx != self._preselected_agent_idx else -1
            )
        elif action == "select_agent":
            self._selected_agent_idx = int(data)  # type: ignore[arg-type]
        elif action == "confirm_agent":
            self._on_choose_confirm()
        elif action == "cancel_agent":
            self._state = "reading"
            self._pending_choice_idx = -1
        elif action == "continue_result":
            self._on_continue_result(str(data))
        elif action == "return_base":
            self._on_return()

    def _on_choose_begin(self, choice_idx: int) -> None:
        """Transition to agent selection for the given choice."""
        scene = self._current_scene()
        if 0 <= choice_idx < len(scene.choices):
            self._pending_choice_idx = choice_idx
            agents = self._deployed_agents()
            if self._preselected_agent_idx >= 0 and self._preselected_agent_idx < len(
                agents
            ):
                self._selected_agent_idx = self._preselected_agent_idx
            else:
                self._selected_agent_idx = 0
            self._state = "agent_select"

    def _on_choose_confirm(self) -> None:
        """Roll with the currently selected agent and transition to result."""
        scene = self._current_scene()
        if self._pending_choice_idx < 0 or self._pending_choice_idx >= len(
            scene.choices
        ):
            return
        choice = scene.choices[self._pending_choice_idx]
        chk = choice.skill_check
        agents = self._deployed_agents()
        if not agents:
            return
        idx = min(self._selected_agent_idx, len(agents) - 1)
        char = agents[idx]
        total = _agent_skill_total(char, chk.skill)
        result_key, roll, total_roll = resolve_skill_check(total, chk.difficulty)

        if result_key == "great":
            next_sid = choice.great_scene or choice.success_scene
        elif result_key == "success":
            next_sid = choice.success_scene
        elif result_key == "partial":
            next_sid = choice.partial_scene or choice.failure_scene
        else:
            next_sid = choice.failure_scene
        next_scene = self._mission.scenes.get(next_sid)
        if next_scene:
            self._total_funds_earned += next_scene.fund_delta
            self._total_stress += next_scene.stress_delta

        self._pending_choice = choice
        self._check_result = (result_key, roll, total_roll, next_sid)
        self._state = "result"

    def _on_continue_result(self, next_scene_id: str) -> None:
        next_scene = self._mission.scenes.get(next_scene_id)
        if next_scene is None:
            self._on_return()
            return
        self._scene_id = next_scene_id
        if next_scene.outcome != "none":
            self._apply_consequences(next_scene)
            self._state = "complete"
        else:
            self._state = "reading"
        self._check_result = None
        self._pending_choice = None

    def _on_return(self) -> None:
        from game.ui.screens.management_screen import ManagementView

        view = ManagementView(self.game_state)
        view.setup()
        self.window.show_view(view)

    def _abort(self) -> None:
        """Player aborted the mission mid-run — apply partial stress."""
        agents = self._deployed_agents()
        for char in agents:
            char.stress = min(int(getattr(char, "stress", 0)) + 8, 100)
        self.game_state.add_event(
            "Narrative mission aborted — operatives return shaken."
        )
        self._on_return()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _current_scene(self) -> "MissionScene":
        return self._mission.scenes[self._scene_id]

    def _deployed_agents(self):
        return selected_deployable_agents(
            self.game_state.characters,
            self.game_state.selected_agent_names,
        )

    def _apply_consequences(self, scene: "MissionScene") -> None:
        gs = self.game_state
        if self._total_funds_earned > 0:
            gs.spend_funds(
                -self._total_funds_earned,
                "text_mission_reward",
                f"Narrative mission reward: ¥{self._total_funds_earned}",
            )
        elif self._total_funds_earned < 0:
            gs.spend_funds(
                abs(self._total_funds_earned),
                "text_mission_loss",
                f"Narrative mission loss: ¥{abs(self._total_funds_earned)}",
            )
        for char in self._deployed_agents():
            char.stress = min(int(getattr(char, "stress", 0)) + self._total_stress, 100)
        outcome = scene.outcome
        gs.add_event(
            f"Narrative mission '{self._mission.title}': {outcome.upper()}"
            + (f"  ¥{self._total_funds_earned}" if self._total_funds_earned else "")
        )
