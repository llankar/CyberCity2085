"""Full-screen world map mission selector."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import arcade

from game.agent_readiness import agents_at_breaking_risk
from game.character import is_deployable
from game.deployment import sanitize_selected_agent_names, selected_deployable_agents
from game.mission_system import (
    ensure_mission_templates,
    launch_selected_mission as _launch_mission,
    selected_mission as _selected_mission,
)
from game.ui import GameView
from game.ui import palette
from game.ui.management.action_requirements import blocked_launch_reason
from game.ui.mission_board import build_selected_mission_lines
from game.ui.panels import draw_panel
from game.ui.screens.world_map import (
    build_world_map_mission_nodes,
    load_world_map_texture,
    mission_label_text,
    mission_site_name,
    texture_rect,
)

if TYPE_CHECKING:
    from game.mission_templates import MissionTemplate


@dataclass(frozen=True)
class _HitRegion:
    left: int
    bottom: int
    right: int
    top: int
    action: str
    data: object = None

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x <= self.right and self.bottom <= y <= self.top


class MissionWorldMapView(GameView):
    """Full-screen mission selector backed by the world map art."""

    def __init__(self, game_state) -> None:
        super().__init__(game_state)
        self._hits: list[_HitRegion] = []
        self._message = ""
        self._pending_launch_confirm = False
        self._pending_launch_mission_id: str | None = None

    def on_show_view(self) -> None:
        arcade.set_background_color((5, 10, 18))
        ensure_mission_templates(self.game_state)

    def on_draw(self) -> None:
        self.clear()
        w, h = self.window.width, self.window.height
        self._hits = []

        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (5, 10, 18, 255))
        arcade.draw_lrbt_rectangle_filled(0, w, h - 54, h, (0, 0, 0, 180))
        arcade.draw_line(0, h - 54, w, h - 54, palette.PANEL_BORDER, 2)
        arcade.draw_text(
            "MISSION WORLD MAP",
            22,
            h - 27,
            palette.HEADER,
            font_size=17,
            bold=True,
            anchor_y="center",
        )
        arcade.draw_text(
            "Click a pin to inspect the mission. Select Mission returns to management.",
            w - 22,
            h - 27,
            palette.MUTED_TEXT,
            font_size=10,
            anchor_x="right",
            anchor_y="center",
        )

        map_left = 24
        map_bottom = 108
        map_right = int(w * 0.62)
        map_top = h - 72
        info_left = map_right + 16
        info_bottom = 108
        info_right = w - 24
        info_top = h - 72

        draw_panel(map_left, map_bottom, map_right - map_left, map_top - map_bottom, "WORLD MAP")
        draw_panel(info_left, info_bottom, info_right - info_left, info_top - info_bottom, "MISSION DETAILS")

        texture = load_world_map_texture()
        image_left = map_left + 16
        image_right = map_right - 16
        image_bottom = map_bottom + 18
        image_top = map_top - 22
        if texture is not None and getattr(texture, "width", 0) and getattr(texture, "height", 0):
            scale = min((image_right - image_left) / texture.width, (image_top - image_bottom) / texture.height)
            draw_w = max(1.0, texture.width * scale)
            draw_h = max(1.0, texture.height * scale)
            tex_left = image_left + ((image_right - image_left) - draw_w) / 2
            tex_bottom = image_bottom + ((image_top - image_bottom) - draw_h) / 2
            map_rect = texture_rect(tex_left, tex_bottom, tex_left + draw_w, tex_bottom + draw_h)
            arcade.draw_texture_rect(texture, map_rect, pixelated=True, alpha=255)
            pin_left, pin_bottom, pin_right, pin_top = tex_left, tex_bottom, tex_left + draw_w, tex_bottom + draw_h
        else:
            map_rect = texture_rect(image_left, image_bottom, image_right, image_top)
            arcade.draw_lrbt_rectangle_filled(image_left, image_right, image_bottom, image_top, (12, 22, 28, 240))
            for gx in range(image_left, image_right + 1, max(80, (image_right - image_left) // 8 or 80)):
                arcade.draw_line(gx, image_bottom, gx, image_top, (40, 58, 68, 120), 1)
            for gy in range(image_bottom, image_top + 1, max(60, (image_top - image_bottom) // 5 or 60)):
                arcade.draw_line(image_left, gy, image_right, gy, (40, 58, 68, 120), 1)
            pin_left, pin_bottom, pin_right, pin_top = image_left, image_bottom, image_right, image_top

        missions = self.game_state.mission_templates
        selected_index = self.game_state.selected_mission_index
        nodes = build_world_map_mission_nodes(
            missions,
            selected_index,
            int(pin_left),
            int(pin_bottom),
            int(pin_right),
            int(pin_top),
        )
        selected_node = None
        for node in nodes:
            if node.mission_index == selected_index:
                selected_node = node
            selected = node.mission_index == selected_index
            risk_col = palette.TACTICAL_GREEN if selected else palette.WARNING
            if selected:
                risk_col = palette.TACTICAL_GREEN
            arcade.draw_circle_filled(node.pin_x, node.pin_y, 8 if selected else 6, risk_col)
            arcade.draw_circle_outline(node.pin_x, node.pin_y, 14, palette.WARNING if selected else risk_col, 2)
            arcade.draw_line(node.pin_x, node.pin_y - 2, node.pin_x, node.pin_y - 15, palette.WARNING if selected else risk_col, 2)
            _rect = (node.label_left, node.label_bottom, node.label_right, node.label_top)
            arcade.draw_lrbt_rectangle_filled(_rect[0], _rect[2], _rect[1], _rect[3], (10, 20, 26, 235) if selected else (8, 16, 22, 220))
            arcade.draw_line(_rect[0], _rect[3], _rect[2], _rect[3], palette.WARNING if selected else risk_col, 2)
            arcade.draw_text(
                mission_label_text(node.mission),
                node.label_left + 8,
                node.label_top - 15,
                palette.TEXT,
                font_size=9,
                bold=True,
                anchor_y="top",
            )
            arcade.draw_text(
                mission_site_name(node.site_key),
                node.label_left + 8,
                node.label_bottom + 5,
                palette.MUTED_TEXT,
                font_size=8,
                anchor_y="bottom",
            )
            self._hits.append(
                _HitRegion(
                    node.hit_left,
                    node.hit_bottom,
                    node.hit_right,
                    node.hit_top,
                    "select_mission",
                    node.mission_index,
                )
            )

        mission = missions[selected_index] if missions else None
        if mission is not None:
            self._draw_mission_details(info_left, info_bottom, info_right, info_top, mission, selected_node)
        else:
            arcade.draw_text(
                "No missions available.",
                (info_left + info_right) // 2,
                (info_bottom + info_top) // 2,
                palette.MUTED_TEXT,
                font_size=11,
                anchor_x="center",
                anchor_y="center",
            )

        select_left = 24
        select_bottom = 34
        select_right = int(w * 0.35)
        select_top = 78
        launch_left = select_right + 12
        launch_right = int(w * 0.70)
        back_left = launch_right + 12
        back_right = w - 24

        self._draw_button(select_left, select_bottom, select_right, select_top, "SELECT MISSION", palette.ACCENT, "confirm_mission")
        self._draw_button(launch_left, select_bottom, launch_right, select_top, "LAUNCH MISSION", palette.TACTICAL_GREEN, "launch_mission")
        self._draw_button(back_left, select_bottom, back_right, select_top, "BACK", palette.MUTED_TEXT, "back")

        arcade.draw_text(
            "Enter/Return launches. Esc closes.",
            w // 2,
            12,
            palette.MUTED_TEXT,
            font_size=9,
            anchor_x="center",
        )

        if self._message:
            arcade.draw_text(
                self._message,
                24,
                h - 68,
                palette.WARNING,
                font_size=10,
            )

    def _draw_button(self, left: int, bottom: int, right: int, top: int, label: str, color, action: str) -> None:
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (10, 24, 18, 240))
        arcade.draw_line(left, top, right, top, color, 2)
        arcade.draw_line(left, bottom, right, bottom, color, 1)
        arcade.draw_text(
            label,
            (left + right) // 2,
            (bottom + top) // 2,
            color,
            font_size=12,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        self._hits.append(_HitRegion(left, bottom, right, top, action, None))

    def _draw_mission_details(
        self,
        left: int,
        bottom: int,
        right: int,
        top: int,
        mission: "MissionTemplate",
        selected_node,
    ) -> None:
        x = left + 14
        y = top - 28
        arcade.draw_text(
            mission.title.upper(),
            x,
            y,
            palette.HEADER,
            font_size=16,
            bold=True,
        )
        if selected_node is not None:
            arcade.draw_text(
                f"SITE: {mission_site_name(selected_node.site_key)}",
                right - 14,
                y,
                palette.ACCENT,
                font_size=10,
                bold=True,
                anchor_x="right",
            )
        y -= 24
        arcade.draw_text(
            f"RISK {mission.risk_level}  |  DURATION {mission.duration_days}D  |  REWARD ¥{mission.fund_reward}",
            x,
            y,
            palette.WARNING,
            font_size=10,
        )
        y -= 26

        for line in build_selected_mission_lines(mission):
            arcade.draw_text(
                line,
                x,
                y,
                palette.TEXT if not line.startswith("Launch status:") else palette.WARNING,
                font_size=9,
                width=(right - left) - 28,
                multiline=True,
            )
            y -= 16
            if y < bottom + 18:
                break

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        xi, yi = int(x), int(y)
        for hit in self._hits:
            if hit.contains(xi, yi):
                self._handle_action(hit.action, hit.data)
                return

    def on_key_press(self, key, modifiers) -> None:
        if key in (arcade.key.ESCAPE,):
            self._back_to_management()
            return
        if key in (arcade.key.ENTER, arcade.key.RETURN):
            self._launch_selected_mission()

    def _handle_action(self, action: str, data: object) -> None:
        if action == "select_mission":
            self.game_state.selected_mission_index = int(data)
            self._pending_launch_confirm = False
            self._pending_launch_mission_id = None
            self._message = ""
            return
        if action == "confirm_mission":
            self._back_to_management()
            return
        if action == "launch_mission":
            self._launch_selected_mission()
            return
        if action == "back":
            self._back_to_management()

    def _launch_selected_mission(self) -> None:
        gs = self.game_state
        gs.selected_agent_names = sanitize_selected_agent_names(gs.characters, gs.selected_agent_names)
        selected_squad = selected_deployable_agents(gs.characters, gs.selected_agent_names)
        selected_mission = _selected_mission(gs)
        if selected_mission is None:
            self._message = "No mission selected."
            return

        blocked = blocked_launch_reason(
            has_deployable_agent=any(is_deployable(c) for c in gs.characters),
            selected_count=len(selected_squad),
            mission_unavailable=selected_mission.id in gs.unavailable_mission_ids,
            mission_title=selected_mission.title,
        )
        if blocked is not None:
            self._message = blocked.to_ui_text()
            self._pending_launch_confirm = False
            self._pending_launch_mission_id = None
            return

        at_risk = agents_at_breaking_risk(selected_squad, selected_mission)
        if at_risk and not (
            self._pending_launch_confirm and self._pending_launch_mission_id == selected_mission.id
        ):
            lead = at_risk[0]
            self._pending_launch_confirm = True
            self._pending_launch_mission_id = selected_mission.id
            self._message = f"WARNING: {lead.name} is at breakdown risk. Launch again to confirm."
            return

        self._pending_launch_confirm = False
        self._pending_launch_mission_id = None
        gs.mark_tutorial_event("launched_mission")

        deploy_total = 0
        for asset in gs.spec_ops_assets:
            if asset.id in gs.selected_asset_ids and asset.deploy_cost > 0:
                deploy_total += asset.deploy_cost
        if deploy_total > 0 and not gs.spend_funds(deploy_total, "asset_deploy", f"Asset deployment costs: ¥{deploy_total}"):
            self._message = f"Insufficient funds for asset deployment costs (¥{deploy_total} needed)."
            return

        mission = _launch_mission(gs)

        from game.ui.screens.mission_briefing_view import MissionBriefingView
        self.window.show_view(MissionBriefingView(gs, mission))

    def _back_to_management(self) -> None:
        from game.ui.screens.management_screen import ManagementView

        view = ManagementView(self.game_state)
        view.setup()
        view.active_tab = "squad"
        self.window.show_view(view)
