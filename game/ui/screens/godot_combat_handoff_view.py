"""Arcade shell screen shown after handing combat UI control to Godot."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import arcade

from game.combat.godot_bridge import GodotCombatLaunchResult
from game.ui.panels import draw_panel
from game.ui.theme import colors

if TYPE_CHECKING:
    from game.gamestate import GameState
    from game.mission_templates import MissionTemplate


class GodotCombatHandoffView(arcade.View):
    """Small bridge screen while the Godot combat-mission UI is open or prepared."""

    def __init__(
        self,
        game_state: "GameState",
        mission: "MissionTemplate",
        launch_result: GodotCombatLaunchResult,
    ) -> None:
        super().__init__()
        self.game_state = game_state
        self.mission = mission
        self.launch_result = launch_result

    def on_draw(self) -> None:
        self.clear()
        w = getattr(self.window, "width", 1280)
        h = getattr(self.window, "height", 720)
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (3, 8, 14, 255))
        panel_w = min(820, w - 80)
        panel_h = 320
        left = (w - panel_w) // 2
        bottom = (h - panel_h) // 2
        draw_panel(left, bottom, panel_w, panel_h)

        title = "GODOT COMBAT UI"
        status = "LAUNCHED" if self.launch_result.launched else "HANDOFF READY"
        arcade.draw_text(
            title,
            w // 2,
            bottom + panel_h - 54,
            colors.text_primary,
            font_size=24,
            bold=True,
            anchor_x="center",
        )
        arcade.draw_text(
            f"{status}: {self.mission.title}",
            w // 2,
            bottom + panel_h - 92,
            colors.accent_primary,
            font_size=14,
            bold=True,
            anchor_x="center",
        )
        lines = [
            self.launch_result.message,
            f"Handoff: {Path(self.launch_result.handoff_path)}",
            "Godot owns the combat mission UI; Arcade remains the campaign shell.",
            "F = local Arcade fallback  |  Esc = return to management",
        ]
        y = bottom + panel_h - 138
        for line in lines:
            arcade.draw_text(
                line,
                left + 34,
                y,
                colors.text_secondary,
                font_size=12,
            )
            y -= 34

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.F:
            self._fallback_to_arcade_battle()
        elif key == arcade.key.ESCAPE:
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
