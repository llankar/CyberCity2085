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

import math
from dataclasses import dataclass
from typing import Callable

import arcade

from game.agent_readiness import agents_at_breaking_risk
from game.character import Character, is_deployable
from game.deployment import (
    sanitize_selected_agent_names,
    sanitize_selected_asset_ids,
    selected_deployable_agents,
    toggle_agent_selection,
    toggle_asset_selection,
)
from game.gamestate import GameState
from game.management.equipment import default_equipment_catalog, EQUIPMENT_SLOTS
from game.management.morale import aggregate_squad_morale
from game.mission_system import (
    ensure_mission_templates,
    launch_selected_mission as _launch_mission,
    selected_mission as _selected_mission,
)
from game.mission_templates import MissionTemplate
from game.persistence import SaveSystem, SaveSystemResult
from game.recruitment import recruit_agent
from game.ui import GameView
from game.ui import palette
from game.ui.action_feedback import push_action
from game.ui.management.action_requirements import (
    blocked_launch_reason,
    blocked_recruit_reason,
)
from game.ui.panels import draw_small_meter
from game.ui.portraits import portrait_path_for_character
from game.ui.screens.command_center import (
    build_command_title,
    build_interactive_tooltips,
)
from game.ui.screens.command_deck.layout import (
    build_corporate_finance_lines,
    build_event_panel_lines,
)
from game.ui.screens.research_lab import build_research_lab_lines
from game.ui.widgets.notification_center import NotificationCenter
from game.ui.widgets.squad_morale_panel import build_squad_morale_panel_lines

# ── Layout constants ────────────────────────────────────────────────────────

