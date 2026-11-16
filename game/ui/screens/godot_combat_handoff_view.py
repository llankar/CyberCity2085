"""Arcade bridge screen that overlays the Godot combat window on top of Arcade's window.

How it works (Windows):
  1. Godot is launched as a normal subprocess.
  2. Once Godot's HWND appears, its title bar and border are stripped and it is
     moved to the exact same screen rectangle as Arcade's window.
  3. Arcade's window is hidden — only Godot is visible from that point.
  4. When Godot writes its result JSON the combat outcome is applied to GameState,
     Godot is terminated, Arcade's window is shown again, and the view navigates
     to ManagementView.

Non-Windows: embedding/hiding is skipped; Godot opens in its own window as
before and the result JSON is still polled and applied.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

import arcade

from game.combat.godot_bridge import GodotCombatLaunchResult
from game.ui.panels import draw_panel
from game.ui.theme import colors

if TYPE_CHECKING:
    from game.gamestate import GameState
    from game.mission_templates import MissionTemplate

_WIN = sys.platform == "win32"

_HWND_POLL_INTERVAL   = 0.15   # seconds between HWND-search attempts


def open_mission_combat(window, game_state, mission) -> None:
    """One route for both launch screens; Arcade is an explicit compatibility choice."""
    if getattr(game_state, "combat_mission_ui_engine", "godot") == "arcade":
        from game.views import BattleView
        battle = BattleView(game_state)
        battle.setup(mission)
        window.show_view(battle)
        return
    from game.combat.godot_bridge import launch_godot_combat_ui
    result = launch_godot_combat_ui(game_state, mission)
    game_state.add_event(result.message)
    window.show_view(GodotCombatHandoffView(game_state, mission, result, window=window))


class GodotCombatHandoffView(arcade.View):
    """Bridge screen: overlays Godot's borderless window over Arcade's window."""

    def __init__(
        self,
        game_state: "GameState",
        mission: "MissionTemplate",
        launch_result: GodotCombatLaunchResult,
        *, window=None,
    ) -> None:
        super().__init__(window=window)
        if window is not None:
            self.window = window
        self.game_state    = game_state
        self.mission       = mission
        self.launch_result = launch_result

        self._result_applied: bool     = False
        self._overlaid:       bool     = False
        self._godot_hwnd:     int | None = None
        self._arcade_hwnd:    int | None = None
        self._hwnd_timer:     float    = 0.0
        self._launch_failed = not getattr(launch_result, "launched", True)
        self._status: str = (
            str(launch_result.message) if self._launch_failed else "LANCEMENT DU COMBAT GODOT…"
        )

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_show_view(self) -> None:
        if _WIN:
            from game.combat.win32_embed import get_current_process_hwnd
            self._arcade_hwnd = get_current_process_hwnd()

    def on_hide_view(self) -> None:
        self._cleanup_godot()

    # ── Update ────────────────────────────────────────────────────────────────

    def on_update(self, delta_time: float) -> None:
        if self._result_applied or self._launch_failed:
            return

        # Poll results even before a native window is found (and on Linux).
        from game.combat.godot_bridge import read_godot_combat_result
        result = read_godot_combat_result()
        if result is not None:
            self._result_applied = True
            self._cleanup_godot()
            self._apply_combat_result(result)
            return
        process = getattr(self.launch_result, "process", None)
        if process is not None and process.poll() is not None:
            self._cleanup_godot()
            self._launch_failed = True
            self._status = f"Godot s'est fermé sans résultat (code {process.returncode}). Réessayez ou choisissez son exécutable."
            self.game_state.add_event(self._status)
            return

        if not self._overlaid:
            self._hwnd_timer += delta_time
            if self._hwnd_timer >= _HWND_POLL_INTERVAL:
                self._hwnd_timer = 0.0
                self._try_overlay()
            return

    def _try_overlay(self) -> None:
        """Find Godot's window, make it borderless, place it over Arcade, hide Arcade."""
        pid = self.launch_result.process_pid
        if not pid:
            # No PID means Godot wasn't launched (or non-Windows); jump to polling.
            self._overlaid = True
            self._status   = "COMBAT GODOT EN COURS"
            return

        if not _WIN:
            self._overlaid = True
            self._status   = "COMBAT GODOT EN COURS"
            return

        from game.combat.win32_embed import (
            get_process_hwnd, get_window_screen_rect,
            make_borderless_at, hide_window,
        )
        hwnd = get_process_hwnd(pid)
        if not hwnd:
            return  # Godot not ready yet — try again next tick

        x, y, w, h = get_window_screen_rect(self._arcade_hwnd) \
            if self._arcade_hwnd else (0, 0, self.window.width, self.window.height)

        make_borderless_at(hwnd, x, y, w, h)
        if self._arcade_hwnd:
            hide_window(self._arcade_hwnd)

        self._godot_hwnd = hwnd
        self._overlaid   = True
        self._status     = "COMBAT GODOT EN COURS"

    def _cleanup_godot(self) -> None:
        """Terminate Godot and restore Arcade's window."""
        process = getattr(self.launch_result, "process", None)
        if process is not None and process.poll() is None:
            process.terminate()
        if not _WIN:
            return
        from game.combat.win32_embed import hide_window, show_window, terminate_pid

        if self._godot_hwnd:
            hide_window(self._godot_hwnd)
            self._godot_hwnd = None

        if self._arcade_hwnd:
            show_window(self._arcade_hwnd)

        if process is None and self.launch_result.process_pid:
            terminate_pid(self.launch_result.process_pid)

        self._overlaid = False

    # ── Drawing ───────────────────────────────────────────────────────────────

    def on_draw(self) -> None:
        self.clear()
        if self._overlaid and _WIN:
            return  # Godot is visible; Arcade's window is hidden.
        self._draw_splash()

    def _draw_splash(self) -> None:
        w = getattr(self.window, "width", 1280)
        h = getattr(self.window, "height", 720)
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (3, 8, 14, 255))

        panel_w = min(820, w - 80)
        panel_h = 280
        left   = (w - panel_w) // 2
        bottom = (h - panel_h) // 2
        draw_panel(left, bottom, panel_w, panel_h)

        arcade.draw_text(
            "COMBAT GODOT INDISPONIBLE" if self._launch_failed else "COMBAT GODOT",
            w // 2, bottom + panel_h - 52,
            colors.text_primary,
            font_size=24, bold=True, anchor_x="center",
        )
        arcade.draw_text(
            self.mission.title,
            w // 2, bottom + panel_h - 90,
            colors.accent_primary,
            font_size=14, bold=True, anchor_x="center",
        )
        arcade.draw_text(
            self._status,
            w // 2, bottom + panel_h - 138,
            colors.text_secondary,
            font_size=12, anchor_x="center", width=panel_w - 64, multiline=True,
        )
        arcade.draw_text(
            "R : réessayer | G : choisir Godot | F : ancien combat Arcade | Échap : retour",
            w // 2, bottom + 28,
            colors.text_secondary,
            font_size=10, anchor_x="center",
        )

    # ── Input ─────────────────────────────────────────────────────────────────

    def on_key_press(self, key: int, _modifiers: int) -> None:
        if key == arcade.key.R and self._launch_failed:
            self._retry_godot()
        elif key == arcade.key.G and self._launch_failed:
            from game.ui.screens.settings_screen import (
                _browse_for_godot_executable, _persist_godot_bin_path, load_settings,
            )
            selected = _browse_for_godot_executable(load_settings().godot_bin_path)
            if selected:
                _persist_godot_bin_path(selected)
                self._retry_godot()
        elif key == arcade.key.F:
            self._result_applied = True
            self._cleanup_godot()
            self.game_state.add_event("Ancien combat Arcade choisi explicitement pour cette mission.")
            self._fallback_to_arcade_battle()
        elif key == arcade.key.ESCAPE:
            self._cleanup_godot()
            self._return_to_management()

    def _retry_godot(self) -> None:
        from game.combat.godot_bridge import launch_godot_combat_ui
        self._cleanup_godot()
        self.launch_result = launch_godot_combat_ui(self.game_state, self.mission)
        self._launch_failed = not self.launch_result.launched
        self._overlaid = False
        self._status = self.launch_result.message
        self.game_state.add_event(self._status)

    # ── Result application ────────────────────────────────────────────────────

    def _apply_combat_result(self, result: dict[str, Any]) -> None:
        outcome        = str(result.get("outcome", "unknown"))
        funds_earned   = int(result.get("funds_earned", 0))
        xp_per_agent   = int(result.get("xp_per_agent", 0))
        enemies_killed = int(result.get("enemies_killed", 0))
        casualties: list[str] = [str(c) for c in result.get("casualties", [])]

        if funds_earned > 0:
            self.game_state.add_funds(
                funds_earned, "mission_reward", f"Combat: {self.mission.title}"
            )

        deployed_names: set[str] = set(
            getattr(self.game_state, "selected_agent_names", [])
        )
        casualty_names = {c.strip().upper() for c in casualties}

        for character in self.game_state.characters:
            name_upper = character.name.strip().upper()
            if name_upper in deployed_names or character.name in deployed_names:
                if xp_per_agent > 0:
                    character.gain_xp(xp_per_agent)
            if name_upper in casualty_names or character.name in casualty_names:
                character.stats.hp = 0
                if "KIA" not in character.injuries:
                    character.injuries.append("KIA")

        summary = (
            f"Mission {outcome.upper()}: {self.mission.title} — "
            f"{enemies_killed} enemies down, {len(casualties)} casualties"
            + (f", ${funds_earned:,} earned" if funds_earned else "")
            + "."
        )
        self.game_state.add_event(summary)
        self._return_to_management()

    def _fallback_to_arcade_battle(self) -> None:
        from game.views import BattleView
        battle = BattleView(self.game_state)
        battle.setup(self.mission)
        self.window.show_view(battle)

    def _return_to_management(self) -> None:
        from game.ui.screens.management_screen import ManagementView
        mgmt = ManagementView(self.game_state)
        mgmt.setup()
        mgmt.active_tab = "squad"
        self.window.show_view(mgmt)
