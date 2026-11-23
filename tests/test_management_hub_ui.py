"""Click-through management hub tests."""

import sys
import types
import unittest
import pytest


class _FakeView:
    def __init__(self, *args, **kwargs):
        self.window = None

    def clear(self):
        pass


fake_arcade = types.SimpleNamespace(
    View=_FakeView,
    key=types.SimpleNamespace(
        B=66,
        N=78,
        C=67,
        A=65,
        D=68,
        X=88,
        R=82,
        T=84,
        S=83,
        L=76,
        V=86,
        H=72,
        M=77,
        TAB=9,
        F1=1001,
        F2=1002,
        F3=1003,
        F4=1004,
        F5=1005,
        F6=1006,
        LEFT=1007,
        RIGHT=1008,
        SPACE=32,
        ENTER=13,
        RETURN=13,
        ESCAPE=27,
        KEY_1=49,
        KEY_2=50,
        KEY_3=51,
        KEY_4=52,
        KEY_5=53,
        KEY_6=54,
        KEY_7=55,
        KEY_8=56,
        KEY_9=57,
        MOD_CTRL=2,
    ),
    draw_text=lambda *args, **kwargs: None,
    draw_lrbt_rectangle_filled=lambda *args, **kwargs: None,
    draw_line=lambda *args, **kwargs: None,
    draw_texture_rect=lambda *args, **kwargs: None,
    draw_circle_outline=lambda *args, **kwargs: None,
    draw_circle_filled=lambda *args, **kwargs: None,
    draw_rect_outline=lambda *args, **kwargs: None,
    draw_lrbt_rectangle_outline=lambda *args, **kwargs: None,
    Camera2D=lambda *args, **kwargs: None,
    SpriteList=lambda *args, **kwargs: types.SimpleNamespace(
        draw=lambda: None,
        append=lambda sprite: None,
        __iter__=lambda self: iter([]),
        __len__=lambda self: 0,
    ),
    Sprite=lambda *args, **kwargs: types.SimpleNamespace(
        kill=lambda: None,
        center_x=kwargs.get("center_x", 0),
        center_y=kwargs.get("center_y", 0),
        width=32,
        height=32,
        visible=True,
    ),
    set_background_color=lambda *args, **kwargs: None,
    LBWH=lambda *args, **kwargs: None,
    load_texture=lambda *args, **kwargs: None,
    color=types.SimpleNamespace(),
)
_previous_arcade = sys.modules.get("arcade")
sys.modules["arcade"] = fake_arcade

from game.gamestate import GameState
from game.management.spec_ops_assets import default_spec_ops_assets
from game.recruitment import create_character
import game.ui.screens.management_screen as management_screen
import game.ui.panels as panels
import game.ui.components.agent.cards as agent_cards
from game.ui.screens.facility import build_facility_rooms
from game.ui.screens.management_screen import ManagementView
from game.ui.room_interaction import open_room
from game.ui.widgets.notification_center import NotificationCenter

if _previous_arcade is None:
    sys.modules.pop("arcade", None)
else:
    sys.modules["arcade"] = _previous_arcade


@pytest.fixture(autouse=True)
def management_arcade_stub(monkeypatch):
    monkeypatch.setitem(sys.modules, "arcade", fake_arcade)
    for name, module in tuple(sys.modules.items()):
        if name.startswith("game.ui.") and hasattr(module, "arcade"):
            monkeypatch.setattr(module, "arcade", fake_arcade)


class _FakeWindow:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.shown_view = None
        self.activated = False

    def show_view(self, view):
        self.shown_view = view

    def activate(self):
        self.activated = True


