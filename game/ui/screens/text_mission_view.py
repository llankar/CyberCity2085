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
from game.ui import palette
from game.ui.panels import _load_texture_once

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


def _rect(l: int, b: int, r: int, t: int, col) -> None:
    arcade.draw_lrbt_rectangle_filled(l, r, b, t, col)


def _outline(l: int, b: int, r: int, t: int, col, w: int = 2) -> None:
    arcade.draw_lrbt_rectangle_outline(l, r, b, t, col, w)


# Maps skill key → the primary attribute used in the total formula.
_SKILL_ATTR: dict[str, str] = {
    "firearms":     "agi",
    "melee":        "str",
    "stealth":      "agi",
    "hacking":      "psi",
    "medicine":     "con",
    "persuasion":   "cha",
    "intimidation": "str",
    "electronics":  "psi",
    "piloting":     "agi",
    "explosives":   "str",
    "leadership":   "cha",
    "survival":     "con",
}


def _agent_skill_total(char, skill_key: str) -> int:
    """Return the numeric skill total for one agent on the given skill."""
    attrs = {
        "level": int(getattr(char.stats, "level", 1)),
        "str":   int(getattr(char.stats, "str",   1)),
        "agi":   int(getattr(char.stats, "agi",   1)),
        "con":   int(getattr(char.stats, "con",   1)),
        "cha":   int(getattr(char.stats, "cha",   1)),
        "psi":   int(getattr(char.stats, "psi",   1)),
    }
    return skill_total(skill_key, attrs, char.skills, {})


def _agent_skill_breakdown(char, skill_key: str) -> tuple[str, int, int, int]:
    """Return (attr_key, attr_val, rank, total) for display in agent cards."""
    attr_key = _SKILL_ATTR.get(skill_key, "agi")
    attr_val = int(getattr(char.stats, attr_key, 1))
    total = _agent_skill_total(char, skill_key)
    rank = max(0, total - attr_val)
    return attr_key, attr_val, rank, total


