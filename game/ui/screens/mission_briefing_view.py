"""Mission Briefing Screen — shown before BattleView launches.

Displays mission objectives, enemy intel, map thumbnail, squad roster,
and emotional impact hint. Player chooses DEPLOY or ABORT.
"""

from __future__ import annotations

import os
import random
from typing import TYPE_CHECKING

import arcade

from game.ui import palette
from game.ui.panels import draw_panel

if TYPE_CHECKING:
    from game.gamestate import GameState
    from game.mission_templates import MissionTemplate


# ── Layout constants ──────────────────────────────────────────────────────────
_THUMB_W = 200
_THUMB_H = 112
_CARD_W  = 64
_CARD_H  = 80


class MissionBriefingView(arcade.View):
    """Full-screen mission briefing shown between management and battle launch."""

    def __init__(self, game_state: "GameState", mission: "MissionTemplate") -> None:
        super().__init__()
        self.game_state = game_state
        self.mission = mission
        self._map_texture: arcade.Texture | None = None
        self._portrait_textures: list[arcade.Texture | None] = []
        self._deploy_rect: tuple[int, int, int, int] | None = None
        self._abort_rect:  tuple[int, int, int, int] | None = None

    def on_show_view(self) -> None:
        arcade.set_background_color((4, 10, 18))
        self._load_assets()
        from game.audio import SoundManager
        from game.ui.screens.settings_screen import SettingsState
        sm = SoundManager.get()
        sm.ensure_loaded()
        from game.ui.screens.settings_screen import load_settings as _ls
        sm.configure_from_settings(_ls())
        sm.play_music("music_briefing", loop=True)

    def _load_assets(self) -> None:
        # Pick a random map thumbnail
        maps_dir = "assets/maps"
        try:
            maps = sorted(
                f for f in os.listdir(maps_dir)
                if f.lower().endswith((".jpeg", ".jpg", ".png")) and not f.startswith(".")
            )
            if maps:
                chosen = random.choice(maps)
                self._map_texture = arcade.load_texture(os.path.join(maps_dir, chosen))
        except Exception:
            pass

        # Load agent portraits for selected squad
        from game.ui.portraits import portrait_path_for_character
        from game.deployment import selected_deployable_agents
        selected = selected_deployable_agents(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        self._portrait_textures = []
        for char in selected:
            try:
                path = portrait_path_for_character(char)
                self._portrait_textures.append(arcade.load_texture(path))
            except Exception:
                self._portrait_textures.append(None)

    def on_draw(self) -> None:
        self.clear()
        w, h = self.window.width, self.window.height
        self._draw_background(w, h)
        self._draw_header(w, h)
        self._draw_left_panel(w, h)
        self._draw_right_panel(w, h)
        self._draw_footer(w, h)

    def _draw_background(self, w: int, h: int) -> None:
        # Subtle scanline-style gradient
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (4, 10, 18, 255))
        arcade.draw_lrbt_rectangle_filled(0, w, h - 2, h, palette.PANEL_BORDER)
        arcade.draw_lrbt_rectangle_filled(0, w, 0, 2, palette.PANEL_BORDER)

    def _draw_header(self, w: int, h: int) -> None:
        hh = 54
        arcade.draw_lrbt_rectangle_filled(0, w, h - hh, h, (0, 0, 0, 200))
        arcade.draw_line(0, h - hh, w, h - hh, palette.PANEL_BORDER, 2)
        # XCOM-style top-left notch
        arcade.draw_line(0, h, 20, h - 20, palette.TACTICAL_GREEN, 2)

        arcade.draw_text(
            "MISSION BRIEFING",
            20, h - hh // 2,
            palette.MUTED_TEXT, font_size=11, bold=True,
            anchor_y="center",
        )
        arcade.draw_text(
            self.mission.title.upper(),
            w // 2, h - hh // 2,
            palette.HEADER, font_size=18, bold=True,
            anchor_x="center", anchor_y="center",
        )
        arcade.draw_text(
            f"DISTRICT: {self.mission.district.upper()}  //  FACTION: {self.mission.target_faction.upper()}",
            w - 20, h - hh // 2,
            palette.MUTED_TEXT, font_size=10,
            anchor_x="right", anchor_y="center",
        )

    def _draw_left_panel(self, w: int, h: int) -> None:
        panel_l = 20
        panel_b = 80
        panel_w = w // 2 - 30
        panel_h = h - 150

        draw_panel(panel_l, panel_b, panel_w, panel_h, "INTEL & OBJECTIVES")

        y = panel_b + panel_h - 50

        # Objective
        arcade.draw_text("OBJECTIVE", panel_l + 14, y, palette.TACTICAL_GREEN, font_size=10, bold=True)
        y -= 18
        arcade.draw_text(
            self.mission.objective_text[:72],
            panel_l + 14, y, palette.TEXT, font_size=10,
            width=panel_w - 28, multiline=True,
        )
        y -= 36

        # Risk + duration
        risk_col = (
            palette.TACTICAL_GREEN if self.mission.risk_level <= 3
            else palette.WARNING if self.mission.risk_level <= 6
            else palette.DANGER
        )
        arcade.draw_text(
            f"RISK: {self.mission.risk_level}/10   DURATION: {self.mission.duration_days}d   REWARD: ¥{self.mission.fund_reward}",
            panel_l + 14, y, risk_col, font_size=10,
        )
        y -= 26

        # Complications
        if self.mission.possible_complications:
            arcade.draw_text("COMPLICATIONS", panel_l + 14, y, palette.WARNING, font_size=10, bold=True)
            y -= 18
            for comp in self.mission.possible_complications[:3]:
                if isinstance(comp, str):
                    label = comp
                else:
                    label = getattr(comp, "trigger_text", None) or getattr(comp, "name", str(comp))
                arcade.draw_text(f"  • {label[:60]}", panel_l + 14, y, palette.MUTED_TEXT, font_size=9)
                y -= 15
            y -= 8

        # Emotional impact
        hint = getattr(self.mission, "emotional_impact_hint", None)
        if hint and isinstance(hint, dict) and hint.get("text"):
            level = hint.get("level", "medium").upper()
            level_col = {"LOW": palette.TACTICAL_GREEN, "MEDIUM": palette.WARNING,
                         "HIGH": palette.DANGER, "CRITICAL": palette.DANGER}.get(level, palette.MUTED_TEXT)
            arcade.draw_text("HUMAN IMPACT", panel_l + 14, y, level_col, font_size=10, bold=True)
            y -= 18
            arcade.draw_text(
                hint["text"][:80],
                panel_l + 14, y, palette.MUTED_TEXT, font_size=9,
                width=panel_w - 28, multiline=True,
            )
            y -= 30

        # Map thumbnail
        thumb_y = panel_b + 8
        if self._map_texture:
            arcade.draw_texture_rect(
                self._map_texture,
                arcade.LBWH(panel_l + 14, thumb_y, _THUMB_W, _THUMB_H),
            )
            arcade.draw_lrbt_rectangle_outline(
                panel_l + 14, panel_l + 14 + _THUMB_W,
                thumb_y, thumb_y + _THUMB_H,
                palette.PANEL_BORDER, 1,
            )
            arcade.draw_text(
                "TACTICAL MAP", panel_l + 14 + _THUMB_W + 10, thumb_y + _THUMB_H // 2,
                palette.MUTED_TEXT, font_size=9, anchor_y="center",
            )

        # Enemy intel
        enemy_x = panel_l + 14 + _THUMB_W + 10
        arcade.draw_text(
            f"ENEMY CONTACTS: ~{self.mission.starting_enemy_count}",
            enemy_x, thumb_y + _THUMB_H // 2 - 20,
            palette.DANGER, font_size=10,
        )
        arcade.draw_text(
            f"PRESSURE: {self.mission.district_pressure}/10",
            enemy_x, thumb_y + _THUMB_H // 2 - 38,
            palette.WARNING, font_size=9,
        )

    def _draw_right_panel(self, w: int, h: int) -> None:
        panel_l = w // 2 + 10
        panel_b = 80
        panel_w = w // 2 - 30
        panel_h = h - 150

        draw_panel(panel_l, panel_b, panel_w, panel_h, "DEPLOYED SQUAD")

        y = panel_b + panel_h - 50
        selected_names = set(self.game_state.selected_agent_names or [])
        from game.deployment import selected_deployable_agents
        agents = selected_deployable_agents(self.game_state.characters, self.game_state.selected_agent_names)

        if not agents:
            arcade.draw_text(
                "No agents selected for deployment.",
                panel_l + 14, y, palette.MUTED_TEXT, font_size=10,
            )
        else:
            card_x = panel_l + 14
            for i, char in enumerate(agents[:6]):
                portrait = self._portrait_textures[i] if i < len(self._portrait_textures) else None
                cx = card_x + i * (_CARD_W + 8)
                # Portrait card background
                arcade.draw_lrbt_rectangle_filled(cx, cx + _CARD_W, y - _CARD_H, y, (16, 34, 48, 220))
                arcade.draw_lrbt_rectangle_outline(cx, cx + _CARD_W, y - _CARD_H, y, palette.PANEL_BORDER, 1)
                if portrait:
                    arcade.draw_texture_rect(
                        portrait,
                        arcade.LBWH(cx + 2, y - _CARD_H + 16, _CARD_W - 4, _CARD_H - 20),
                    )
                # Name
                arcade.draw_text(
                    char.name[:9], cx + _CARD_W // 2, y - _CARD_H + 8,
                    palette.TEXT, font_size=8,
                    anchor_x="center", anchor_y="center",
                )
                # Role tag
                arcade.draw_text(
                    char.role.upper()[:6], cx + _CARD_W // 2, y - 10,
                    palette.ACCENT, font_size=7,
                    anchor_x="center", anchor_y="center",
                )

            y -= _CARD_H + 20

            # Stress summary
            stress_sum = sum(c.stress for c in agents)
            avg_stress = stress_sum // max(1, len(agents))
            stress_col = (
                palette.TACTICAL_GREEN if avg_stress < 30
                else palette.WARNING if avg_stress < 60
                else palette.DANGER
            )
            arcade.draw_text(
                f"SQUAD STRESS AVG: {avg_stress}%",
                panel_l + 14, y, stress_col, font_size=10,
            )
            y -= 20

            # Tag list
            if self.mission.tags:
                arcade.draw_text("MISSION TAGS:", panel_l + 14, y, palette.MUTED_TEXT, font_size=9)
                y -= 16
                tags_str = "  ".join(f"[{t}]" for t in self.mission.tags[:6])
                arcade.draw_text(tags_str, panel_l + 14, y, palette.ACCENT, font_size=9)
                y -= 20

            # Consequence preview
            def _consequence_text(c) -> str:
                if isinstance(c, str):
                    return c
                return getattr(c, "narrative_text", str(c)) or str(c)

            if self.mission.success_consequences:
                arcade.draw_text("ON SUCCESS:", panel_l + 14, y, palette.TACTICAL_GREEN, font_size=9, bold=True)
                y -= 15
                for c in self.mission.success_consequences[:2]:
                    arcade.draw_text(f"  {_consequence_text(c)[:55]}", panel_l + 14, y, palette.MUTED_TEXT, font_size=8)
                    y -= 13
            y -= 8
            if self.mission.failure_consequences:
                arcade.draw_text("ON FAILURE:", panel_l + 14, y, palette.DANGER, font_size=9, bold=True)
                y -= 15
                for c in self.mission.failure_consequences[:2]:
                    arcade.draw_text(f"  {_consequence_text(c)[:55]}", panel_l + 14, y, palette.MUTED_TEXT, font_size=8)
                    y -= 13

    def _draw_footer(self, w: int, h: int) -> None:
        fh = 68
        arcade.draw_lrbt_rectangle_filled(0, w, 0, fh, (0, 0, 0, 200))
        arcade.draw_line(0, fh, w, fh, palette.PANEL_BORDER, 2)

        bw, bh = 180, 44
        by = (fh - bh) // 2

        # DEPLOY button
        deploy_x = w // 2 + 10
        arcade.draw_lrbt_rectangle_filled(deploy_x, deploy_x + bw, by, by + bh, (16, 48, 24, 230))
        arcade.draw_line(deploy_x, by + bh, deploy_x + bw, by + bh, palette.TACTICAL_GREEN, 2)
        arcade.draw_text(
            "DEPLOY  [Enter]",
            deploy_x + bw // 2, by + bh // 2,
            palette.TACTICAL_GREEN, font_size=13, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._deploy_rect = (deploy_x, by, deploy_x + bw, by + bh)

        # ABORT button
        abort_x = w // 2 - bw - 10
        arcade.draw_lrbt_rectangle_filled(abort_x, abort_x + bw, by, by + bh, (40, 14, 14, 220))
        arcade.draw_line(abort_x, by + bh, abort_x + bw, by + bh, palette.DANGER, 2)
        arcade.draw_text(
            "ABORT  [Esc]",
            abort_x + bw // 2, by + bh // 2,
            palette.DANGER, font_size=13, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._abort_rect = (abort_x, by, abort_x + bw, by + bh)

        # Hint text
        arcade.draw_text(
            "Enter = Deploy   Esc = Abort",
            w // 2, 8,
            palette.MUTED_TEXT, font_size=9,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers) -> None:
        if key in (arcade.key.RETURN, arcade.key.ENTER):
            self._launch_battle()
        elif key == arcade.key.ESCAPE:
            self._abort()

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        if self._deploy_rect:
            l, b, r, t = self._deploy_rect
            if l <= x <= r and b <= y <= t:
                self._launch_battle()
                return
        if self._abort_rect:
            l, b, r, t = self._abort_rect
            if l <= x <= r and b <= y <= t:
                self._abort()

    def _launch_battle(self) -> None:
        from game.views import BattleView
        battle = BattleView(self.game_state)
        battle.setup(self.mission)
        self.window.show_view(battle)

    def _abort(self) -> None:
        from game.ui.screens.management_screen import ManagementView
        mgmt = ManagementView(self.game_state)
        mgmt.setup()
        mgmt.active_tab = "squad"
        self.window.show_view(mgmt)
