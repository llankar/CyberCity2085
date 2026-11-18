"""Arcade bridge screen that overlays the Godot combat window on top of Arcade's window.

How it works (Windows):
  1. Godot is launched as a normal subprocess.
  2. Once Godot's HWND appears, its title bar and border are stripped and it is
     moved to the exact same screen rectangle as Arcade's window.
  3. Arcade retains the transition surface behind Godot.
  4. Only a player-confirmed, validated session result is resolved by the common
     campaign service. An acknowledgement releases Godot, then Arcade shows
     Debrief → optional Promotions → Headquarters.

Non-Windows: embedding/hiding is skipped; Godot opens in its own window as
before and the result JSON is still polled and applied.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

import arcade

from game.combat.godot_bridge import GodotCombatLaunchResult

if TYPE_CHECKING:
    from game.gamestate import GameState
    from game.mission_templates import MissionTemplate

_WIN = sys.platform == "win32"

_HWND_POLL_INTERVAL = 0.15  # seconds between HWND-search attempts


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
        *,
        window=None,
    ) -> None:
        super().__init__(window=window)
        if window is not None:
            self.window = window
        self.game_state = game_state
        self.mission = mission
        self.launch_result = launch_result

        self._result_applied: bool = False
        self._overlaid: bool = False
        self._godot_hwnd: int | None = None
        self._arcade_hwnd: int | None = None
        self._hwnd_timer: float = 0.0
        self._launch_failed = not getattr(launch_result, "launched", True)
        self._status: str = (
            str(launch_result.message)
            if self._launch_failed
            else "LANCEMENT DU COMBAT GODOT…"
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
        self._elapsed = getattr(self, "_elapsed", 0.0) + delta_time
        if hasattr(self, "_visual_deck"):
            self._visual_deck.update(delta_time)
        if self._result_applied:
            pending = getattr(self, "_pending_return", None)
            if pending is not None:
                self._write_pending_ack()
                self._return_wait = getattr(self,"_return_wait",0.0)+delta_time
                process = getattr(self.launch_result,"process",None)
                if process is None or process.poll() is not None or self._return_wait>=2.0:
                    self._pending_return=None
                    self._cleanup_godot()
                    from game.ui.screens.mission_return import show_mission_debrief
                    context,survivors,units=pending
                    context.window=self.window
                    show_mission_debrief(context, context._victory, survivors, units)
            return
        if self._launch_failed:
            return

        # Poll results even before a native window is found (and on Linux).
        from game.combat.godot_bridge import read_godot_combat_result

        result_path = getattr(self.launch_result,"result_path",None)
        result = read_godot_combat_result(result_path) if result_path else None
        if result is not None:
            try:
                self._apply_combat_result(result)
            except (ValueError, KeyError, TypeError, OSError) as exc:
                self._cleanup_godot()
                self._launch_failed=True
                self._status=f"Résultat refusé ; campagne inchangée : {exc}"
                self.game_state.add_event(self._status)
            return
        process = getattr(self.launch_result, "process", None)
        if process is not None and process.poll() is not None:
            self._cleanup_godot()
            self._launch_failed = True
            self._status = f"Godot s'est fermé sans résultat (code {process.returncode}). C : confirmer un résultat préparé récupérable ; R : réessayer ; G : choisir l’exécutable."
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
            self._status = "COMBAT GODOT EN COURS"
            return

        if not _WIN:
            self._overlaid = True
            self._status = "COMBAT GODOT EN COURS"
            return

        from game.combat.win32_embed import (
            get_process_hwnd,
            get_window_screen_rect,
            make_borderless_at,
            hide_window,
        )

        hwnd = get_process_hwnd(pid)
        if not hwnd:
            return  # Godot not ready yet — try again next tick

        x, y, w, h = (
            get_window_screen_rect(self._arcade_hwnd)
            if self._arcade_hwnd
            else (0, 0, self.window.width, self.window.height)
        )

        make_borderless_at(hwnd, x, y, w, h)
        # Keep the campaign surface behind Godot so exit cannot reveal the desktop.

        self._godot_hwnd = hwnd
        self._overlaid = True
        self._status = "COMBAT GODOT EN COURS"

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
        if self._overlaid and _WIN:
            return  # Preserve the last transition frame behind Godot.
        self.clear()
        self._draw_splash()

    def _draw_splash(self):
        if not hasattr(self, "_visual_deck"):
            from game.ui.components.utilities.handoff import HandoffDeck

            self._visual_deck = HandoffDeck()
        self._elapsed = getattr(self, "_elapsed", 0.0)
        self._visual_deck.draw(self)

    def on_mouse_motion(self, x, y, dx, dy):
        if hasattr(self, "_visual_deck"):
            self._visual_deck.motion(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for hit in getattr(self, "_hits", []):
            if hit.contains(x, y):
                if not self._visual_deck.activate(hit):
                    self.on_key_press(hit.data, 0)
                return

    # ── Input ─────────────────────────────────────────────────────────────────

    def on_key_press(self, key: int, _modifiers: int) -> None:
        if hasattr(self, "_visual_deck") and key in (
            arcade.key.TAB,
            arcade.key.UP,
            arcade.key.DOWN,
            arcade.key.SPACE,
        ):
            result = self._visual_deck.keyboard(key)
            if result and result is not True:
                if not self._visual_deck.activate(result):
                    self.on_key_press(result.data, 0)
            return
        if key == getattr(arcade.key,"C",67) and self._launch_failed:
            self._recover_prepared_result()
        elif key == arcade.key.R and self._launch_failed:
            self._retry_godot()
        elif key == arcade.key.G and self._launch_failed:
            from game.ui.screens.settings_screen import (
                _browse_for_godot_executable,
                _persist_godot_bin_path,
                load_settings,
            )

            selected = _browse_for_godot_executable(load_settings().godot_bin_path)
            if selected:
                _persist_godot_bin_path(selected)
                self._retry_godot()
        elif key == arcade.key.F:
            self._abandon_session()
            self._result_applied = True
            self._cleanup_godot()
            self.game_state.add_event(
                "Ancien combat Arcade choisi explicitement pour cette mission."
            )
            self._fallback_to_arcade_battle()
        elif key == arcade.key.ESCAPE:
            self._abandon_session()
            self._cleanup_godot()
            self._return_to_management()

    def _abandon_session(self) -> None:
        sessions=getattr(self.game_state,"combat_sessions",{})
        record=sessions.get(getattr(self.launch_result,"session_id",""))
        if record is not None and record.get("status")=="pending":
            record["status"]="abandoned"

    def _recover_prepared_result(self) -> None:
        from game.combat.godot_bridge import read_godot_combat_result
        session=self.game_state.combat_sessions.get(getattr(self.launch_result,"session_id",""),{})
        path=session.get("session",{}).get("prepared_path")
        result=read_godot_combat_result(path) if path else None
        if result is None:
            self._status="Aucun résultat préparé récupérable ; choisissez explicitement une nouvelle tentative."
            return
        result["phase"]="confirmed"
        try:
            self._apply_combat_result(result)
            self._launch_failed=False
        except (ValueError,KeyError,TypeError,OSError) as exc:
            self._status=f"Récupération refusée : {exc}"

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
        from game.combat.godot_resolution import resolve_godot_result

        session_id=getattr(self.launch_result,"session_id","")
        resolved=resolve_godot_result(self.game_state,self.mission,result,session_id)
        record=self.game_state.combat_sessions[session_id]
        self._pending_ack=(record["session"]["ack_path"],{
            "protocol_version":2,"session_id":session_id,"status":"accepted",
            "result_digest":record["result_digest"],
        })
        self._write_pending_ack()
        self._result_applied=True
        if resolved is None:
            self._cleanup_godot()
            self._return_to_management()
            return
        context,survivors,units=resolved
        context._victory=result["outcome"]=="victory"
        self._pending_return=(context,survivors,units)
        self._return_wait=0.0

    def _write_pending_ack(self) -> None:
        from game.combat.session_protocol import atomic_json
        pending=getattr(self,"_pending_ack",None)
        if pending is None:return
        try:
            atomic_json(*pending)
            self._pending_ack=None
        except OSError:
            self._status="Résultat appliqué ; acquittement différé. Aucun second paiement ne sera appliqué."

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