def _wrap_lines(text: str, max_chars: int) -> list[str]:
    """Word-wrap text at word boundaries to avoid mid-word breaks."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > max_chars:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        lines.append(current)
    return lines


class TextMissionView(GameView):
    """Arcade view for a narrative text mission."""

    HEADER_H = 44
    CHOICE_BAR_H = 92
    PANEL_MARGIN = 16
    NARRATIVE_FRAC = 0.62   # left panel fraction of screen width

    def __init__(self, game_state, mission: "TextMissionTemplate") -> None:
        super().__init__(game_state)
        self._mission = mission
        self._bg_tex: arcade.Texture | None = None
        self._portrait_cache: dict[str, arcade.Texture | None] = {}

        # State machine: "reading" | "agent_select" | "result" | "complete"
        self._state = "reading"
        self._scene_id = mission.opening_scene_id
        self._pending_choice: "SceneChoice | None" = None
        self._pending_choice_idx: int = -1    # which choice triggered agent_select
        self._selected_agent_idx: int = 0     # highlighted agent in agent_select screen
        self._preselected_agent_idx: int = -1  # agent clicked in reading panel (-1 = none)
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

    def on_draw(self) -> None:
        self.clear()
        w, h = self.window.width, self.window.height
        self._hits = []

        self._draw_background(w, h)
        if self._state == "reading":
            self._draw_reading(w, h)
        elif self._state == "agent_select":
            self._draw_agent_select(w, h)
        elif self._state == "result":
            self._draw_result(w, h)
        elif self._state == "complete":
            self._draw_complete(w, h)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        xi, yi = int(x), int(y)
        for hit in self._hits:
            if hit.contains(xi, yi):
                self._handle(hit.action, hit.data)
                return

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        self._hover_choice_idx = -1
        for i, hit in enumerate(h for h in self._hits if h.action == "choose"):
            if hit.contains(int(x), int(y)):
                self._hover_choice_idx = i

    def on_key_press(self, key: int, _modifiers: int) -> None:
        if self._state == "agent_select":
            agents = self._deployed_agents()
            if key == arcade.key.ESCAPE:
                self._state = "reading"
                self._pending_choice_idx = -1
            elif key in (arcade.key.UP, arcade.key.W):
                self._selected_agent_idx = max(0, self._selected_agent_idx - 1)
            elif key in (arcade.key.DOWN, arcade.key.S):
                self._selected_agent_idx = min(len(agents) - 1, self._selected_agent_idx + 1)
            elif key in (arcade.key.ENTER, arcade.key.RETURN):
                self._on_choose_confirm()
            return
        if key == arcade.key.ESCAPE:
            self._abort()

    # ── Drawing helpers ────────────────────────────────────────────────────────

    def _draw_background(self, w: int, h: int) -> None:
        """Full-screen scene image, heavily dimmed so the text panel is readable."""
        if self._bg_tex is not None:
            try:
                scale = max(w / self._bg_tex.width, h / self._bg_tex.height)
                dw = self._bg_tex.width * scale
                dh = self._bg_tex.height * scale
                bx = (w - dw) / 2
                by = (h - dh) / 2
                rect = getattr(arcade, "LBWH", None)
                if rect:
                    arcade.draw_texture_rect(
                        self._bg_tex,
                        arcade.LBWH(bx, by, dw, dh),
                        alpha=130,
                    )
                else:
                    arcade.draw_texture_rect(self._bg_tex, arcade.LBWH(bx, by, dw, dh))
            except Exception:
                _rect(0, 0, w, h, (8, 14, 20, 255))
        else:
            _rect(0, 0, w, h, (8, 14, 20, 255))
        # Dark gradient overlay
        _rect(0, 0, w, h, (0, 0, 0, 100))

    def _draw_header(self, w: int, h: int, scene: "MissionScene") -> None:
        hb = h - self.HEADER_H
        _rect(0, hb, w, h, (4, 10, 16, 240))
        arcade.draw_line(0, hb, w, hb, palette.ACCENT, 2)
        arcade.draw_text(
            self._mission.title.upper(),
            self.PANEL_MARGIN + 4, h - self.HEADER_H // 2,
            palette.HEADER, font_size=13, bold=True, anchor_y="center",
        )
        mission_type = "NARRATIVE MISSION"
        arcade.draw_text(
            f"{mission_type}  ·  RISK {self._mission.risk_level}  ·  ¥{self._mission.fund_reward} REWARD",
            w - self.PANEL_MARGIN,
            h - self.HEADER_H // 2,
            palette.MUTED_TEXT, font_size=9, anchor_x="right", anchor_y="center",
        )
        arcade.draw_text(
            "ESC = ABORT",
            w // 2, h - self.HEADER_H // 2,
            palette.PANEL_BORDER_MUTED, font_size=8, anchor_x="center", anchor_y="center",
        )

    def _layout(self, w: int, h: int) -> tuple[int, int, int, int, int, int, int, int]:
        """Return (narr_l, narr_b, narr_r, narr_t, agent_l, agent_b, agent_r, agent_t)."""
        m = self.PANEL_MARGIN
        narr_l = m
        narr_r = int(w * self.NARRATIVE_FRAC) - m // 2
        agent_l = int(w * self.NARRATIVE_FRAC) + m // 2
        agent_r = w - m
        bottom = self.CHOICE_BAR_H + m
        top = h - self.HEADER_H - m
        return narr_l, bottom, narr_r, top, agent_l, bottom, agent_r, top

    # ── READING STATE ──────────────────────────────────────────────────────────

    def _draw_reading(self, w: int, h: int) -> None:
        scene = self._current_scene()
        self._draw_header(w, h, scene)

        narr_l, narr_b, narr_r, narr_t, ag_l, ag_b, ag_r, ag_t = self._layout(w, h)
        narr_w = narr_r - narr_l
        ag_w = ag_r - ag_l

        # Narrative panel
        _rect(narr_l, narr_b, narr_r, narr_t, (4, 12, 20, 220))
        _outline(narr_l, narr_b, narr_r, narr_t, palette.PANEL_BORDER)
        self._draw_narrative_text(scene, narr_l + 14, narr_b, narr_r - 14, narr_t)

        # Agent panel
        _rect(ag_l, ag_b, ag_r, ag_t, (4, 10, 16, 215))
        _outline(ag_l, ag_b, ag_r, ag_t, palette.PANEL_BORDER)
        self._draw_agent_panel(scene, ag_l, ag_b, ag_r, ag_t)

        # Choice bar
        self._draw_choice_bar(scene, w, h)

    def _draw_narrative_text(
        self, scene: "MissionScene",
        x0: int, y_bot: int, x1: int, y_top: int,
    ) -> None:
        panel_w = x1 - x0
        # Approximate chars per line: panel_w pixels / 7 px per char at font_size=11
        cpl = max(30, panel_w // 7)

        y = y_top - 18
        lines = _wrap_lines(scene.text, cpl)
        for line in lines:
            if y < y_bot + 14:
                break
            arcade.draw_text(line, x0, y, palette.TEXT, font_size=11)
            y -= 18

    def _draw_agent_panel(
        self,
        scene: "MissionScene",
        l: int, b: int, r: int, t: int,
    ) -> None:
        from game.ui.portraits import portrait_path_for_character

        w = r - l
        x = l + 10
        y = t - 16

        arcade.draw_text("OPERATIVES", x, y, palette.ACCENT, font_size=9, bold=True)
        arcade.draw_line(l + 6, y - 8, r - 6, y - 8, palette.ACCENT, 1)
        y -= 24

        agents = self._deployed_agents()
        portrait_size = min(52, max(36, (w - 20) // max(1, min(4, len(agents)))))
        gap = 8
        px = l + 10
        for i, char in enumerate(agents[:4]):
            pb = y - portrait_size
            if pb < b + 14:
                break
            sel = (i == self._preselected_agent_idx)
            if sel:
                _rect(px - 3, pb - 3, px + portrait_size + 3, pb + portrait_size + 3, (0, 180, 140, 60))
            path = portrait_path_for_character(char)
            if path not in self._portrait_cache:
                self._portrait_cache[path] = _load_texture_once(path) if path else None
            tex = self._portrait_cache.get(path)
            if tex and hasattr(arcade, "LBWH"):
                try:
                    arcade.draw_texture_rect(tex, arcade.LBWH(px, pb, portrait_size, portrait_size))
                except Exception:
                    _rect(px, pb, px + portrait_size, pb + portrait_size, (30, 52, 68, 200))
            else:
                _rect(px, pb, px + portrait_size, pb + portrait_size, (30, 52, 68, 200))
            if sel:
                _outline(px - 2, pb - 2, px + portrait_size + 2, pb + portrait_size + 2, palette.TACTICAL_GREEN, 2)
            arcade.draw_text(
                char.name.split()[0][:8],
                px + portrait_size // 2,
                pb - 12,
                palette.TACTICAL_GREEN if sel else palette.MUTED_TEXT,
                font_size=7, anchor_x="center",
            )
            arcade.draw_text(
                "ASSIGNED" if sel else "click",
                px + portrait_size // 2,
                pb - 22,
                palette.TACTICAL_GREEN if sel else (60, 80, 70, 180),
                font_size=6, anchor_x="center",
            )
            self._hits.append(_Hit(px, pb, px + portrait_size, pb + portrait_size, "preselect_agent", i))
            px += portrait_size + gap
        y -= portrait_size + 24

        # Required skills section
        if scene.choices:
            arcade.draw_text("SKILL CHECKS", x, y, palette.ACCENT, font_size=9, bold=True)
            arcade.draw_line(l + 6, y - 8, r - 6, y - 8, palette.PANEL_BORDER_MUTED, 1)
            y -= 22

            for i, choice in enumerate(scene.choices):
                chk = choice.skill_check
                skill_lbl = chk.skill.replace("_", " ").upper()

                # Show assigned agent's stat if one was selected, otherwise best
                if self._preselected_agent_idx >= 0 and self._preselected_agent_idx < len(agents):
                    display_char = agents[self._preselected_agent_idx]
                    display_name = display_char.name.split()[0][:10]
                    display_val = _agent_skill_total(display_char, chk.skill)
                    stat_prefix = "Assigned"
                else:
                    raw_name, display_val = best_skill_agent(agents, chk.skill)
                    display_name = raw_name.split()[0][:10]
                    stat_prefix = "Best"

                hover = (i == self._hover_choice_idx)
                card_h = 58
                card_b = y - card_h
                if card_b < b + 8:
                    break
                bg = (24, 44, 32, 200) if hover else (14, 26, 36, 200)
                _rect(l + 6, card_b, r - 6, y, bg)
                _outline(l + 6, card_b, r - 6, y, palette.RESOURCE if hover else palette.PANEL_BORDER_MUTED)

                arcade.draw_text(skill_lbl, x, y - 14, palette.RESOURCE, font_size=9, bold=True)
                arcade.draw_text(
                    f"Difficulty  {chk.difficulty}",
                    r - 10, y - 14,
                    palette.MUTED_TEXT, font_size=8, anchor_x="right",
                )
                arcade.draw_text(
                    f"{stat_prefix}: {display_name}  {display_val}",
                    x, y - 30,
                    palette.TACTICAL_GREEN if stat_prefix == "Assigned" else palette.TEXT,
                    font_size=8,
                )
                delta = display_val - chk.difficulty
                if delta >= 2:
                    diff_txt, diff_col = "Likely ✓", palette.TACTICAL_GREEN
                elif delta >= 0:
                    diff_txt, diff_col = "Possible", palette.RESOURCE
                elif delta >= -2:
                    diff_txt, diff_col = "Risky", palette.WARNING
                else:
                    diff_txt, diff_col = "Unlikely ✗", palette.DANGER
                arcade.draw_text(diff_txt, r - 10, y - 30, diff_col, font_size=8, anchor_x="right")
                y -= card_h + 6

    def _draw_choice_bar(self, scene: "MissionScene", w: int, h: int) -> None:
        _rect(0, 0, w, self.CHOICE_BAR_H, (4, 10, 16, 235))
        arcade.draw_line(0, self.CHOICE_BAR_H, w, self.CHOICE_BAR_H, palette.ACCENT, 2)

        choices = scene.choices
        if not choices:
            return
        n = len(choices)
        gap = 12
        btn_w = (w - gap * (n + 1)) // n
        x = gap

        for i, choice in enumerate(choices):
            chk = choice.skill_check
            agents = self._deployed_agents()
            if self._preselected_agent_idx >= 0 and self._preselected_agent_idx < len(agents):
                best = _agent_skill_total(agents[self._preselected_agent_idx], chk.skill)
            else:
                _, best = best_skill_agent(agents, chk.skill)
            hover = (i == self._hover_choice_idx)

            btn_l = x
            btn_r = x + btn_w
            btn_b = 8
            btn_t = self.CHOICE_BAR_H - 8

            bg = (26, 54, 38, 240) if hover else (12, 28, 22, 235)
            border = palette.TACTICAL_GREEN if hover else palette.RESOURCE
            _rect(btn_l, btn_b, btn_r, btn_t, bg)
            arcade.draw_line(btn_l, btn_t, btn_r, btn_t, border, 2)
            arcade.draw_line(btn_l, btn_b, btn_r, btn_b, border, 1)

            center_x = (btn_l + btn_r) // 2
            center_y = (btn_b + btn_t) // 2

            arcade.draw_text(
                choice.label.upper(),
                center_x, center_y + 12,
                palette.TEXT, font_size=11, bold=True,
                anchor_x="center", anchor_y="center",
            )
            skill_lbl = chk.skill.replace("_", " ").upper()
            arcade.draw_text(
                f"{skill_lbl}  {best}  vs  {chk.difficulty}",
                center_x, center_y - 10,
                palette.RESOURCE, font_size=8,
                anchor_x="center", anchor_y="center",
            )

            self._hits.append(_Hit(btn_l, btn_b, btn_r, btn_t, "choose", i))
            x += btn_w + gap

    # ── AGENT SELECTION STATE ──────────────────────────────────────────────────

    def _draw_agent_select(self, w: int, h: int) -> None:
        """Full-screen operative picker shown after the player clicks a choice."""
        from game.ui.portraits import portrait_path_for_character

        scene = self._current_scene()
        if self._pending_choice_idx < 0 or self._pending_choice_idx >= len(scene.choices):
            self._state = "reading"
            return
        choice = scene.choices[self._pending_choice_idx]
        chk = choice.skill_check

        # Header
        hb = h - self.HEADER_H
        _rect(0, hb, w, h, (4, 10, 16, 245))
        arcade.draw_line(0, hb, w, hb, palette.ACCENT, 2)
        arcade.draw_text(
            self._mission.title.upper(),
            self.PANEL_MARGIN + 4, h - self.HEADER_H // 2,
            palette.HEADER, font_size=13, bold=True, anchor_y="center",
        )
        arcade.draw_text(
            "CHOOSE OPERATIVE  ·  ESC = BACK",
            w - self.PANEL_MARGIN, h - self.HEADER_H // 2,
            palette.MUTED_TEXT, font_size=9, anchor_x="right", anchor_y="center",
        )

        # Bottom action bar
        bar_h = 72
        _rect(0, 0, w, bar_h, (4, 10, 16, 240))
        arcade.draw_line(0, bar_h, w, bar_h, palette.ACCENT, 2)

        gap = 16
        btn_w = (w - gap * 3) // 2
        # CONFIRM button
        cl, cr = gap, gap + btn_w
        cb, ct = 10, bar_h - 10
        _rect(cl, cb, cr, ct, (18, 44, 28, 240))
        arcade.draw_line(cl, ct, cr, ct, palette.TACTICAL_GREEN, 2)
        arcade.draw_text(
            "ROLL WITH OPERATIVE",
            (cl + cr) // 2, (cb + ct) // 2,
            palette.TACTICAL_GREEN, font_size=12, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hits.append(_Hit(cl, cb, cr, ct, "confirm_agent"))

        # CANCEL button
        canc_l = gap * 2 + btn_w
        canc_r = canc_l + btn_w
        _rect(canc_l, cb, canc_r, ct, (28, 16, 16, 240))
        arcade.draw_line(canc_l, ct, canc_r, ct, palette.MUTED_TEXT, 2)
        arcade.draw_text(
            "BACK TO CHOICES",
            (canc_l + canc_r) // 2, (cb + ct) // 2,
            palette.MUTED_TEXT, font_size=12, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hits.append(_Hit(canc_l, cb, canc_r, ct, "cancel_agent"))

        # --- Layout: left 38% = context, right 60% = agent list ---
        m = self.PANEL_MARGIN
        panel_top = h - self.HEADER_H - m
        panel_bot = bar_h + m
        ctx_l, ctx_r = m, int(w * 0.38) - m // 2
        ag_l, ag_r   = int(w * 0.38) + m // 2, w - m

        # Left panel — context
        _rect(ctx_l, panel_bot, ctx_r, panel_top, (4, 12, 20, 220))
        _outline(ctx_l, panel_bot, ctx_r, panel_top, palette.PANEL_BORDER)

        ctx_w = ctx_r - ctx_l
        cpl = max(24, ctx_w // 7)
        y = panel_top - 18
        arcade.draw_text("SITUATION", ctx_l + 10, y, palette.ACCENT, font_size=9, bold=True)
        y -= 20
        for line in _wrap_lines(scene.text, cpl)[:6]:
            if y < panel_bot + 80:
                break
            arcade.draw_text(line, ctx_l + 10, y, palette.MUTED_TEXT, font_size=9)
            y -= 16

        y -= 10
        arcade.draw_line(ctx_l + 8, y, ctx_r - 8, y, palette.PANEL_BORDER_MUTED, 1)
        y -= 20

        arcade.draw_text("YOUR CHOICE", ctx_l + 10, y, palette.ACCENT, font_size=9, bold=True)
        y -= 18
        for line in _wrap_lines(choice.label, cpl):
            if y < panel_bot + 60:
                break
            arcade.draw_text(line, ctx_l + 10, y, palette.TEXT, font_size=10, bold=True)
            y -= 16

        y -= 16
        skill_lbl = chk.skill.replace("_", " ").upper()
        arcade.draw_text(f"SKILL CHECK: {skill_lbl}", ctx_l + 10, y, palette.RESOURCE, font_size=9)
        y -= 16
        arcade.draw_text(f"DIFFICULTY: {chk.difficulty}", ctx_l + 10, y, palette.WARNING, font_size=9)

        # Right panel — agent list
        _rect(ag_l, panel_bot, ag_r, panel_top, (4, 10, 16, 215))
        _outline(ag_l, panel_bot, ag_r, panel_top, palette.PANEL_BORDER)

        y = panel_top - 16
        arcade.draw_text("SELECT OPERATIVE", ag_l + 12, y, palette.HEADER, font_size=10, bold=True)
        arcade.draw_text(
            "↑↓ navigate  ·  Enter confirm",
            ag_r - 12, y, palette.MUTED_TEXT, font_size=8, anchor_x="right",
        )
        y -= 18
        arcade.draw_line(ag_l + 8, y, ag_r - 8, y, palette.ACCENT, 1)
        y -= 14

        agents = self._deployed_agents()
        portrait_sz = 64
        card_h = portrait_sz + 24   # portrait + name row
        card_gap = 10

        for ai, char in enumerate(agents[:4]):
            if y - card_h < panel_bot + 8:
                break
            selected = (ai == self._selected_agent_idx)
            card_b = y - card_h
            card_l = ag_l + 8
            card_r = ag_r - 8

            border_col = palette.TACTICAL_GREEN if selected else palette.PANEL_BORDER_MUTED
            bg_col     = (20, 48, 32, 235) if selected else (10, 22, 32, 220)
            _rect(card_l, card_b, card_r, y, bg_col)
            _outline(card_l, card_b, card_r, y, border_col, 2 if selected else 1)

            # Portrait
            path = portrait_path_for_character(char)
            if path not in self._portrait_cache:
                self._portrait_cache[path] = _load_texture_once(path) if path else None
            tex = self._portrait_cache.get(path)
            port_x = card_l + 8
            port_b = card_b + 12
            if tex and hasattr(arcade, "LBWH"):
                try:
                    arcade.draw_texture_rect(tex, arcade.LBWH(port_x, port_b, portrait_sz, portrait_sz))
                except Exception:
                    _rect(port_x, port_b, port_x + portrait_sz, port_b + portrait_sz, (30, 52, 68, 200))
            else:
                _rect(port_x, port_b, port_x + portrait_sz, port_b + portrait_sz, (30, 52, 68, 200))

            # Stat block to the right of portrait
            info_x = port_x + portrait_sz + 14
            info_y = y - 14

            arcade.draw_text(
                char.name,
                info_x, info_y,
                palette.HEADER if selected else palette.TEXT,
                font_size=11, bold=True,
            )
            role = getattr(char, "role", "") or ""
            if role:
                arcade.draw_text(role.upper(), info_x, info_y - 16, palette.MUTED_TEXT, font_size=8)

            # Skill breakdown
            attr_key, attr_val, rank, total = _agent_skill_breakdown(char, chk.skill)
            info_y -= 34
            arcade.draw_text(
                f"{skill_lbl}:  {attr_key.upper()}({attr_val}) + rank({rank}) = {total}",
                info_x, info_y, palette.RESOURCE, font_size=9,
            )

            # Chance indicator
            delta = total - chk.difficulty
            if delta >= 2:
                diff_txt, diff_col = "LIKELY   (roll 1+ to succeed)", palette.TACTICAL_GREEN
            elif delta >= 0:
                diff_txt, diff_col = "POSSIBLE (roll 0+ to succeed)", palette.RESOURCE
            elif delta >= -2:
                diff_txt, diff_col = "RISKY    (need lucky roll)",      palette.WARNING
            else:
                diff_txt, diff_col = "UNLIKELY (very hard)",            palette.DANGER
            info_y -= 16
            arcade.draw_text(diff_txt, info_x, info_y, diff_col, font_size=9, bold=True)

            # Total vs difficulty summary at far right
            arcade.draw_text(
                f"{total} vs {chk.difficulty}",
                card_r - 12, y - 14,
                diff_col, font_size=11, bold=True, anchor_x="right",
            )

            # Hit region for this card
            self._hits.append(_Hit(card_l, card_b, card_r, y, "select_agent", ai))
            y -= card_h + card_gap

    # ── RESULT STATE ───────────────────────────────────────────────────────────

    def _draw_result(self, w: int, h: int) -> None:
        assert self._check_result is not None
        result_key, roll, total, next_scene_id = self._check_result
        choice = self._pending_choice
        assert choice is not None

        # Dim overlay
        _rect(0, 0, w, h, (0, 0, 0, 160))

        # Result card
        card_w = min(680, w - 80)
        card_h = min(380, h - 120)
        cx = (w - card_w) // 2
        cy = (h - card_h) // 2
        _rect(cx, cy, cx + card_w, cy + card_h, (6, 16, 24, 248))
        result_col = tuple(RESULT_COLORS[result_key]) + (255,)
        arcade.draw_line(cx, cy + card_h, cx + card_w, cy + card_h, result_col, 3)
        _outline(cx, cy, cx + card_w, cy + card_h, palette.PANEL_BORDER)

        y = cy + card_h - 24
        arcade.draw_text(
            RESULT_LABELS[result_key],
            cx + card_w // 2, y,
            result_col, font_size=18, bold=True,
            anchor_x="center",
        )

        y -= 36
        chk = choice.skill_check
        agents = self._deployed_agents()
        agent_name, best = best_skill_agent(agents, chk.skill)
        skill_lbl = chk.skill.replace("_", " ").upper()
        arcade.draw_text(
            f"{agent_name.split()[0]}  ·  {skill_lbl} {best}  +  roll {roll}  =  {total}  vs  {chk.difficulty}",
            cx + card_w // 2, y,
            palette.MUTED_TEXT, font_size=9,
            anchor_x="center",
        )

        y -= 28
        arcade.draw_line(cx + 20, y, cx + card_w - 20, y, palette.PANEL_BORDER_MUTED, 1)
        y -= 16

        # Outcome scene text (outcome of this result)
        next_scene = self._mission.scenes.get(next_scene_id)
        if next_scene:
            panel_w = card_w - 40
            cpl = max(30, panel_w // 7)
            lines = _wrap_lines(next_scene.text, cpl)
            for line in lines[:8]:
                if y < cy + 64:
                    break
                arcade.draw_text(line, cx + 20, y, palette.TEXT, font_size=10)
                y -= 16

            if next_scene.fund_delta:
                y -= 8
                delta_col = palette.TACTICAL_GREEN if next_scene.fund_delta > 0 else palette.DANGER
                arcade.draw_text(
                    f"Reward: ¥{next_scene.fund_delta}" if next_scene.fund_delta > 0 else f"Loss: ¥{abs(next_scene.fund_delta)}",
                    cx + 20, y, delta_col, font_size=9, bold=True,
                )
            if next_scene.stress_delta:
                stress_y = y - (20 if next_scene.fund_delta else 8)
                arcade.draw_text(
                    f"Stress: +{next_scene.stress_delta} per operative",
                    cx + 20, stress_y, palette.WARNING, font_size=9,
                )

        # Continue button
        btn_b = cy + 12
        btn_t = cy + 44
        btn_l = cx + card_w // 2 - 80
        btn_r = cx + card_w // 2 + 80
        _rect(btn_l, btn_b, btn_r, btn_t, (18, 40, 28, 235))
        arcade.draw_line(btn_l, btn_t, btn_r, btn_t, palette.TACTICAL_GREEN, 2)
        arcade.draw_text(
            "CONTINUE",
            (btn_l + btn_r) // 2, (btn_b + btn_t) // 2,
            palette.TACTICAL_GREEN, font_size=11, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hits.append(_Hit(btn_l, btn_b, btn_r, btn_t, "continue_result", next_scene_id))

    # ── COMPLETE STATE ─────────────────────────────────────────────────────────

    def _draw_complete(self, w: int, h: int) -> None:
        scene = self._current_scene()

        _rect(0, 0, w, h, (0, 0, 0, 180))

        card_w = min(600, w - 80)
        card_h = min(340, h - 120)
        cx = (w - card_w) // 2
        cy = (h - card_h) // 2
        _rect(cx, cy, cx + card_w, cy + card_h, (6, 16, 24, 250))

        outcome = scene.outcome
        if outcome == "success":
            title = "MISSION COMPLETE"
            border_col = palette.TACTICAL_GREEN
        elif outcome == "partial":
            title = "PARTIAL SUCCESS"
            border_col = palette.WARNING
        else:
            title = "MISSION FAILED"
            border_col = palette.DANGER

        arcade.draw_line(cx, cy + card_h, cx + card_w, cy + card_h, border_col, 3)
        _outline(cx, cy, cx + card_w, cy + card_h, palette.PANEL_BORDER)

        y = cy + card_h - 24
        arcade.draw_text(
            title,
            cx + card_w // 2, y,
            border_col, font_size=16, bold=True, anchor_x="center",
        )
        y -= 24
        arcade.draw_text(
            self._mission.title.upper(),
            cx + card_w // 2, y,
            palette.TEXT, font_size=11, anchor_x="center",
        )
        y -= 28
        arcade.draw_line(cx + 20, y, cx + card_w - 20, y, palette.PANEL_BORDER_MUTED, 1)
        y -= 18

        if self._total_funds_earned:
            col = palette.TACTICAL_GREEN if self._total_funds_earned > 0 else palette.DANGER
            arcade.draw_text(
                f"EARNED  ¥{self._total_funds_earned}",
                cx + 20, y, col, font_size=11, bold=True,
            )
            y -= 20
        if self._total_stress:
            arcade.draw_text(
                f"STRESS  +{self._total_stress} per operative",
                cx + 20, y, palette.WARNING, font_size=10,
            )
            y -= 20

        y -= 8
        arcade.draw_line(cx + 20, y, cx + card_w - 20, y, palette.PANEL_BORDER_MUTED, 1)
        y -= 18

        agents = self._deployed_agents()
        for char in agents[:4]:
            arcade.draw_text(
                f"{char.name}  —  HP {char.stats.hp}/{char.stats.max_hp}  Stress {char.stress}",
                cx + 20, y, palette.MUTED_TEXT, font_size=8,
            )
            y -= 14

        # Return button
        btn_b = cy + 12
        btn_t = cy + 46
        btn_l = cx + card_w // 2 - 100
        btn_r = cx + card_w // 2 + 100
        _rect(btn_l, btn_b, btn_r, btn_t, (10, 24, 18, 235))
        arcade.draw_line(btn_l, btn_t, btn_r, btn_t, border_col, 2)
        arcade.draw_text(
            "RETURN TO BASE",
            (btn_l + btn_r) // 2, (btn_b + btn_t) // 2,
            border_col, font_size=11, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hits.append(_Hit(btn_l, btn_b, btn_r, btn_t, "return_base"))

    # ── Action handling ────────────────────────────────────────────────────────

    def _handle(self, action: str, data: object) -> None:
        if action == "choose":
            self._on_choose_begin(int(data))  # type: ignore[arg-type]
        elif action == "preselect_agent":
            idx = int(data)  # type: ignore[arg-type]
            # Toggle: clicking the already-assigned agent deselects
            self._preselected_agent_idx = idx if idx != self._preselected_agent_idx else -1
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
            if self._preselected_agent_idx >= 0 and self._preselected_agent_idx < len(agents):
                self._selected_agent_idx = self._preselected_agent_idx
            else:
                self._selected_agent_idx = 0
            self._state = "agent_select"

    def _on_choose_confirm(self) -> None:
        """Roll with the currently selected agent and transition to result."""
        scene = self._current_scene()
        if self._pending_choice_idx < 0 or self._pending_choice_idx >= len(scene.choices):
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

        next_sid = choice.success_scene if result_key in ("great", "success") else choice.failure_scene
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
        self.game_state.add_event("Narrative mission aborted — operatives return shaken.")
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
            gs.spend_funds(-self._total_funds_earned, "text_mission_reward",
                           f"Narrative mission reward: ¥{self._total_funds_earned}")
        elif self._total_funds_earned < 0:
            gs.spend_funds(abs(self._total_funds_earned), "text_mission_loss",
                           f"Narrative mission loss: ¥{abs(self._total_funds_earned)}")
        for char in self._deployed_agents():
            char.stress = min(int(getattr(char, "stress", 0)) + self._total_stress, 100)
        outcome = scene.outcome
        gs.add_event(
            f"Narrative mission '{self._mission.title}': {outcome.upper()}"
            + (f"  ¥{self._total_funds_earned}" if self._total_funds_earned else "")
        )
