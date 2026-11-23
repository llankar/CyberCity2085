"""Full-screen world map mission selector."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import arcade

from game.agent_readiness import agents_at_breaking_risk
from game.character import is_deployable
from game.deployment import (
    build_tactical_briefing,
    sanitize_selected_agent_names,
    selected_deployable_agents,
)
from game.missions.flow import (
    ensure_mission_templates,
    launch_selected_mission as _launch_mission,
    selected_mission as _selected_mission,
)
from game.text_missions.text_mission_library import text_missions_for_day
from game.ui import GameView
from game.ui.theme.colors import colors
from game.ui.mission_board import risk_label
from game.ui.management.action_requirements import blocked_launch_reason
from game.ui.screens.world_map import (
    build_world_map_mission_nodes,
    load_world_map_texture,
    mission_site_name,
    texture_rect,
)
from game.narrative.mission_briefing_conventions import translate_legacy_briefing_text
from game.ui.components.world_map_beacons import (
    HolographicRenderer,
    PALETTE,
    CATEGORY,
    category_for,
    rgba,
)
from game.ui.layouts.world_map_beacons import (
    Beacon,
    Rect,
    arrange_beacons,
    artwork_obstacles,
    briefing_link,
)

if TYPE_CHECKING:
    from game.mission_templates import MissionTemplate
    from game.text_missions.text_mission_template import TextMissionTemplate


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


@dataclass(frozen=True)
class WorldMapLayout:
    header_height: int
    footer_bottom: int
    footer_top: int
    map_left: int
    map_bottom: int
    map_right: int
    map_top: int
    briefing_left: int
    briefing_bottom: int
    briefing_right: int
    briefing_top: int

    @property
    def map_rect(self) -> tuple[int, int, int, int]:
        return self.map_left, self.map_bottom, self.map_right, self.map_top

    @property
    def briefing_rect(self) -> tuple[int, int, int, int]:
        return (
            self.briefing_left,
            self.briefing_bottom,
            self.briefing_right,
            self.briefing_top,
        )


def _shorten(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else f"{text[: max(0, limit - 3)]}..."


def _compact_briefing_lines(mission: "MissionTemplate") -> list[str]:
    hint = getattr(mission, "emotional_impact_hint", None)
    emotional = "neutral"
    if isinstance(hint, dict):
        emotional = translate_legacy_briefing_text(
            hint.get("short_text") or hint.get("text") or emotional
        )
    duration = f"{mission.duration_days} day{'s' if mission.duration_days != 1 else ''}"
    return [
        f"Risk: {mission.risk_level} ({risk_label(mission.risk_level)})",
        f"Duration: {duration}",
        f"Reward: ¥{mission.fund_reward}",
        f"Emotional: {_shorten(str(emotional), 58)}",
    ]


def build_world_map_layout(
    width: int, height: int, selected_pin_x: int | None = None
) -> WorldMapLayout:
    """Build the full-screen map layout with a floating mission briefing card."""
    header_height = 48
    footer_bottom = 34
    footer_top = 78
    map_margin = 14
    map_left = map_margin
    map_right = max(map_left + 1, width - map_margin)
    map_bottom = footer_top + 12
    map_top = max(map_bottom + 1, height - header_height - 10)

    briefing_width = min(
        max(300, int(width * 0.28)), 420, max(260, width - map_margin * 2)
    )
    briefing_height = min(max(340, int(height * 0.56)), 520, map_top - map_bottom - 12)
    briefing_top = map_top - 12
    briefing_bottom = max(map_bottom + 12, briefing_top - briefing_height)

    prefer_left = selected_pin_x is not None and selected_pin_x > width * 0.56
    briefing_left = (
        map_margin
        if prefer_left
        else max(map_margin, width - map_margin - briefing_width)
    )
    briefing_right = briefing_left + briefing_width
    if briefing_right > width - map_margin:
        briefing_right = width - map_margin
        briefing_left = briefing_right - briefing_width
    if briefing_left < map_margin:
        briefing_left = map_margin
        briefing_right = briefing_left + briefing_width

    return WorldMapLayout(
        header_height=header_height,
        footer_bottom=footer_bottom,
        footer_top=footer_top,
        map_left=map_left,
        map_bottom=map_bottom,
        map_right=map_right,
        map_top=map_top,
        briefing_left=briefing_left,
        briefing_bottom=briefing_bottom,
        briefing_right=briefing_right,
        briefing_top=briefing_top,
    )


# Normalized (x, y) anchors for text-mission pins, separated by district type.
# These sit in visually distinct map regions from the combat-mission pins.
_TXT_CITY_PINS: list[tuple[float, float]] = [
    (0.14, 0.72),
    (0.40, 0.76),
    (0.68, 0.64),
    (0.90, 0.58),
]
# Wasteland pins are placed in the mid-band of the map (y ≥ 0.38) to stay clear
# of the info-panel overlay that occupies the bottom ~35% of the map image.
_TXT_WASTE_PINS: list[tuple[float, float]] = [
    (0.12, 0.44),
    (0.46, 0.40),
    (0.72, 0.48),
    (0.30, 0.52),
]


class MissionWorldMapView(GameView):
    """Full-screen mission selector backed by the world map art.

    Combat and narrative missions share holographic beacons and a collision-tested
    cartouche layout. Selection and launch retain their existing mission routes.
    """

    def __init__(self, game_state) -> None:
        super().__init__(game_state)
        self._hits: list[_HitRegion] = []
        self._message = ""
        self._pending_launch_confirm = False
        self._pending_launch_mission_id: str | None = None
        # Text-mission state
        self._text_missions: list["TextMissionTemplate"] = []
        self._selection_type: str = "combat"  # "combat" | "text"
        self._selected_text_index: int = 0
        self._renderer = HolographicRenderer()
        self._elapsed = 0.0
        self._hover_key = None
        self._hover_amounts = {}
        self._placement_key = None
        self._placements = []
        self._briefing_scroll = 0.0
        self._briefing_content_height = 0.0
        self._briefing_body_height = 1.0
        self._briefing_bounds = None

    def on_show_view(self) -> None:
        arcade.set_background_color((5, 10, 18))
        ensure_mission_templates(self.game_state)
        day = self.game_state.calendar.current_day
        self._text_missions = text_missions_for_day(day, count=6)

    def on_update(self, delta_time):
        self._elapsed += delta_time
        for p in self._placements:
            target = 1.0 if p.beacon.key == self._hover_key else 0.0
            current = self._hover_amounts.get(p.beacon.key, 0.0)
            self._hover_amounts[p.beacon.key] = current + (target - current) * min(
                1.0, delta_time * 12
            )

    def on_mouse_motion(self, x, y, dx, dy):
        self._hover_key = None
        for hit in reversed(self._hits):
            if hit.contains(x, y):
                if hit.action == "select_mission":
                    self._hover_key = f"combat:{hit.data}"
                elif hit.action == "select_text_mission":
                    self._hover_key = f"text:{hit.data}"
                break

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._briefing_bounds and self._briefing_bounds.contains(x, y):
            self._briefing_scroll = max(
                0,
                min(
                    max(0, self._briefing_content_height - self._briefing_body_height),
                    self._briefing_scroll - scroll_y * 32,
                ),
            )

    def _beacons(self, image):
        specs = []
        missions = self.game_state.mission_templates
        selected = (
            self.game_state.selected_mission_index % len(missions) if missions else 0
        )
        nodes = build_world_map_mission_nodes(
            missions,
            selected,
            int(image.left),
            int(image.bottom),
            int(image.right),
            int(image.top),
        )
        for node in nodes:
            mission = node.mission
            specs.append(
                Beacon(
                    f"combat:{node.mission_index}",
                    "combat",
                    node.mission_index,
                    category_for(mission),
                    mission.title,
                    mission_site_name(node.site_key),
                    (
                        (node.pin_x - image.left) / image.width,
                        (node.pin_y - image.bottom) / image.height,
                    ),
                    self._selection_type == "combat" and node.mission_index == selected,
                )
            )
        counters = {"city": 0, "wasteland": 0}
        for index, mission in enumerate(self._text_missions):
            district = mission.district_type
            bases = _TXT_CITY_PINS if district == "city" else _TXT_WASTE_PINS
            anchor = bases[counters.get(district, 0) % len(bases)]
            counters[district] = counters.get(district, 0) + 1
            specs.append(
                Beacon(
                    f"text:{index}",
                    "text",
                    index,
                    category_for(mission, True),
                    mission.title,
                    ("MEGACITY" if district == "city" else "BADLANDS"),
                    anchor,
                    self._selection_type == "text"
                    and index == self._selected_text_index,
                )
            )
        return specs

    def on_draw(self) -> None:
        self.clear()
        w, h = self.window.width, self.window.height
        self._hits = []
        layout = build_world_map_layout(w, h)
        ui = max(0.78, min(1.35, min(w / 1672, h / 941)))
        painter = self._renderer
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (2, 7, 13, 255))
        arcade.draw_line(
            0,
            h - layout.header_height,
            w,
            h - layout.header_height,
            (35, 174, 205, 150),
            1,
        )
        painter.text(
            "MISSION WORLD MAP",
            20,
            h - 24,
            20 * ui,
            (255, 183, 65),
            bold=True,
            anchor_y="center",
        )
        painter.text(
            "INSPECT  /  PREPARE  /  DEPLOY",
            w - 20,
            h - 24,
            11 * ui,
            (80, 189, 218),
            anchor_x="right",
            anchor_y="center",
        )
        texture = load_world_map_texture()
        # A dedicated transparent HUD gutter preserves the *entire* original
        # artwork, including every baked legend, city name and compass.
        available = Rect(
            layout.map_left + 8,
            layout.map_bottom + 8,
            layout.briefing_left - 16,
            layout.map_top - 8,
        )
        if texture is not None and getattr(texture, "width", 0):
            ratio = min(
                available.width / texture.width, available.height / texture.height
            )
            iw, ih = texture.width * ratio, texture.height * ratio
            cx, cy = available.center
            image = Rect(cx - iw / 2, cy - ih / 2, cx + iw / 2, cy + ih / 2)
            arcade.draw_texture_rect(
                texture,
                texture_rect(image.left, image.bottom, image.right, image.top),
                pixelated=False,
            )
        else:
            image = available
            arcade.draw_lrbt_rectangle_filled(
                image.left, image.right, image.bottom, image.top, (8, 22, 33, 255)
            )
        arcade.draw_lrbt_rectangle_outline(
            layout.map_left,
            layout.map_right,
            layout.map_bottom,
            layout.map_top,
            (36, 182, 223, 130),
            1,
        )
        self._image_bounds = image
        specs = self._beacons(image)
        signature = (w, h, tuple(specs))
        if signature != self._placement_key:
            if self._placement_key and self._placement_key[:2] != (w, h):
                painter.resize()
            self._placements = arrange_beacons(specs, image, scale=ui)
            self._placement_key = signature
        selected = next((p for p in self._placements if p.beacon.selected), None)
        briefing = Rect(*layout.briefing_rect)
        if selected is not None:
            color = PALETTE[selected.beacon.category]
            if signature != getattr(self, "_link_signature", None):
                pad = 1.5 * ui
                start = (selected.label.right + pad, selected.label.center[1])
                end = (briefing.left - pad, briefing.top - 78 * ui)
                reserved = artwork_obstacles(image) + [
                    r for p in self._placements for r in [p.marker, p.label]
                ]
                self._selected_link = briefing_link(
                    start,
                    end,
                    reserved,
                    Rect(
                        layout.map_left + 2,
                        layout.map_bottom + 2,
                        briefing.left,
                        layout.map_top - 2,
                    ),
                    pad,
                )
                self._link_signature = signature
            points = self._selected_link
            for a, b in zip(points, points[1:]):
                arcade.draw_line(*a, *b, rgba(color, 14), 6 * ui)
                arcade.draw_line(*a, *b, rgba(color, 130), 1.2 * ui)
            if len(points) > 1:
                lengths = [
                    abs(b[0] - a[0]) + abs(b[1] - a[1])
                    for a, b in zip(points, points[1:])
                ]
                distance = ((self._elapsed * 0.35) % 1) * sum(lengths)
                for a, b, length in zip(points, points[1:], lengths):
                    if distance <= length:
                        fraction = distance / max(0.001, length)
                        painter.glow(
                            a[0] + (b[0] - a[0]) * fraction,
                            a[1] + (b[1] - a[1]) * fraction,
                            6 * ui,
                            6 * ui,
                            color,
                            165,
                        )
                        break
                    distance -= length
        for placement in sorted(self._placements, key=lambda p: p.beacon.selected):
            painter.beacon(
                placement,
                self._elapsed,
                self._hover_amounts.get(placement.beacon.key, 0),
            )
            action = (
                "select_mission"
                if placement.beacon.kind == "combat"
                else "select_text_mission"
            )
            for bounds in [placement.marker, placement.label]:
                self._hits.append(
                    _HitRegion(
                        bounds.left,
                        bounds.bottom,
                        bounds.right,
                        bounds.top,
                        action,
                        placement.beacon.index,
                    )
                )
        if selected is not None:
            if selected.beacon.kind == "text":
                self._draw_text_mission_details(
                    *layout.briefing_rect, self._text_missions[selected.beacon.index]
                )
            else:
                self._draw_mission_details(
                    *layout.briefing_rect,
                    self.game_state.mission_templates[selected.beacon.index],
                    selected,
                )
        else:
            painter.panel(briefing, PALETTE["operation"])
            painter.text(
                "NO MISSIONS AVAILABLE",
                briefing.left + 18,
                briefing.top - 36,
                15 * ui,
                (215, 231, 240),
                bold=True,
            )
        self._hits.append(_HitRegion(*layout.briefing_rect, "briefing"))
        # Compact color key uses the HUD gutter, never the map's painted legend.
        key_y = briefing.bottom - 28 * ui
        for index, category in enumerate(["story", "operation", "narrative", "urgent"]):
            y = key_y - index * 22 * ui
            if y < layout.map_bottom + 15:
                break
            arcade.draw_line(
                briefing.left + 8, y, briefing.left + 23, y, PALETTE[category], 3
            )
            painter.text(
                CATEGORY[category],
                briefing.left + 31,
                y,
                10 * ui,
                PALETTE[category],
                bold=True,
                anchor_y="center",
            )
        select_right = int(w * 0.35)
        launch_right = int(w * 0.70)
        self._draw_button(
            24,
            layout.footer_bottom,
            select_right,
            layout.footer_top,
            "PREPARE SQUAD",
            (255, 183, 65),
            "confirm_mission",
        )
        launch_label, launch_color = self._launch_button_presentation()
        self._draw_button(
            select_right + 12,
            layout.footer_bottom,
            launch_right,
            layout.footer_top,
            launch_label,
            launch_color,
            "launch_mission",
        )
        self._draw_button(
            launch_right + 12,
            layout.footer_bottom,
            w - 24,
            layout.footer_top,
            "BACK",
            (52, 199, 230),
            "back",
        )
        painter.text(
            "ENTER: LAUNCH   //   ESC: BACK",
            w / 2,
            14,
            10 * ui,
            (65, 177, 204),
            anchor_x="center",
            anchor_y="center",
        )
        if self._message:
            arcade.draw_lrbt_rectangle_filled(
                18, w - 18, h - 82, h - 52, (24, 6, 12, 245)
            )
            painter.text(self._message, 28, h - 72, 11 * ui, (255, 183, 65))

    def _draw_button(
        self,
        left: int,
        bottom: int,
        right: int,
        top: int,
        label: str,
        color,
        action: str,
    ) -> None:
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (10, 24, 18, 240))
        arcade.draw_line(left, top, right, top, color, 2)
        arcade.draw_line(left, bottom, right, bottom, color, 1)
        self._renderer.text(
            label,
            (left + right) / 2,
            (bottom + top) / 2,
            color=color,
            size=max(11, min(14, self.window.width / 120)),
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        self._hits.append(_HitRegion(left, bottom, right, top, action, None))

    def _briefing(self, left, bottom, right, top, mission, site, narrative=False):
        painter = self._renderer
        category = category_for(mission, narrative)
        color = PALETTE[category]
        ui = max(0.85, min(1.3, self.window.height / 941))
        bounds = Rect(left, bottom, right, top)
        self._briefing_bounds = bounds
        painter.panel(bounds, color, selected=True)
        painter.text("MISSION BRIEFING", left + 15, top - 23, 12 * ui, color, bold=True)
        painter.text(
            "LIVE // " + CATEGORY[category],
            left + 15,
            top - 43,
            9 * ui,
            rgba(color, 180),
        )
        arcade.draw_line(left + 15, top - 52, right - 15, top - 52, rgba(color, 100), 1)
        body_top = top - 65
        body_bottom = bottom + 32
        self._briefing_body_height = max(1, body_top - body_bottom)
        y = body_top + self._briefing_scroll
        old_scissor = self.window.ctx.scissor
        self.window.ctx.scissor = (
            int(left + 12),
            int(body_bottom),
            int(right - left - 24),
            int(self._briefing_body_height + 3),
        )

        def paragraph(text, size=12, tint=(210, 225, 235), gap=13, bold=False):
            nonlocal y
            label = painter.text(
                text,
                left + 17,
                y,
                size * ui,
                tint,
                bold=bold,
                width=int(right - left - 36),
                anchor_y="top",
                multiline=True,
            )
            y -= label.content_height + gap * ui

        try:
            paragraph(mission.title.upper(), 21, (244, 246, 250), 12, True)
            paragraph("SITE // " + site, 11, color, 16, True)
            paragraph(
                f"RISK {mission.risk_level}   /   {mission.duration_days} DAYS   /   ¥{mission.fund_reward:,}",
                12,
                color,
                18,
                True,
            )
            if narrative:
                paragraph(mission.description, 13)
                if mission.required_skills:
                    paragraph(
                        "SKILLS // " + ", ".join(mission.required_skills),
                        12,
                        PALETTE["narrative"],
                    )
                selected = selected_deployable_agents(
                    self.game_state.characters, self.game_state.selected_agent_names
                )
                paragraph(
                    f"TEAM // {len(selected)} AGENT(S) ASSIGNED",
                    12,
                    (205, 229, 238),
                )
            else:
                paragraph(mission.objective_text, 13)
                selected = selected_deployable_agents(
                    self.game_state.characters, self.game_state.selected_agent_names
                )
                tactical = build_tactical_briefing(mission, selected)
                paragraph("HOSTILES // " + tactical.enemy_label, 13, color, 10, True)
                paragraph("DOCTRINE // " + tactical.doctrine, 12)
                paragraph(
                    f"SQUAD // {tactical.squad_count} assigned · {tactical.armed_count} armed",
                    12,
                    (112, 237, 214),
                    10,
                    True,
                )
                paragraph("LOADOUT // " + tactical.loadout_summary, 12)
                paragraph(
                    "ROLES // "
                    + tactical.capability_summary
                    + " · "
                    + tactical.tactical_gap,
                    12,
                )
                paragraph(
                    "RECOVERY // " + tactical.recovery_load, 12, color, 12, True
                )
            self._briefing_content_height = body_top + self._briefing_scroll - y
        finally:
            self.window.ctx.scissor = old_scissor
        maximum = max(0, self._briefing_content_height - self._briefing_body_height)
        self._briefing_scroll = min(self._briefing_scroll, maximum)
        if maximum:
            rail_top, rail_bottom = body_top, body_bottom
            thumb = max(
                24,
                (rail_top - rail_bottom)
                * self._briefing_body_height
                / self._briefing_content_height,
            )
            thumb_y = (
                rail_top
                - thumb
                - (rail_top - rail_bottom - thumb) * self._briefing_scroll / maximum
            )
            arcade.draw_line(
                right - 7, rail_bottom, right - 7, rail_top, rgba(color, 40), 2
            )
            arcade.draw_line(
                right - 7, thumb_y, right - 7, thumb_y + thumb, rgba(color, 200), 2
            )
        painter.text(
            "WHEEL: DETAILS" if maximum else "LIVE INTELLIGENCE",
            left + 15,
            bottom + 12,
            9 * ui,
            rgba(color, 160),
        )

    def _draw_mission_details(self, left, bottom, right, top, mission, selected_node):
        self._briefing(left, bottom, right, top, mission, selected_node.beacon.site)

    def _launch_button_presentation(self) -> tuple[str, tuple[int, int, int]]:
        """Make missing squad preparation visible before the player clicks launch."""
        if self._selection_type == "text":
            selected = selected_deployable_agents(
                self.game_state.characters, self.game_state.selected_agent_names
            )
            return (
                ("LAUNCH NARRATIVE MISSION", colors.accent_success)
                if selected
                else ("ASSIGN AN AGENT FIRST", colors.accent_warning_text)
            )
        mission = _selected_mission(self.game_state)
        selected = selected_deployable_agents(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        if mission is None:
            return "SELECT A MISSION", colors.accent_warning_text
        if not selected:
            return "ASSIGN AN AGENT FIRST", colors.accent_warning_text
        tactical = build_tactical_briefing(mission, selected)
        if not tactical.ready:
            return "LAUNCH MISSION", colors.accent_warning_text
        return "LAUNCH MISSION", colors.accent_success

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        xi, yi = int(x), int(y)
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        for hit in reversed(self._hits):
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
        if action in {"select_mission", "select_text_mission"}:
            self._briefing_scroll = 0.0
        if action == "select_mission":
            self.game_state.selected_mission_index = int(data)
            self._selection_type = "combat"
            self._pending_launch_confirm = False
            self._pending_launch_mission_id = None
            self._message = ""
            return
        if action == "select_text_mission":
            self._selected_text_index = int(data)
            self._selection_type = "text"
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
            return
        if action == "upgrade_hangar":
            _, self._message = self.game_state.upgrade_hangar()

    def _launch_selected_mission(self) -> None:
        if self._selection_type == "text":
            self._launch_text_mission()
            return
        gs = self.game_state
        gs.selected_agent_names = sanitize_selected_agent_names(
            gs.characters, gs.selected_agent_names
        )
        selected_squad = selected_deployable_agents(
            gs.characters, gs.selected_agent_names
        )
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
            self._pending_launch_confirm
            and self._pending_launch_mission_id == selected_mission.id
        ):
            lead = at_risk[0]
            self._pending_launch_confirm = True
            self._pending_launch_mission_id = selected_mission.id
            self._message = (
                f"WARNING: {lead.name} is at breakdown risk. Launch again to confirm."
            )
            return

        self._pending_launch_confirm = False
        self._pending_launch_mission_id = None
        gs.mark_tutorial_event("launched_mission")

        deploy_total = 0
        for asset in gs.spec_ops_assets:
            if asset.id in gs.selected_asset_ids and asset.deploy_cost > 0:
                deploy_total += asset.deploy_cost
        if deploy_total > 0 and not gs.spend_funds(
            deploy_total, "asset_deploy", f"Asset deployment costs: ¥{deploy_total}"
        ):
            self._message = f"Insufficient funds for asset deployment costs (¥{deploy_total} needed)."
            return

        mission = _launch_mission(gs)

        from game.ui.screens.mission_briefing_view import MissionBriefingView

        self.window.show_view(MissionBriefingView(gs, mission))

    def _launch_text_mission(self) -> None:
        if not self._text_missions:
            self._message = "No narrative mission selected."
            return
        gs = self.game_state
        gs.selected_agent_names = sanitize_selected_agent_names(
            gs.characters, gs.selected_agent_names
        )
        squad = selected_deployable_agents(gs.characters, gs.selected_agent_names)
        if not squad:
            self._message = (
                "Assign at least one operative before launching a narrative mission."
            )
            return
        tm = self._text_missions[self._selected_text_index]
        from game.ui.screens.text_mission_view import TextMissionView

        self.window.show_view(TextMissionView(gs, tm))

    def _draw_text_mission_details(self, left, bottom, right, top, tm):
        self._briefing(left, bottom, right, top, tm, tm.district_type.upper(), True)

    def _back_to_management(self) -> None:
        from game.ui.screens.management_screen import ManagementView

        view = ManagementView(self.game_state)
        view.setup()
        self.window.show_view(view)


__all__ = ["MissionWorldMapView", "WorldMapLayout", "build_world_map_layout"]