class _StubPainter:
    """Exercise production geometry/actions without needing an OpenGL context."""

    def __init__(self):
        self._texts = {}

    def resize(self):
        pass

    def panel(self, *args, **kwargs):
        pass

    def glow(self, *args, **kwargs):
        pass

    def fit(self, text, width, size, bold=True):
        count = max(1, int(width / (size * 0.58)))
        return str(text) if len(str(text)) <= count else str(text)[: count - 1] + "…"

    def text(self, text, x, y, size=12, color=(255, 255, 255), **kwargs):
        import math

        width = kwargs.get("width")
        rows = max(1, math.ceil(len(str(text)) * size * 0.58 / width)) if width else 1
        fake_arcade.draw_text(
            text,
            x,
            y,
            color,
            font_size=size,
            **{k: v for k, v in kwargs.items() if k not in ("accessibility",)},
        )
        return types.SimpleNamespace(
            text=str(text),
            content_width=min(width or 99999, len(str(text)) * size * 0.58),
            content_height=rows * size * 1.3,
        )


class ManagementHubUITest(unittest.TestCase):
    def setUp(self):
        from unittest.mock import patch

        self.paint_patch = patch(
            "game.ui.components.visual_kit.HolographicRenderer", _StubPainter
        )
        self.paint_patch.start()
        self.addCleanup(self.paint_patch.stop)

    def _seed_interactive_state(self, view: ManagementView) -> None:
        view.game_state.ui_language = "en"
        view.game_state.characters = [
            create_character("Rook", "samurai"),
            create_character("Longshot", "sniper"),
            create_character("Oracle", "psi"),
            create_character("Katana", "samurai"),
        ]
        view.game_state.characters[0].pending_points = 5
        view.game_state.selected_agent_names = [view.game_state.characters[0].name]
        view.game_state.spec_ops_assets = default_spec_ops_assets()

    def test_single_click_selects_agent_and_double_click_toggles_squad(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        selected_before = list(view.game_state.selected_agent_names)
        view._dispatch("agent_card", 0)

        self.assertEqual(view.deployment_cursor, 0)
        self.assertEqual(view.game_state.selected_agent_names, selected_before)

        view._dispatch("agent_card", 0)

        self.assertNotIn("Rook", view.game_state.selected_agent_names)
        self.assertIsNone(view.expanded_agent_sheet_index)

    def test_opening_and_closing_agent_sheet_toggles_topmost_focus(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        calls = []
        original = management_screen._set_window_topmost

        def _capture(window, enabled):
            calls.append(enabled)

        management_screen._set_window_topmost = _capture
        try:
            view._open_agent_sheet(0)
            view.on_key_press(management_screen.arcade.key.ESCAPE, 0)
        finally:
            management_screen._set_window_topmost = original

        self.assertGreaterEqual(calls.count(True), 1)
        self.assertEqual(calls[-1], False)
        self.assertIsNone(view.expanded_agent_sheet_index)

    def test_expanded_agent_sheet_draws_allocation_hits(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view.expanded_agent_sheet_index = 0

        view.on_draw()

        stat_hit = next(
            hit for hit in view._modal_hits if hit.action == "sheet_spend_stat"
        )
        before_points = view.game_state.characters[0].pending_points
        before_str = view.game_state.characters[0].stats.str

        view.on_mouse_press(
            (stat_hit.left + stat_hit.right) // 2,
            (stat_hit.bottom + stat_hit.top) // 2,
            0,
            0,
        )
        self.assertEqual(
            view.game_state.characters[0].pending_points, before_points - 1
        )
        self.assertGreater(view.game_state.characters[0].stats.str, before_str)

        view.game_state.characters[0].pending_points = 1
        view.on_draw()
        skill_hit = next(
            (hit for hit in view._modal_hits if hit.action == "sheet_spend_skill_rank"),
            None,
        )
        if skill_hit is not None:
            before_skills = dict(view.game_state.characters[0].skills)
            view.on_mouse_press(
                (skill_hit.left + skill_hit.right) // 2,
                (skill_hit.bottom + skill_hit.top) // 2,
                0,
                0,
            )
            self.assertEqual(view.game_state.characters[0].pending_points, 0)
            skill_key = skill_hit.data[1]
            self.assertGreater(
                view.game_state.characters[0].skills.get(skill_key, 0),
                before_skills.get(skill_key, 0),
            )

    def test_cyberware_sheet_installs_implant_and_spends_humanity(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view.game_state.add_funds(10_000, "test", "Cyberware fixture")
        view._open_agent_sheet(0)
        view.cyberware_sheet_open = True

        view.on_draw()
        zones = [hit for hit in view._modal_hits if hit.action == "cyberware_zone"]
        self.assertEqual(len(zones), 6)
        eyes = next(hit for hit in zones if hit.data == "EYES")
        view._dispatch(eyes.action, eyes.data)
        view.on_draw()
        self.assertEqual(
            len([hit for hit in view._modal_hits if hit.action == "cyberware_toggle"]),
            10,
        )
        implant = next(hit for hit in view._modal_hits if hit.action == "cyberware_toggle")
        from game.agents.cyberware import BY_ID
        funds_before = view.game_state.available_funds
        view._dispatch(implant.action, implant.data)
        agent = view.game_state.characters[0]
        self.assertIn(implant.data, agent.installed_cyberware)
        self.assertLess(agent.humanity, 5)
        self.assertEqual(
            view.game_state.available_funds,
            funds_before - BY_ID[implant.data].credit_cost,
        )

    def test_escape_closes_expanded_agent_sheet(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view.expanded_agent_sheet_index = 0

        view.on_key_press(management_screen.arcade.key.ESCAPE, 0)

        self.assertIsNone(view.expanded_agent_sheet_index)

    def test_management_view_uses_the_hub_room_model(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()

        rooms = build_facility_rooms(view.window.width, view.window.height, "hub")
        command = rooms[0]

        self.assertEqual(view.room_ui.mode, "hub")
        self.assertEqual(
            [room.key for room in rooms],
            ["command", "city", "squad", "assets", "research", "intel"],
        )

        view.on_mouse_press(command.left + 1, command.bottom + 1, 0, 0)

        self.assertTrue(view.room_ui.is_open)
        self.assertEqual(view.room_ui.active_room_key, "command")
        self.assertTrue(
            any(
                button.action.key == "advance_day"
                for button in view.room_ui.action_buttons
            )
        )

    def test_clicking_hangar_on_base_opens_world_map_directly(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        from game.ui.layouts.headquarters import headquarters_layout
        hangar = headquarters_layout(view.window.width, view.window.height).hangar

        view.on_mouse_press(hangar.left + 1, hangar.bottom + 1, 0, 0)

        self.assertEqual(view.window.shown_view.__class__.__name__, "MissionWorldMapView")
        self.assertFalse(view.room_ui.is_open)

    def test_asset_bay_remains_a_distinct_management_room(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        from game.ui.layouts.headquarters import headquarters_layout
        asset_bay = headquarters_layout(view.window.width, view.window.height).rooms[3]

        view.on_mouse_press(asset_bay.left + 1, asset_bay.bottom + 1, 0, 0)

        self.assertIsNone(view.window.shown_view)
        self.assertTrue(view.room_ui.is_open)
        self.assertEqual(view.room_ui.active_room_key, "assets")

    def test_keyboard_shortcut_opens_the_correct_room(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()

        original_key_ns = management_screen.arcade.key
        management_screen.arcade.key = types.SimpleNamespace(
            F1=1001,
            F2=1002,
            F3=1003,
            F4=1004,
            F5=1005,
            F6=1006,
        )
        try:
            view.on_key_press(1003, 0)
        finally:
            management_screen.arcade.key = original_key_ns

        self.assertEqual(view.room_ui.active_room_key, "squad")
        self.assertFalse(any(button.action.key == "open_mission_map" for button in view.room_ui.action_buttons))
        view._open_hub_room("assets")
        self.assertTrue(any(button.action.key == "open_mission_map" for button in view.room_ui.action_buttons))

    def test_room_info_lines_use_the_current_room_content_sources(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()

        lines = view._room_info_lines()

        self.assertTrue(
            any("Funds" in line or "Turn" in line for line in lines["command"])
        )
        self.assertTrue(
            any(
                "District" in line or "Control faction" in line
                for line in lines["city"]
            )
        )
        self.assertTrue(any("Squad morale" in line for line in lines["squad"]))
        self.assertTrue(
            any("Spec Ops Assets Guide" in line for line in lines["assets"])
        )
        self.assertTrue(any("Research tree" in line for line in lines["research"]))
        self.assertTrue(any("Event log entries" in line for line in lines["intel"]))

    def test_legacy_room_renderer_is_used_for_open_rooms(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        open_room(view.room_ui, view.window.width, view.window.height, "command")
        view.room_ui.expansion = 1.0
        called = []

        def _record(*args, **kwargs):
            called.append((args, kwargs))

        view._draw_command_tab = _record
        view._draw_legacy_room_content()

        self.assertTrue(called)

    def test_draw_path_no_longer_paints_summary_text_over_rooms(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()

        from unittest.mock import patch

        with patch.object(
            management_screen, "draw_graphical_command_surface"
        ) as legacy:
            view.on_draw()
            legacy.assert_not_called()
        self.assertIsNotNone(view._headquarters)
        self.assertEqual(
            len([hit for hit in view._hits if hit.action == "hq_room"]), 12
        )
        self.assertFalse(any(hit.action == "agent_card" for hit in view._hits))

    def test_squad_room_uses_dedicated_renderer_instead_of_graphical_shell(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        view.room_ui.expansion = 1.0

        captured = {}

        def _capture(
            width,
            height,
            state,
            resources,
            room_info_lines=None,
            roster_cards=None,
            available_funds=None,
            draw_controls=None,
        ):
            captured["roster_cards"] = roster_cards

        original = management_screen.draw_graphical_command_surface
        management_screen.draw_graphical_command_surface = _capture
        try:
            view.on_draw()
        finally:
            management_screen.draw_graphical_command_surface = original

        self.assertNotIn("roster_cards", captured)
        self.assertIsNotNone(view._squad_command)
        self.assertTrue(any(hit.action == "agent_card" for hit in view._hits))

    def test_squad_does_not_dispatch_invisible_legacy_buttons(self):
        from unittest.mock import patch

        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        button = view.room_ui.action_buttons[0]
        view._hits = []
        with patch.object(view, "_dispatch_hub_action") as dispatch:
            view.on_mouse_press(button.rect.center_x, button.rect.center_y, 0, 0)
            dispatch.assert_not_called()

    def test_resource_strip_shows_all_resource_labels(self):
        calls = []
        original = panels.arcade.draw_text

        def _capture(text, *args, **kwargs):
            calls.append((text, args, kwargs))

        panels.arcade.draw_text = _capture
        try:
            panels.draw_icon_resource_hud(
                1280,
                720,
                {"credits": 12, "intel": 3, "salvage": 5, "influence": 7},
                available_funds=2500,
            )
        finally:
            panels.arcade.draw_text = original

        drawn_text = {call[0] for call in calls}
        self.assertIn("INFLUENCE", drawn_text)
        self.assertTrue(any(text.startswith("¥ 2,500") for text in drawn_text))
        funds_call = next(call for call in calls if call[0] == "FUNDS")
        influence_label_call = next(call for call in calls if call[0] == "INFLUENCE")
        influence_value_call = next(call for call in calls if call[0] == "7")
        self.assertGreaterEqual(funds_call[2].get("font_size", 0), 8)
        self.assertGreaterEqual(influence_label_call[2].get("font_size", 0), 8)
        self.assertGreaterEqual(influence_value_call[2].get("font_size", 0), 12)

    def test_agent_card_shows_defense_stat(self):
        calls = []
        original = agent_cards.arcade.draw_text

        def _capture(text, *args, **kwargs):
            calls.append((text, args, kwargs))

        agent_cards.arcade.draw_text = _capture
        try:
            agent_cards.draw_agent_card(
                {
                    "name": "Agent 1",
                    "role": "samurai",
                    "defense": 6,
                    "active": True,
                    "selected": True,
                    "portrait_path": None,
                    "pending_points": 0,
                },
                10,
                20,
                260,
                140,
                management_screen.palette.HEADER,
                lambda *args, **kwargs: None,
                lambda *args, **kwargs: None,
                lambda *args, **kwargs: None,
            )
        finally:
            agent_cards.arcade.draw_text = original

        self.assertTrue(any(text == "DEF 6" for text, *_ in calls))

    def test_intel_room_wraps_long_text_with_explicit_width(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        view.game_state.event_log = [
            "Intel relay: a very long event log entry that should wrap instead of running off the right side of the panel.",
        ]

        calls = []
        original = management_screen.arcade.draw_text

        def _capture(text, *args, **kwargs):
            calls.append((text, args, kwargs))

        management_screen.arcade.draw_text = _capture
        try:
            view._draw_intel_tab(100, 50, 520, 430)
        finally:
            management_screen.arcade.draw_text = original

        wrapped = next(call for call in calls if "right side of the panel" in call[0])
        kwargs = wrapped[2]
        self.assertEqual(kwargs.get("align"), "left")
        self.assertGreaterEqual(kwargs.get("font_size", 0), 11)
        content_w = 520 - 100 - 10
        expected_left_width = min(
            max(240, int(content_w * 0.60)), max(120, content_w - 150)
        )
        self.assertEqual(kwargs.get("width"), max(10, expected_left_width - 24))

    def test_notification_toast_moves_toward_the_center(self):
        notifications = NotificationCenter()
        notifications.success("Campaign saved to slot 1")

        calls = []
        original = management_screen.arcade.draw_text

        def _capture(text, *args, **kwargs):
            calls.append((text, args, kwargs))

        management_screen.arcade.draw_text = _capture
        try:
            management_screen._draw_notification_toast(notifications, 1920, 1080)
        finally:
            management_screen.arcade.draw_text = original

        toast = next(call for call in calls if call[0].startswith("[SUCCESS]"))
        x = toast[1][0]
        panel_w = min(760, max(460, int(1920 * 0.40)))
        expected_x = ((1920 + panel_w) // 2) - panel_w + 8
        self.assertEqual(x, expected_x)
        self.assertLess(x, 1000)

    def test_hub_overlay_does_not_draw_the_generic_room_title_layer(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        open_room(view.room_ui, view.window.width, view.window.height, "command")
        view.room_ui.expansion = 1.0

        import game.ui.panels as panels

        called = []
        original = panels.draw_room_title_and_info

        def _record(*args, **kwargs):
            called.append((args, kwargs))

        panels.draw_room_title_and_info = _record
        try:
            view.on_draw()
        finally:
            panels.draw_room_title_and_info = original

        self.assertFalse(called)

    def test_hub_rooms_keep_their_original_click_regions_and_dispatch(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        view.game_state.strategic_resources.update(
            credits=50, salvage=50, intel=50, influence=50
        )

        cases = {
            "command": ("weekly_directive_",),
            "city": ("city_upgrade_",),
            "squad": (
                "agent_card",
                "spend_stat_point",
                "equip_prev",
                "equip_next",
                "squad_sheet",
            ),
            "assets": (
                "asset_select",
                "asset_repair",
                "asset_deploy_toggle",
                "catalog_acquire",
                "catalog_scroll",
            ),
            "research": ("start_research_",),
        }

        for room_key, expected_prefixes in cases.items():
            with self.subTest(room=room_key):
                open_room(view.room_ui, view.window.width, view.window.height, room_key)
                view.room_ui.expansion = 1.0
                view.on_draw()
                actions = [hit.action for hit in view._hits]
                self.assertTrue(
                    any(
                        action == prefix or action.startswith(prefix)
                        for prefix in expected_prefixes
                        for action in actions
                    ),
                    msg=f"missing expected hit regions for {room_key}: {actions}",
                )
                if room_key == "squad":
                    first_agent = next(
                        hit for hit in view._hits if hit.action == "agent_card"
                    )
                    first_stat = next(
                        hit for hit in view._hits if hit.action == "spend_stat_point"
                    )
                    first_equip = next(
                        hit for hit in view._hits if hit.action == "equip_next"
                    )

                    agent_name = view.game_state.characters[0].name
                    before_points = view.game_state.characters[0].pending_points
                    before_str = view.game_state.characters[0].stats.str
                    before_item = view.game_state.characters[0].loadout.item_for_slot(
                        "primary_weapon"
                    )

                    view.on_mouse_press(
                        (first_agent.left + first_agent.right) // 2,
                        (first_agent.bottom + first_agent.top) // 2,
                        0,
                        0,
                    )
                    self.assertIn(agent_name, view.game_state.selected_agent_names)

                    view.on_mouse_press(
                        (first_agent.left + first_agent.right) // 2,
                        (first_agent.bottom + first_agent.top) // 2,
                        0,
                        0,
                    )
                    self.assertNotIn(agent_name, view.game_state.selected_agent_names)

                    view.on_mouse_press(
                        (first_stat.left + first_stat.right) // 2,
                        (first_stat.bottom + first_stat.top) // 2,
                        0,
                        0,
                    )
                    self.assertEqual(
                        view.game_state.characters[0].pending_points, before_points - 1
                    )
                    self.assertGreater(
                        view.game_state.characters[0].stats.str, before_str
                    )

                    view.on_mouse_press(
                        (first_equip.left + first_equip.right) // 2,
                        (first_equip.bottom + first_equip.top) // 2,
                        0,
                        0,
                    )
                    after_item = view.game_state.characters[0].loadout.item_for_slot(
                        "primary_weapon"
                    )
                    self.assertIsNotNone(after_item)
                    self.assertNotEqual(after_item, before_item)


    def test_rect_skips_invalid_lrbt_inputs(self):
        calls = []
        original = management_screen.arcade.draw_lrbt_rectangle_filled

        def _capture(*args, **kwargs):
            calls.append((args, kwargs))

        management_screen.arcade.draw_lrbt_rectangle_filled = _capture
        try:
            management_screen._rect(100, 120, 80, 200, (255, 255, 255, 255))
            management_screen._rect(100, 220, 180, 200, (255, 255, 255, 255))
            management_screen._rect(100, 120, 180, 200, (255, 255, 255, 255))
        finally:
            management_screen.arcade.draw_lrbt_rectangle_filled = original

        self.assertEqual(len(calls), 1)

    def test_recruit_prompt_opens_a_named_candidate_list(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        starting_funds = 500
        view.game_state.add_funds(starting_funds, "test", "Recruitment test budget")

        view._do_recruit_prompt()
        view.on_draw()
        self.assertTrue(
            any(hit.action == "recruit_candidate" for hit in view._modal_hits)
        )

        self.assertTrue(view.recruit_window_open)
        self.assertGreaterEqual(len(view.pending_recruit_candidates), 6)
        self.assertTrue(
            all(candidate.name for candidate in view.pending_recruit_candidates)
        )
        self.assertTrue(
            all(
                candidate.role in {"samurai", "sniper", "psi", "robot"}
                for candidate in view.pending_recruit_candidates
            )
        )
        self.assertTrue(
            all(candidate.function for candidate in view.pending_recruit_candidates)
        )
        self.assertTrue(
            all(candidate.background for candidate in view.pending_recruit_candidates)
        )
        self.assertTrue(
            all(candidate.advantages for candidate in view.pending_recruit_candidates)
        )
        self.assertTrue(
            all(candidate.price > 0 for candidate in view.pending_recruit_candidates)
        )
        self.assertTrue(
            all(
                candidate.skill_line().startswith("SKILLS")
                for candidate in view.pending_recruit_candidates
            )
        )
        self.assertNotIn(
            "Agent 1", {candidate.name for candidate in view.pending_recruit_candidates}
        )

        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        view.room_ui.expansion = 1.0

        calls = []
        original = management_screen.arcade.draw_text

        def _capture(text, *args, **kwargs):
            calls.append((text, args, kwargs))

        management_screen.arcade.draw_text = _capture
        try:
            view.on_draw()
            pages = view._recruitment_deck.capacities["candidate_detail"][0]
            for page in range(1, pages):
                view._dispatch("department_page", ("candidate_detail", 1))
                view.on_draw()

        finally:
            management_screen.arcade.draw_text = original

        first_candidate = view.pending_recruit_candidates[0]
        drawn_text = {str(call[0]) for call in calls}
        normalized = " ".join(" ".join(str(call[0]) for call in calls).split()).upper()
        self.assertTrue(
            any("RECRUTEMENT" in text or "RECRUITMENT" in text for text in drawn_text)
        )
        self.assertIn(first_candidate.function.upper(), normalized)
        self.assertIn(first_candidate.skill_line().upper(), normalized)
        self.assertTrue(any(f"¥{first_candidate.price}" in text for text in drawn_text))
        self.assertTrue(
            any(
                first_candidate.background[:24].upper() in text.upper()
                for text in drawn_text
            )
        )
        self.assertIn(" / ".join(first_candidate.advantages).upper(), normalized)

        recruited_name = view.pending_recruit_candidates[0].name
        recruited_price = view.pending_recruit_candidates[0].price
        before_funds = view.game_state.available_funds
        view._do_recruit_candidate(0)

        self.assertEqual(len(view.pending_recruit_candidates), 0)
        self.assertFalse(view.recruit_window_open)
        self.assertIn(
            recruited_name, {character.name for character in view.game_state.characters}
        )
        self.assertIn(recruited_name, view.game_state.selected_agent_names)
        recruited = next(
            character
            for character in view.game_state.characters
            if character.name == recruited_name
        )
        self.assertIsNotNone(recruited.loadout.primary_weapon)
        self.assertIn("starter kit", view.message.lower())
        self.assertEqual(
            view.game_state.available_funds, before_funds - recruited_price
        )

    def test_agent_sheet_spreads_readiness_and_skills_better(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view.expanded_agent_sheet_index = 0

        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        view.room_ui.expansion = 1.0

        calls = []
        original = management_screen.arcade.draw_text

        def _capture(text, x, y, *args, **kwargs):
            calls.append((str(text), float(x), float(y)))

        management_screen.arcade.draw_text = _capture
        try:
            view.on_draw()
        finally:
            management_screen.arcade.draw_text = original

        readiness_labels = {"HP", "AIM", "DEF", "INIT", "RES", "REC"}
        right_side_ready_ys = [
            y for text, x, y in calls if text in readiness_labels and x > 300
        ]
        self.assertGreaterEqual(len(right_side_ready_ys), len(readiness_labels))
        self.assertGreater(len({round(y, 1) for y in right_side_ready_ys}), 1)

        # Skills are now shown as individual cards with +1 buttons; no TRAIN SKILLS button.
        skill_labels = [
            text
            for text, x, y in calls
            if text in ("FIREARMS", "CLOSE COMBAT", "TACTICS") and x > 300
        ]
        self.assertGreater(len(skill_labels), 0)

    def test_agent_sheet_keeps_recovery_text_above_stress_meter(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view.expanded_agent_sheet_index = 0

        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        view.room_ui.expansion = 1.0

        calls = []
        original = management_screen.arcade.draw_text
        rect_calls = []
        original_rect = management_screen._rect

        def _capture(text, x, y, *args, **kwargs):
            calls.append((str(text), float(x), float(y)))

        def _capture_rect(l, b, r, t, color):
            rect_calls.append((float(l), float(b), float(r), float(t), color))
            return original_rect(l, b, r, t, color)

        management_screen.arcade.draw_text = _capture
        management_screen._rect = _capture_rect
        try:
            view.on_draw()
        finally:
            management_screen.arcade.draw_text = original
            management_screen._rect = original_rect

        recovery_y = max(y for text, x, y in calls if text == "Recovery")
        stress_label_y = max(y for text, x, y in calls if text == "STRESS" and x < 300)
        self.assertGreater(recovery_y, stress_label_y + 20)

        dossier = view._character_sheet_renderer
        self.assertGreater(dossier.layout.identity.top, dossier.layout.identity.bottom)
        self.assertEqual(dossier.data.derived["stress_cap"], 12)

    def test_squad_room_requires_confirmation_before_removing_agent(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view.deployment_cursor = 0
        removed_name = view.game_state.characters[0].name

        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        remove_button = next(
            button
            for button in view.room_ui.action_buttons
            if button.action.key == "remove_agent"
        ).rect

        view._do_remove_agent()

        self.assertEqual(len(view.game_state.characters), 4)
        self.assertEqual(view.pending_remove_agent_name, removed_name)
        self.assertIn("Confirm removal", view.message)

        view._do_remove_agent()

        self.assertEqual(len(view.game_state.characters), 3)
        self.assertNotIn(
            removed_name, {character.name for character in view.game_state.characters}
        )
        self.assertNotIn(removed_name, view.game_state.selected_agent_names)

    def test_squad_restores_mission_intel_and_keeps_cyberware_in_agent_sheet(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        open_room(view.room_ui, view.window.width, view.window.height, "squad")
        view.room_ui.expansion = 1.0
        view.on_draw()

        renderer = view._squad_command
        self.assertIn("mission_art", renderer.regions)
        self.assertIn("downtime", renderer.regions)
        self.assertFalse(
            any(hit.data == "open_cyberware" for hit in view._hits)
        )
        self.assertFalse(any(hit.action == "open_mission_map" for hit in view._hits))
        footer_hits = [hit for hit in view._hits if hit.action == "squad_nav"]
        self.assertEqual(len(footer_hits), 10)
        self.assertLess(
            max(hit.top for hit in footer_hits), renderer.layout.roster.bottom
        )

    def test_mission_selection_is_exposed_from_asset_hangar(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view._open_hub_room("assets")
        view.on_draw()
        open_map = next(hit for hit in view._hits if hit.action == "open_mission_map")
        view.on_mouse_press((open_map.left + open_map.right) // 2, (open_map.bottom + open_map.top) // 2, 0, 0)
        self.assertEqual(view.window.shown_view.__class__.__name__, "MissionWorldMapView")

    def test_primary_room_actions_keep_missions_in_hangar(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        view._open_hub_room("squad")
        view._perform_primary_hub_action()
        self.assertIsNotNone(view.expanded_agent_sheet_index)
        self.assertFalse(view.cyberware_sheet_open)
        self.assertIsNone(view.window.shown_view)

        view.on_draw()
        cyberware = next(
            hit for hit in view._modal_hits if hit.action == "sheet_cyberware"
        )
        view._dispatch(cyberware.action, cyberware.data)
        self.assertTrue(view.cyberware_sheet_open)

        view._close_agent_sheet()
        self.assertFalse(view.cyberware_sheet_open)
        view._open_hub_room("assets")
        view._perform_primary_hub_action()
        self.assertEqual(view.window.shown_view.__class__.__name__, "MissionWorldMapView")

    def test_b_shortcut_opens_missions_only_inside_hangar(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)

        view._open_hub_room("squad")
        view.on_key_press(management_screen.arcade.key.B, 0)
        self.assertIsNone(view.window.shown_view)

        view._open_hub_room("assets")
        view.on_key_press(management_screen.arcade.key.B, 0)
        self.assertEqual(view.window.shown_view.__class__.__name__, "MissionWorldMapView")

    def test_room_click_starts_fast_transition_and_reduced_motion_skips_it(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        view._hq_reduced_motion = False
        view._open_hub_room("research")
        self.assertEqual(view._room_entry_elapsed, 0.0)
        view.on_update(0.23)
        self.assertGreater(view._room_entry_elapsed, 0.22)

        view._hq_reduced_motion = True
        view._open_hub_room("intel")
        self.assertEqual(view._room_entry_elapsed, 1.0)

    def test_operative_dossier_renders_all_five_integrated_pages(self):
        view = ManagementView(GameState())
        view.window = _FakeWindow()
        view.setup()
        self._seed_interactive_state(view)
        view._open_agent_sheet(0)

        expected_actions = {
            "overview": "dossier_overview_inventory",
            "skills": "sheet_spend_stat",
            "inventory": "dossier_inventory_slot",
            "cyberware": "cyberware_zone",
            "journal": "dossier_journal_section",
        }
        for page, action in expected_actions.items():
            view.dossier_page = page
            view.on_draw()
            self.assertTrue(
                any(hit.action == action for hit in view._modal_hits),
                f"{page} did not expose {action}",
            )


if __name__ == "__main__":
    unittest.main()
