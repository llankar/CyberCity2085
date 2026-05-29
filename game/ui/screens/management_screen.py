"""CyberCity 2085 — Unified Management Screen.

Replaces CorpView, CityView, and RPGView with a single XCOM2-style
tabbed management interface:

    ┌──────────────────────────────────────────────────────┐  ←  52px top HUD
    │ ■ AEGIS CORP  │  DAY 14  │  ¥ 2,450  │  THREAT ███  │
    ├────────┬─────────────────────────────────────────────┤
    │ COMMAND│                                              │
    │ CITY   │           active tab content                │
    │ SQUAD  │                                              │
    │ RESEARCH                                             │
    │ INTEL  │                                              │
    └────────┴─────────────────────────────────────────────┘  ←  48px bottom bar
    │ [ADVANCE DAY]  [SAVE ·1]  [LOAD]          [LAUNCH ▶] │

All game-logic mutations are identical to the originals — only the
presentation layer changes.
"""

from __future__ import annotations

import ctypes
import math
import time
from dataclasses import dataclass

import arcade

from game.agents.sheet_calculations import compute_derived_stats, skill_total
from game.progression import ALLOWED_SKILL_KEYS, option_b_plan
from game.agent_readiness import agents_at_breaking_risk
from game.character import is_deployable
from game.deployment import (
    sanitize_selected_agent_names,
    selected_deployable_agents,
    remove_agent_from_roster,
    toggle_agent_selection,
)
from game.gamestate import GameState
from game.management.equipment import default_equipment_catalog
from game.mission_system import (
    ensure_mission_templates,
    launch_selected_mission as _launch_mission,
    selected_mission as _selected_mission,
)
from game.persistence import SaveSystem, SaveSystemResult
from game.agent_specializations import (
    available_talent_nodes,
    talent_node_by_id,
    talent_nodes_for_role,
    unlock_talent,
)
from game.recruitment import build_recruitment_candidates, recruit_agent
from game.management.morale import aggregate_squad_morale
from game.management.downtime import DOWNTIME_ACTIVITIES, apply_activity
from game.ui import GameView
from game.ui import palette
from game.ui.action_feedback import push_action
from game.ui.management.action_requirements import (
    blocked_launch_reason,
    blocked_recruit_reason,
)
from game.ui.command_deck import build_corporate_finance_lines, build_event_panel_lines
from game.ui.panels import draw_expanded_room_controls, draw_graphical_command_surface
from game.ui.panels import draw_small_meter
from game.ui.portraits import portrait_path_for_character, portrait_path_for_power_armor, portrait_path_for_robot
from game.ui.room_interaction import (
    RoomUIState,
    action_at_point,
    active_room_rect,
    close_button_rect,
    close_room,
    open_room,
    room_at_point,
    step_room_ui,
)
from game.ui.screens.research_lab import build_research_lab_lines
from game.ui.screens.spec_ops_assets import (
    build_asset_outcome_lines,
    build_mission_prep_asset_state_lines,
    build_spec_ops_acquisition_lines,
    build_spec_ops_assets_guide_lines,
)
from game.ui.widgets.squad_morale_panel import build_squad_morale_panel_lines
from game.ui.widgets.notification_center import NotificationCenter
from game.ui.guidance.next_action import compute_next_action

# ── Layout constants ────────────────────────────────────────────────────────

_SIDEBAR_W    = 190
_TOP_HUD_H    = 52
_BOT_BAR_H    = 48
_TAB_H        = 64
_TABS: list[tuple[str, str]] = [
    ("COMMAND", "command"),
    ("CITY",    "city"),
    ("SQUAD",   "squad"),
    ("ASSETS",  "assets"),
    ("RESEARCH","research"),
    ("INTEL",   "intel"),
]

# ── Hit-region helper ───────────────────────────────────────────────────────

@dataclass
class _HitRegion:
    left:   int
    bottom: int
    right:  int
    top:    int
    action: str
    data:   object = None

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x <= self.right and self.bottom <= y <= self.top


# ── Helper draw primitives ───────────────────────────────────────────────────

def _rect(l, b, r, t, color) -> None:
    if l >= r or b >= t:
        return
    arcade.draw_lrbt_rectangle_filled(l, r, b, t, color)


def _trim_text(text: str, limit: int = 96) -> str:
    """Keep long UI labels from overflowing narrow panels."""
    return text if len(text) <= limit else f"{text[: limit - 3]}..."


def _draw_notification_toast(notifications: "NotificationCenter", w: int, h: int) -> None:
    """Render the most-recent notification lines just below the top HUD (top-right)."""
    lines = notifications.latest_text_lines(4)
    if not lines:
        return
    pad, line_h, font_sz = 8, 18, 11
    panel_w = min(760, max(460, int(w * 0.40)))
    panel_h = pad * 2 + len(lines) * line_h
    rx = (w + panel_w) // 2
    ry = h - _TOP_HUD_H - 6 - panel_h   # anchor below the HUD bar
    left = rx - panel_w
    _rect(left, ry, rx, ry + panel_h, (0, 0, 0, 200))
    arcade.draw_line(left, ry + panel_h, rx, ry + panel_h, palette.PANEL_BORDER, 1)
    for i, text in enumerate(lines):
        color = palette.TACTICAL_GREEN if "[SUCCESS]" in text else (
            palette.WARNING if "[WARNING]" in text else palette.DANGER
        )
        arcade.draw_text(
            text, left + pad, ry + pad + i * line_h,
            color, font_sz, anchor_x="left", anchor_y="bottom",
        )


def _border(l, b, r, t, color, width: int = 1) -> None:
    arcade.draw_line(l, t, r, t, color, width)
    arcade.draw_line(l, b, r, b, color, width)
    arcade.draw_line(l, b, l, t, color, width)
    arcade.draw_line(r, b, r, t, color, width)