_SIDEBAR_W    = 190
_TOP_HUD_H    = 52
_BOT_BAR_H    = 48
_TAB_H        = 64
_TABS: list[tuple[str, str]] = [
    ("COMMAND", "command"),
    ("CITY",    "city"),
    ("SQUAD",   "squad"),
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
    arcade.draw_lrbt_rectangle_filled(l, r, b, t, color)


def _draw_notification_toast(notifications: "NotificationCenter", w: int, _h: int) -> None:
    """Render the most-recent notification lines in the bottom-right corner."""
    lines = notifications.latest_text_lines(4)
    if not lines:
        return
    pad, line_h, font_sz = 8, 16, 10
    panel_w = 340
    panel_h = pad * 2 + len(lines) * line_h
    rx = w - 8
    ry = _BOT_BAR_H + 8
    _rect(rx - panel_w, ry, rx, ry + panel_h, (0, 0, 0, 180))
    for i, text in enumerate(lines):
        color = palette.SUCCESS if "[SUCCESS]" in text else (
            palette.WARNING if "[WARNING]" in text else palette.DANGER
        )
        arcade.draw_text(
            text, rx - panel_w + pad, ry + pad + i * line_h,
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


def _meter(l: int, b: int, w: int, value: float, color, label: str = "") -> None:
    """Compact 0-100 progress meter with optional label."""
    h = 10
    _rect(l, b, l + w, b + h, palette.PANEL_FILL_DARK)
    fill_w = int(w * max(0.0, min(1.0, value)))
    _rect(l, b, l + fill_w, b + h, color)
    if label:
        arcade.draw_text(label, l, b + 13, palette.MUTED_TEXT, font_size=9)


def _badge(text: str, x: int, y: int, color, bg=None) -> None:
    """Small text badge (e.g. risk level)."""
    w = max(48, len(text) * 8 + 10)
    bg = bg or (*color[:3], 60)
    _rect(x, y, x + w, y + 18, bg)
    arcade.draw_line(x, y + 18, x + w, y + 18, color, 2)
    arcade.draw_text(text, x + 5, y + 4, color, font_size=9, bold=True)


def _risk_color(risk: str):
    r = (risk or "").lower()
    if r in ("high", "critical", "extreme"):
        return palette.DANGER
    if r in ("medium", "moderate"):
        return palette.WARNING
    return palette.TACTICAL_GREEN


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
        self.pending_launch_confirm: bool = False
        self.pending_launch_mission_id: str | None = None
        self.message: str = ""
        self.equipment_catalog = default_equipment_catalog()

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

    def on_draw(self) -> None:
        self.clear()
        self._hits = []
        w, h = self.window.width, self.window.height

        # Draw city-tower background
        from game.ui.panels import draw_city_corporate_backdrop
        draw_city_corporate_backdrop(w, h, "corp")

        # Dark overlay so panels read clearly
        _rect(0, 0, w, h, (0, 0, 0, 120))

        self._draw_top_hud(w, h)
        self._draw_sidebar(w, h)
        self._draw_content(w, h)
        self._draw_bottom_bar(w, h)

        # Notifications toast — newest-first, bottom-right corner
        _draw_notification_toast(self.notifications, w, h)

    def on_key_press(self, key: int, modifiers: int) -> None:
        # Tab shortcuts
        tab_keys = {
            arcade.key.F1: "command",
            arcade.key.F2: "city",
            arcade.key.F3: "squad",
            arcade.key.F4: "research",
            arcade.key.F5: "intel",
        }
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
            elif key in (arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3):
                idx = key - arcade.key.KEY_1
                if idx < len(self.game_state.mission_templates):
                    self.game_state.selected_mission_index = idx
                    self.pending_launch_confirm = False

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
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
        arcade.draw_text(
            "▌ AEGIS CORP", 14, cy,
            palette.HEADER, font_size=15, bold=True,
            anchor_y="center",
        )

        # Day / calendar
        day_txt = f"DAY {gs.calendar.current_day}"
        arcade.draw_text(day_txt, 260, cy, palette.ACCENT, font_size=13, anchor_y="center")

        # Funds
        funds_txt = f"¥ {gs.available_funds:,}"
        arcade.draw_text("FUNDS", 400, cy + 7, palette.MUTED_TEXT, font_size=9, anchor_y="center")
        arcade.draw_text(funds_txt, 400, cy - 7, palette.RESOURCE, font_size=12, bold=True, anchor_y="center")

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
            palette.MUTED_TEXT, font_size=11, anchor_y="center",
        )

        # Agent count
        roster = len(gs.characters)
        selected = len(gs.selected_agent_names)
        arcade.draw_text(
            f"AGENTS {selected}/{roster}", 920, cy,
            palette.ACCENT, font_size=11, anchor_y="center",
        )

        # Slot indicator (right side)
        arcade.draw_text(
            f"SLOT {self.selected_save_slot}",
            w - 120, cy,
            palette.MUTED_TEXT, font_size=10, anchor_y="center",
        )

        # Next step guidance (right)
        from game.ui.guidance.next_action import compute_next_action
        guidance = compute_next_action(self.game_state, self.active_tab)
        arcade.draw_text(
            f"► {guidance.text}",
            w - 440, cy,
            palette.ACCENT, font_size=10, anchor_y="center",
        )

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _draw_sidebar(self, w: int, h: int) -> None:
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
                font_size=12, bold=active, anchor_y="center",
            )

            # Count badge per tab
            badge_txt = self._tab_badge(key)
            if badge_txt:
                arcade.draw_text(
                    badge_txt, _SIDEBAR_W - 14, (by + ty) // 2,
                    palette.ACCENT, font_size=9, anchor_x="right", anchor_y="center",
                )

            self._hits.append(_HitRegion(0, by, _SIDEBAR_W - 2, ty, "tab", key))

    def _tab_badge(self, key: str) -> str:
        gs = self.game_state
        if key == "squad":
            roster = len(gs.characters)
            sel    = len(gs.selected_agent_names)
            return f"{sel}/{roster}"
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

    # ── SQUAD tab ─────────────────────────────────────────────────────────────

    def _draw_squad_tab(self, x0: int, y0: int, x1: int, y1: int) -> None:
        gs  = self.game_state
        gap = 10
        aw  = int((x1 - x0 - gap) * 0.38)   # agent roster
        mw  = x1 - x0 - gap - aw             # mission board

        ax0, ax1 = x0,        x0 + aw
        mx0, mx1 = ax1 + gap, x1

        self._draw_agent_panel(ax0, y0, ax1, y1, gs)
        self._draw_mission_panel(mx0, y0, mx1, y1, gs)

    def _draw_agent_panel(self, x0: int, y0: int, x1: int, y1: int, gs: GameState) -> None:
        _panel(x0, y0, x1, y1, f"AGENTS  {len(gs.selected_agent_names)}/{len(gs.characters)}", palette.ACCENT)

        selected_set  = set(gs.selected_agent_names)
        card_h        = 72
        card_gap      = 6
        scroll_top    = y1 - 34

        for i, char in enumerate(gs.characters):
            ct = scroll_top - i * (card_h + card_gap)
            cb = ct - card_h
            if cb < y0 + card_h:
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
            arcade.draw_text(char.name.upper(), tx, ct - 16, palette.TEXT, font_size=11, bold=True)
            arcade.draw_text(char.role.upper(), tx, ct - 30, role_col, font_size=9)

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

        # Recruit button at bottom
        btn_y = y0 + 4
        btn_h = 32
        _rect(x0 + 10, btn_y, x1 - 10, btn_y + btn_h, (8, 24, 14, 220))
        arcade.draw_line(x0 + 10, btn_y + btn_h, x1 - 10, btn_y + btn_h, palette.TACTICAL_GREEN, 2)
        arcade.draw_text(
            "RECRUIT  [N]",
            (x0 + x1) // 2, btn_y + btn_h // 2,
            palette.TACTICAL_GREEN, font_size=11, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hits.append(_HitRegion(x0 + 10, btn_y, x1 - 10, btn_y + btn_h, "recruit_prompt", None))

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
            arcade.draw_text(m.title.upper(), x0 + 66, ct - 16, palette.TEXT, font_size=12, bold=True)

            # Risk badge
            _badge(m.risk_level.upper(), x1 - 90, ct - 18, risk_col)

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
                x0 + 66, ct - 32, palette.MUTED_TEXT, font_size=9,
            )

            # Objective type
            arcade.draw_text(
                m.objective_type.upper(), x0 + 66, cb + 6,
                palette.ACCENT, font_size=9,
            )

            # Emotional impact
            if hasattr(m, "emotional_impact") and m.emotional_impact:
                arcade.draw_text(
                    f"⚠ {m.emotional_impact}", x1 - 200, cb + 6,
                    palette.MUTED_TEXT, font_size=9,
                )

            self._hits.append(_HitRegion(x0 + 8, cb, x1 - 8, ct, "select_mission", mi))

        # ── Selected mission detail ───────────────────────────────────────
        _panel(x0, y0, x1, split_y, "MISSION DETAILS", palette.ACCENT)

        m = _selected_mission(gs)
        if m:
            dx, dy = x0 + 14, split_y - 34

            # Title
            arcade.draw_text(m.title.upper(), dx, dy, palette.HEADER, font_size=14, bold=True)
            dy -= 26

            # Risk + reward row
            risk_col = _risk_color(m.risk_level)
            _badge(m.risk_level.upper(), dx, dy, risk_col)
            arcade.draw_text(f"¥ {m.fund_reward:,} reward", dx + 80, dy + 3, palette.RESOURCE, font_size=10)
            dur = getattr(m, "duration_days", 1)
            arcade.draw_text(f"{dur} day{'s' if dur != 1 else ''}", dx + 200, dy + 3, palette.MUTED_TEXT, font_size=10)
            dy -= 28

            # Objective text
            obj_lines = (m.objective_text or "").split(". ")
            for ln in obj_lines[:3]:
                if not ln:
                    continue
                arcade.draw_text(ln.strip(), dx, dy, palette.TEXT, font_size=10)
                dy -= 16

            # Complications
            complications = getattr(m, "possible_complications", [])
            if complications:
                dy -= 6
                arcade.draw_text(
                    f"Complications: {', '.join(str(c) for c in complications[:2])}",
                    dx, dy, palette.WARNING, font_size=9,
                )
                dy -= 16

            # Breakdown risk
            selected_squad = selected_deployable_agents(gs.characters, gs.selected_agent_names)
            at_risk = agents_at_breaking_risk(selected_squad, m) if selected_squad else []
            if at_risk:
                names = ", ".join(a.name for a in at_risk)
                arcade.draw_text(
                    f"⚠ BREAKDOWN RISK: {names}",
                    dx, dy, palette.DANGER, font_size=9, bold=True,
                )
                dy -= 16

        # Launch button (very prominent)
        lb = y0 + 4
        lt = lb + 44
        _rect(x0 + 10, lb, x1 - 10, lt, (10, 34, 16, 240))
        arcade.draw_line(x0 + 10, lt, x1 - 10, lt, palette.TACTICAL_GREEN, 3)
        arcade.draw_line(x0 + 10, lb, x1 - 10, lb, palette.TACTICAL_GREEN, 1)
        # Pulse the launch button
        pulse = 0.7 + 0.3 * math.sin(self._elapsed * 2.5)
        lbl_col = (
            int(palette.TACTICAL_GREEN[0] * pulse),
            int(palette.TACTICAL_GREEN[1] * pulse),
            int(palette.TACTICAL_GREEN[2] * pulse),
        )
        arcade.draw_text(
            "▶  LAUNCH MISSION  [B]",
            (x0 + x1) // 2, lb + 22,
            palette.TACTICAL_GREEN, font_size=14, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hits.append(_HitRegion(x0 + 10, lb, x1 - 10, lt, "launch_mission", None))

        # Message display
        if self.message:
            arcade.draw_text(
                self.message, x0 + 14, y0 + 58,
                palette.WARNING, font_size=10,
            )

    # ── RESEARCH tab ──────────────────────────────────────────────────────────

    def _draw_research_tab(self, x0: int, y0: int, x1: int, y1: int) -> None:
        gs = self.game_state
        _panel(x0, y0, x1, y1, "RESEARCH LABORATORY", palette.ROLE_PSI)

        lines = build_research_lab_lines(gs)
        ry = y1 - 38
        for line in lines[:30]:
            col = palette.RESOURCE if line.startswith("✓") else (
                palette.ACCENT if "[" in line or "day" in line.lower() else
                palette.TEXT
            )
            arcade.draw_text(line, x0 + 14, ry, col, font_size=10)
            ry -= 18
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
            arcade.draw_text(f"¥{proj.cost}", bx0 + 6, by0 + 4, palette.RESOURCE, font_size=8)
            self._hits.append(_HitRegion(bx0, by0, bx0 + bw, by0 + bh, f"start_research_{pi}", None))

    # ── INTEL tab ─────────────────────────────────────────────────────────────

    def _draw_intel_tab(self, x0: int, y0: int, x1: int, y1: int) -> None:
        gs  = self.game_state
        gap = 10
        hw  = (x1 - x0 - gap) // 2

        # ── Left: Narrative event log ────────────────────────────────────
        lx0, lx1 = x0, x0 + hw
        _panel(lx0, y0, lx1, y1, "NARRATIVE FEED", palette.ACCENT)

        iy = y1 - 36
        for log_entry in reversed(gs.event_log[-30:]):
            if iy < y0 + 12:
                break
            line = log_entry if isinstance(log_entry, str) else str(log_entry)
            col = (
                palette.DANGER if any(w in line.lower() for w in ("killed", "wounded", "lost", "failed"))
                else palette.TACTICAL_GREEN if any(w in line.lower() for w in ("success", "victory", "completed", "recruited"))
                else palette.TEXT
            )
            arcade.draw_text(line[:76], lx0 + 10, iy, col, font_size=9)
            iy -= 15

        # ── Right: Latest debrief ────────────────────────────────────────
        rx0, rx1 = lx1 + gap, x1
        _panel(rx0, y0, rx1, y1, "LATEST DEBRIEF", palette.HEADER)

        dy = y1 - 36
        debrief = getattr(gs, "latest_mission_debrief", None)
        if debrief:
            for section_key in ("mission_title", "outcome", "lines"):
                val = debrief.get(section_key, "")
                if isinstance(val, list):
                    for line in val[:12]:
                        if not isinstance(line, dict):
                            continue
                        text = line.get("text", "")
                        arcade.draw_text(text[:72], rx0 + 12, dy, palette.TEXT, font_size=9)
                        dy -= 14
                elif val:
                    col = palette.HEADER if section_key == "mission_title" else palette.TEXT
                    arcade.draw_text(str(val)[:70], rx0 + 12, dy, col, font_size=10)
                    dy -= 18
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
                arcade.draw_text(line[:70], rx0 + 12, dy, palette.TEXT, font_size=9)
                dy -= 14

    # ── Bottom bar ────────────────────────────────────────────────────────────

    def _draw_bottom_bar(self, w: int, h: int) -> None:
        _rect(0, 0, w, _BOT_BAR_H, palette.PANEL_FILL_DARK)
        arcade.draw_line(0, _BOT_BAR_H, w, _BOT_BAR_H, palette.PANEL_BORDER, 2)

        cy = _BOT_BAR_H // 2
        x  = 14

        def _btn(label: str, action: str, key_hint: str, col=None):
            nonlocal x
            col = col or palette.ACCENT
            bw = len(label) * 9 + 24
            _rect(x, 6, x + bw, _BOT_BAR_H - 6, (8, 20, 28, 220))
            arcade.draw_line(x, _BOT_BAR_H - 6, x + bw, _BOT_BAR_H - 6, col, 2)
            arcade.draw_text(
                f"{label} [{key_hint}]", x + 10, cy,
                col, font_size=10, anchor_y="center",
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
            # Double-click / toggle selection
            char = gs.characters[data] if data < len(gs.characters) else None
            if char:
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

        if action == "recruit_prompt":
            self._do_recruit_prompt()
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

    def _do_recruit_prompt(self) -> None:
        """Recruit a random agent (cycle roles: samurai → sniper → psi)."""
        gs = self.game_state
        if gs.spend_funds(5, "recruitment", "Recruited agent."):
            roles = ["samurai", "sniper", "psi"]
            role  = roles[len(gs.characters) % 3]
            agent = recruit_agent(gs.characters, role)
            self.deployment_cursor = len(gs.characters) - 1
            self.message = ""
            gs.add_event(push_action(self.notifications, "recruitment", True, f"{agent.name} as {role}"))
        else:
            blocked = blocked_recruit_reason(gs.available_funds)
            if blocked:
                self.message = blocked.to_ui_text()
                self.notifications.warning(self.message)
                gs.add_event(self.message)

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
        mission = _launch_mission(gs)

        from game.views import BattleView
        battle = BattleView(gs)
        battle.setup(mission)
        self.window.show_view(battle)