def _panel(l: int, b: int, r: int, t: int, title: str = "", accent=None) -> None:
    """Draw a glass-dark panel with optional title header."""
    _rect(l, b, r, t, palette.PANEL_FILL)
    border_col = accent or palette.PANEL_BORDER_MUTED
    arcade.draw_line(l, t, r, t, border_col, 2)
    arcade.draw_line(l, b, r, b, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(l, b, l, t, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(r, b, r, t, palette.PANEL_BORDER_MUTED, 1)
    if title:
        _rect(l, t - 26, r, t, palette.PANEL_FILL_DARK)
        arcade.draw_line(l, t - 26, r, t - 26, border_col, 1)
        arcade.draw_text(
            title.upper(), l + 10, t - 17,
            palette.HEADER, font_size=11, bold=True,
        )


def _meter(l: int, b: int, w: int, value: float, color, label: str = "", label_offset: int = 13) -> None:
    """Compact 0-100 progress meter with optional label."""
    h = 10
    _rect(l, b, l + w, b + h, palette.PANEL_FILL_DARK)
    fill_w = int(w * max(0.0, min(1.0, value)))
    _rect(l, b, l + fill_w, b + h, color)
    if label:
        arcade.draw_text(label, l, b + label_offset, palette.MUTED_TEXT, font_size=9)


def _badge(text: str, x: int, y: int, color, bg=None) -> None:
    """Small text badge (e.g. risk level)."""
    w = max(48, len(text) * 8 + 10)
    bg = bg or (*color[:3], 60)
    _rect(x, y, x + w, y + 18, bg)
    arcade.draw_line(x, y + 18, x + w, y + 18, color, 2)
    arcade.draw_text(text, x + 5, y + 4, color, font_size=9, bold=True)


def _risk_color(risk):
    """Return a threat colour for a risk value that may be int (1-5) or str."""
    if isinstance(risk, int):
        if risk >= 4:
            return palette.DANGER
        if risk >= 2:
            return palette.WARNING
        return palette.TACTICAL_GREEN
    r = (risk or "").lower()
    if r in ("high", "critical", "extreme"):
        return palette.DANGER
    if r in ("medium", "moderate"):
        return palette.WARNING
    return palette.TACTICAL_GREEN


def _set_window_topmost(window, enabled: bool) -> None:
    """Best-effort raise/lower helper for modal overlays on Windows."""
    if window is None:
        return
    activate = getattr(window, "activate", None)
    if callable(activate):
        try:
            activate()
        except Exception:
            pass
    hwnd = getattr(window, "_hwnd", None)
    if hwnd is None:
        return
    try:
        user32 = ctypes.windll.user32
        flags = 0x0001 | 0x0002 | 0x0040  # SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW
        insert_after = -1 if enabled else -2  # HWND_TOPMOST / HWND_NOTOPMOST
        user32.SetWindowPos(hwnd, insert_after, 0, 0, 0, 0, flags)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
class ManagementView(GameView):
    """Unified XCOM2-style management hub."""

    # ── Setup ────────────────────────────────────────────────────────────────

    def setup(self) -> None:
        self.active_tab: str = "command"
        self.notifications    = NotificationCenter()
        self.selected_save_slot: int = 1
        self._hits: list[_HitRegion] = []
        self._elapsed: float = 0.0

        # Squad / deployment state
        self.deployment_cursor: int = 0
        self._asset_cursor: int     = 0
        self._catalog_scroll: int   = 0
        self.pending_launch_confirm: bool = False
        self.pending_launch_mission_id: str | None = None
        self.message: str = ""
        self.equipment_catalog = default_equipment_catalog()
        self._last_agent_click_time: float = 0.0
        self._last_agent_click_index: int | None = None
        self.expanded_agent_sheet_index: int | None = None

        ensure_mission_templates(self.game_state)
        self.game_state.selected_agent_names = sanitize_selected_agent_names(
            self.game_state.characters, self.game_state.selected_agent_names
        )

        # Give seed funds if empty
        if self.game_state.available_funds <= 0:
            self.game_state.add_funds(
                self.game_state.compute_budget(),
                "mgmt_setup",
                "Emergency operating funds.",
            )

    # ── Arcade lifecycle ──────────────────────────────────────────────────────

    def on_show_view(self) -> None:
        arcade.set_background_color(palette.BACKGROUND)
        ensure_mission_templates(self.game_state)

    def on_update(self, delta_time: float) -> None:
        self._elapsed += delta_time

    # Tab → room image mapping (content area background)
    _TAB_ROOM_IMAGE: dict[str, str] = {
        "command":  "assets/ui/rooms/top_right.png",
        "city":     "assets/ui/rooms/mid_right.png",
        "squad":    "assets/ui/rooms/low_left.png",
        "assets":   "assets/ui/rooms/top_left.png",
        "research": "assets/ui/rooms/bottom_left.png",
        "intel":    "assets/ui/rooms/bottom_right.png",
    }

    def on_draw(self) -> None:
        self.clear()
        self._hits = []
        w, h = self.window.width, self.window.height

        # Draw city-tower background (full-screen)
        from game.ui.panels import draw_city_corporate_backdrop, _load_texture_once
        draw_city_corporate_backdrop(w, h, "corp")

        # Lighter overlay — let the background art show through
        _rect(0, 0, w, h, (0, 0, 0, 60))

        # Room image in the content panel area based on active tab
        room_img_path = self._TAB_ROOM_IMAGE.get(self.active_tab)
        if room_img_path:
            import os
            abs_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", room_img_path)
            abs_path = os.path.normpath(abs_path)
            tex = _load_texture_once(abs_path)
            if tex:
                cx0 = _SIDEBAR_W + 8
                cy0 = _BOT_BAR_H + 8
                cx1 = w - 8
                cy1 = h - _TOP_HUD_H - 8
                # Draw room image, then dim it so panels remain legible
                arcade.draw_texture_rect(
                    tex, arcade.LBWH(cx0, cy0, cx1 - cx0, cy1 - cy0)
                )
                _rect(cx0, cy0, cx1, cy1, (0, 0, 0, 140))

        self._draw_top_hud(w, h)
        self._draw_sidebar(w, h)
        self._draw_content(w, h)
        self._draw_bottom_bar(w, h)

        # Notifications toast — newest-first, bottom-right corner
        _draw_notification_toast(self.notifications, w, h)
        self._draw_expanded_agent_sheet_modal(w, h)


    def _draw_expanded_agent_sheet_modal(self, w: int, h: int) -> None:
        if self.expanded_agent_sheet_index is None:
            return
        gs = self.game_state
        if self.expanded_agent_sheet_index >= len(gs.characters):
            self._close_agent_sheet()
            return

        char = gs.characters[self.expanded_agent_sheet_index]
        self._modal_hits = []

        from game.ui.panels import _load_texture_once
        from game.ui.portraits import portrait_path_for_character

        stats = char.stats
        sheet_attrs = {
            "level": int(stats.level),
            "str": int(stats.str),
            "agi": int(stats.agi),
            "con": int(stats.con),
            "cha": int(stats.cha),
            "psi": int(stats.psi),
            "defense": int(stats.defense),
        }
        stress_state = "steady" if char.stress < 35 else "rattled" if char.stress < 65 else "frayed" if char.stress < 85 else "breaking"
        loadout_bonuses = char.loadout.total_stat_bonuses()
        derived = compute_derived_stats(sheet_attrs, char.skills, loadout_bonuses, stress_state)
        planned_skills = option_b_plan(char)
        planned_deltas = {k: v - int(char.skills.get(k, 0)) for k, v in planned_skills.items()}
        role_col = {
            "samurai": palette.ROLE_SAMURAI,
            "sniper": palette.ROLE_SNIPER,
            "psi": palette.ROLE_PSI,
        }.get(char.role, palette.ACCENT)

        _rect(0, 0, w, h, (0, 0, 0, 195))
        mw = min(1080, w - 56)
        mh = min(700, h - 44)
        mx0 = (w - mw) // 2
        my0 = (h - mh) // 2
        mx1 = mx0 + mw
        my1 = my0 + mh
        _rect(mx0, my0, mx1, my1, (6, 14, 20, 248))
        _border(mx0, my0, mx1, my1, role_col, 2)
        _rect(mx0, my1 - 74, mx1, my1, (10, 24, 34, 248))
        arcade.draw_line(mx0, my1 - 74, mx1, my1 - 74, role_col, 2)
        arcade.draw_text(
            f"{char.name.upper()}  |  {char.role.upper()}  |  LEVEL {stats.level}",
            mx0 + 20,
            my1 - 28,
            palette.TEXT,
            font_size=18,
            bold=True,
        )
        arcade.draw_text(
            f"Pending points {char.pending_points}   Talent points {char.talent_points}   Stress {char.stress}",
            mx0 + 20,
            my1 - 50,
            palette.MUTED_TEXT,
            font_size=11,
        )
        close_left = mx1 - 42
        close_bottom = my1 - 56
        _rect(close_left, close_bottom, close_left + 28, close_bottom + 28, (14, 24, 30, 240))
        arcade.draw_line(close_left, close_bottom + 28, close_left + 28, close_bottom + 28, palette.PANEL_BORDER_MUTED, 1)
        arcade.draw_text("X", close_left + 14, close_bottom + 14, palette.DANGER, font_size=14, bold=True, anchor_x="center", anchor_y="center")
        self._modal_hits.append(_HitRegion(close_left, close_bottom, close_left + 28, close_bottom + 28, "sheet_close"))

        left_w = 280
        pad = 18
        left_x0 = mx0 + pad
        left_x1 = left_x0 + left_w
        right_x0 = left_x1 + 18
        right_x1 = mx1 - pad

        # Left dossier column
        portrait_size = 198
        portrait_left = left_x0 + 4
        portrait_bottom = my1 - 110 - portrait_size
        _rect(portrait_left - 8, portrait_bottom - 10, portrait_left + portrait_size + 8, portrait_bottom + portrait_size + 10, (15, 34, 44, 220))
        arcade.draw_line(portrait_left - 8, portrait_bottom + portrait_size + 10, portrait_left + portrait_size + 8, portrait_bottom + portrait_size + 10, role_col, 2)
        portrait_path = portrait_path_for_character(char)
        portrait_tex = _load_texture_once(portrait_path) if portrait_path else None
        if portrait_tex is not None and hasattr(arcade, "draw_texture_rect"):
            arcade.draw_texture_rect(portrait_tex, arcade.LBWH(portrait_left, portrait_bottom, portrait_size, portrait_size))
        else:
            center_x = portrait_left + portrait_size // 2
            center_y = portrait_bottom + portrait_size // 2
            radius = portrait_size // 2
            arcade.draw_circle_filled(center_x, center_y, radius, palette.AGENT_PORTRAIT_FILL)
            arcade.draw_circle_outline(center_x, center_y, radius, role_col, 3)
        arcade.draw_text("DOSSIER PORTRAIT", portrait_left + 10, portrait_bottom + portrait_size + 16, palette.MUTED_TEXT, font_size=8, bold=True)

        info_y = portrait_bottom - 18
        info_lines = [
            f"Role {char.role.upper()}",
            f"HP {stats.hp}/{stats.max_hp}   DEF {stats.defense}",
            f"XP {stats.xp}   Lvl {stats.level}   Loyalty {char.loyalty}",
            f"Recovery {char.recovery_turns}d   Stress cap {derived['stress_cap']}",
        ]
        for idx, line in enumerate(info_lines):
            arcade.draw_text(line, left_x0, info_y - idx * 20, palette.TEXT if idx == 0 else palette.MUTED_TEXT, font_size=11 if idx == 0 else 10, bold=idx == 0)

        meter_y = info_y - 132
        _meter(left_x0, meter_y + 28, left_w - 24, stats.hp / max(1, stats.max_hp), palette.TACTICAL_GREEN, "HP")
        _meter(left_x0, meter_y - 16, left_w - 24, char.stress / max(1, derived["stress_cap"]), palette.WARNING, "STRESS", label_offset=18)

        loadout_lines = char.loadout.summary_lines()[:5]
        loadout_top = my0 + 34
        _rect(left_x0 - 6, loadout_top - 8, left_x1 - 2, loadout_top + 118, (9, 20, 26, 210))
        arcade.draw_line(left_x0 - 6, loadout_top + 118, left_x1 - 2, loadout_top + 118, palette.PANEL_BORDER_MUTED, 1)
        arcade.draw_text("LOADOUT", left_x0 + 6, loadout_top + 98, palette.ACCENT, font_size=11, bold=True)
        for idx, line in enumerate(loadout_lines or ["No equipment assigned."]):
            arcade.draw_text(line, left_x0 + 6, loadout_top + 76 - idx * 18, palette.MUTED_TEXT, font_size=9, width=left_w - 18, align="left")

        # Right details column
        stats_top = my1 - 104
        arcade.draw_text("ATTRIBUTES", right_x0, stats_top + 16, palette.ACCENT, font_size=12, bold=True)
        stat_order = [
            ("str", "STR"),
            ("agi", "AGI"),
            ("psi", "PSI"),
            ("def", "DEF"),
            ("con", "CON"),
        ]
        stat_gap = 8
        stat_card_w = (right_x1 - right_x0 - stat_gap * (len(stat_order) - 1)) // len(stat_order)
        stat_card_h = 76
        for idx, (stat_key, label) in enumerate(stat_order):
            card_left = right_x0 + idx * (stat_card_w + stat_gap)
            card_bottom = stats_top - stat_card_h
            current = getattr(stats, "defense" if stat_key == "def" else stat_key)
            fill = (13, 25, 33, 235) if char.pending_points <= 0 else (18, 40, 28, 235)
            accent = role_col if char.pending_points <= 0 else palette.RESOURCE
            _rect(card_left, card_bottom, card_left + stat_card_w, card_bottom + stat_card_h, fill)
            arcade.draw_line(card_left, card_bottom + stat_card_h, card_left + stat_card_w, card_bottom + stat_card_h, accent, 2)
            arcade.draw_text(label, card_left + 10, card_bottom + 50, palette.MUTED_TEXT, font_size=9, bold=True)
            arcade.draw_text(str(current), card_left + 10, card_bottom + 20, palette.TEXT, font_size=18, bold=True)
            arcade.draw_text("SPEND", card_left + stat_card_w - 10, card_bottom + 10, palette.RESOURCE if char.pending_points > 0 else palette.PANEL_BORDER_MUTED, font_size=8, bold=True, anchor_x="right")
            if char.pending_points > 0:
                self._modal_hits.append(_HitRegion(card_left, card_bottom, card_left + stat_card_w, card_bottom + stat_card_h, "sheet_spend_stat", (self.expanded_agent_sheet_index, stat_key)))

        readiness_top = stats_top - stat_card_h - 20
        arcade.draw_text("READINESS", right_x0, readiness_top + 16, palette.ACCENT, font_size=12, bold=True)
        ready_metrics = [
            ("HP", f"{derived['hp']}"),
            ("AIM", f"{derived['aim']}"),
            ("DEF", f"{derived['defense']}"),
            ("INIT", f"{derived['initiative']}"),
            ("RES", f"{derived['resolve']}"),
            ("REC", f"{derived['recovery_rate']}"),
        ]
        metric_gap = 10
        metric_cols = 3
        metric_rows = (len(ready_metrics) + metric_cols - 1) // metric_cols
        metric_card_w = (right_x1 - right_x0 - metric_gap * (metric_cols - 1)) // metric_cols
        metric_card_h = 60
        for idx, (label, value) in enumerate(ready_metrics):
            row = idx // metric_cols
            col = idx % metric_cols
            card_left = right_x0 + col * (metric_card_w + metric_gap)
            card_top = readiness_top - row * (metric_card_h + 10)
            card_bottom = card_top - metric_card_h
            _rect(card_left, card_bottom, card_left + metric_card_w, card_bottom + metric_card_h, (10, 21, 28, 220))
            arcade.draw_line(card_left, card_bottom + metric_card_h, card_left + metric_card_w, card_bottom + metric_card_h, palette.PANEL_BORDER_MUTED, 1)
            arcade.draw_text(label, card_left + 10, card_bottom + 36, palette.MUTED_TEXT, font_size=8, bold=True)
            arcade.draw_text(value, card_left + 10, card_bottom + 12, palette.TEXT, font_size=14, bold=True)

        skills_top = readiness_top - metric_rows * (metric_card_h + 10) - 18
        arcade.draw_text("SKILLS", right_x0, skills_top + 16, palette.ACCENT, font_size=12, bold=True)
        skill_button_text = "TRAIN SKILLS"
        skill_summary = ", ".join(f"{key[:4].upper()}+{delta}" for key, delta in planned_deltas.items()) if planned_deltas else "No eligible skills"
        button_left = right_x0
        button_bottom = skills_top - 10
        button_h = 48
        button_fill = (22, 42, 30, 240) if planned_deltas and char.pending_points > 0 else (11, 20, 25, 210)
        button_col = palette.RESOURCE if planned_deltas and char.pending_points > 0 else palette.PANEL_BORDER_MUTED
        _rect(button_left, button_bottom, right_x1, button_bottom + button_h, button_fill)
        arcade.draw_line(button_left, button_bottom + button_h, right_x1, button_bottom + button_h, button_col, 2)
        arcade.draw_text(skill_button_text, button_left + 12, button_bottom + 30, button_col, font_size=10, bold=True)
        arcade.draw_text(skill_summary[:72], button_left + 12, button_bottom + 12, palette.MUTED_TEXT, font_size=8)
        if planned_deltas and char.pending_points > 0:
            self._modal_hits.append(_HitRegion(button_left, button_bottom, right_x1, button_bottom + button_h, "sheet_train_skills", self.expanded_agent_sheet_index))

        skills_grid_top = button_bottom - 18
        skill_cols = 3
        skill_gap = 10
        skill_card_w = (right_x1 - right_x0 - skill_gap * (skill_cols - 1)) // skill_cols
        skill_card_h = 64
        for idx, skill_key in enumerate(ALLOWED_SKILL_KEYS):
            row = idx // skill_cols
            col = idx % skill_cols
            card_left = right_x0 + col * (skill_card_w + skill_gap)
            card_top = skills_grid_top - row * (skill_card_h + skill_gap)
            card_bottom = card_top - skill_card_h
            rank = int(char.skills.get(skill_key, 0))
            total = skill_total(skill_key, sheet_attrs, char.skills, {})
            planned_delta = planned_deltas.get(skill_key, 0)
            highlight = planned_delta > 0
            fill = (19, 29, 38, 232) if not highlight else (22, 48, 37, 232)
            border = palette.PANEL_BORDER_MUTED if not highlight else palette.RESOURCE
            _rect(card_left, card_bottom, card_left + skill_card_w, card_top, fill)
            arcade.draw_line(card_left, card_top, card_left + skill_card_w, card_top, border, 2)
            arcade.draw_text(skill_key.replace("_", " ").upper(), card_left + 8, card_top - 16, palette.TEXT, font_size=8, bold=True)
            arcade.draw_text(f"RANK {rank}", card_left + 8, card_bottom + 22, palette.MUTED_TEXT, font_size=8)
            arcade.draw_text(f"TOTAL {total}", card_left + 8, card_bottom + 10, palette.ACCENT, font_size=9, bold=True)
            if highlight:
                arcade.draw_text(f"+{planned_delta}", card_left + skill_card_w - 10, card_bottom + 10, palette.RESOURCE, font_size=10, bold=True, anchor_x="right")

        footer_y = my0 + 14
        arcade.draw_text(
            "Click a stat card to spend 1 point. Train Skills applies the current 2-rank plan.",
            right_x0,
            footer_y,
            palette.MUTED_TEXT,
            font_size=9,
        )
        arcade.draw_text("ESC closes this sheet.", mx1 - 18, footer_y, palette.MUTED_TEXT, font_size=9, anchor_x="right")

    def _draw_recruit_window_modal(self, w: int, h: int) -> None:
        if not self.recruit_window_open or not self.pending_recruit_candidates:
            return

        gs = self.game_state
        self._modal_hits = []

        from game.ui.panels import _load_texture_once

        _rect(0, 0, w, h, (0, 0, 0, 185))
        mw = min(1120, w - 64)
        mh = min(680, h - 44)
        mx0 = (w - mw) // 2
        my0 = (h - mh) // 2
        mx1 = mx0 + mw
        my1 = my0 + mh
        _rect(mx0, my0, mx1, my1, (7, 16, 22, 250))
        _border(mx0, my0, mx1, my1, palette.ACCENT, 2)
        _rect(mx0, my1 - 78, mx1, my1, (10, 24, 32, 246))
        arcade.draw_line(mx0, my1 - 78, mx1, my1 - 78, palette.ACCENT, 2)
        arcade.draw_text(
            "RECRUITMENT WINDOW",
            mx0 + 20,
            my1 - 28,
            palette.TEXT,
            font_size=18,
            bold=True,
        )
        arcade.draw_text(
            f"{len(self.pending_recruit_candidates)} AVAILABLE AGENTS   |   FUNDS ¥{gs.available_funds}   |   N REFRESHES   |   ESC CLOSES",
            mx0 + 20,
            my1 - 50,
            palette.MUTED_TEXT,
            font_size=10,
        )

        close_left = mx1 - 42
        close_bottom = my1 - 56
        _rect(close_left, close_bottom, close_left + 28, close_bottom + 28, (14, 24, 30, 240))
        arcade.draw_line(close_left, close_bottom + 28, close_left + 28, close_bottom + 28, palette.PANEL_BORDER_MUTED, 1)
        arcade.draw_text("X", close_left + 14, close_bottom + 14, palette.DANGER, font_size=14, bold=True, anchor_x="center", anchor_y="center")
        self._modal_hits.append(_HitRegion(close_left, close_bottom, close_left + 28, close_bottom + 28, "recruit_close"))

        cols = 2
        gap = 10
        card_pad = 18
        rows = math.ceil(len(self.pending_recruit_candidates) / cols)
        usable_w = mx1 - mx0 - card_pad * 2
        usable_h = my1 - my0 - 118
        card_w = (usable_w - gap * (cols - 1)) // cols
        card_h = max(96, min(120, (usable_h - gap * max(0, rows - 1)) // max(1, rows)))
        card_top = my1 - 92

        for idx, candidate in enumerate(self.pending_recruit_candidates):
            row = idx // cols
            col = idx % cols
            left = mx0 + card_pad + col * (card_w + gap)
            top = card_top - row * (card_h + gap)
            bottom = top - card_h
            if bottom < my0 + 18:
                break

            role_col = {
                "samurai": palette.ROLE_SAMURAI,
                "sniper": palette.ROLE_SNIPER,
                "psi": palette.ROLE_PSI,
            }.get(candidate.role, palette.ACCENT)
            affordable = gs.available_funds >= candidate.price
            fill = (13, 26, 34, 236) if affordable else (31, 23, 22, 236)
            border = role_col if affordable else (95, 96, 100)
            _rect(left, bottom, left + card_w, top, fill)
            arcade.draw_line(left, top, left + card_w, top, border, 2)

            portrait_size = min(52, card_h - 28)
            portrait_left = left + 12
            portrait_bottom = bottom + max(10, (card_h - portrait_size) // 2)
            tex = _load_texture_once(candidate.portrait_path)
            if tex is not None and hasattr(arcade, "draw_texture_rect"):
                arcade.draw_texture_rect(tex, arcade.LBWH(portrait_left, portrait_bottom, portrait_size, portrait_size))
            else:
                arcade.draw_circle_filled(
                    portrait_left + portrait_size // 2,
                    portrait_bottom + portrait_size // 2,
                    portrait_size // 2,
                    palette.AGENT_PORTRAIT_FILL,
                )
                arcade.draw_circle_outline(
                    portrait_left + portrait_size // 2,
                    portrait_bottom + portrait_size // 2,
                    portrait_size // 2,
                    role_col,
                    2,
                )

            text_left = portrait_left + portrait_size + 12
            text_right = left + card_w - 12
            arcade.draw_text(candidate.name.upper(), text_left, top - 18, palette.TEXT, font_size=12, bold=True)
            arcade.draw_text(candidate.role.upper(), text_left, top - 32, role_col, font_size=8, bold=True)
            arcade.draw_text(candidate.function.upper(), text_left, top - 44, palette.MUTED_TEXT, font_size=8, bold=True)
            arcade.draw_text(candidate.stat_line(), text_left, top - 60, palette.TEXT, font_size=8)
            arcade.draw_text(candidate.skill_line(), text_left, top - 74, palette.RESOURCE, font_size=8)
            arcade.draw_text(
                _trim_text(candidate.background, 92),
                text_left,
                bottom + 28,
                palette.MUTED_TEXT,
                font_size=8,
                width=max(40, text_right - text_left),
                align="left",
            )
            arcade.draw_text(
                "ADV: " + _trim_text(" | ".join(candidate.advantages), 68),
                text_left,
                bottom + 12,
                palette.RESOURCE,
                font_size=7,
                width=max(40, text_right - text_left),
                align="left",
            )
            price_label = f"¥{candidate.price}"
            price_col = palette.TACTICAL_GREEN if affordable else palette.DANGER
            arcade.draw_text(price_label, left + card_w - 64, bottom + 10, price_col, font_size=12, bold=True)
            arcade.draw_text(
                "HIRE" if affordable else "LOCKED",
                left + card_w - 66,
                bottom + 28,
                price_col,
                font_size=8,
                bold=True,
            )
            self._modal_hits.append(_HitRegion(left, bottom, left + card_w, top, "recruit_candidate", idx))

    def on_key_press(self, key: int, modifiers: int) -> None:
        # Tab shortcuts
        tab_keys = {
            arcade.key.F1: "command",
            arcade.key.F2: "city",
            arcade.key.F3: "squad",
            arcade.key.F4: "research",
            arcade.key.F5: "intel",
        }
        if key == arcade.key.ESCAPE and self.expanded_agent_sheet_index is not None:
            self.expanded_agent_sheet_index = None
            return

        if key in tab_keys:
            self.active_tab = tab_keys[key]
            return

        # Universal shortcuts
        if key == arcade.key.D:
            self._do_advance_day()
        elif key == arcade.key.S and not (modifiers & arcade.key.MOD_CTRL):
            self._do_save()
        elif key == arcade.key.L and not (modifiers & arcade.key.MOD_CTRL):
            self._do_load()
        elif key == arcade.key.H:
            self.active_tab = "intel"
        elif key == arcade.key.ESCAPE:
            # Return to title
            from game.ui.screens.title_screen import TitleView
            self.window.show_view(TitleView())

        # Squad-tab specific
        elif self.active_tab == "squad":
            if key == arcade.key.B:
                self._do_launch_mission()
            elif key == arcade.key.N:
                self._do_recruit_prompt()
            elif key == arcade.key.A and self.game_state.characters:
                self.deployment_cursor = (
                    (self.deployment_cursor - 1) % len(self.game_state.characters)
                )
            elif key == arcade.key.D and self.game_state.characters:
                # D is overloaded — advance day if NOT in squad tab context
                pass
            elif key == arcade.key.SPACE and self.game_state.characters:
                self.game_state.selected_agent_names, self.message = toggle_agent_selection(
                    self.game_state.characters,
                    self.game_state.selected_agent_names,
                    self.deployment_cursor,
                )
                self.pending_launch_confirm = False
            elif key in (arcade.key.KEY_7, arcade.key.KEY_8, arcade.key.KEY_9):
                idx = key - arcade.key.KEY_7
                self._do_downtime_activity(idx)
            elif key in (arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3):
                idx = key - arcade.key.KEY_1
                if idx < len(self.game_state.mission_templates):
                    self.game_state.selected_mission_index = idx
                    self.pending_launch_confirm = False

    def on_mouse_press(self, x: float, y: float, _button: int, _modifiers: int) -> None:
        xi, yi = int(x), int(y)
        for hit in self._hits:
            if hit.contains(xi, yi):
                self._dispatch(hit.action, hit.data)
                return

    # ── Top HUD ──────────────────────────────────────────────────────────────

    def _draw_top_hud(self, w: int, h: int) -> None:
        # Background
        _rect(0, h - _TOP_HUD_H, w, h, palette.PANEL_FILL_DARK)
        arcade.draw_line(0, h - _TOP_HUD_H, w, h - _TOP_HUD_H, palette.PANEL_BORDER, 2)

        gs = self.game_state
        cy = h - _TOP_HUD_H // 2

        # Corp logo / name
        _rect(0, h - _TOP_HUD_H, 240, h, (31, 18, 6, 220))
        arcade.draw_line(240, h - _TOP_HUD_H, 240, h, palette.AMBER_BORDER, 2)
        corp_label = f"▌ {gs.corp_name.upper()[:18]}"
        arcade.draw_text(
            corp_label, 14, cy,
            palette.HEADER, font_size=17, bold=True,
            anchor_y="center",
        )

        # Day / calendar
        day_txt = f"DAY {gs.calendar.current_day}"
        arcade.draw_text(day_txt, 260, cy, palette.ACCENT, font_size=15, anchor_y="center")

        # Funds
        funds_txt = f"¥ {gs.available_funds:,}"
        arcade.draw_text("FUNDS", 400, cy + 8, palette.MUTED_TEXT, font_size=11, anchor_y="center")
        arcade.draw_text(funds_txt, 400, cy - 8, palette.RESOURCE, font_size=14, bold=True, anchor_y="center")

        # Threat meter (max hostile faction + max district unrest)
        threat = 0
        if gs.factions:
            threat = max(f.hostility_to_player for f in gs.factions)
        threat = max(threat, gs.district.unrest)
        threat_frac = threat / 100
        threat_col = _risk_color("high" if threat >= 70 else "medium" if threat >= 40 else "low")
        arcade.draw_text("THREAT", 540, cy + 7, palette.MUTED_TEXT, font_size=9, anchor_y="center")
        _rect(540, cy - 9, 700, cy - 1, palette.PANEL_FILL_DARK)
        _rect(540, cy - 9, 540 + int(160 * threat_frac), cy - 1, threat_col)
        arcade.draw_text(f"{threat}%", 708, cy - 9, threat_col, font_size=9)

        # Active missions count
        active_m = len([t for t in gs.mission_templates])
        arcade.draw_text(
            f"MISSIONS {active_m}", 780, cy,
            palette.MUTED_TEXT, font_size=13, anchor_y="center",
        )

        # Agent count
        roster = len(gs.characters)
        selected = len(gs.selected_agent_names)
        arcade.draw_text(
            f"AGENTS {selected}/{roster}", 940, cy,
            palette.ACCENT, font_size=13, anchor_y="center",
        )

        # Slot indicator (right side)
        arcade.draw_text(
            f"SLOT {self.selected_save_slot}",
            w - 120, cy,
            palette.MUTED_TEXT, font_size=12, anchor_y="center",
        )

        # Next step guidance (right)
        from game.ui.guidance.next_action import compute_next_action
        guidance = compute_next_action(self.game_state, self.active_tab)
        arcade.draw_text(
            f"► {guidance.text}",
            w - 460, cy,
            palette.ACCENT, font_size=11, anchor_y="center",
        )

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _draw_sidebar(self, _w: int, h: int) -> None:
        top = h - _TOP_HUD_H
        bot = _BOT_BAR_H

        # Sidebar background
        _rect(0, bot, _SIDEBAR_W, top, palette.PANEL_FILL_DARK)
        arcade.draw_line(_SIDEBAR_W, bot, _SIDEBAR_W, top, palette.PANEL_BORDER, 2)

        # Divider below corp block
        arcade.draw_line(0, top - 4, _SIDEBAR_W, top - 4, palette.PANEL_BORDER_MUTED, 1)

        # Tab buttons
        for i, (label, key) in enumerate(_TABS):
            ty = top - 20 - i * (_TAB_H + 4)
            by = ty - _TAB_H
            active = (key == self.active_tab)

            fill = (32, 75, 98, 240) if active else (6, 14, 18, 200)
            _rect(0, by, _SIDEBAR_W - 2, ty, fill)

            border_col = palette.HEADER if active else palette.PANEL_BORDER_MUTED
            arcade.draw_line(0, ty, _SIDEBAR_W - 2, ty, border_col, 1 if not active else 2)

            if active:
                # Left accent bar
                _rect(0, by, 4, ty, palette.HEADER)

            arcade.draw_text(
                label, 22, (by + ty) // 2,
                palette.TEXT if active else palette.MUTED_TEXT,
                font_size=14, bold=active, anchor_y="center",
            )

            # Count badge per tab
            badge_txt = self._tab_badge(key)
            if badge_txt:
                arcade.draw_text(
                    badge_txt, _SIDEBAR_W - 14, (by + ty) // 2,
                    palette.ACCENT, font_size=11, anchor_x="right", anchor_y="center",
                )

            self._hits.append(_HitRegion(0, by, _SIDEBAR_W - 2, ty, "tab", key))

    def _tab_badge(self, key: str) -> str:
        gs = self.game_state
        if key == "squad":
            roster = len(gs.characters)
            sel    = len(gs.selected_agent_names)
            return f"{sel}/{roster}"
        if key == "assets":
            n = len(gs.spec_ops_assets)
            ready = sum(1 for a in gs.spec_ops_assets if a.is_deployable)
            return f"{ready}/{n}" if n else ""
        if key == "research":
            active = len(gs.active_research)
            return f"{active}" if active else ""
        if key == "command":
            evts = len(gs.active_events)
            return f"! {evts}" if evts else ""
        return ""

    # ── Content dispatcher ────────────────────────────────────────────────────

    def _draw_content(self, w: int, h: int) -> None:
        x0 = _SIDEBAR_W + 8
        y0 = _BOT_BAR_H + 8
        x1 = w - 8
        y1 = h - _TOP_HUD_H - 8
        {
            "command":  self._draw_command_tab,
            "city":     self._draw_city_tab,
            "squad":    self._draw_squad_tab,
            "assets":   self._draw_assets_tab,
            "research": self._draw_research_tab,
            "intel":    self._draw_intel_tab,
        }.get(self.active_tab, self._draw_command_tab)(x0, y0, x1, y1)

    # ── COMMAND tab ───────────────────────────────────────────────────────────

    def _draw_command_tab(self, x0: int, y0: int, x1: int, y1: int) -> None:
        gs  = self.game_state
        gap = 10
        cw  = (x1 - x0 - gap * 2) // 3

        # ── Left column: Corp status ─────────────────────────────────────
        lx0, lx1 = x0, x0 + cw
        _panel(lx0, y0, lx1, y1, "COMMAND STATUS", palette.AMBER_BORDER)
        cy = y1 - 42
        lines = [
            f"{gs.calendar.campaign_date_label}",
            f"Day {gs.calendar.current_day}  |  Week {gs.calendar.current_week}",
            "",
            f"Funds:      ¥ {gs.available_funds:,}",
            f"Income:     ¥ {gs.projected_weekly_income:,} / week",
            f"Next payout: Day {gs.next_weekly_income_date}",
            "",
            f"Research:   {len(gs.active_research)} active",
            f"Security:   {gs.corp_budget.get('security', 0)}",
            f"Black Ops:  {gs.corp_budget.get('black_ops', 0)}",
            f"Politics:   {gs.corp_budget.get('politics', 0)}",
        ]
        for line in lines:
            if not line:
                cy -= 8
                continue
            col = palette.RESOURCE if "¥" in line else palette.TEXT
            arcade.draw_text(line, lx0 + 12, cy, col, font_size=11)
            cy -= 18
        if cy > y0 + 60:
            arcade.draw_line(lx0 + 12, cy - 4, lx1 - 12, cy - 4, palette.GRID_LINE, 1)
            arcade.draw_text("Corp Resources", lx0 + 12, cy - 20, palette.MUTED_TEXT, font_size=9)
            cy -= 32
            resources = gs.strategic_resources
            for rkey in ("credits", "intel", "salvage", "influence"):
                val = resources.get(rkey, 0)
                arcade.draw_text(f"{rkey.upper():<10} {val}", lx0 + 12, cy, palette.MUTED_TEXT, font_size=10)
                cy -= 16

        # ── Middle column: Events ────────────────────────────────────────
        mx0, mx1 = lx1 + gap, lx1 + gap + cw
        _panel(mx0, y0, mx1, y1, "ACTIVE EVENTS", palette.PANEL_BORDER)
        if gs.active_events:
            ey = y1 - 48
            for ei, event in enumerate(gs.active_events[:4]):
                ey -= 14
                _rect(mx0 + 8, ey - 28, mx1 - 8, ey + 10, (20, 40, 50, 200))
                arcade.draw_line(mx0 + 8, ey + 10, mx1 - 8, ey + 10, palette.WARNING, 2)
                arcade.draw_text(event.title, mx0 + 14, ey - 2, palette.WARNING, font_size=11, bold=True)
                # Show description (truncated)
                desc = event.description[:80] + "…" if len(event.description) > 80 else event.description
                arcade.draw_text(desc, mx0 + 14, ey - 18, palette.TEXT, font_size=9)
                ey -= 46

                # Response choices
                for ci, choice in enumerate(event.choices[:3]):
                    cy2 = ey
                    hit_top = cy2 + 22
                    hit_bot = cy2
                    _rect(mx0 + 14, hit_bot, mx1 - 14, hit_top, (8, 24, 32, 220))
                    arcade.draw_line(mx0 + 14, hit_top, mx1 - 14, hit_top, palette.ACCENT, 1)
                    arcade.draw_text(
                        f"[{ci + 1}] {choice.label}",
                        mx0 + 22, cy2 + 6,
                        palette.ACCENT, font_size=10,
                    )
                    self._hits.append(_HitRegion(
                        mx0 + 14, hit_bot, mx1 - 14, hit_top,
                        f"event_response_{ei}_{ci}", None
                    ))
                    ey -= 28
                ey -= 10
        else:
            arcade.draw_text(
                "No active events.",
                mx0 + 14, y1 - 60,
                palette.MUTED_TEXT, font_size=11,
            )
            arcade.draw_text(
                "Advance day to generate events.",
                mx0 + 14, y1 - 80,
                (50, 80, 95), font_size=10,
            )

        # ── Right column: Actions ────────────────────────────────────────
        rx0, rx1 = mx1 + gap, x1
        _panel(rx0, y0, rx1, y1, "CORP ACTIONS", palette.TACTICAL_GREEN)
        ry = y1 - 50

        # Corp upgrade buttons
        upgrades = [
            ("research",  "Intel +5",        {"intel": 5}),
            ("security",  "Credits -10 / Salvage -2", {"credits": 10, "salvage": 2}),
            ("politics",  "Influence -3",    {"influence": 3}),
            ("black_ops", "Credits -5 / Intel -3", {"credits": 5, "intel": 3}),
        ]
        arcade.draw_text("CORP UPGRADES", rx0 + 12, ry, palette.MUTED_TEXT, font_size=9)
        ry -= 22
        for ukey, ulabel, _costs in upgrades:
            alloc = gs.corp_budget.get(ukey, 0)
            bh = 30
            _rect(rx0 + 10, ry - bh, rx1 - 10, ry, (12, 28, 36, 220))
            arcade.draw_line(rx0 + 10, ry, rx1 - 10, ry, palette.ACCENT, 1)
            arcade.draw_text(
                f"{ukey.upper():<12} {alloc:>3}",
                rx0 + 18, ry - bh + 9,
                palette.TEXT, font_size=10,
            )
            arcade.draw_text(ulabel, rx0 + 18, ry - bh - 2, palette.MUTED_TEXT, font_size=8)
            self._hits.append(_HitRegion(rx0 + 10, ry - bh, rx1 - 10, ry, f"corp_upgrade_{ukey}", None))
            ry -= bh + 8

    # ── CITY tab ──────────────────────────────────────────────────────────────

    def _draw_city_tab(self, x0: int, y0: int, x1: int, y1: int) -> None:
        gs  = self.game_state
        gap = 10
        hw  = (x1 - x0 - gap) // 2

        # ── Left: District Status ────────────────────────────────────────
        lx0, lx1 = x0, x0 + hw
        _panel(lx0, y0, lx1, y1, "DISTRICT STATUS", palette.PANEL_BORDER)

        d  = gs.district
        dy = y1 - 48
        arcade.draw_text(d.name.upper(), lx0 + 12, dy, palette.HEADER, font_size=18, bold=True)
        dy -= 28
        arcade.draw_text(
            f"Control: {d.control_faction}",
            lx0 + 12, dy, palette.MUTED_TEXT, font_size=11,
        )
        dy -= 30

        meters = [
            ("STABILITY",  d.stability  / 100, palette.TACTICAL_GREEN),
            ("UNREST",     d.unrest     / 100, palette.WARNING),
            ("MEDIA HEAT", d.media_heat / 100, palette.DANGER),
        ]
        for label, frac, col in meters:
            arcade.draw_text(label, lx0 + 12, dy + 14, palette.MUTED_TEXT, font_size=9)
            mw = lx1 - lx0 - 24
            _rect(lx0 + 12, dy, lx1 - 12, dy + 12, palette.PANEL_FILL_DARK)
            _rect(lx0 + 12, dy, lx0 + 12 + int(mw * frac), dy + 12, col)
            arcade.draw_text(f"{int(frac * 100)}", lx1 - 30, dy + 1, col, font_size=9)
            dy -= 38

        dy -= 12
        arcade.draw_line(lx0 + 12, dy, lx1 - 12, dy, palette.GRID_LINE, 1)
        dy -= 22
        arcade.draw_text("CITY UPGRADES", lx0 + 12, dy, palette.MUTED_TEXT, font_size=9)
        dy -= 24

        city_upgrades = [
            ("armaments",     "Credits -5 / Salvage -3"),
            ("garrisons",     "Credits -10 / Influence -2"),
            ("defense_zones", "Credits -5 / Salvage -5"),
        ]
        for ukey, ucost in city_upgrades:
            alloc = gs.city_budget.get(ukey, 0)
            bh = 28
            _rect(lx0 + 10, dy - bh, lx1 - 10, dy, (12, 28, 36, 220))
            arcade.draw_line(lx0 + 10, dy, lx1 - 10, dy, palette.ACCENT, 1)
            arcade.draw_text(
                f"{ukey.upper():<16} {alloc:>3}",
                lx0 + 18, dy - bh + 8, palette.TEXT, font_size=10,
            )
            arcade.draw_text(ucost, lx0 + 18, dy - bh - 2, palette.MUTED_TEXT, font_size=8)
            self._hits.append(_HitRegion(lx0 + 10, dy - bh, lx1 - 10, dy, f"city_upgrade_{ukey}", None))
            dy -= bh + 8

        # ── Right: Faction status ────────────────────────────────────────
        rx0, rx1 = lx1 + gap, x1
        _panel(rx0, y0, rx1, y1, "FACTION STATUS", palette.DANGER)

        fy = y1 - 48
        factions_sorted = sorted(gs.factions, key=lambda f: f.hostility_to_player, reverse=True)
        if factions_sorted:
            for fac in factions_sorted[:8]:
                _rect(rx0 + 8, fy - 40, rx1 - 8, fy, (12, 22, 28, 200))
                hostile_col = _risk_color(
                    "high" if fac.hostility_to_player >= 70
                    else "medium" if fac.hostility_to_player >= 40 else "low"
                )
                arcade.draw_line(rx0 + 8, fy, rx1 - 8, fy, hostile_col, 2)
                arcade.draw_text(
                    fac.name.upper(), rx0 + 14, fy - 14,
                    palette.TEXT, font_size=12, bold=True,
                )
                arcade.draw_text(
                    f"Influence: {fac.influence}  |  Hostility: {fac.hostility_to_player}%",
                    rx0 + 14, fy - 30,
                    palette.MUTED_TEXT, font_size=9,
                )
                fw = rx1 - rx0 - 24
                _rect(rx0 + 12, fy - 38, rx1 - 12, fy - 32, palette.PANEL_FILL_DARK)
                _rect(rx0 + 12, fy - 38, rx0 + 12 + int(fw * fac.hostility_to_player / 100), fy - 32, hostile_col)
                fy -= 52
        else:
            arcade.draw_text("No active factions.", rx0 + 14, y1 - 60, palette.MUTED_TEXT, font_size=11)


    # ── ASSETS tab ────────────────────────────────────────────────────────────

    _ASSET_PORTRAIT_MAP: dict[str, str] = {
        "combat_robot":  "assets/ui/portraits/robot_combat.png",
        "support_robot": "assets/ui/portraits/robot_support.png",
        "power_armor":   "assets/ui/portraits/power_armor_pilot.png",
        "heavy_armor":   "assets/ui/portraits/power_armor_heavy_pilot.png",
    }

    def _asset_portrait_path(self, asset) -> str:
        atype = getattr(asset, "asset_type", "").lower()
        if atype in {"combat_robot", "support_robot", "robot", "drone"}:
            identifier = getattr(asset, "id", getattr(asset, "name", atype))
            return portrait_path_for_robot(identifier, atype)
        if atype in {"power_armor", "heavy_armor"}:
            identifier = getattr(asset, "id", getattr(asset, "name", atype))
            return portrait_path_for_power_armor(identifier, atype)
        return self._ASSET_PORTRAIT_MAP.get(atype, "assets/ui/portraits/robot_combat.png")

    def _draw_assets_tab(self, x0: int, y0: int, x1: int, y1: int) -> None:
        """Spec-ops asset bay with portrait images, pilot assignment, deploy costs, and catalog."""
        from game.ui.panels import _load_texture_once, _draw_icon
        from game.management.spec_ops_assets import asset_catalog as _asset_catalog
        import os

        gs  = self.game_state
        gap = 10
        aw  = int((x1 - x0 - gap) * 0.44)
        dx0, dx1 = x0, x0 + aw
        rx0, rx1 = dx0 + aw + gap, x1

        assets = gs.spec_ops_assets
        _panel(dx0, y0, dx1, y1, f"HANGAR  {len(assets)} UNITS", palette.AMBER_BORDER)

        # ── Asset cards (with portrait images) ──────────────────────────
        card_h   = 90
        card_gap = 6
        catalog_strip_h = 160  # bottom section reserved for catalog
        list_h   = y1 - 34 - y0 - catalog_strip_h - 10
        max_cards = max(1, list_h // (card_h + card_gap))
        at_top   = y1 - 34
        sel_idx  = self._asset_cursor

        for i, asset in enumerate(assets[:max_cards]):
            ct = at_top - i * (card_h + card_gap)
            cb = ct - card_h
            if cb < y0 + catalog_strip_h + card_h:
                break

            active     = (i == sel_idx)
            deployable = asset.is_deployable
            is_armor   = hasattr(asset, 'pilot_required') and asset.pilot_required
            col        = palette.TACTICAL_GREEN if deployable else palette.WARNING

            fill = (32, 58, 30, 230) if (active and deployable) else (
                (36, 28, 8, 230) if active else (8, 18, 24, 200)
            )
            _rect(dx0 + 8, cb, dx1 - 8, ct, fill)
            arcade.draw_line(dx0 + 8, ct, dx1 - 8, ct, col if active else palette.PANEL_BORDER_MUTED, 2)

            # Portrait image
            ps  = card_h - 8
            px0 = dx0 + 12
            py0 = cb + 4
            port_path = self._asset_portrait_path(asset)
            abs_port  = os.path.abspath(port_path)
            tex = _load_texture_once(abs_port)
            if tex:
                arcade.draw_texture_rect(tex, arcade.LBWH(px0, py0, ps, ps))
            else:
                kind = "robot" if "robot" in asset.asset_type else "power_armor"
                _draw_icon(kind, px0 + ps // 2, py0 + ps // 2, ps - 8, col)

            # Name + type
            tx = dx0 + 14 + ps + 6
            arcade.draw_text(asset.name.upper(), tx, ct - 18, palette.TEXT, font_size=14, bold=True)
            arcade.draw_text(asset.display_role.upper(), tx, ct - 34, col, font_size=11)

            # Deploy cost badge
            if asset.deploy_cost > 0:
                arcade.draw_text(f"DEPLOY ¥{asset.deploy_cost}", tx, ct - 50, palette.RESOURCE, font_size=9)

            # Pilot badge for power armors
            if is_armor:
                pilot = getattr(asset, 'pilot_agent_name', None)
                pilot_txt = f"PILOT: {pilot}" if pilot else "PILOT: NONE"
                pilot_col = palette.TACTICAL_GREEN if pilot else palette.WARNING
                arcade.draw_text(pilot_txt, tx, cb + 8, pilot_col, font_size=9, bold=True)

            # Integrity bar
            int_frac = asset.maintenance.integrity / 100
            bw = dx1 - 20 - tx
            arcade.draw_lrbt_rectangle_filled(tx, tx + bw, cb + 24, cb + 32, palette.PANEL_FILL_DARK)
            int_col = palette.TACTICAL_GREEN if int_frac >= 0.7 else (palette.WARNING if int_frac >= 0.4 else palette.DANGER)
            arcade.draw_lrbt_rectangle_filled(tx, tx + int(bw * int_frac), cb + 24, cb + 32, int_col)
            arcade.draw_text(f"INT {asset.maintenance.integrity}%", tx, cb + 14, int_col, font_size=8)

            # Status text
            if asset.maintenance.cooldown_days > 0:
                arcade.draw_text(f"COOLDOWN {asset.maintenance.cooldown_days}d", dx1 - 90, ct - 18, palette.DANGER, font_size=8)
            elif deployable:
                arcade.draw_text("READY", dx1 - 60, ct - 18, palette.TACTICAL_GREEN, font_size=8, bold=True)

            self._hits.append(_HitRegion(dx0 + 8, cb, dx1 - 8, ct, "asset_select", i))

        # ── Catalog section (bottom of left panel) ────────────────────────
        cat_y0 = y0 + 2
        cat_y1 = cat_y0 + catalog_strip_h
        arcade.draw_line(dx0 + 8, cat_y1, dx1 - 8, cat_y1, palette.PANEL_BORDER_MUTED, 1)
        arcade.draw_text("CATALOG", dx0 + 12, cat_y1 - 16, palette.MUTED_TEXT, font_size=12, bold=True)

        catalog = _asset_catalog()
        scroll  = self._catalog_scroll % len(catalog)
        visible_cats = catalog[scroll:scroll + 2] + (catalog[:max(0, scroll + 2 - len(catalog))])
        visible_cats = visible_cats[:2]

        cat_card_h = (catalog_strip_h - 22) // 2
        for ci, cat_item in enumerate(visible_cats):
            cct = cat_y1 - 22 - ci * (cat_card_h + 4)
            ccb = cct - cat_card_h
            if ccb < cat_y0 + 2:
                break
            acquire_cost = getattr(cat_item, '_acquire_cost', 60)
            can_afford   = gs.available_funds >= acquire_cost
            is_armor     = cat_item.asset_type in ("power_armor", "heavy_armor")
            cat_col      = palette.AMBER_BORDER if can_afford else (50, 55, 60)

            _rect(dx0 + 8, ccb, dx1 - 8, cct, (10, 22, 30, 220))
            arcade.draw_line(dx0 + 8, cct, dx1 - 8, cct, cat_col, 1)

            # Small portrait
            sps  = cat_card_h - 6
            port_path = self._asset_portrait_path(cat_item)
            abs_port  = os.path.abspath(port_path)
            tex = _load_texture_once(abs_port)
            if tex:
                arcade.draw_texture_rect(tex, arcade.LBWH(dx0 + 12, ccb + 3, sps, sps))

            itx = dx0 + 14 + sps + 4
            arcade.draw_text(cat_item.name.upper(), itx, cct - 16, palette.TEXT, font_size=12, bold=True)
            arcade.draw_text(
                f"{'ROBOT' if not is_armor else 'POWER ARMOR'}  |  DEPLOY ¥{cat_item.deploy_cost}/mission",
                itx, cct - 30, palette.MUTED_TEXT, font_size=8,
            )
            # Weapons preview
            if cat_item.hardpoints:
                wpn_txt = "  ".join(f"• {hp.name}" for hp in cat_item.hardpoints[:2])
                arcade.draw_text(wpn_txt, itx, ccb + 10, (120, 160, 120), font_size=8)

            # Buy button
            btn_w = 64
            bx0, bx1 = dx1 - 10 - btn_w, dx1 - 10
            by0, by1 = ccb + 8, ccb + 28
            _rect(bx0, by0, bx1, by1, (12, 30, 14, 220) if can_afford else (20, 20, 22, 180))
            arcade.draw_line(bx0, by1, bx1, by1, cat_col, 2)
            arcade.draw_text(
                f"BUY ¥{acquire_cost}", (bx0 + bx1) // 2, (by0 + by1) // 2,
                cat_col, font_size=9, bold=True, anchor_x="center", anchor_y="center",
            )
            self._hits.append(_HitRegion(bx0, by0, bx1, by1, "catalog_acquire", ci))

        # Scroll arrows
        arr_y = cat_y0 + 6
        for di, (lbl, delta) in enumerate([("◀", -1), ("▶", 1)]):
            ax = dx0 + 12 + di * 28
            _rect(ax, arr_y, ax + 22, arr_y + 18, (14, 28, 36, 200))
            arcade.draw_text(lbl, ax + 11, arr_y + 9, palette.ACCENT, font_size=10, anchor_x="center", anchor_y="center")
            self._hits.append(_HitRegion(ax, arr_y, ax + 22, arr_y + 18, "catalog_scroll", delta))

        # ── Right panel: selected asset detail ───────────────────────────
        if sel_idx < len(assets):
            asset   = assets[sel_idx]
            is_armor = hasattr(asset, 'pilot_required') and asset.pilot_required
            col      = palette.TACTICAL_GREEN if asset.is_deployable else palette.WARNING

            _panel(rx0, y0, rx1, y1, "ASSET PROFILE", col)

            # Large portrait
            ps = 72
            port_path = self._asset_portrait_path(asset)
            abs_port  = os.path.abspath(port_path)
            tex = _load_texture_once(abs_port)
            if tex:
                arcade.draw_texture_rect(tex, arcade.LBWH(rx0 + 12, y1 - 34 - ps, ps, ps))
            else:
                kind = "robot" if "robot" in asset.asset_type else "power_armor"
                _draw_icon(kind, rx0 + 48, y1 - 70, 60, col)

            dy = y1 - 38
            arcade.draw_text(asset.name.upper(), rx0 + 100, dy, palette.HEADER, font_size=16, bold=True)
            dy -= 22
            arcade.draw_text(asset.display_role.upper(), rx0 + 100, dy, col, font_size=11)
            dy -= 22

            # Deploy cost
            if asset.deploy_cost > 0:
                arcade.draw_text(f"DEPLOY COST: ¥{asset.deploy_cost} / mission", rx0 + 100, dy, palette.RESOURCE, font_size=10)
                dy -= 18

            # Divider
            arcade.draw_line(rx0 + 12, dy, rx1 - 12, dy, palette.GRID_LINE, 1)
            dy -= 18

            # Stats block
            stats = asset.combat_stats()
            stat_lines = [
                ("HP",      f"{stats.hp} / {stats.max_hp}", palette.TACTICAL_GREEN),
                ("DEFENSE", str(asset.armor.defense_bonus),  palette.ACCENT),
                ("PLATING", str(asset.armor.plating),        palette.MUTED_TEXT),
                ("MISSILE", str(asset.missile_capacity),     palette.WARNING),
                ("AP",      str(asset.action_points),        palette.ACCENT),
            ]
            for label, val, scol in stat_lines:
                arcade.draw_text(f"{label:<10}", rx0 + 14, dy, palette.MUTED_TEXT, font_size=11)
                arcade.draw_text(val, rx0 + 110, dy, scol, font_size=11, bold=True)
                dy -= 20

            dy -= 6
            arcade.draw_line(rx0 + 12, dy, rx1 - 12, dy, palette.GRID_LINE, 1)
            dy -= 18

            # Hardpoints (weapons)
            arcade.draw_text("WEAPONS", rx0 + 14, dy, palette.MUTED_TEXT, font_size=10, bold=True)
            dy -= 16
            if asset.hardpoints:
                for hp in asset.hardpoints[:4]:
                    arcade.draw_text(
                        f"• {hp.name}  RNG {hp.range_cells}  DMG+{hp.damage_bonus}",
                        rx0 + 20, dy, palette.TEXT, font_size=10,
                    )
                    dy -= 16
            else:
                arcade.draw_text("None equipped", rx0 + 20, dy, (40, 60, 80), font_size=10)
                dy -= 16

            dy -= 6
            arcade.draw_line(rx0 + 12, dy, rx1 - 12, dy, palette.GRID_LINE, 1)
            dy -= 18

            # Pilot assignment (power armors only)
            if is_armor:
                arcade.draw_text("PILOT ASSIGNMENT", rx0 + 14, dy, palette.WARNING, font_size=10, bold=True)
                dy -= 18
                pilot = getattr(asset, 'pilot_agent_name', None)
                arcade.draw_text(
                    f"Assigned: {pilot if pilot else 'None — click to assign'}",
                    rx0 + 14, dy,
                    palette.TACTICAL_GREEN if pilot else palette.MUTED_TEXT,
                    font_size=10,
                )
                dy -= 18

                # Agent buttons
                bw_per = max(80, (rx1 - rx0 - 28) // max(1, len(gs.characters)))
                bx = rx0 + 14
                for ai, char in enumerate(gs.characters[:4]):
                    assigned = (getattr(asset, 'pilot_agent_name', None) == char.name)
                    bcol = palette.TACTICAL_GREEN if assigned else palette.ACCENT
                    bfill = (18, 46, 18, 220) if assigned else (12, 24, 32, 200)
                    bw_ = min(bw_per, 90)
                    _rect(bx, dy - 28, bx + bw_, dy, bfill)
                    arcade.draw_line(bx, dy, bx + bw_, dy, bcol, 2)
                    arcade.draw_text(
                        char.name.split()[0].upper(), bx + bw_ // 2, dy - 14,
                        bcol, font_size=9, bold=assigned,
                        anchor_x="center", anchor_y="center",
                    )
                    self._hits.append(_HitRegion(bx, dy - 28, bx + bw_, dy, "assign_pilot", (sel_idx, char.name)))
                    bx += bw_ + 4

                # Clear pilot button
                _rect(bx, dy - 28, bx + 48, dy, (28, 12, 12, 200))
                arcade.draw_line(bx, dy, bx + 48, dy, palette.DANGER, 1)
                arcade.draw_text("CLEAR", bx + 24, dy - 14, palette.DANGER, font_size=8, anchor_x="center", anchor_y="center")
                self._hits.append(_HitRegion(bx, dy - 28, bx + 48, dy, "assign_pilot", (sel_idx, None)))
                dy -= 36

            # Maintenance info
            arcade.draw_line(rx0 + 12, dy, rx1 - 12, dy, palette.GRID_LINE, 1)
            dy -= 16
            m = asset.maintenance
            arcade.draw_text("MAINTENANCE", rx0 + 14, dy, palette.MUTED_TEXT, font_size=10, bold=True)
            dy -= 16
            for line in [f"Integrity: {m.integrity}%", f"Repair: ¥{m.repair_cost}", f"Upkeep/day: ¥{m.base_upkeep}"]:
                arcade.draw_text(line, rx0 + 20, dy, palette.TEXT, font_size=10)
                dy -= 14

            # Action buttons
            btn_y = y0 + 8
            btn_h = 36
            btn_w = (rx1 - rx0 - 30) // 2

            rep_cost = m.repair_cost
            can_rep  = rep_cost > 0 and gs.available_funds >= rep_cost
            rep_col  = palette.ACCENT if can_rep else (40, 50, 55)
            _rect(rx0 + 10, btn_y, rx0 + 10 + btn_w, btn_y + btn_h, (8, 20, 28, 220))
            arcade.draw_line(rx0 + 10, btn_y + btn_h, rx0 + 10 + btn_w, btn_y + btn_h, rep_col, 2)
            arcade.draw_text(f"REPAIR  ¥{rep_cost}", rx0 + 10 + btn_w // 2, btn_y + btn_h // 2, rep_col, font_size=11, bold=True, anchor_x="center", anchor_y="center")
            self._hits.append(_HitRegion(rx0 + 10, btn_y, rx0 + 10 + btn_w, btn_y + btn_h, "asset_repair", sel_idx))

            dep_sel   = asset.id in gs.selected_asset_ids
            dep_col   = palette.TACTICAL_GREEN if asset.is_deployable else (40, 50, 55)
            dep_fill  = (22, 50, 18, 230) if dep_sel else (8, 20, 28, 220)
            dep_label = "★ DEPLOYED" if dep_sel else "DEPLOY"
            _rect(rx0 + 14 + btn_w + 8, btn_y, rx1 - 10, btn_y + btn_h, dep_fill)
            arcade.draw_line(rx0 + 14 + btn_w + 8, btn_y + btn_h, rx1 - 10, btn_y + btn_h, dep_col, 2)
            arcade.draw_text(dep_label, (rx0 + 14 + btn_w + 8 + rx1 - 10) // 2, btn_y + btn_h // 2, dep_col, font_size=11, bold=True, anchor_x="center", anchor_y="center")
            self._hits.append(_HitRegion(rx0 + 14 + btn_w + 8, btn_y, rx1 - 10, btn_y + btn_h, "asset_deploy_toggle", sel_idx))
        else:
            _panel(rx0, y0, rx1, y1, "ASSET PROFILE", palette.PANEL_BORDER)
            arcade.draw_text("No assets in hangar.", rx0 + 14, (y0 + y1) // 2, palette.MUTED_TEXT, font_size=12, anchor_y="center")
            arcade.draw_text("Purchase from the catalog below.", rx0 + 14, (y0 + y1) // 2 - 22, (40, 65, 80), font_size=10, anchor_y="center")

    # ── SQUAD tab ─────────────────────────────────────────────────────────────

    def _draw_squad_tab(self, x0: int, y0: int, x1: int, y1: int) -> None:
        gs  = self.game_state
        gap = 10
        total_w = x1 - x0
        # 3-column split: agents | equipment | missions
        aw  = int(total_w * 0.27)   # agent roster
        ew  = int(total_w * 0.28)   # equipment panel
        # mission panel fills the rest
        ax0, ax1 = x0,              x0 + aw
        ex0, ex1 = ax1 + gap,       ax1 + gap + ew
        mx0, mx1 = ex1 + gap,       x1

        self._draw_agent_panel(ax0, y0, ax1, y1, gs)
        self._draw_equipment_panel(ex0, y0, ex1, y1, gs)
        self._draw_mission_panel(mx0, y0, mx1, y1, gs)

    def _draw_agent_panel(self, x0: int, y0: int, x1: int, y1: int, gs: GameState) -> None:
        _panel(x0, y0, x1, y1, f"AGENTS  {len(gs.selected_agent_names)}/{len(gs.characters)}", palette.ACCENT)
        from game.ui.panels import _load_texture_once

        selected_set  = set(gs.selected_agent_names)
        card_h        = 72
        card_gap      = 6
        chooser_h     = 40
        scroll_top    = y1 - 34

        for i, char in enumerate(gs.characters):
            ct = scroll_top - i * (card_h + card_gap)
            cb = ct - card_h
            if cb < y0 + chooser_h:
                break

            active  = (i == self.deployment_cursor)
            sel     = char.name in selected_set
            filling = palette.AGENT_CARD_SELECTED if sel else (
                (54, 68, 44, 230) if active else palette.AGENT_CARD_FILL
            )
            _rect(x0 + 8, cb, x1 - 8, ct, filling)
            border_col = palette.ACTIVE_AGENT_BORDER if active else (
                palette.TACTICAL_GREEN if sel else palette.PANEL_BORDER_MUTED
            )
            arcade.draw_line(x0 + 8, ct, x1 - 8, ct, border_col, 2)

            # Portrait placeholder / small square
            ps = 48
            px0, px1 = x0 + 14, x0 + 14 + ps
            py0, py1 = cb + (card_h - ps) // 2, cb + (card_h - ps) // 2 + ps
            _rect(px0, py0, px1, py1, palette.AGENT_PORTRAIT_FILL)
            role_col = {
                "sniper": palette.ROLE_SNIPER,
                "psi":    palette.ROLE_PSI,
            }.get(char.role, palette.ROLE_SAMURAI)
            arcade.draw_line(px0, py1, px1, py1, role_col, 2)

            # Try portrait
            from game.ui.panels import _load_texture_once
            ppath = portrait_path_for_character(char)
            tex   = _load_texture_once(ppath) if ppath else None
            if tex:
                arcade.draw_texture_rect(tex, arcade.LBWH(px0, py0, ps, ps))

            # Text info
            tx = px1 + 10
            arcade.draw_text(char.name.upper(), tx, ct - 16, palette.TEXT, font_size=13, bold=True)
            arcade.draw_text(char.role.upper(), tx, ct - 32, role_col, font_size=11)

            # HP / stress bars
            bw = x1 - 20 - tx
            max_hp = max(1, char.stats.max_hp)
            draw_small_meter(tx, cb + 22, bw, max(0, char.stats.hp / max_hp), palette.TACTICAL_GREEN)
            draw_small_meter(tx, cb + 10, bw, max(0, char.stress / 100), palette.WARNING)

            if char.recovery_turns > 0:
                arcade.draw_text(
                    f"RECOVERING {char.recovery_turns}d", tx, cb + 34,
                    palette.DANGER, font_size=8,
                )

            # Selected checkmark
            if sel:
                arcade.draw_text("✓", x1 - 22, ct - 22, palette.TACTICAL_GREEN, font_size=14, bold=True)

            if char.pending_points > 0:
                _badge(f"+{char.pending_points}", x1 - 46, ct - 20, palette.RESOURCE)

            self._hits.append(_HitRegion(x0 + 8, cb, x1 - 8, ct, "agent_card", i))

        else:
            btn_y = y0 + 4
            btn_h = 32
            _rect(x0 + 10, btn_y, x1 - 10, btn_y + btn_h, (8, 24, 14, 220))
            arcade.draw_line(x0 + 10, btn_y + btn_h, x1 - 10, btn_y + btn_h, palette.TACTICAL_GREEN, 2)
            arcade.draw_text(
                "RECRUIT WINDOW  [N]",
                (x0 + x1) // 2, btn_y + btn_h // 2,
                palette.TACTICAL_GREEN, font_size=11, bold=True,
                anchor_x="center", anchor_y="center",
            )
            self._hits.append(_HitRegion(x0 + 10, btn_y, x1 - 10, btn_y + btn_h, "recruit_prompt", None))

    # ── Equipment panel ────────────────────────────────────────────────────────

    _SLOT_ICONS: dict[str, str] = {
        "primary_weapon": "armory",
        "sidearm":        "armory",
        "armor":          "shield",
        "utility_item":   "medbay",
        "psi_focus":      "intel",
        "special_gear":   "black_ops",
    }
    _SLOT_LABELS: dict[str, str] = {
        "primary_weapon": "PRIMARY",
        "sidearm":        "SIDEARM",
        "armor":          "ARMOR",
        "utility_item":   "UTILITY",
        "psi_focus":      "PSI FOCUS",
        "special_gear":   "SPECIAL",
    }
    _SLOT_COLORS: dict[str, tuple] = {
        "primary_weapon": (220, 140,  60),
        "sidearm":        (200, 110,  50),
        "armor":          ( 80, 180, 120),
        "utility_item":   ( 80, 160, 220),
        "psi_focus":      (160,  80, 220),
        "special_gear":   (220, 180,  60),
    }

    def _draw_equipment_panel(self, x0: int, y0: int, x1: int, y1: int, gs: GameState) -> None:
        from game.management.equipment import EQUIPMENT_SLOTS as _SLOTS
        from game.ui.panels import _draw_icon

        char: object | None = (
            gs.characters[self.deployment_cursor]
            if self.deployment_cursor < len(gs.characters)
            else None
        )

        header_title = f"LOADOUT — {char.name.upper()[:16]}" if char else "LOADOUT"
        _panel(x0, y0, x1, y1, header_title, palette.ACCENT)

        if char is None:
            arcade.draw_text(
                "Select an agent", x0 + 14, (y0 + y1) // 2,
                palette.MUTED_TEXT, font_size=11, anchor_y="center",
            )
            return

        loadout = char.loadout

        # ── Stat upgrade panel (shown when pending_points > 0) ───────────
        pts = char.pending_points
        stat_panel_h = 0
        if pts > 0:
            stat_panel_h = 90
            sp_top = y1 - 34
            sp_bot = sp_top - stat_panel_h
            _rect(x0 + 8, sp_bot, x1 - 8, sp_top, (20, 40, 18, 220))
            arcade.draw_line(x0 + 8, sp_top, x1 - 8, sp_top, palette.RESOURCE, 2)
            # Blink indicator
            pulse_col = (*palette.RESOURCE[:3], int(180 + 70 * math.sin(self._elapsed * 3.0)))
            arcade.draw_text(
                f"▲ {pts} STAT POINT{'S' if pts != 1 else ''}  AVAILABLE",
                (x0 + x1) // 2, sp_top - 14,
                pulse_col, font_size=10, bold=True,
                anchor_x="center", anchor_y="center",
            )
            # Six stat buttons: STR AGI PSI DEF CON
            upgradeable = [("STR", "str"), ("AGI", "agi"), ("PSI", "psi"),
                           ("DEF", "def"), ("CON", "con")]
            btn_w = (x1 - x0 - 20) // len(upgradeable)
            for si, (slbl, skey) in enumerate(upgradeable):
                bx = x0 + 10 + si * btn_w
                by = sp_bot + 8
                bh = 32
                cur_val = getattr(char.stats, skey, 0) if hasattr(char.stats, skey) else getattr(char.stats, skey, 0)
                _rect(bx, by, bx + btn_w - 4, by + bh, (14, 28, 14, 220))
                arcade.draw_line(bx, by + bh, bx + btn_w - 4, by + bh, palette.TACTICAL_GREEN, 1)
                arcade.draw_text(
                    f"+{slbl}", bx + (btn_w - 4) // 2, by + bh // 2 + 4,
                    palette.TACTICAL_GREEN, font_size=9, bold=True,
                    anchor_x="center", anchor_y="center",
                )
                arcade.draw_text(
                    str(cur_val), bx + (btn_w - 4) // 2, by + 6,
                    palette.MUTED_TEXT, font_size=8,
                    anchor_x="center",
                )
                self._hits.append(_HitRegion(
                    bx, by, bx + btn_w - 4, by + bh,
                    "spend_stat_point",
                    (self.deployment_cursor, skey),
                ))

        talent_panel_h = 112
        slot_h  = min(78, (y1 - y0 - 90 - stat_panel_h - talent_panel_h - 16) // len(_SLOTS))
        slot_gap = 4
        sy       = y1 - 34 - (stat_panel_h + 6 if pts > 0 else 0)

        for slot in _SLOTS:
            item     = loadout.item_for_slot(slot)
            slot_col = self._SLOT_COLORS.get(slot, palette.ACCENT)
            label    = self._SLOT_LABELS.get(slot, slot.replace("_", " ").upper())
            icon_k   = self._SLOT_ICONS.get(slot, "select")

            # Slot card
            sl, sb, sr, st = x0 + 8, sy - slot_h, x1 - 8, sy
            fill = (*slot_col, 40) if item else (8, 18, 24, 200)
            _rect(sl, sb, sr, st, fill)
            arcade.draw_line(sl, st, sr, st, slot_col if item else palette.PANEL_BORDER_MUTED, 2)
            arcade.draw_line(sl, sb, sr, sb, palette.GRID_LINE, 1)

            # Icon
            icon_cx = sl + 22
            icon_cy = (sb + st) // 2
            _draw_icon(icon_k, icon_cx, icon_cy, 20, slot_col)

            # Slot label
            tx = sl + 44
            arcade.draw_text(label, tx, st - 16, palette.MUTED_TEXT, font_size=10, bold=True)

            # Item name / Empty
            if item:
                arcade.draw_text(
                    item.name.upper(), tx, st - 30,
                    palette.TEXT, font_size=12, bold=True,
                )
                # Extra info for weapons / armor (priority line)
                from game.management.equipment import Weapon, Armor
                if isinstance(item, Weapon):
                    arcade.draw_text(
                        f"RNG {item.range_cells}  DMG+{item.damage_bonus}  [{item.action_name}]",
                        tx, sb + 22,
                        (*slot_col, 220), font_size=10,
                    )
                elif isinstance(item, Armor):
                    arcade.draw_text(
                        f"MITIGATION +{item.mitigation}",
                        tx, sb + 22,
                        (*slot_col, 220), font_size=10,
                    )
                # Stat bonuses
                bonuses = item.stat_bonuses
                bonus_parts = [f"+{v} {k.upper()}" for k, v in bonuses.items() if v > 0]
                if bonus_parts:
                    arcade.draw_text(
                        "  ".join(bonus_parts[:4]),
                        tx, sb + 8,
                        slot_col, font_size=10,
                    )
            else:
                arcade.draw_text(
                    "— EMPTY —", tx, (sb + st) // 2,
                    (40, 70, 90), font_size=11, anchor_y="center",
                )

            # Cycle arrows: ◀ ▶
            arr_y = (sb + st) // 2
            _rect(sr - 48, arr_y - 9, sr - 28, arr_y + 9, (12, 24, 32, 200))
            _rect(sr - 24, arr_y - 9, sr -  4, arr_y + 9, (12, 24, 32, 200))
            arcade.draw_text("◀", sr - 38, arr_y, palette.ACCENT, font_size=10, anchor_x="center", anchor_y="center")
            arcade.draw_text("▶", sr - 14, arr_y, palette.ACCENT, font_size=10, anchor_x="center", anchor_y="center")

            self._hits.append(_HitRegion(sr - 48, arr_y - 9, sr - 28, arr_y + 9, "equip_prev", (self.deployment_cursor, slot)))
            self._hits.append(_HitRegion(sr - 24, arr_y - 9, sr -  4, arr_y + 9, "equip_next", (self.deployment_cursor, slot)))

            sy -= slot_h + slot_gap

        talent_bottom = y0 + 8
        talent_top = talent_bottom + talent_panel_h
        _rect(x0 + 8, talent_bottom, x1 - 8, talent_top, (10, 22, 30, 210))
        arcade.draw_line(x0 + 8, talent_top, x1 - 8, talent_top, palette.ACCENT, 2)
        arcade.draw_text(
            f"SPECIALIZATION  |  {char.role.upper()}  |  POINTS {char.talent_points}",
            x0 + 16,
            talent_top - 14,
            palette.ACCENT,
            font_size=10,
            bold=True,
        )
        unlocked = set(char.specializations)
        nodes = list(talent_nodes_for_role(char.role))
        cols = 3
        node_gap = 6
        node_w = max(90, (x1 - x0 - 32 - node_gap * (cols - 1)) // cols)
        node_h = 36
        node_top = talent_top - 26
        for idx, node in enumerate(nodes[:6]):
            row = idx // cols
            col = idx % cols
            left = x0 + 16 + col * (node_w + node_gap)
            top = node_top - row * (node_h + 6)
            bottom = top - node_h
            unlocked_node = node.id in unlocked
            available_node = node in available_talent_nodes(char.role, unlocked)
            if unlocked_node:
                fill = (*palette.TACTICAL_GREEN[:3], 70)
                border = palette.TACTICAL_GREEN
            elif available_node and char.talent_points > 0:
                fill = (36, 68, 48, 190)
                border = palette.RESOURCE
            else:
                fill = (14, 24, 34, 190)
                border = palette.PANEL_BORDER_MUTED
            _rect(left, bottom, left + node_w, top, fill)
            arcade.draw_line(left, top, left + node_w, top, border, 2)
            arcade.draw_text(node.name.upper(), left + 8, top - 13, palette.TEXT, font_size=9, bold=True)
            arcade.draw_text(
                node.description,
                left + 8,
                bottom + 6,
                palette.MUTED_TEXT,
                font_size=7,
                width=max(60, node_w - 16),
            )
            status = "OWNED" if unlocked_node else ("UNLOCK" if available_node else "LOCKED")
            arcade.draw_text(status, left + node_w - 8, bottom + 6, border, font_size=8, bold=True, anchor_x="right")
            prereq = " + ".join(node.prerequisites) if node.prerequisites else "START"
            arcade.draw_text(prereq[:18], left + 8, bottom + node_h - 24, border, font_size=7)
            if available_node and char.talent_points > 0 and not unlocked_node:
                self._hits.append(_HitRegion(left, bottom, left + node_w, top, "unlock_talent", (self.deployment_cursor, node.id)))

        # Summary row: total bonuses
        bonuses_total = loadout.total_stat_bonuses()
        if bonuses_total:
            summary_y = talent_top + 6
            arcade.draw_line(x0 + 10, summary_y + 18, x1 - 10, summary_y + 18, palette.GRID_LINE, 1)
            bx = x0 + 12
            by = summary_y
            arcade.draw_text("TOTALS:", bx, by, palette.MUTED_TEXT, font_size=10)
            bx += 66
            for stat, val in bonuses_total.items():
                if val:
                    col = palette.TACTICAL_GREEN if val > 0 else palette.DANGER
                    arcade.draw_text(f"{stat.upper()} {val:+d}", bx, by, col, font_size=10)
                    bx += 80
                    if bx > x1 - 20:
                        break

    def _draw_mission_panel(self, x0: int, y0: int, x1: int, y1: int, gs: GameState) -> None:
        content_h = y1 - y0
        # Split: top 55% mission list, bottom 45% mission detail
        split_y = y0 + int(content_h * 0.45)

        # ── Mission list ─────────────────────────────────────────────────
        _panel(x0, split_y, x1, y1, "MISSION BOARD", palette.WARNING)

        card_h   = 70
        card_gap = 8
        mc_top   = y1 - 34
        missions = gs.mission_templates

        for mi, m in enumerate(missions[:5]):
            ct = mc_top - mi * (card_h + card_gap)
            cb = ct - card_h
            if cb < split_y + 4:
                break

            selected = (mi == gs.selected_mission_index)
            fill = (38, 56, 68, 230) if selected else (10, 20, 26, 210)
            _rect(x0 + 8, cb, x1 - 8, ct, fill)
            risk_col = _risk_color(m.risk_level)
            arcade.draw_line(x0 + 8, ct, x1 - 8, ct, risk_col if selected else palette.PANEL_BORDER_MUTED, 2)

            # Index badge
            _badge(f"{mi + 1:02d}", x0 + 10, cb + 2, risk_col)

            # Title
            arcade.draw_text(m.title.upper(), x0 + 66, ct - 18, palette.TEXT, font_size=13, bold=True)

            # Risk badge — risk_level may be int (1-5) or str
            _risk_label = (
                m.risk_level.upper()
                if isinstance(m.risk_level, str)
                else {1: "LOW", 2: "LOW", 3: "MED", 4: "HIGH", 5: "CRIT"}.get(m.risk_level, str(m.risk_level))
            )
            _badge(_risk_label, x1 - 90, ct - 20, risk_col)

            # Metadata row
            meta_parts = []
            if hasattr(m, "target_faction") and m.target_faction:
                meta_parts.append(m.target_faction)
            if hasattr(m, "duration_days") and m.duration_days:
                meta_parts.append(f"{m.duration_days}d")
            if hasattr(m, "fund_reward") and m.fund_reward:
                meta_parts.append(f"+¥{m.fund_reward}")
            arcade.draw_text(
                "  ·  ".join(meta_parts),
                x0 + 66, ct - 36, palette.MUTED_TEXT, font_size=11,
            )

            # Objective type
            arcade.draw_text(
                m.objective_type.upper(), x0 + 66, cb + 8,
                palette.ACCENT, font_size=11,
            )

            # Emotional impact
            if hasattr(m, "emotional_impact") and m.emotional_impact:
                arcade.draw_text(
                    f"⚠ {m.emotional_impact}", x1 - 220, cb + 8,
                    palette.MUTED_TEXT, font_size=10,
                )

            self._hits.append(_HitRegion(x0 + 8, cb, x1 - 8, ct, "select_mission", mi))

        # ── Selected mission detail ───────────────────────────────────────
        _panel(x0, y0, x1, split_y, "MISSION DETAILS", palette.ACCENT)

        m = _selected_mission(gs)
        if m:
            dx, dy = x0 + 14, split_y - 44

            # Title
            arcade.draw_text(m.title.upper(), dx, dy, palette.HEADER, font_size=16, bold=True)
            dy -= 30

            # Risk + reward row
            risk_col = _risk_color(m.risk_level)
            _risk_label2 = (
                m.risk_level.upper()
                if isinstance(m.risk_level, str)
                else {1: "LOW", 2: "LOW", 3: "MED", 4: "HIGH", 5: "CRIT"}.get(m.risk_level, str(m.risk_level))
            )
            _badge(_risk_label2, dx, dy, risk_col)
            arcade.draw_text(f"¥ {m.fund_reward:,} reward", dx + 80, dy + 3, palette.RESOURCE, font_size=12)
            dur = getattr(m, "duration_days", 1)
            arcade.draw_text(f"{dur} day{'s' if dur != 1 else ''}", dx + 220, dy + 3, palette.MUTED_TEXT, font_size=12)
            dy -= 30

            # Objective text
            obj_lines = (m.objective_text or "").split(". ")
            for ln in obj_lines[:3]:
                if not ln:
                    continue
                arcade.draw_text(ln.strip(), dx, dy, palette.TEXT, font_size=11)
                dy -= 18

            # Complications
            complications = getattr(m, "possible_complications", [])
            if complications:
                dy -= 6
                comp_names = ", ".join(
                    getattr(c, "name", str(c)) for c in complications[:2]
                )
                arcade.draw_text(
                    _trim_text(f"Complications: {comp_names}", 92),
                    dx, dy, palette.WARNING, font_size=10,
                )
                dy -= 18

            # Breakdown risk
            selected_squad = selected_deployable_agents(gs.characters, gs.selected_agent_names)
            at_risk = agents_at_breaking_risk(selected_squad, m) if selected_squad else []
            if at_risk:
                names = ", ".join(a.name for a in at_risk)
                arcade.draw_text(
                    _trim_text(f"⚠ BREAKDOWN RISK: {names}", 92),
                    dx, dy, palette.DANGER, font_size=11, bold=True,
                )
                dy -= 18

        # Launch button (very prominent)
        lb = y0 + 28
        lt = lb + 46
        _rect(x0 + 10, lb, x1 - 10, lt, (10, 34, 16, 240))
        arcade.draw_line(x0 + 10, lt, x1 - 10, lt, palette.TACTICAL_GREEN, 3)
        arcade.draw_line(x0 + 10, lb, x1 - 10, lb, palette.TACTICAL_GREEN, 1)
        # Pulse the launch button text brightness
        pulse = 0.7 + 0.3 * math.sin(self._elapsed * 2.5)
        lbl_col = (
            int(palette.TACTICAL_GREEN[0] * pulse),
            int(palette.TACTICAL_GREEN[1] * pulse),
            int(palette.TACTICAL_GREEN[2] * pulse),
        )
        arcade.draw_text(
            "▶  LAUNCH MISSION  [B]",
            (x0 + x1) // 2, lb + 22,
            lbl_col, font_size=15, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hits.append(_HitRegion(x0 + 10, lb, x1 - 10, lt, "launch_mission", None))

        # Downtime menu
        dt_top = lb - 10
        dt_bottom = max(y0 + 84, dt_top - 108)
        _rect(x0 + 10, dt_bottom, x1 - 10, dt_top, (10, 20, 28, 220))
        arcade.draw_line(x0 + 10, dt_top, x1 - 10, dt_top, palette.ACCENT, 2)
        arcade.draw_text("DOWNTIME [7-9]", x0 + 18, dt_top - 16, palette.ACCENT, font_size=10, bold=True)
        by = dt_top - 42
        for idx, activity in enumerate(DOWNTIME_ACTIVITIES):
            row_h = 26
            row_top = by - idx * (row_h + 6)
            row_bottom = row_top - row_h
            if row_bottom <= dt_bottom + 4:
                break
            _rect(x0 + 14, row_bottom, x1 - 14, row_top, (8, 16, 22, 210))
            arcade.draw_text(
                f"{idx + 7}. {activity.label}", x0 + 20, row_top - 16, palette.TEXT, font_size=10, bold=True
            )
            arcade.draw_text(
                f"-{activity.days_cost}d  -{activity.resource_cost} {activity.resource_key}  morale {activity.morale_delta:+}  stress {activity.stress_delta:+}",
                x0 + 180, row_top - 16, palette.MUTED_TEXT, font_size=9,
            )
            self._hits.append(_HitRegion(x0 + 14, row_bottom, x1 - 14, row_top, "downtime_activity", idx))

        # Message display
        if self.message:
            arcade.draw_text(
                self.message, x0 + 14, y0 + 72,
                palette.WARNING, font_size=10,
            )

    # ── RESEARCH tab ──────────────────────────────────────────────────────────

    def _draw_research_tab(self, x0: int, y0: int, x1: int, y1: int) -> None:
        gs = self.game_state
        _panel(x0, y0, x1, y1, "RESEARCH LABORATORY", palette.ROLE_PSI)

        lines = build_research_lab_lines(gs)
        ry = y1 - 38
        for line in lines[:24]:
            col = palette.RESOURCE if line.startswith("✓") else (
                palette.ACCENT if "[" in line or "day" in line.lower() else
                palette.TEXT
            )
            arcade.draw_text(line, x0 + 14, ry, col, font_size=12)
            ry -= 20
            if ry < y0 + 10:
                break

        # Research project start buttons (from corp view logic)
        completed   = set(gs.completed_research)
        active_ids  = {a.project_id for a in gs.active_research}
        available   = gs.research_tree.available_projects(completed, active_ids)

        bx = x0 + 14
        by = y0 + 8
        arcade.draw_line(x0 + 12, by + 56, x1 - 12, by + 56, palette.GRID_LINE, 1)
        arcade.draw_text("AVAILABLE PROJECTS", bx, by + 60, palette.MUTED_TEXT, font_size=9)
        for pi, proj in enumerate(available[:6]):
            bh = 30
            bw = (x1 - x0 - 28) // 3 - 6
            col_i = pi % 3
            row_i = pi // 3
            bx0 = x0 + 14 + col_i * (bw + 6)
            by0 = by + 76 + row_i * (bh + 8)
            _rect(bx0, by0, bx0 + bw, by0 + bh, (8, 20, 30, 220))
            arcade.draw_line(bx0, by0 + bh, bx0 + bw, by0 + bh, palette.ROLE_PSI, 1)
            arcade.draw_text(proj.name[:22], bx0 + 6, by0 + bh - 14, palette.TEXT, font_size=9)
            arcade.draw_text(f"¥{proj.funds_cost}", bx0 + 6, by0 + 4, palette.RESOURCE, font_size=8)
            self._hits.append(_HitRegion(bx0, by0, bx0 + bw, by0 + bh, f"start_research_{pi}", None))

    # ── INTEL tab ─────────────────────────────────────────────────────────────

    def _draw_intel_tab(self, x0: int, y0: int, x1: int, y1: int) -> None:
        gs  = self.game_state
        gap = 10
        content_w = max(0, x1 - x0 - gap)
        hw = min(
            max(240, int(content_w * 0.60)),
            max(120, content_w - 150),
        )

        # ── Left: Narrative event log ────────────────────────────────────
        lx0, lx1 = x0, x0 + hw
        _panel(lx0, y0, lx1, y1, "NARRATIVE FEED", palette.ACCENT)

        iy = y1 - 36
        for log_entry in reversed(gs.event_log[-24:]):
            if iy < y0 + 12:
                break
            line = log_entry if isinstance(log_entry, str) else str(log_entry)
            col = (
                palette.DANGER if any(w in line.lower() for w in ("killed", "wounded", "lost", "failed"))
                else palette.TACTICAL_GREEN if any(w in line.lower() for w in ("success", "victory", "completed", "recruited"))
                else palette.TEXT
            )
            arcade.draw_text(
                line[:120],
                lx0 + 10,
                iy,
                col,
                font_size=11,
                width=max(10, lx1 - lx0 - 24),
                align="left",
            )
            iy -= 17

        # ── Right: Latest debrief ────────────────────────────────────────
        rx0, rx1 = lx1 + gap, x1
        _panel(rx0, y0, rx1, y1, "LATEST DEBRIEF", palette.HEADER)

        dy = y1 - 36
        debrief = getattr(gs, "latest_mission_debrief", None)
        if debrief:
            header_lines = [
                debrief.get("mission_title", ""),
                debrief.get("mission_outcome", debrief.get("outcome", "")),
            ]
            for text in [line for line in header_lines if line]:
                arcade.draw_text(str(text)[:90], rx0 + 14, dy, palette.HEADER if text == header_lines[0] else palette.TEXT, font_size=11)
                dy -= 19

            blocks = (
                ("Décision clé", debrief.get("decision_key", "")),
                ("Risque pris", debrief.get("risk_taken", "")),
                ("Action héroïque", debrief.get("heroic_action", "")),
            )
            for title, text in blocks:
                arcade.draw_text(title, rx0 + 12, dy, palette.MUTED_TEXT, font_size=9)
                dy -= 14
                arcade.draw_text(str(text)[:120], rx0 + 14, dy, palette.TEXT, font_size=10, width=max(10, rx1 - rx0 - 28), align="left")
                dy -= 24

            for line in debrief.get("lines", [])[:6]:
                if isinstance(line, dict) and line.get("text"):
                    arcade.draw_text(
                        str(line.get("text"))[:120],
                        rx0 + 14,
                        dy,
                        palette.TEXT,
                        font_size=10,
                        width=max(10, rx1 - rx0 - 28),
                        align="left",
                    )
                    dy -= 15

            rpg_links = debrief.get("rpg_links", [])
            if rpg_links:
                arcade.draw_text("RPG LINKS", rx0 + 12, dy - 2, palette.MUTED_TEXT, font_size=9)
                dy -= 18
                for line in rpg_links[:3]:
                    arcade.draw_text(str(line)[:120], rx0 + 14, dy, palette.TEXT, font_size=10, width=max(10, rx1 - rx0 - 28), align="left")
                    dy -= 15
        else:
            arcade.draw_text("No debrief data yet.", rx0 + 14, y1 - 60, palette.MUTED_TEXT, font_size=11)
            arcade.draw_text("Launch a mission to generate a debrief.", rx0 + 14, y1 - 80, (50, 80, 95), font_size=9)

        # Aftermath
        aftermath = getattr(gs, "latest_agent_aftermath", [])
        if aftermath:
            arcade.draw_line(rx0 + 12, dy - 4, rx1 - 12, dy - 4, palette.GRID_LINE, 1)
            dy -= 20
            arcade.draw_text("AFTERMATH", rx0 + 12, dy, palette.MUTED_TEXT, font_size=9)
            dy -= 18
            for line in aftermath:
                arcade.draw_text(
                    line[:100],
                    rx0 + 14,
                    dy,
                    palette.TEXT,
                    font_size=10,
                    width=max(10, rx1 - rx0 - 28),
                    align="left",
                )
                dy -= 15

    # ── Bottom bar ────────────────────────────────────────────────────────────

    def _draw_bottom_bar(self, w: int, _h: int) -> None:
        _rect(0, 0, w, _BOT_BAR_H, palette.PANEL_FILL_DARK)
        arcade.draw_line(0, _BOT_BAR_H, w, _BOT_BAR_H, palette.PANEL_BORDER, 2)

        cy = _BOT_BAR_H // 2
        x  = 14

        def _btn(label: str, action: str, key_hint: str, col=None):
            nonlocal x
            col = col or palette.ACCENT
            bw = len(label) * 10 + 28
            _rect(x, 6, x + bw, _BOT_BAR_H - 6, (8, 20, 28, 220))
            arcade.draw_line(x, _BOT_BAR_H - 6, x + bw, _BOT_BAR_H - 6, col, 2)
            arcade.draw_text(
                f"{label} [{key_hint}]", x + 10, cy,
                col, font_size=12, anchor_y="center",
            )
            self._hits.append(_HitRegion(x, 6, x + bw, _BOT_BAR_H - 6, action, None))
            x += bw + 10

        _btn("ADVANCE DAY", "advance_day", "D",    palette.HEADER)
        _btn("SAVE",        "save",        "S",    palette.ACCENT)
        _btn("LOAD",        "load",        "L",    palette.MUTED_TEXT)

        # Slot selector
        sx = x
        arcade.draw_text(
            f"SLOT {self.selected_save_slot}",
            sx, cy, palette.MUTED_TEXT, font_size=10, anchor_y="center",
        )
        for di, (label, delta) in enumerate([("◀", -1), ("▶", 1)]):
            bx = sx + 64 + di * 28
            _rect(bx, 8, bx + 22, _BOT_BAR_H - 8, (12, 24, 32, 200))
            arcade.draw_text(label, bx + 11, cy, palette.ACCENT, font_size=11, anchor_x="center", anchor_y="center")
            self._hits.append(_HitRegion(bx, 8, bx + 22, _BOT_BAR_H - 8, "slot_delta", delta))
        x += 130

        # Tab hints
        arcade.draw_text(
            "F1 COMMAND  F2 CITY  F3 SQUAD  F4 RESEARCH  F5 INTEL  |  ESC → TITLE",
            x + 10, cy,
            (40, 65, 80), font_size=9, anchor_y="center",
        )

    # ── Action dispatch ───────────────────────────────────────────────────────

    def _dispatch(self, action: str, data: object) -> None:
        gs = self.game_state

        if action == "tab":
            self.active_tab = data
            return

        if action == "advance_day":
            self._do_advance_day()
            return

        if action == "save":
            self._do_save()
            return

        if action == "load":
            self._do_load()
            return

        if action == "slot_delta":
            self.selected_save_slot = ((self.selected_save_slot - 1 + data) % 5) + 1
            gs.add_event(f"Active save slot: {self.selected_save_slot}.")
            return

        if action == "agent_card":
            self.deployment_cursor = data
            self.message = ""
            now = time.monotonic()
            is_double_click = (
                self._last_agent_click_index == data
                and (now - self._last_agent_click_time) <= 0.35
            )
            self._last_agent_click_time = now
            self._last_agent_click_index = data
            char = gs.characters[data] if data < len(gs.characters) else None
            if char:
                if is_double_click:
                    self._open_agent_sheet(data)
                    self.pending_launch_confirm = False
                    self.message = f"Opened full sheet for {char.name}."
                    return
                gs.selected_agent_names, self.message = toggle_agent_selection(
                    gs.characters, gs.selected_agent_names, data
                )
                self.pending_launch_confirm = False
            return

        if action == "select_mission":
            gs.selected_mission_index = data
            self.pending_launch_confirm = False
            self.message = ""
            return

        if action == "launch_mission":
            self._do_launch_mission()
            return

        if action == "downtime_activity":
            self._do_downtime_activity(int(data))
            return

        if action == "recruit_prompt":
            self._do_recruit_prompt()
            return
        if action == "recruit_candidate":
            self._do_recruit_candidate(int(data))
            return
        if action == "recruit_close":
            self._close_recruit_window()
            return
        if action == "remove_agent":
            self._do_remove_agent()
            return
        if action == "unlock_talent":
            char_idx, node_id = data
            self._do_unlock_talent(char_idx, node_id)
            return

        if action == "sheet_close":
            self._close_agent_sheet()
            return

        if action == "sheet_spend_stat":
            char_idx, stat_key = data  # type: ignore[misc]
            self._do_spend_stat_point(char_idx, stat_key)
            return

        if action == "sheet_train_skills":
            self._do_train_skill_points(int(data))
            return

        if action.startswith("corp_upgrade_"):
            key = action.removeprefix("corp_upgrade_")
            costs = {
                "research":  {"intel": 5},
                "security":  {"credits": 10, "salvage": 2},
                "politics":  {"influence": 3},
                "black_ops": {"credits": 5, "intel": 3},
            }.get(key, {})
            if costs:
                self._do_corp_upgrade(key, costs)
            return

        if action.startswith("city_upgrade_"):
            key = action.removeprefix("city_upgrade_")
            costs = {
                "armaments":     {"credits": 5,  "salvage": 3},
                "garrisons":     {"credits": 10, "influence": 2},
                "defense_zones": {"credits": 5,  "salvage": 5},
            }.get(key, {})
            if costs:
                self._do_city_upgrade(key, costs)
            return

        if action.startswith("event_response_"):
            parts = action.split("_")
            if len(parts) >= 4:
                ei, ci = int(parts[2]), int(parts[3])
                self._do_event_response(ei, ci)
            return

        if action.startswith("start_research_"):
            idx = int(action.rsplit("_", 1)[-1])
            completed  = set(gs.completed_research)
            active_ids = {a.project_id for a in gs.active_research}
            available  = gs.research_tree.available_projects(completed, active_ids)
            if idx < len(available):
                gs.start_research(available[idx].id)
                gs.add_event(f"Research started: {available[idx].name}.")
            return

        if action == "spend_stat_point":
            char_idx, stat_key = data  # type: ignore[misc]
            self._do_spend_stat_point(char_idx, stat_key)
            return

        if action in ("equip_prev", "equip_next"):
            char_idx, slot = data  # type: ignore[misc]
            self._do_cycle_equipment(char_idx, slot, direction=1 if action == "equip_next" else -1)
            return

        if action == "asset_select":
            self._asset_cursor = data  # type: ignore[assignment]
            return

        if action == "asset_repair":
            self._do_asset_repair(data)  # type: ignore[arg-type]
            return

        if action == "asset_deploy_toggle":
            self._do_asset_deploy_toggle(data)  # type: ignore[arg-type]
            return

        if action == "catalog_acquire":
            self._do_catalog_acquire(data)
            return

        if action == "catalog_scroll":
            from game.management.spec_ops_assets import asset_catalog as _ac
            self._catalog_scroll = (self._catalog_scroll + data) % max(1, len(_ac()))
            return

        if action == "assign_pilot":
            asset_idx, agent_name = data
            self._do_assign_pilot(asset_idx, agent_name)
            return

        if action == "asset_acquire":
            self._do_asset_acquire()
            return

    # ── Game logic helpers ────────────────────────────────────────────────────

    def _do_advance_day(self) -> None:
        self.game_state.advance_one_day("manual command")
        self.game_state.add_event(push_action(self.notifications, "advance_day", True, f"Day {self.game_state.calendar.current_day}"))

    def _do_save(self) -> None:
        result: SaveSystemResult = SaveSystem.save_game(
            self.game_state, SaveSystem.slot_path(self.selected_save_slot)
        )
        self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))

    def _do_load(self) -> None:
        loaded, result = SaveSystem.load_game(SaveSystem.slot_path(self.selected_save_slot))
        self.game_state.add_event(push_action(self.notifications, "load", result.ok, result.message))
        if loaded is not None:
            self.game_state = loaded
            self.deployment_cursor = 0
            self.pending_launch_confirm = False
            ensure_mission_templates(self.game_state)

    def _do_corp_upgrade(self, key: str, costs: dict) -> None:
        if self.game_state.spend_resources(costs):
            self.game_state.corp_budget[key] = self.game_state.corp_budget.get(key, 0) + 10
            cost_txt = ", ".join(f"-{v} {k}" for k, v in costs.items())
            self.game_state.add_event(push_action(self.notifications, "budget_allocation", True, f"{key} ({cost_txt})"))
        else:
            cost_txt = ", ".join(f"{v} {k}" for k, v in costs.items())
            self.game_state.add_event(push_action(self.notifications, "budget_allocation", False, f"{key} requires {cost_txt}"))

    def _do_city_upgrade(self, key: str, costs: dict) -> None:
        if self.game_state.spend_resources(costs):
            self.game_state.city_budget[key] = self.game_state.city_budget.get(key, 0) + 10
            cost_txt = ", ".join(f"-{v} {k}" for k, v in costs.items())
            self.game_state.add_event(push_action(self.notifications, "budget_allocation", True, f"{key} ({cost_txt})"))
        else:
            cost_txt = ", ".join(f"{v} {k}" for k, v in costs.items())
            self.game_state.add_event(push_action(self.notifications, "budget_allocation", False, f"{key} requires {cost_txt}"))

    def _do_event_response(self, event_index: int, choice_index: int) -> None:
        events = self.game_state.active_events
        if event_index >= len(events):
            return
        event = events[event_index]
        if 0 <= choice_index < len(event.choices):
            self.game_state.respond_to_event(event.id, event.choices[choice_index].key)

    def _do_downtime_activity(self, activity_index: int) -> None:
        gs = self.game_state
        if activity_index < 0 or activity_index >= len(DOWNTIME_ACTIVITIES):
            return
        activity = DOWNTIME_ACTIVITIES[activity_index]
        squad = selected_deployable_agents(gs.characters, gs.selected_agent_names)
        result = apply_activity(gs, activity, squad)
        self.message = result
        gs.add_event(result)

    def _do_recruit_prompt(self) -> None:
        """Open the recruit chooser with a small list of named agents."""
        gs = self.game_state
        self._close_agent_sheet()
        self.pending_recruit_candidates = build_recruitment_candidates(gs.characters)
        self.recruit_window_open = True
        self.message = "Recruitment window opened."

    def _do_recruit_candidate(self, candidate_index: int) -> None:
        gs = self.game_state
        if candidate_index >= len(self.pending_recruit_candidates):
            return
        candidate = self.pending_recruit_candidates[candidate_index]
        if not gs.spend_funds(candidate.price, "recruitment", f"Recruited {candidate.name}."):
            blocked = blocked_recruit_reason(gs.available_funds, candidate.price)
            if blocked:
                self.message = blocked.to_ui_text()
                self.notifications.warning(self.message)
                gs.add_event(self.message)
            return
        agent = recruit_agent(
            gs.characters,
            candidate.role,
            candidate.name,
            stats=candidate.stats,
            skills=candidate.skill_ranks,
            sex=candidate.sex,
        )
        self.deployment_cursor = len(gs.characters) - 1
        self._close_recruit_window()
        self.message = f"{agent.name} joins as {candidate.role} for ¥{candidate.price}."
        gs.add_event(push_action(self.notifications, "recruitment", True, f"{agent.name} as {candidate.role} (¥{candidate.price})"))

    def _do_remove_agent(self) -> None:
        gs = self.game_state
        if not gs.characters:
            return
        index = min(max(self.deployment_cursor, 0), len(gs.characters) - 1)
        removed, sanitized_agents, sanitized_assets = remove_agent_from_roster(
            gs.characters,
            gs.spec_ops_assets,
            gs.selected_agent_names,
            gs.selected_asset_ids,
            index,
        )
        if removed is None:
            return
        gs.selected_agent_names = sanitized_agents
        gs.selected_asset_ids = sanitized_assets
        self.deployment_cursor = min(index, len(gs.characters) - 1) if gs.characters else 0
        self.pending_breakdown_confirmation = False
        self.pending_breakdown_mission_id = None
        self.pending_launch_confirm = False
        if self.expanded_agent_sheet_index is not None:
            if self.expanded_agent_sheet_index == index:
                self._close_agent_sheet()
            elif self.expanded_agent_sheet_index > index:
                self.expanded_agent_sheet_index -= 1
        self.message = f"{removed.name} removed from roster."
        gs.add_event(push_action(self.notifications, "remove_agent", True, removed.name))

    def _do_launch_mission(self) -> None:
        gs = self.game_state
        gs.selected_agent_names = sanitize_selected_agent_names(gs.characters, gs.selected_agent_names)
        selected_squad = selected_deployable_agents(gs.characters, gs.selected_agent_names)
        selected_mission = _selected_mission(gs)

        blocked = blocked_launch_reason(
            has_deployable_agent=any(is_deployable(c) for c in gs.characters),
            selected_count=len(selected_squad),
            mission_unavailable=selected_mission.id in gs.unavailable_mission_ids,
            mission_title=selected_mission.title,
        )
        if blocked is not None:
            self.message = blocked.to_ui_text()
            self.notifications.warning(self.message)
            gs.add_event(self.message)
            self.active_tab = "squad"
            return

        at_risk = agents_at_breaking_risk(selected_squad, selected_mission)
        if at_risk and not (
            self.pending_launch_confirm
            and self.pending_launch_mission_id == selected_mission.id
        ):
            self.pending_launch_confirm = True
            self.pending_launch_mission_id = selected_mission.id
            lead = at_risk[0]
            self.message = f"⚠ CONFIRM LAUNCH — {lead.name} at breakdown risk! Press B again."
            self.notifications.warning(self.message)
            return

        self.pending_launch_confirm = False
        self.pending_launch_mission_id = None
        gs.mark_tutorial_event("launched_mission")

        # Deduct deploy cost for each selected asset
        deploy_total = 0
        for asset in gs.spec_ops_assets:
            if asset.id in gs.selected_asset_ids and asset.deploy_cost > 0:
                deploy_total += asset.deploy_cost
        if deploy_total > 0:
            if not gs.spend_funds(deploy_total, "asset_deploy", f"Asset deployment costs: ¥{deploy_total}"):
                self.message = f"Insufficient funds for asset deployment costs (¥{deploy_total} needed)."
                self.notifications.warning(self.message)
                return

        mission = _launch_mission(gs)

        from game.ui.screens.mission_briefing_view import MissionBriefingView
        self.window.show_view(MissionBriefingView(gs, mission))

    def _do_asset_repair(self, idx: int) -> None:
        gs = self.game_state
        if idx >= len(gs.spec_ops_assets):
            return
        asset = gs.spec_ops_assets[idx]
        cost  = asset.maintenance.repair_cost
        if cost <= 0:
            self.notifications.info(f"{asset.name} is already at full integrity.")
            return
        if gs.spend_funds(cost, "asset_repair", f"Repaired {asset.name}."):
            asset.maintenance.mark_repaired()
            gs.add_event(push_action(self.notifications, "asset_repair", True, f"{asset.name} fully repaired — ¥{cost}"))
        else:
            gs.add_event(push_action(self.notifications, "asset_repair", False, f"Insufficient funds (need ¥{cost})"))

    def _do_asset_deploy_toggle(self, idx: int) -> None:
        gs = self.game_state
        if idx >= len(gs.spec_ops_assets):
            return
        asset = gs.spec_ops_assets[idx]
        if not asset.is_deployable:
            self.notifications.warning(f"{asset.name} is not ready for deployment.")
            return
        # Toggle this specific asset's ID in the deployment list
        if asset.id in gs.selected_asset_ids:
            gs.selected_asset_ids.remove(asset.id)
            selected = False
        else:
            gs.selected_asset_ids.append(asset.id)
            selected = True
        gs.add_event(f"{asset.name} {'added to' if selected else 'removed from'} deployment manifest.")

    def _do_asset_acquire(self) -> None:
        """Purchase a new spec-ops asset (alternating robot / power armor)."""
        gs = self.game_state
        cost = 50
        if not gs.spend_funds(cost, "asset_acquire", "Acquired new spec-ops asset."):
            gs.add_event(push_action(self.notifications, "asset_acquire", False, f"Need ¥{cost} to acquire asset"))
            return
        from game.management.spec_ops_assets import CombatRobot, PowerArmorSuit
        idx = len(gs.spec_ops_assets)
        if idx % 2 == 0:
            asset = CombatRobot(
                id=f"robot_{idx:03d}",
                name=f"K-{idx + 9} Combat Drone",
            )
        else:
            asset = PowerArmorSuit(
                id=f"armor_{idx:03d}",
                name=f"Mantis Mk.{idx} Suit",
            )
        gs.spec_ops_assets.append(asset)
        self._asset_cursor = len(gs.spec_ops_assets) - 1
        gs.add_event(push_action(self.notifications, "asset_acquire", True, f"Acquired {asset.name}"))

    def _do_catalog_acquire(self, catalog_idx: int) -> None:
        from game.management.spec_ops_assets import asset_catalog as _ac
        import copy
        gs = self.game_state
        catalog = _ac()
        scroll  = self._catalog_scroll % len(catalog)
        items   = catalog[scroll:scroll + 2] + catalog[:max(0, scroll + 2 - len(catalog))]
        items   = items[:2]
        if catalog_idx >= len(items):
            return
        template = items[catalog_idx]
        acquire_cost = getattr(template, '_acquire_cost', 60)
        if not gs.spend_funds(acquire_cost, "asset_acquire", f"Purchased {template.name}"):
            gs.add_event(push_action(self.notifications, "asset_acquire", False, f"Need ¥{acquire_cost}"))
            return
        # Clone the template with a unique ID
        uid = f"{template.id}_{len(gs.spec_ops_assets):03d}"
        new_asset = copy.deepcopy(template)
        new_asset.id   = uid
        new_asset.name = template.name
        new_asset.pilot_agent_name = None
        gs.spec_ops_assets.append(new_asset)
        self._asset_cursor = len(gs.spec_ops_assets) - 1
        gs.add_event(push_action(self.notifications, "asset_acquire", True, f"Acquired {new_asset.name}"))

    def _do_assign_pilot(self, asset_idx: int, agent_name: str | None) -> None:
        gs = self.game_state
        if asset_idx >= len(gs.spec_ops_assets):
            return
        asset = gs.spec_ops_assets[asset_idx]
        asset.pilot_agent_name = agent_name
        if agent_name:
            gs.add_event(f"{agent_name} assigned as pilot for {asset.name}.")
        else:
            gs.add_event(f"Pilot cleared from {asset.name}.")

    def _do_spend_stat_point(self, char_idx: int, stat_key: str) -> None:
        """Spend one pending_point to raise *stat_key* by 1 for character at *char_idx*."""
        gs = self.game_state
        if char_idx >= len(gs.characters):
            return
        char = gs.characters[char_idx]
        if char.pending_points <= 0:
            return
        # Supported stats on PlayerStats
        supported = {"str", "agi", "psi", "def", "con"}
        if stat_key not in supported:
            return
        # Map "def" → "defense" for the actual attribute name
        attr = "defense" if stat_key == "def" else stat_key
        if not hasattr(char.stats, attr):
            return
        setattr(char.stats, attr, getattr(char.stats, attr) + 1)
        char.stats.recalculate_hp()
        char.pending_points -= 1
        gs.add_event(push_action(
            self.notifications, "stat_upgrade", True,
            f"{char.name} +1 {stat_key.upper()} (now {getattr(char.stats, attr)})"
        ))

    def _do_unlock_talent(self, char_idx: int, node_id: str) -> None:
        gs = self.game_state
        if char_idx >= len(gs.characters):
            return
        char = gs.characters[char_idx]
        if unlock_talent(char, node_id):
            node = talent_node_by_id(node_id)
            node_name = node.name if node else node_id
            self.message = f"{char.name} unlocked {node_name}."
            gs.add_event(push_action(self.notifications, "talent_unlock", True, f"{char.name} learned {node_name}"))
        else:
            self.message = "Talent locked or no points available."
            self.notifications.warning(self.message)

    def _open_agent_sheet(self, char_idx: int) -> None:
        if not 0 <= char_idx < len(self.game_state.characters):
            return
        self.expanded_agent_sheet_index = char_idx
        _set_window_topmost(self.window, True)

    def _close_agent_sheet(self) -> None:
        if self.expanded_agent_sheet_index is None:
            return
        self.expanded_agent_sheet_index = None
        _set_window_topmost(self.window, False)

    def _close_recruit_window(self) -> None:
        self.recruit_window_open = False
        self.pending_recruit_candidates = []

    def _do_train_skill_points(self, char_idx: int) -> None:
        gs = self.game_state
        if char_idx >= len(gs.characters):
            return
        char = gs.characters[char_idx]
        if char.pending_points <= 0:
            return
        planned = option_b_plan(char)
        if not planned:
            self.message = f"{char.name} has no eligible skills to raise."
            self.notifications.warning(self.message)
            return
        applied: list[str] = []
        for key, target in planned.items():
            current = int(char.skills.get(key, 0))
            if target > current:
                char.skills[key] = target
                applied.append(f"{key}+{target - current}")
        char.pending_points -= 1
        self.message = f"{char.name} trained: {', '.join(applied)}."
        gs.add_event(push_action(self.notifications, "upgrade", True, self.message))

    def _do_cycle_equipment(self, char_idx: int, slot: str, direction: int) -> None:
        """Cycle equipment in *slot* for character at *char_idx* by *direction* (+1 / -1)."""
        gs = self.game_state
        if char_idx >= len(gs.characters):
            return
        char   = gs.characters[char_idx]
        catalog_options = self.equipment_catalog.get(slot, [])
        # Build pool: None (empty) + catalog items that fit the slot
        pool = [None] + [it for it in catalog_options if it.can_equip_to(slot)]
        if len(pool) <= 1:
            return
        current = char.loadout.item_for_slot(slot)
        try:
            cur_idx = next(i for i, it in enumerate(pool) if it is current or (it and current and it.id == current.id))
        except StopIteration:
            cur_idx = 0
        new_idx = (cur_idx + direction) % len(pool)
        new_item = pool[new_idx]
        char.loadout.equip(slot, new_item)
        name = new_item.name if new_item else "empty"
        gs.add_event(f"{char.name} — {slot.replace('_', ' ')}: {name}")
    # â”€â”€ Hub overrides â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def setup(self) -> None:
        self.room_ui = RoomUIState("hub")
        self.notifications = NotificationCenter()
        self.selected_save_slot = 1
        self.deployment_cursor = 0
        self._asset_cursor = 0
        self._catalog_scroll = 0
        self.pending_launch_confirm = False
        self.pending_launch_mission_id = None
        self.message = ""
        self.pending_recruit_candidates: list = []
        self.recruit_window_open = False
        self._elapsed = 0.0
        self._hits = []
        self._modal_hits = []
        self.active_tab = "command"
        self.equipment_catalog = default_equipment_catalog()
        self._last_agent_click_time: float = 0.0
        self._last_agent_click_index: int | None = None
        self.expanded_agent_sheet_index: int | None = None

        ensure_mission_templates(self.game_state)
        self.game_state.selected_agent_names = sanitize_selected_agent_names(
            self.game_state.characters, self.game_state.selected_agent_names
        )

        if self.game_state.available_funds <= 0:
            self.game_state.add_funds(
                self.game_state.compute_budget(),
                "mgmt_setup",
                "Emergency operating funds.",
            )

    def on_show_view(self) -> None:
        arcade.set_background_color(palette.BACKGROUND)
        ensure_mission_templates(self.game_state)

    def on_update(self, delta_time: float) -> None:
        self._elapsed += delta_time
        step_room_ui(self.room_ui, delta_time)

    def on_draw(self) -> None:
        self.clear()
        w, h = self.window.width, self.window.height
        roster_cards = self._build_hub_roster_cards() if self.room_ui.active_room_key == "squad" else []
        draw_graphical_command_surface(
            w,
            h,
            self.room_ui,
            self.game_state.strategic_resources,
            {},
            roster_cards=roster_cards,
            available_funds=self.game_state.available_funds,
            draw_controls=False,
        )
        arcade.draw_text(
            "F1 COMMAND  F2 CITY  F3 SQUAD  F4 ASSETS  F5 RESEARCH  F6 INTEL  |  ESC CLOSE",
            22,
            16,
            (90, 120, 130),
            10,
        )
        if self.message:
            arcade.draw_text(self.message, 22, 34, palette.WARNING, 10)
        _draw_notification_toast(self.notifications, w, h)
        self._draw_legacy_room_content()
        draw_expanded_room_controls(w, h, self.room_ui)
        self._draw_expanded_agent_sheet_modal(w, h)
        self._draw_recruit_window_modal(w, h)


    def _draw_expanded_agent_sheet_modal(self, w: int, h: int) -> None:
        if self.expanded_agent_sheet_index is None:
            return
        gs = self.game_state
        if self.expanded_agent_sheet_index >= len(gs.characters):
            self._close_agent_sheet()
            return

        char = gs.characters[self.expanded_agent_sheet_index]
        self._modal_hits = []

        from game.ui.panels import _load_texture_once
        from game.ui.portraits import portrait_path_for_character

        stats = char.stats
        sheet_attrs = {
            "level": int(stats.level),
            "str": int(stats.str),
            "agi": int(stats.agi),
            "con": int(stats.con),
            "cha": int(stats.cha),
            "psi": int(stats.psi),
            "defense": int(stats.defense),
        }
        stress_state = "steady" if char.stress < 35 else "rattled" if char.stress < 65 else "frayed" if char.stress < 85 else "breaking"
        loadout_bonuses = char.loadout.total_stat_bonuses()
        derived = compute_derived_stats(sheet_attrs, char.skills, loadout_bonuses, stress_state)
        planned_skills = option_b_plan(char)
        planned_deltas = {k: v - int(char.skills.get(k, 0)) for k, v in planned_skills.items()}
        role_col = {
            "samurai": palette.ROLE_SAMURAI,
            "sniper": palette.ROLE_SNIPER,
            "psi": palette.ROLE_PSI,
        }.get(char.role, palette.ACCENT)

        _rect(0, 0, w, h, (0, 0, 0, 195))
        mw = min(1080, w - 56)
        mh = min(700, h - 44)
        mx0 = (w - mw) // 2
        my0 = (h - mh) // 2
        mx1 = mx0 + mw
        my1 = my0 + mh
        _rect(mx0, my0, mx1, my1, (6, 14, 20, 248))
        _border(mx0, my0, mx1, my1, role_col, 2)
        _rect(mx0, my1 - 74, mx1, my1, (10, 24, 34, 248))
        arcade.draw_line(mx0, my1 - 74, mx1, my1 - 74, role_col, 2)
        arcade.draw_text(
            f"{char.name.upper()}  |  {char.role.upper()}  |  LEVEL {stats.level}",
            mx0 + 20,
            my1 - 28,
            palette.TEXT,
            font_size=18,
            bold=True,
        )
        arcade.draw_text(
            f"Pending points {char.pending_points}   Talent points {char.talent_points}   Stress {char.stress}",
            mx0 + 20,
            my1 - 50,
            palette.MUTED_TEXT,
            font_size=11,
        )
        close_left = mx1 - 42
        close_bottom = my1 - 56
        _rect(close_left, close_bottom, close_left + 28, close_bottom + 28, (14, 24, 30, 240))
        arcade.draw_line(close_left, close_bottom + 28, close_left + 28, close_bottom + 28, palette.PANEL_BORDER_MUTED, 1)
        arcade.draw_text("X", close_left + 14, close_bottom + 14, palette.DANGER, font_size=14, bold=True, anchor_x="center", anchor_y="center")
        self._modal_hits.append(_HitRegion(close_left, close_bottom, close_left + 28, close_bottom + 28, "sheet_close"))

        left_w = 280
        pad = 18
        left_x0 = mx0 + pad
        left_x1 = left_x0 + left_w
        right_x0 = left_x1 + 18
        right_x1 = mx1 - pad

        portrait_size = 198
        portrait_left = left_x0 + 4
        portrait_bottom = my1 - 110 - portrait_size
        _rect(portrait_left - 8, portrait_bottom - 10, portrait_left + portrait_size + 8, portrait_bottom + portrait_size + 10, (15, 34, 44, 220))
        arcade.draw_line(portrait_left - 8, portrait_bottom + portrait_size + 10, portrait_left + portrait_size + 8, portrait_bottom + portrait_size + 10, role_col, 2)
        portrait_path = portrait_path_for_character(char)
        portrait_tex = _load_texture_once(portrait_path) if portrait_path else None
        if portrait_tex is not None and hasattr(arcade, "draw_texture_rect"):
            arcade.draw_texture_rect(portrait_tex, arcade.LBWH(portrait_left, portrait_bottom, portrait_size, portrait_size))
        else:
            center_x = portrait_left + portrait_size // 2
            center_y = portrait_bottom + portrait_size // 2
            radius = portrait_size // 2
            arcade.draw_circle_filled(center_x, center_y, radius, palette.AGENT_PORTRAIT_FILL)
            arcade.draw_circle_outline(center_x, center_y, radius, role_col, 3)
        arcade.draw_text("DOSSIER PORTRAIT", portrait_left + 10, portrait_bottom + portrait_size + 16, palette.MUTED_TEXT, font_size=8, bold=True)

        info_y = portrait_bottom - 18
        info_lines = [
            f"Role {char.role.upper()}",
            f"HP {stats.hp}/{stats.max_hp}   DEF {stats.defense}",
            f"XP {stats.xp}   Lvl {stats.level}   Loyalty {char.loyalty}",
            f"Recovery {char.recovery_turns}d   Stress cap {derived['stress_cap']}",
        ]
        for idx, line in enumerate(info_lines):
            arcade.draw_text(line, left_x0, info_y - idx * 20, palette.TEXT if idx == 0 else palette.MUTED_TEXT, font_size=11 if idx == 0 else 10, bold=idx == 0)

        meter_y = info_y - 132
        _meter(left_x0, meter_y + 28, left_w - 24, stats.hp / max(1, stats.max_hp), palette.TACTICAL_GREEN, "HP")
        _meter(left_x0, meter_y - 16, left_w - 24, char.stress / max(1, derived["stress_cap"]), palette.WARNING, "STRESS", label_offset=18)

        loadout_lines = char.loadout.summary_lines()[:5]
        loadout_top = my0 + 34
        _rect(left_x0 - 6, loadout_top - 8, left_x1 - 2, loadout_top + 118, (9, 20, 26, 210))
        arcade.draw_line(left_x0 - 6, loadout_top + 118, left_x1 - 2, loadout_top + 118, palette.PANEL_BORDER_MUTED, 1)
        arcade.draw_text("LOADOUT", left_x0 + 6, loadout_top + 98, palette.ACCENT, font_size=11, bold=True)
        for idx, line in enumerate(loadout_lines or ["No equipment assigned."]):
            arcade.draw_text(line, left_x0 + 6, loadout_top + 76 - idx * 18, palette.MUTED_TEXT, font_size=9, width=left_w - 18, align="left")

        stats_top = my1 - 104
        arcade.draw_text("ATTRIBUTES", right_x0, stats_top + 16, palette.ACCENT, font_size=12, bold=True)
        stat_order = [
            ("str", "STR"),
            ("agi", "AGI"),
            ("psi", "PSI"),
            ("def", "DEF"),
            ("con", "CON"),
        ]
        stat_gap = 8
        stat_card_w = (right_x1 - right_x0 - stat_gap * (len(stat_order) - 1)) // len(stat_order)
        stat_card_h = 76
        for idx, (stat_key, label) in enumerate(stat_order):
            card_left = right_x0 + idx * (stat_card_w + stat_gap)
            card_bottom = stats_top - stat_card_h
            current = getattr(stats, "defense" if stat_key == "def" else stat_key)
            fill = (13, 25, 33, 235) if char.pending_points <= 0 else (18, 40, 28, 235)
            accent = role_col if char.pending_points <= 0 else palette.RESOURCE
            _rect(card_left, card_bottom, card_left + stat_card_w, card_bottom + stat_card_h, fill)
            arcade.draw_line(card_left, card_bottom + stat_card_h, card_left + stat_card_w, card_bottom + stat_card_h, accent, 2)
            arcade.draw_text(label, card_left + 10, card_bottom + 50, palette.MUTED_TEXT, font_size=9, bold=True)
            arcade.draw_text(str(current), card_left + 10, card_bottom + 20, palette.TEXT, font_size=18, bold=True)
            arcade.draw_text("SPEND", card_left + stat_card_w - 10, card_bottom + 10, palette.RESOURCE if char.pending_points > 0 else palette.PANEL_BORDER_MUTED, font_size=8, bold=True, anchor_x="right")
            if char.pending_points > 0:
                self._modal_hits.append(_HitRegion(card_left, card_bottom, card_left + stat_card_w, card_bottom + stat_card_h, "sheet_spend_stat", (self.expanded_agent_sheet_index, stat_key)))

        readiness_top = stats_top - stat_card_h - 20
        arcade.draw_text("READINESS", right_x0, readiness_top + 16, palette.ACCENT, font_size=12, bold=True)
        ready_metrics = [
            ("HP", f"{derived['hp']}"),
            ("AIM", f"{derived['aim']}"),
            ("DEF", f"{derived['defense']}"),
            ("INIT", f"{derived['initiative']}"),
            ("RES", f"{derived['resolve']}"),
            ("REC", f"{derived['recovery_rate']}"),
        ]
        metric_gap = 10
        metric_cols = 3
        metric_rows = (len(ready_metrics) + metric_cols - 1) // metric_cols
        metric_card_w = (right_x1 - right_x0 - metric_gap * (metric_cols - 1)) // metric_cols
        metric_card_h = 60
        for idx, (label, value) in enumerate(ready_metrics):
            row = idx // metric_cols
            col = idx % metric_cols
            card_left = right_x0 + col * (metric_card_w + metric_gap)
            card_top = readiness_top - row * (metric_card_h + 10)
            card_bottom = card_top - metric_card_h
            _rect(card_left, card_bottom, card_left + metric_card_w, card_bottom + metric_card_h, (10, 21, 28, 220))
            arcade.draw_line(card_left, card_bottom + metric_card_h, card_left + metric_card_w, card_bottom + metric_card_h, palette.PANEL_BORDER_MUTED, 1)
            arcade.draw_text(label, card_left + 10, card_bottom + 36, palette.MUTED_TEXT, font_size=8, bold=True)
            arcade.draw_text(value, card_left + 10, card_bottom + 12, palette.TEXT, font_size=14, bold=True)

        skills_top = readiness_top - metric_rows * (metric_card_h + 10) - 18
        arcade.draw_text("SKILLS", right_x0, skills_top + 16, palette.ACCENT, font_size=12, bold=True)
        skill_button_text = "TRAIN SKILLS"
        skill_summary = ", ".join(f"{key[:4].upper()}+{delta}" for key, delta in planned_deltas.items()) if planned_deltas else "No eligible skills"
        button_left = right_x0
        button_bottom = skills_top - 10
        button_h = 48
        button_fill = (22, 42, 30, 240) if planned_deltas and char.pending_points > 0 else (11, 20, 25, 210)
        button_col = palette.RESOURCE if planned_deltas and char.pending_points > 0 else palette.PANEL_BORDER_MUTED
        _rect(button_left, button_bottom, right_x1, button_bottom + button_h, button_fill)
        arcade.draw_line(button_left, button_bottom + button_h, right_x1, button_bottom + button_h, button_col, 2)
        arcade.draw_text(skill_button_text, button_left + 12, button_bottom + 30, button_col, font_size=10, bold=True)
        arcade.draw_text(skill_summary[:72], button_left + 12, button_bottom + 12, palette.MUTED_TEXT, font_size=8)
        if planned_deltas and char.pending_points > 0:
            self._modal_hits.append(_HitRegion(button_left, button_bottom, right_x1, button_bottom + button_h, "sheet_train_skills", self.expanded_agent_sheet_index))

        skills_grid_top = button_bottom - 18
        skill_cols = 3
        skill_gap = 10
        skill_card_w = (right_x1 - right_x0 - skill_gap * (skill_cols - 1)) // skill_cols
        skill_card_h = 64
        for idx, skill_key in enumerate(ALLOWED_SKILL_KEYS):
            row = idx // skill_cols
            col = idx % skill_cols
            card_left = right_x0 + col * (skill_card_w + skill_gap)
            card_top = skills_grid_top - row * (skill_card_h + skill_gap)
            card_bottom = card_top - skill_card_h
            rank = int(char.skills.get(skill_key, 0))
            total = skill_total(skill_key, sheet_attrs, char.skills, {})
            planned_delta = planned_deltas.get(skill_key, 0)
            highlight = planned_delta > 0
            fill = (19, 29, 38, 232) if not highlight else (22, 48, 37, 232)
            border = palette.PANEL_BORDER_MUTED if not highlight else palette.RESOURCE
            _rect(card_left, card_bottom, card_left + skill_card_w, card_top, fill)
            arcade.draw_line(card_left, card_top, card_left + skill_card_w, card_top, border, 2)
            arcade.draw_text(skill_key.replace("_", " ").upper(), card_left + 8, card_top - 16, palette.TEXT, font_size=8, bold=True)
            arcade.draw_text(f"RANK {rank}", card_left + 8, card_bottom + 22, palette.MUTED_TEXT, font_size=8)
            arcade.draw_text(f"TOTAL {total}", card_left + 8, card_bottom + 10, palette.ACCENT, font_size=9, bold=True)
            if highlight:
                arcade.draw_text(f"+{planned_delta}", card_left + skill_card_w - 10, card_bottom + 10, palette.RESOURCE, font_size=10, bold=True, anchor_x="right")

        footer_y = my0 + 14
        arcade.draw_text(
            "Click a stat card to spend 1 point. Train Skills applies the current 2-rank plan.",
            right_x0,
            footer_y,
            palette.MUTED_TEXT,
            font_size=9,
        )
        arcade.draw_text("ESC closes this sheet.", mx1 - 18, footer_y, palette.MUTED_TEXT, font_size=9, anchor_x="right")

    def on_key_press(self, key: int, modifiers: int) -> None:
        if self.recruit_window_open:
            if key == getattr(arcade.key, "ESCAPE", None):
                self._close_recruit_window()
            elif key == getattr(arcade.key, "N", None):
                self._do_recruit_prompt()
            return

        if self.expanded_agent_sheet_index is not None:
            if key == getattr(arcade.key, "ESCAPE", None):
                self._close_agent_sheet()
            return

        esc_key = getattr(arcade.key, "ESCAPE", None)
        save_key = getattr(arcade.key, "S", None)
        load_key = getattr(arcade.key, "L", None)
        day_key = getattr(arcade.key, "D", None)
        enter_key = getattr(arcade.key, "ENTER", None)
        return_key = getattr(arcade.key, "RETURN", None)
        b_key = getattr(arcade.key, "B", None)
        n_key = getattr(arcade.key, "N", None)
        left_key = getattr(arcade.key, "LEFT", None)
        right_key = getattr(arcade.key, "RIGHT", None)
        space_key = getattr(arcade.key, "SPACE", None)
        r_key = getattr(arcade.key, "R", None)
        t_key = getattr(arcade.key, "T", None)
        key_1 = getattr(arcade.key, "KEY_1", None)
        key_2 = getattr(arcade.key, "KEY_2", None)
        key_3 = getattr(arcade.key, "KEY_3", None)

        room_shortcuts = {
            code: room
            for code, room in (
                (getattr(arcade.key, "F1", None), "command"),
                (getattr(arcade.key, "F2", None), "city"),
                (getattr(arcade.key, "F3", None), "squad"),
                (getattr(arcade.key, "F4", None), "assets"),
                (getattr(arcade.key, "F5", None), "research"),
                (getattr(arcade.key, "F6", None), "intel"),
            )
            if code is not None
        }
        if esc_key is not None and key == esc_key:
            if self.expanded_agent_sheet_index is not None:
                self.expanded_agent_sheet_index = None
            elif self.room_ui.is_open:
                close_room(self.room_ui)
            else:
                from game.ui.screens.title_screen import TitleView

                self.window.show_view(TitleView())
            return

        if key in room_shortcuts:
            self._open_hub_room(room_shortcuts[key])
            return

        mod_ctrl = getattr(arcade.key, "MOD_CTRL", 0)
        if save_key is not None and key == save_key and not (modifiers & mod_ctrl):
            self._do_save()
            return
        if load_key is not None and key == load_key and not (modifiers & mod_ctrl):
            self._do_load()
            return
        if day_key is not None and key == day_key:
            self._do_advance_day()
            return
        if key in {k for k in (enter_key, return_key) if k is not None} and self.room_ui.is_open:
            self._dispatch_hub_action("next_step")
            return

        if not self.room_ui.is_open:
            return

        active_room = self.room_ui.active_room_key
        if active_room == "squad":
            if b_key is not None and key == b_key:
                self._do_launch_mission()
                return
            if n_key is not None and key == n_key:
                self._do_recruit_prompt()
                return
            if left_key is not None and key == left_key:
                self._cycle_agent_cursor(-1)
                return
            if right_key is not None and key == right_key:
                self._cycle_agent_cursor(1)
                return
            if space_key is not None and key == space_key:
                self._toggle_selected_agent()
                return
        elif active_room == "assets":
            if left_key is not None and key == left_key:
                self._cycle_asset_cursor(-1)
                return
            if right_key is not None and key == right_key:
                self._cycle_asset_cursor(1)
                return
            if r_key is not None and key == r_key:
                self._do_asset_repair(self._asset_cursor)
                return
            if t_key is not None and key == t_key:
                self._do_asset_deploy_toggle(self._asset_cursor)
                return
        elif active_room == "research":
            research_key_map = {k: i for i, k in enumerate((key_1, key_2, key_3)) if k is not None}
            if key in research_key_map:
                self._dispatch_hub_action(f"start_research_{research_key_map[key]}")
                return

    def on_mouse_press(self, x: float, y: float, _button: int, _modifiers: int) -> None:
        xi, yi = int(x), int(y)
        w, h = self.window.width, self.window.height

        if self.recruit_window_open:
            for hit in reversed(self._modal_hits):
                if hit.contains(xi, yi):
                    self._dispatch(hit.action, hit.data)
                    return
            return

        if self.expanded_agent_sheet_index is not None:
            for hit in reversed(self._modal_hits):
                if hit.contains(xi, yi):
                    self._dispatch(hit.action, hit.data)
                    return
            return

        if self.room_ui.is_open:
            if close_button_rect(w, h).contains(xi, yi):
                close_room(self.room_ui)
                return
            for hit in reversed(self._hits):
                if hit.contains(xi, yi):
                    self._dispatch(hit.action, hit.data)
                    return
            action = action_at_point(self.room_ui.action_buttons, xi, yi)
            if action is not None:
                self._dispatch_hub_action(action.key)
                return
            return

        room = room_at_point(w, h, "hub", xi, yi)
        if room is None:
            return
        open_room(self.room_ui, w, h, room.key)
        self.game_state.mark_tutorial_event("entered_room")
        self.message = ""

    def _open_hub_room(self, room_key: str) -> None:
        open_room(self.room_ui, self.window.width, self.window.height, room_key)
        self.game_state.mark_tutorial_event("entered_room")
        self.message = ""

    def _cycle_agent_cursor(self, step: int) -> None:
        if not self.game_state.characters:
            return
        self.deployment_cursor = (self.deployment_cursor + step) % len(self.game_state.characters)

    def _toggle_selected_agent(self) -> None:
        if not self.game_state.characters:
            return
        self.game_state.selected_agent_names, self.message = toggle_agent_selection(
            self.game_state.characters,
            self.game_state.selected_agent_names,
            self.deployment_cursor,
        )
        self.pending_launch_confirm = False

    def _cycle_asset_cursor(self, step: int) -> None:
        assets = self.game_state.spec_ops_assets
        if not assets:
            return
        self._asset_cursor = (self._asset_cursor + step) % len(assets)

    def _dispatch_hub_action(self, action: str) -> None:
        gs = self.game_state

        if action == "next_step":
            self._perform_primary_hub_action()
            return
        if action == "advance_day":
            self._do_advance_day()
            return
        if action == "save":
            self._do_save()
            return
        if action == "load":
            self._do_load()
            return
        if action == "slot_prev":
            self.selected_save_slot = ((self.selected_save_slot - 2) % 5) + 1
            gs.add_event(f"Active save slot: {self.selected_save_slot}.")
            return
        if action == "slot_next":
            self.selected_save_slot = (self.selected_save_slot % 5) + 1
            gs.add_event(f"Active save slot: {self.selected_save_slot}.")
            return

        if action == "recruit_prompt":
            self._do_recruit_prompt()
            return
        if action == "launch_mission":
            self._do_launch_mission()
            return
        if action == "remove_agent":
            self._do_remove_agent()
            return
        if action == "agent_prev":
            self._cycle_agent_cursor(-1)
            return
        if action == "agent_next":
            self._cycle_agent_cursor(1)
            return
        if action == "select_agent":
            self._toggle_selected_agent()
            return

        if action == "asset_prev":
            self._cycle_asset_cursor(-1)
            return
        if action == "asset_next":
            self._cycle_asset_cursor(1)
            return
        if action == "asset_repair":
            self._do_asset_repair(self._asset_cursor)
            return
        if action == "asset_deploy_toggle":
            self._do_asset_deploy_toggle(self._asset_cursor)
            return
        if action == "catalog_acquire":
            self._do_catalog_acquire(self._asset_cursor)
            return

        if action.startswith("corp_upgrade_"):
            key = action.removeprefix("corp_upgrade_")
            costs = {
                "research": {"intel": 5},
                "security": {"credits": 10, "salvage": 2},
                "politics": {"influence": 3},
                "black_ops": {"credits": 5, "intel": 3},
            }.get(key, {})
            if costs:
                self._do_corp_upgrade(key, costs)
            return

        if action.startswith("city_upgrade_"):
            key = action.removeprefix("city_upgrade_")
            costs = {
                "armaments": {"credits": 5, "salvage": 3},
                "garrisons": {"credits": 10, "influence": 2},
                "defense_zones": {"credits": 5, "salvage": 5},
            }.get(key, {})
            if costs:
                self._do_city_upgrade(key, costs)
            return

        if action.startswith("start_research_"):
            idx = int(action.rsplit("_", 1)[-1])
            completed = set(gs.completed_research)
            active_ids = {research.project_id for research in gs.active_research}
            available = gs.research_tree.available_projects(completed, active_ids)
            if idx < len(available):
                gs.start_research(available[idx].id)
                gs.add_event(f"Research started: {available[idx].name}.")
            return

    def _perform_primary_hub_action(self) -> None:
        active_room = self.room_ui.active_room_key
        if active_room == "command":
            self._do_advance_day()
            return
        if active_room == "city":
            self._do_city_upgrade("armaments", {"credits": 5, "salvage": 3})
            return
        if active_room == "squad":
            self._do_launch_mission()
            return
        if active_room == "assets":
            asset = self.game_state.spec_ops_assets[self._asset_cursor] if self.game_state.spec_ops_assets else None
            if asset is None:
                return
            if asset.is_deployable:
                self._do_asset_deploy_toggle(self._asset_cursor)
            else:
                self._do_asset_repair(self._asset_cursor)
            return
        if active_room == "research":
            completed = set(self.game_state.completed_research)
            active_ids = {research.project_id for research in self.game_state.active_research}
            available = self.game_state.research_tree.available_projects(completed, active_ids)
            if available:
                self.game_state.start_research(available[0].id)
                self.game_state.add_event(f"Research started: {available[0].name}.")
            return
        if active_room == "intel":
            self._do_advance_day()

    def _draw_legacy_room_content(self) -> None:
        if not self.room_ui.is_open or self.room_ui.expansion < 0.5:
            return
        active = active_room_rect(self.room_ui, self.window.width, self.window.height)
        if active is None:
            return
        _, rect = active
        pad_x = max(24, rect.width // 28)
        pad_y = max(24, rect.height // 22)
        x0 = rect.left + pad_x
        bottom_reserve = max(84, rect.height // 8)
        y0 = rect.bottom + pad_y + bottom_reserve
        x1 = rect.right - pad_x
        y1 = rect.top - pad_y * 2
        if y0 >= y1 - 40:
            y0 = rect.bottom + pad_y + 40
        room_key = self.room_ui.active_room_key
        renderers = {
            "command": self._draw_command_tab,
            "city": self._draw_city_tab,
            "squad": self._draw_squad_tab,
            "assets": self._draw_assets_tab,
            "research": self._draw_research_tab,
            "intel": self._draw_intel_tab,
        }
        renderer = renderers.get(room_key or "")
        if renderer is not None:
            renderer(x0, y0, x1, y1)

    def _build_hub_roster_cards(self) -> list[dict]:
        cards: list[dict] = []
        selected_names = set(self.game_state.selected_agent_names)
        for index, character in enumerate(self.game_state.characters):
            stats = character.stats
            max_hp = max(1, stats.max_hp)
            cards.append(
                {
                    "name": character.name,
                    "role": character.role,
                    "active": index == self.deployment_cursor,
                    "selected": character.name in selected_names,
                    "portrait_path": portrait_path_for_character(character),
                    "hp_ratio": max(0, min(stats.hp / max_hp, 1)),
                    "stress_ratio": max(0, min(character.stress / 100, 1)),
                    "pending_points": character.pending_points,
                    "talent_points": character.talent_points,
                    "specialization_count": len(character.specializations),
                    "specializations": list(character.specializations),
                    "recovery_turns": character.recovery_turns,
                    "defense": stats.defense + character.loadout.total_stat_bonuses().get("defense", 0),
                }
            )
        return cards

    def _room_info_lines(self) -> dict[str, list[str]]:
        gs = self.game_state
        selected_mission = _selected_mission(gs)
        selected_agents = selected_deployable_agents(gs.characters, gs.selected_agent_names)
        at_risk = (
            agents_at_breaking_risk(selected_agents, selected_mission)
            if selected_mission and selected_agents
            else []
        )
        guidance = compute_next_action(gs, "corp")

        finance_lines = build_corporate_finance_lines(
            gs.next_weekly_income_date,
            gs.projected_weekly_income,
        )
        event_lines = build_event_panel_lines(gs.active_events, gs.calendar.current_day)

        previous_morale = getattr(gs, "_last_squad_morale", None)
        morale_summary = aggregate_squad_morale(selected_agents, previous_morale)
        gs._last_squad_morale = morale_summary.global_morale
        morale_lines = [line.text for line in build_squad_morale_panel_lines(morale_summary)]

        selected_asset_count = len(gs.selected_asset_ids)
        ready_asset_count = sum(1 for asset in gs.spec_ops_assets if asset.is_deployable)
        asset_lines = (
            build_spec_ops_assets_guide_lines()
            + build_spec_ops_acquisition_lines(gs)[1:]
            + build_mission_prep_asset_state_lines(gs)[1:4]
            + build_asset_outcome_lines(gs)[1:]
        )

        city_factions = sorted(
            gs.factions,
            key=lambda faction: faction.hostility_to_player,
            reverse=True,
        )
        lead_faction = city_factions[0].name if city_factions else "no active faction"
        hostility = city_factions[0].hostility_to_player if city_factions else 0

        command_lines = [
            f"Next Step: {guidance.text}",
            f"{gs.calendar.campaign_date_label} | Day {gs.calendar.current_day}",
            f"Turn {gs.turn} | Funds {gs.available_funds:,}",
            *event_lines[:3],
            *finance_lines,
            f"Politics allocation {gs.corp_budget['politics']}",
            f"Influence reserve {gs.strategic_resources.get('influence', 0)}",
        ]

        city_lines = [
            f"Next Step: {guidance.text}",
            f"{gs.calendar.campaign_date_label} | Week {gs.calendar.current_week}",
            f"District {gs.district.name}",
            f"Control faction {gs.district.control_faction}",
            f"Stability {gs.district.stability}/100",
            f"Unrest {gs.district.unrest}/100",
            f"Media heat {gs.district.media_heat}/100",
            f"Highest pressure: {lead_faction}",
            f"Hostility {hostility}/100 | Active factions {len(gs.factions)}",
            f"Garrisons {gs.city_budget['garrisons']} | Armaments {gs.city_budget['armaments']} | Defense zones {gs.city_budget['defense_zones']}",
        ]

        squad_lines = [
            f"Next Step: {guidance.text}",
            f"Roster {len(gs.characters)} agents | Selected {len(gs.selected_agent_names)}",
            f"Selected squad {len(selected_agents)} + {selected_asset_count} support",
            f"Risk agents {len(at_risk)}",
            *morale_lines[:3],
            f"Mission {selected_mission.title if selected_mission else 'No active mission'}",
            f"Risk {selected_mission.risk_level if selected_mission else 0} | Objective {selected_mission.objective_type if selected_mission else 'none'}",
            f"Target faction {selected_mission.target_faction if selected_mission else 'none'}",
        ]

        assets = gs.spec_ops_assets
        selected_asset = assets[self._asset_cursor] if assets else None
        assets_lines = [
            f"Next Step: {guidance.text}",
            f"Assets ready {ready_asset_count}/{len(assets)}",
            f"Selected support assets {selected_asset_count}",
            f"Current asset: {selected_asset.name if selected_asset else 'None'}",
            *asset_lines,
        ]

        research_lines = build_research_lab_lines(gs)
        if not research_lines:
            research_lines = ["No research data available."]

        intel_lines = [
            f"Next Step: {guidance.text}",
            f"Event log entries: {len(gs.event_log)}",
        ]
        if getattr(gs, "latest_mission_debrief", None):
            debrief = gs.latest_mission_debrief
            intel_lines.append(f"Latest outcome: {debrief.get('mission_outcome', debrief.get('outcome', 'pending'))}")
            title = debrief.get("mission_title")
            if title:
                intel_lines.append(f"Latest mission: {title}")
            lines = debrief.get("lines", [])
            for row in lines[:3]:
                if isinstance(row, dict):
                    text = row.get("text", "")
                    if text:
                        intel_lines.append(str(text))
        if getattr(gs, "latest_agent_aftermath", None):
            intel_lines.append("Aftermath:")
            intel_lines.extend([str(line)[:80] for line in gs.latest_agent_aftermath[:4]])
        intel_lines.extend(str(entry)[:80] for entry in reversed(gs.event_log[-4:]))

        return {
            "command": command_lines,
            "city": city_lines,
            "squad": squad_lines,
            "assets": assets_lines,
            "research": research_lines,
            "intel": intel_lines,
        }
